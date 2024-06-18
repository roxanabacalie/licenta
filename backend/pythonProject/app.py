import json
import logging
from datetime import datetime, timedelta
import jwt
from bson import ObjectId
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from pymongo.errors import PyMongoError

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
    if username in users and users[username] == password:
        # If authentication is successful, create and return an access token
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/routes/<route_id>', methods = ['GET'])
def get_route(route_id):
    route_id=str(route_id)
    print("get_route")
    try:
        route = collection.find_one({'_id': ObjectId(route_id)})
        if route:
            route['_id'] = str(route['_id'])
            return jsonify(route), 200
        else:
            return jsonify({'error': 'Route not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
	current_user = get_jwt_identity()
	return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
