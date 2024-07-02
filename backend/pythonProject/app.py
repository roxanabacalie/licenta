import csv
import json
import logging
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO
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

routes_data = [[100, 101, 102, 122, 121, 125, 123, 0, 1, 2, 3, 4, 150, 5, 24, 53, 65, 90, 85, 66, 68, 190, 189, 67, 72, 71, 55, 20, 33, 91, 40, 34, 117, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [148, 166, 170, 184, 23, 22, 66, 90, 189], [100, 101, 102, 122, 121, 125, 123, 1, 2, 3, 4, 5, 24, 53, 65, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182], [78, 79, 50, 41, 26, 116, 27, 28, 47, 48, 29, 150, 30, 8, 136, 134, 115, 12, 13, 14, 138, 143, 139, 46, 45, 44, 43, 42, 178, 179], [136, 134, 9, 129, 10, 168, 31, 32, 69, 40, 119, 20, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [183, 182, 181, 180, 64, 63, 62, 61, 60, 59, 58, 34, 104, 103, 40, 19, 93, 16, 118, 17, 15, 94, 14, 13, 12, 95, 138, 139, 140, 141, 142, 143], [89, 87, 86, 88, 114, 124, 109, 84, 54, 120, 57, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [100, 101, 102, 122, 121, 125, 123, 0, 1, 2, 3, 29, 150, 48, 47, 124, 109, 85, 87, 86, 83, 82, 144, 145, 151, 146, 147], [160, 175, 29, 28, 27, 116, 26, 79, 128, 127, 126], [183, 182, 181, 180, 64, 63, 62, 61, 60, 59, 58, 34, 33, 67, 135, 23, 8, 155, 156, 172, 157, 173, 174, 159, 175], [92, 118, 16, 32, 31, 8, 30, 29, 28, 27, 116, 26, 79, 126, 128, 127], [126, 79, 50, 114, 124, 109, 83, 82, 110, 81, 111, 37, 36], [147, 146, 151, 145, 144, 80, 119, 69, 15, 94, 46, 45], [163, 162, 161, 176, 5, 24, 53, 65, 90, 85, 66, 68, 190, 189, 67, 72, 71, 55, 20, 33, 91, 40, 34, 117, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [150, 48, 47, 7, 22, 70, 21, 55, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [143, 12, 95, 115, 135, 68, 120, 73, 39, 56, 38, 37, 36, 35, 34, 104, 103, 19, 93, 16, 99, 98, 97, 167, 169, 44, 43, 42, 178, 179], [164, 165, 166, 170, 184, 23, 135, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180], [100, 101, 102, 122, 121, 125, 123, 1, 2, 3, 29, 124, 109, 83, 82, 144, 145], [77, 79, 50, 41, 26, 116, 27, 28, 86, 29, 30, 8, 31, 32, 16, 93, 105, 106, 107, 108], [91, 19, 18, 103, 152, 32, 31, 168, 10, 129, 9, 184, 170, 185, 166, 177, 165, 164, 163, 162, 3, 161], [33, 57, 119, 71, 72, 38, 56, 39, 113, 112, 111, 81, 110, 82, 83, 109, 124, 114, 153, 89, 87, 85, 65, 22, 135, 190, 69, 16, 15, 94], [118, 17, 92, 93, 16, 32, 31, 8, 155, 156, 172, 157, 173, 174, 159, 175, 160, 176, 161, 2], [111, 21, 70, 22, 23, 8, 30, 4, 3, 2, 1, 123, 125, 121, 122, 102, 101, 100], [131, 149, 130, 168, 31, 32, 69, 119, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [78, 79, 50, 41, 51, 52, 47, 48, 49, 154, 53, 65, 90, 85, 66, 68, 190, 189, 67, 72, 71, 33, 91, 34, 117, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [108, 107, 106, 105, 99, 98, 97, 169, 45, 46, 14, 13, 12, 115, 8, 30, 5, 24, 6, 54, 71, 81], [76, 79, 26, 116, 27, 28, 86, 29, 30, 184, 149, 131, 137, 186, 171, 132, 133, 94], [188, 187, 58, 34, 104, 103, 93, 16, 167, 169, 44, 43, 42, 178, 179], [179, 178, 42, 43, 44, 45, 46, 14, 13, 12, 115, 8, 30, 29, 28, 27, 116, 26, 41, 51], [100, 101, 102, 122, 121, 125, 123, 0, 1, 164, 165, 177, 166, 185, 170, 184, 11, 95, 12, 13, 14, 138, 143, 139, 46, 45, 44, 43, 42, 178, 179], [50, 79, 25, 51, 52, 49, 53, 65, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [179, 178, 42, 43, 44, 45, 46, 14, 13, 12, 115, 8, 155, 156, 172, 157, 173, 174, 159, 175, 160], [75, 74, 73, 113, 112, 111, 80, 135, 23, 8, 155, 156, 172, 157, 173, 174, 158, 5, 52, 28, 48], [78, 79, 50, 41, 26, 116, 27, 28, 4, 3, 2, 1, 123, 125, 121, 122, 102, 101, 100], [138, 133, 96, 132, 171, 186, 137, 131, 149, 130, 23, 135, 80, 144, 145, 151, 146, 147]]

running_algorithms = {}
executor = ThreadPoolExecutor()

def run_genetic_algorithm(params):
    try:
        population_size = int(params['populationSize'])
        tournament_size = int(params['tournamentSize'])
        crossover_probability = float(params['crossoverProbability'])
        deletion_probability = float(params['deletionProbability'])
        small_mutation_probability = float(params['smallMutationProbability'])
        number_of_generations = int(params['numberOfGenerations'])
        elite_size = int(params['eliteSize'])

        print("Running genetic algorithm with params:", params)

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
        print("Running genetic algorithm finished")
        return "Genetic algorithm finished."
    except Exception as e:
        print("Error running genetic algorithm:", e)
        return str(e)

@app.route('/api/run-algorithm', methods=['POST'])
def trigger_algorithm():
    data = request.get_json()
    future = executor.submit(run_genetic_algorithm, data)
    running_algorithms[future] = data
    return jsonify({"message": "Genetic algorithm started."}), 200


def monitor_algorithm_completion(future):
    try:
        result = future.result()
        params = running_algorithms.pop(future)
        socketio.emit('algorithm_complete', {
            "message": "Genetic algorithm finished successfully.",
            "result": result,
            "params": params
        })

    except Exception as e:
        print(f"Algorithm execution error: {str(e)}")

def monitor_running_algorithms():
    while True:
        for future in list(running_algorithms.keys()):
            if future.done():
                monitor_algorithm_completion(future)

        time.sleep(1)


monitor_thread = threading.Thread(target=monitor_running_algorithms)
monitor_thread.start()

socketio.init_app(app)


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
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/routes', methods=['GET'])
def get_routes():
    try:
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
            return jsonify(routes_data), 200

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


