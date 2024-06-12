import json

from bson import ObjectId
from pymongo import MongoClient

# Conectarea la MongoDB
client = MongoClient('mongodb+srv://ioanaroxanabacalie:XNZ9IwfAmyRjju3y@cluster0.ulbfdch.mongodb.net/')
db = client['licenta']
collection = db['routes']

filepath = 'directions.json'
with open(filepath, 'r') as file:
            data = json.load(file)
            print(data)
            collection.insert_one({"directions": data})
def get_route_data(start_lat, start_lng, end_lat, end_lng):
    # Căutarea rutei în baza de date
    route = collection.find_one({
        "_id": ObjectId("6660a679c1653b524b6e73cb")
    }, {"_id": 0})
    return route if route else "Ruta nu a fost găsită"

start_lat = 47.19052
start_lng = 27.55848
end_lat = 47.19100
end_lng = 27.56000

route_data = get_route_data(start_lat, start_lng, end_lat, end_lng)
print(route_data)
