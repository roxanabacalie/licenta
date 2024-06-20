import json
import logging
from bson import ObjectId
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient

from models import verify_account

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


routes_data = [
    [160, 175, 159, 174, 173, 157, 172, 156, 155, 8, 23, 135, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [100, 101, 102, 122, 121, 125, 123, 1, 2, 3, 70, 21, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [26, 116, 27, 52, 49, 53, 65, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [141, 140, 139, 94, 15, 16, 93, 103, 104, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [92, 93, 16, 32, 31, 8, 30, 4, 3, 2, 1, 123, 125, 121, 122, 102, 101],
    [137, 131, 149, 130, 168, 31, 32, 104, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [100, 101, 102, 122, 121, 125, 123, 1, 2, 3, 124, 109, 83, 82, 144, 145, 151, 146, 147],
    [146, 151, 145, 144, 39, 56, 38, 37, 36, 35, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [119, 69, 32, 31, 168, 10, 129, 9, 184, 170, 166, 165, 164],
    [14, 13, 12, 95, 11, 184, 170, 166, 165, 164, 1, 123, 125, 121, 122, 102, 101, 100],
    [78, 79, 26, 116, 27, 28, 29, 30, 184, 169, 44, 43, 42, 178, 179],
    [163, 162, 161, 176, 5, 54, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183, 33],
    [164, 165, 166, 170, 184, 23, 135, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183],
    [153, 114, 124, 109, 84, 67, 33, 34, 58, 59, 60, 61, 62, 63, 64, 180, 181, 182, 183, 136, 115],
    [39, 56, 38, 37, 36, 35, 34, 104, 103, 93, 16, 167, 169, 44, 43, 42, 178, 27],
    [56, 39, 120, 54, 5, 4, 3, 2, 1, 123, 125, 121, 122, 102, 101, 100],
    [147, 146, 151, 145, 144, 135, 23, 8, 155, 156, 172, 157, 173, 174, 159, 175, 160],
    [14, 13, 12, 115, 8, 30, 29, 28, 27, 116, 26, 79, 77],
    [100, 101, 102, 122, 121, 125, 123, 1, 164, 165, 166, 170, 46, 45, 44, 43, 42, 178, 179],
    [92, 93, 16, 32, 31, 8, 155, 156, 172, 157, 173, 174, 159, 175, 160]
]




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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
