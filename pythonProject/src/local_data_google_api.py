import requests
from datetime import datetime, timedelta, timezone


def get_timestamp_for_5pm():
	# Obține data curentă
	today = datetime.now().date() + timedelta(days=1)

	# Setează ora la 5 PM ora României (UTC+3)
	five_pm_romania = datetime(today.year, today.month, today.day, 8, 50, tzinfo=timezone(timedelta(hours=3)))

	# Convertește în timestamp de la epoch (midnight, January 1, 1970 UTC)
	timestamp = int(five_pm_romania.timestamp())

	return timestamp


def get_distance_matrix(origin_lat, origin_lng, dest_lat, dest_lng, api_key, departure_time):
	url = "https://maps.googleapis.com/maps/api/distancematrix/json"
	params = {
		"origins": f"{origin_lat},{origin_lng}",
		"destinations": f"{dest_lat},{dest_lng}",
		"key": api_key,
		"departure_time": departure_time,
		"traffic_model": "best_guess",
		"mode": "driving"
	}
	response = requests.get(url, params=params)
	data = response.json()
	return data


# Exemplu de utilizare
origin_lat = 47.1585
origin_lng = 27.6014
dest_lat = 47.1749
dest_lng = 27.5723
api_key = "AIzaSyAL9n-iu4Ata_D057iAE-Fo2sly5rhuZiA"

# Obține timestamp-ul pentru ora 5 PM ora României
departure_time = get_timestamp_for_5pm()

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
