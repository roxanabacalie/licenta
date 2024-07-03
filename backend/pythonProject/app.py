import concurrent
import csv
import json
import logging
import multiprocessing
import signal
import threading
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO
from db_management import ga_runs, users
from db_management.users import verify_account
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.initial_solution import TransitNetwork

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
jwt = JWTManager(app)
logging.basicConfig(level=logging.DEBUG)

iasi_transit_network = TransitNetwork(
		191,
		"data/iasi/Iasi_links.txt",
		"data/iasi/Iasi_demand.txt"
	)

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
            120
        )
        result_file = ga_iasi.run_genetic_algorithm()
        stop_timestamp = datetime.now()
        print(stop_timestamp)
        ga_runs.update_stop_timestamp(run_id, stop_timestamp)
        ga_runs.update_percent_complete(run_id, 100)
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
        return str(e)


@app.route('/api/run-algorithm', methods=['POST'])
@jwt_required()
def trigger_algorithm():
    data = request.get_json()
    user_id = get_jwt_identity()
    print(user_id)
    data['user_id'] = user_id
    future = executor.submit(run_genetic_algorithm, data)
    running_algorithms[future] = data
    return jsonify({"message": "Genetic algorithm started."}), 200


def monitor_algorithm_completion(future):
    try:
        result = future.result()
        params = running_algorithms.pop(future)
        socketio.emit('algorithm_complete', {
            "message": "Genetic algorithm finished successfully.",
            "routes": result,  # Send the routes data to the frontend
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


monitor_thread = threading.Thread(target=monitor_running_algorithms)
monitor_thread.start()

socketio.init_app(app)

@app.route('/api/cancel-algorithm', methods=['POST'])
@jwt_required()
def cancel_algorithm():
    user_id = get_jwt_identity()
    pid = ga_runs.get_pid_by_userid(user_id)
    try:
        if pid:
            # Terminate the process using psutil
            process = psutil.Process(int(pid))
            process.terminate()
            process.wait()  # Wait for the process to terminate

            # Find and cancel the corresponding future
            for future, params in list(running_algorithms.items()):
                if params['user_id'] == user_id:
                    future.cancel()
                    running_algorithms.pop(future, None)
                    break
            return jsonify({'message': f'Process with PID {pid} terminated.'}), 200
        else:
            return jsonify({'error': f'No PID found for user_id {user_id}.'}), 404
    except psutil.NoSuchProcess:
        return jsonify({'error': f'No process found with PID {pid}.'}), 404
    except psutil.AccessDenied:
        return jsonify({'error': 'Access denied when trying to terminate the process.'}), 403
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


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

    if verify_account(username, password):
        user_id = users.get_userid_by_username(username)
        access_token = create_access_token(identity=user_id)
        return jsonify({'access_token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/routes', methods=['GET'])
def get_routes():
    try:
        filename = ga_runs.get_last_filename()
        with open(filename, 'r') as f:
            data = json.load(f)
        routes_data = data["best_individual"]
        routes = []
        for idx, route in enumerate(routes_data):
            route_dict = {'id': idx + 1, 'stops': route}
            routes.append(route_dict)

        return jsonify(routes), 200
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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, use_reloader=True, allow_unsafe_werkzeug=True)


