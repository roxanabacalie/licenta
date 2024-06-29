import csv
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from db_management.users import verify_account

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'  # MySQL database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, 'templates')
app.template_folder = template_folder

# Configuration
app.config['SECRET_KEY'] = 'your_strong_secret_key'
app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Conectarea la MongoDB
client = MongoClient('mongodb+srv://ioanaroxanabacalie:XNZ9IwfAmyRjju3y@cluster0.ulbfdch.mongodb.net/')
db = client['licenta']
collection = db['routes']

# JWT Initialization
jwt = JWTManager(app)

users = {
    "test": "test"
}

logging.basicConfig(level=logging.DEBUG)


routes_data = [[160, 175, 159, 174, 173, 157, 172, 156, 155, 7, 8, 136, 143, 138, 134, 23, 135, 97, 99, 98, 20, 66, 86, 88, 89, 87, 90, 85, 68, 190, 189, 71, 73, 75, 74, 72, 80, 67, 17, 118, 18, 19, 40, 152, 91, 33, 34, 117, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [101, 102, 122, 121, 125, 123, 1, 2, 3, 4, 30, 8, 31, 32, 152, 99], [183, 182, 181, 180, 64, 63, 62, 61, 60, 59, 58, 34, 104, 103, 93, 16, 15, 94, 133, 132, 171], [143, 142, 141, 140, 139, 94, 15, 16, 93, 103, 104, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [77, 147, 146, 151, 145, 144, 135, 23, 130, 149, 131, 137], [170, 148, 186, 171, 137, 131, 149, 130, 168, 31, 32, 104, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [99, 66, 89, 50, 100, 101, 102, 122, 121, 125, 123, 0, 1, 2, 3, 48, 124, 109, 47, 6, 83, 82, 144, 145, 151, 146, 147, 126, 127, 128, 76], [147, 146, 151, 145, 144, 135, 23, 8, 155, 156, 172, 157, 173], [40, 119, 69, 32, 31, 168, 10, 129, 9, 7, 184, 170, 148, 166, 177, 165, 164, 163, 2], [134, 139, 17, 14, 13, 12, 95, 11, 184, 170, 148, 166, 177, 165, 164, 1, 0, 123, 125, 121, 122, 102, 101, 100, 50, 79], [128, 127, 126, 78, 79, 26, 116, 27, 28, 29, 30, 184, 169, 44, 43, 42, 178, 179], [164, 163, 162, 161, 176, 5, 150, 54, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [183, 182, 181, 180, 64, 63, 62, 61, 60, 59, 58, 34, 33, 67, 135, 23, 8, 155, 156, 172, 157, 173, 174, 158], [89, 88, 50, 153, 114, 48, 124, 87, 86, 85, 90, 109, 47, 6, 84, 66, 152, 68, 98, 99, 97, 71, 73, 75, 74, 72, 80, 189, 190, 67, 20, 134, 138, 143, 136, 18, 118, 19, 33, 91, 34, 117, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [176, 84, 47, 69, 189, 92, 74, 39, 56, 38, 37, 36, 35, 34, 104, 103, 93, 16, 167, 169, 44, 43, 42, 178, 179, 108, 107, 106, 105, 20, 66, 152], [20, 38, 56, 39, 120, 54, 47, 48, 5, 150, 4, 3, 2, 1, 0, 123, 125, 121, 122, 102, 101, 100, 41], [75, 74, 147, 146, 151, 145, 144, 17, 143, 138, 118, 19, 91, 152, 40, 18, 20, 98, 117, 99, 97, 66, 189, 190, 71, 73, 80, 72, 68, 86, 88, 89, 87, 90, 85, 135, 23, 134, 136, 8, 7, 155, 156, 172, 157, 173, 174, 159, 175, 160], [14, 13, 12, 115, 8, 7, 30, 150, 29, 48, 28, 27, 116, 26, 79, 77, 126, 127, 128], [188, 187, 58, 34, 33, 67, 135, 23, 8, 155, 156, 172, 157, 173], [33, 118, 92, 93, 16, 32, 31, 8, 7, 155, 156, 172, 157, 173, 174, 159, 175, 160, 176, 90, 89, 50], [160, 175, 159, 174, 173, 157, 172, 156, 155, 8, 23, 135, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181], [183, 182, 181, 180, 64, 63, 62, 61, 60, 59, 58, 34, 33, 67, 21, 70, 3, 2, 1, 123, 125, 121, 122, 102, 101], [6, 90, 5, 158, 150, 48, 47, 82, 110, 81, 111, 37, 36, 35, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [100, 101, 102, 122, 121, 125, 123, 1, 164, 165, 166, 170, 46, 45, 44, 43], [99, 71, 73, 34, 33, 119, 68, 86, 41, 26, 116, 27, 28, 29, 30, 8, 31, 32, 15, 94, 138, 118, 69, 190, 88], [119, 74, 83, 90, 72, 21, 70, 22, 23, 8, 155, 156, 172, 157, 173, 174, 158, 5, 30, 175, 114, 3, 161], [160, 175, 159, 174, 173, 157, 172, 156, 155, 8, 23, 135, 67, 33, 34], [128, 79, 51, 52, 49, 53, 65, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181], [55, 120, 57, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [172, 156, 155, 8, 23, 135, 71], [5, 150, 48, 47, 7, 9, 129, 10, 168, 31, 32, 104, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183], [128, 127, 126, 76, 79, 26, 116, 27, 28, 29, 30, 184, 149, 131, 137, 186, 171, 132, 133, 96], [79, 25, 50, 100, 101, 102, 122, 121, 125, 123, 0, 1, 2, 3, 4, 174, 173, 157, 172, 156, 155, 7, 40, 57, 20, 21, 32], [73, 74, 113, 112, 111, 135, 23, 8, 155, 156, 172, 157, 173, 174, 159, 175, 160], [99, 69, 65, 53, 154, 47, 6, 24, 5, 150, 4, 3, 2, 1, 0, 123, 125, 121, 122, 102, 101, 100, 25]]

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
        '''
        try:
            collection.insert_one({"directions": data})
        except PyMongoError as mongo_error:
            logging.error(f"MongoDB Error: {str(mongo_error)}")
            return jsonify({"error": f"MongoDB Error: {str(mongo_error)}"}), 500
        '''
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
def get_route():
    start_id = request.args.get('start_id')
    stop_id = request.args.get('stop_id')

    try:
        if start_id and stop_id:
            # Construct file path for the specific route based on start_id and stop_id
            file_path = f"data/iasi/directions/directions_{start_id}_{stop_id}.json"
            # Check if the file exists before attempting to open it
            if not os.path.isfile(file_path):
                return jsonify({'error': f'Route file not found for start_id={start_id}, stop_id={stop_id}'}), 404

            # Load route data from the JSON file
            with open(file_path, 'r') as file:
                route = json.load(file)
                return jsonify(route), 200

        else:
            # Handle request to fetch all routes (routes_data needs to be defined)
            return jsonify(routes_data), 200

    except ValueError as ve:
        return jsonify({'error': f'Invalid value: {str(ve)}'}), 400
    except FileNotFoundError:
        return jsonify({'error': f'Route file not found for start_id={start_id}, stop_id={stop_id}'}), 404
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/protected', methods=['GET'])
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
