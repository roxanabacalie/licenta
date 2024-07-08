import concurrent
import csv
import json
import logging
import multiprocessing
import re
import threading
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from flask_socketio import SocketIO
import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from db_management import ga_runs, users
from db_management.ga_runs import delete_ga_run, find_user_id, get_running_ga_run_by_user_id, update_process_id, \
     get_running_pid_by_user_id, delete_ga_run_by_user_id
from db_management.users import verify_account
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.initial_solution import TransitNetwork
from src.data_processing.files_handler import read_travel_info, update_links_file, update_demands_file, remove_link, \
    read_default_file, write_default_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, 'templates')
app.template_folder = template_folder
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SECRET_KEY'] = 'your_strong_secret_key'
app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
jwt = JWTManager(app)
logging.basicConfig(level=logging.DEBUG)



#'''
iasi_transit_network = TransitNetwork(
    191,
    "data/iasi/Iasi_links.txt",
    "data/iasi/Iasi_demand.txt"
)
#'''
'''
iasi_transit_network = TransitNetwork (
    40,
    "data/iasi/Iasi_30stops_links.txt",
"data/iasi/Iasi_30stops_demand.txt")
'''


running_processes={}
running_algorithms = {}
executor = ProcessPoolExecutor()

def run_genetic_algorithm(params):
    try:
        print("Running genetic algorithm with params:", params)
        process_id = multiprocessing.current_process().pid
        start_timestamp = datetime.now()
        user_id = int(params['user_id'])
        run_id = ga_runs.insert_ga_run(None, process_id, start_timestamp, None, 0, user_id)

        population_size = int(params['populationSize'])
        tournament_size = int(params['tournamentSize'])
        crossover_probability = float(params['crossoverProbability'])
        deletion_probability = float(params['deletionProbability'])
        small_mutation_probability = float(params['smallMutationProbability'])
        number_of_generations = int(params['numberOfGenerations'])
        elite_size = int(params['eliteSize'])
        #'''
        ga_iasi = GeneticAlgorithm(
            population_size,
            tournament_size,
            crossover_probability,
            deletion_probability,
            small_mutation_probability,
            number_of_generations,
            iasi_transit_network,
            elite_size,
            35,
            60,
            120,
            user_id
        )
        #'''

        '''
        ga_iasi = GeneticAlgorithm(
            population_size,
            tournament_size,
            crossover_probability,
            deletion_probability,
            small_mutation_probability,
            number_of_generations,
            iasi_transit_network,
            elite_size,
            9,
            60,
            120,
            user_id
        )
        '''


        result_file = ga_iasi.run_genetic_algorithm()
        stop_timestamp = datetime.now()
        print(stop_timestamp)
        ga_runs.update_stop_timestamp(run_id, stop_timestamp)
        print(result_file)
        ga_runs.update_filename(run_id, result_file)
        print("Running genetic algorithm finished")

        with open(result_file, 'r') as f:
            data = json.load(f)
            routes_data = data["best_individual"]

        routes = []
        for idx, route in enumerate(routes_data):
            route_dict = {'id': idx + 1, 'stops': route}
            routes.append(route_dict)

        return routes
    except Exception as e:
        print("Error running genetic algorithm:", e)
        traceback.print_exc()
        return str(e)


def monitor_algorithm_completion(future):
    try:
        print("algorithm completion")
        result = future.result()
        params = running_algorithms.pop(future)
        socketio.emit('algorithm_complete', {
            "message": "Genetic algorithm finished successfully.",
            "routes": result,
            "params": params
        })
    except concurrent.futures.CancelledError:
        print("Algorithm execution was cancelled.")
    except concurrent.futures.process.BrokenProcessPool as e:
        print("Algorithm execution was cancelled by termination.")
        traceback.print_exc()
    except Exception as e:
        print(f"Algorithm execution error: {str(e)}")
        traceback.print_exc()

def monitor_running_algorithms():
    while True:
        for future in list(running_algorithms.keys()):
            if future.done():
                monitor_algorithm_completion(future)
        time.sleep(1)


@app.route('/api/travel-info', methods=['GET'])
def get_travel_info():
    from_station = int(request.args.get('from'))
    to_station = int(request.args.get('to'))

    if from_station == to_station:
        result = {
            'travel_time': 0,
            'demand': 0
        }
        return jsonify(result)
    else:
        travel_times, demands = read_travel_info()
        travel_time = next(
            (item['travel_time'] for item in travel_times if item['from'] == from_station and item['to'] == to_station),
            None)
        demand = next((item['demand'] for item in demands if item['from'] == from_station and item['to'] == to_station),
                      None)

        if travel_time is None:
            travel_time_display = "infinit"
        else:
            travel_time_display = travel_time

        result = {
            'travel_time': travel_time_display,
            'demand': demand
        }
        return jsonify(result)


@app.route('/api/travel-info', methods=['POST'])
def update_travel_info():
    data = request.json
    try:
        if data['travelTime'] != 'infinit':
            data['travelTime'] = int(data['travelTime'])
    except ValueError:
        return jsonify({'error': 'travelTime must be an integer'}), 400
    if data['travelTime'] != 'infinit' and data['travelTime'] <= 0:
        return jsonify({'error': 'travelTime must be an integer greater than 0'}), 400

    try:
        data['demand'] = int(data['demand'])
    except ValueError:
        return jsonify({'error': 'demand must be an integer'}), 400
    if data['demand'] < 0:
        return jsonify({'error': 'demand must be an integer greater than or equal to 0'}), 400

    from_station = int(data['from'])
    to_station = int(data['to'])

    demand = int(data['demand'])
    if data['travelTime'] != 'infinit':
        travel_time = int(data['travelTime'])
        update_links_file('data/iasi/Iasi_links.txt', from_station, to_station, travel_time)
    else:
        remove_link('data/iasi/Iasi_links.txt', from_station, to_station)
    update_demands_file('data/iasi/Iasi_demand.txt', from_station, to_station, demand)
    if os.path.isfile("data/Iasi/Iasi_links_initial_population.json"):(
        os.remove("data/Iasi/Iasi_links_initial_population.json"))
    return jsonify({'message': 'Travel times updated successfully.'}), 200


@app.route('/api/run-algorithm', methods=['POST'])
@jwt_required()
def trigger_algorithm():
    data = request.get_json()
    user_id = get_jwt_identity()
    print(user_id)
    data['user_id'] = user_id

    try:
        data['populationSize'] = int(data['populationSize'])
    except ValueError:
        return jsonify({'error': 'populationSize must be an integer'}), 400

    if data['populationSize'] < 5:
        return jsonify({'error': 'populationSize must be an integer greater than or equal to 5'}), 400

    try:
        data['tournamentSize'] = int(data['tournamentSize'])
    except ValueError:
        return jsonify({'error': 'tournamentSize must be an integer'}), 400

    if data['tournamentSize'] < 2:
        return jsonify({'error': 'tournamentSize must be an integer greater than or equal to 2'}), 400

    crossover_probability = data.get('crossoverProbability')
    if not re.match(r'^[0-9]*\.?[0-9]+$', str(crossover_probability)) or not (0 <= float(crossover_probability) <= 1):
        return jsonify({'error': 'crossoverProbability must be a float between 0 and 1'}), 400

    deletion_probability = data.get('deletionProbability')
    if not re.match(r'^[0-9]*\.?[0-9]+$', str(deletion_probability)) or not (0 <= float(deletion_probability) <= 1):
        return jsonify({'error': 'deletionProbability must be a float between 0 and 1'}), 400

    small_mutation_probability = data.get('smallMutationProbability')
    if not re.match(r'^[0-9]*\.?[0-9]+$', str(small_mutation_probability)) or not (
            0 <= float(small_mutation_probability) <= 1):
        return jsonify({'error': 'smallMutationProbability must be a float between 0 and 1'}), 400

    try:
        data['numberOfGenerations'] = int(data['numberOfGenerations'])
    except ValueError:
        return jsonify({'error': 'numberOfGenerations must be an integer'}), 400

    if data['numberOfGenerations'] < 0:
        return jsonify({'error': 'numberOfGenerations must be an integer greater than or equal to 0'}), 400

    try:
        data['eliteSize'] = int(data['eliteSize'])
    except ValueError:
        return jsonify({'error': 'eliteSize must be an integer'}), 400

    if data['eliteSize'] < 1:
        return jsonify({'error': 'eliteSize must be an integer greater than or equal to 1'}), 400


    print("Data validated successfully:", data)
    future = executor.submit(run_genetic_algorithm, data)
    running_algorithms[future] = data
    return jsonify({"message": "Genetic algorithm started."}), 200


@app.route('/api/cancel-algorithm', methods=['POST'])
@jwt_required()
def cancel_algorithm():
    user_id = get_jwt_identity()
    print(f"Canceling algorithm for user_id: {user_id}")
    process_id = get_running_pid_by_user_id(int(user_id))
    delete_ga_run_by_user_id(int(user_id))
    if process_id:
        try:
            psutil_process = psutil.Process(int(process_id))
            psutil_process.terminate()
            psutil_process.wait()
            for future, params in list(running_algorithms.items()):
                if params['user_id'] == user_id:
                    future.cancel()
                    running_algorithms.pop(future, None)
                    break

            return jsonify({'message': f'Process with PID {process_id} terminated.'}), 200
        except psutil.NoSuchProcess as e:
            print(f'Error: No process found with PID {process_id}. Details: {str(e)}')
            return jsonify({'error': f'No process found with PID {process_id}.'}), 404
        except psutil.AccessDenied as e:
            print(f'Error: Access denied when trying to terminate the process. Details: {str(e)}')
            return jsonify({'error': 'Access denied when trying to terminate the process.'}), 403
        except Exception as e:
            print(f'Error: Unexpected error occurred: {str(e)}')
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    else:
        return jsonify({'error': f'No running process found for user_id {user_id}.'}), 404



@app.route('/directions', methods=['POST'])
def save_directions():
    data = request.get_json()
    try:
        start_id = data.get('start_id')
        stop_id = data.get('stop_id')
        if not start_id or not stop_id:
            logging.error("Missing start_id or stop_id in the data")
            return jsonify({"error": "Missing start_id or stop_id in the data"}), 400

        filename = f'data/iasi/directions/directions_{start_id}_{stop_id}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        logging.error(f"General Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        return jsonify({'message': 'Numele de utilizator trebuie să conțină doar litere, '
                                   'cifre, cratime și underscore și să aibă între 3 și 20 de caractere.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Parola trebuie să aibă cel puțin 8 caractere.'}), 400

    if verify_account(username, password):
        user_id = users.get_userid_by_username(username)
        access_token = create_access_token(identity=user_id)
        return jsonify({'access_token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/is-algorithm-running', methods=['GET'])
@jwt_required()
def is_algorithm_running():
    user_id = get_jwt_identity()
    if user_id in running_processes and running_processes[user_id].is_alive():
        return jsonify({'running': True}), 200
    else:
        return jsonify({'running': False}), 200


@app.route('/api/routes', methods=['GET'])
def get_routes():
    try:
        print("sunt in ruta")
        filename_param = request.args.get('filename', type=str)
        print(filename_param)
        if filename_param:
            filename = filename_param
        else:
            with open('default_file.txt', 'r') as f:
                filename =str(f.readline().strip())
        with open(filename, 'r') as f:
            data = json.load(f)
        routes_data = data["best_individual"]
        routes = []
        for idx, route in enumerate(routes_data):
            route_dict = {'id': idx + 1, 'stops': route}
            routes.append(route_dict)
        return jsonify(routes), 200
    except FileNotFoundError as e:
        print(f"File not found: {str(e)}")
        return jsonify({'error': f'Fișierul "{filename}" nu a fost găsit.'}), 404

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return jsonify({'error': f'Eroare în decodarea fișierului JSON: {str(e)}'}), 500

    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/set_default_file', methods=['POST'])
def set_default_file_route():
    try:
        new_default_file = request.json.get('filename')
        if not isinstance(new_default_file, str):
            raise ValueError('Numele fișierului trebuie să fie un șir de caractere.')
        write_default_file(new_default_file)
        return jsonify({'message': f'Fișierul implicit a fost setat la "{new_default_file}"'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/directions', methods=['GET'])
def get_direction():
    start_id = request.args.get('start_id')
    stop_id = request.args.get('stop_id')
    try:
        if start_id and stop_id:
            file_path = f"data/iasi/directions/directions_{start_id}_{stop_id}.json"
            if not os.path.isfile(file_path):
                return jsonify({'error': f'Route file not found for start_id={start_id}, stop_id={stop_id}'}), 404
            with open(file_path, 'r') as file:
                route = json.load(file)
                return jsonify(route), 200
        else:
            return None
    except ValueError as ve:
        return jsonify({'error': f'Invalid value: {str(ve)}'}), 400
    except FileNotFoundError:
        return jsonify({'error': f'Route file not found for start_id={start_id}, stop_id={stop_id}'}), 404
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/edit-routes', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/api/stops', methods=['GET'])
def get_stops():
    stops = []
    try:
        with open('data/iasi/iasi_filtered_stops_data.csv', mode='r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                stop = {
                    "stop_id": row['Stop ID'],
                    "stop_name": row['Stop Name'],
                    "stop_lat": float(row['Stop Latitude']),
                    "stop_lon": float(row['Stop Longitude'])
                }
                stops.append(stop)
        return jsonify(stops), 200
    except FileNotFoundError:
        return jsonify({'error': 'Stops file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        files = ga_runs.get_files()
        print(files)
        return jsonify(files)
    except Exception as err:
        print("Error: ", err)
        return jsonify([]), 500

monitor_thread = threading.Thread(target=monitor_running_algorithms)
monitor_thread.start()
socketio.init_app(app)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, use_reloader=True, allow_unsafe_werkzeug=True)