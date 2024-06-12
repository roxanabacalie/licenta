import json
import requests
from datetime import datetime, timedelta, timezone

def get_timestamp(hours, minutes):
    today = datetime.now().date() + timedelta(days=1)
    five_pm_romania = datetime(today.year, today.month, today.day, hours, minutes, tzinfo=timezone(timedelta(hours=3)))
    timestamp = int(five_pm_romania.timestamp())
    return timestamp

def get_directions(origin_lat, origin_lon, destination_lat, destination_lon, api_key, departure_time):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin_lat},{origin_lon}",
        "destination": f"{destination_lat},{destination_lon}",
        "key": api_key,
        "departure_time": departure_time,
        "mode": "driving"
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Build the JSON object with the desired structure
    result = {
        "geocoded_waypoints": [],
        "routes": [],
        "status": "",
        "request": {
            "origin": {
                "location": {
                    "lat": origin_lat,
                    "lng": origin_lon
                }
            },
            "destination": {
                "location": {
                    "lat": destination_lat,
                    "lng": destination_lon
                }
            },
            "travelMode": "driving"
        }
    }

    # Copy geocoded_waypoints if present
    if "geocoded_waypoints" in data:
        result["geocoded_waypoints"] = data["geocoded_waypoints"]

    # Copy routes if present
    if "routes" in data:
        result["routes"] = data["routes"]

    # Copy status if present
    if "status" in data:
        result["status"] = data["status"]

    return result


def save_directions_list_to_file(directions_list, filename):
    with open(filename, 'w') as f:
        json.dump(directions_list, f, indent=4)


'''
def get_distance_matrix(origin_lat, origin_lng, dest_lat, dest_lng, api_key, departure_time):
	url = "https://maps.googleapis.com/maps/api/distancematrix/json"
	params = {
		"origins": f"{origin_lat},{origin_lng}",
		"destinations": f"{dest_lat},{dest_lng}",
		"key": api_key,
		"departure_time": departure_time,
		"traffic_model": "best_guess",
		"mode": "DRIVING"
	}
	response = requests.get(url, params=params)
	data = response.json()
	return data
'''

# Exemplu de utilizare
origin_coords = [
	(47.1585, 27.6014),
	(47.1685, 27.6014)
]

dest_coords = [
	(47.1749, 27.5723),
	(47.1849, 27.5423)
]

api_key = "AIzaSyAL9n-iu4Ata_D057iAE-Fo2sly5rhuZiA"

directions_list = []
departure_time = get_timestamp(3, 30)

for origin in origin_coords:
    for dest in dest_coords:
        if origin != dest:  # Evită cererile de la un punct la el însuși
            directions_data = get_directions(origin[0], origin[1], dest[0], dest[1], api_key, departure_time)
            directions_list.append(directions_data)

save_directions_list_to_file(directions_list, '../../static/directions_data_list.json')

'''
distance_matrix = get_distance_matrix(origin_lat, origin_lng, dest_lat, dest_lng, api_key, departure_time)
print(distance_matrix)

# Preluarea datelor
if distance_matrix['status'] == 'OK':
	distance = distance_matrix['rows'][0]['elements'][0]['distance']['text']
	duration = distance_matrix['rows'][0]['elements'][0]['duration']['text']
	print(f"Distanța: {distance}")
	print(f"Timpul de călătorie: {duration}")
else:
	print("Nu s-au putut obține informațiile de la API.")
'''
