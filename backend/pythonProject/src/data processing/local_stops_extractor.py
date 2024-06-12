import csv
import requests

class Stop:
    def __init__(self, stop_id, stop_name, stop_lat, stop_lon):
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon

class Trip:
    def __init__(self, trip_id, route_id, route_short_name, route_long_name, trip_headsign, direction_id, block_id, shape_id):
        self.trip_id = trip_id
        self.route_id = route_id
        self.route_short_name = route_short_name
        self.route_long_name = route_long_name
        self.trip_headsign = trip_headsign
        self.direction_id = direction_id
        self.block_id = block_id
        self.shape_id = shape_id
        self.stops = []

class Route:
    def __init__(self, route_id, route_short_name, route_long_name):
        self.route_id = route_id
        self.route_short_name = route_short_name
        self.route_long_name = route_long_name

def connect_stops_to_trips(stops_data, stop_times_data, trips_data, routes_data):
    connected_trips = {}
    for id, trip_info in trips_data.items():
        trip_id = trip_info['trip_id']
        route_id = trip_info['route_id']
        trip_headsign = trip_info['headsign']
        direction_id = trip_info['direction_id']
        block_id = trip_info['block_id']
        shape_id = trip_info['shape_id']
        route_info = routes_data.get(route_id)
        route_short_name = route_info.get('route_short_name', '')
        route_long_name = route_info.get('route_long_name', '')
        trip = Trip(trip_id, route_id, route_short_name, route_long_name, trip_headsign, direction_id, block_id, shape_id)

        if trip_id in stop_times_data:
            for stop_id, stop_sequence in stop_times_data[trip_id]:
                stop_info = stops_data.get(stop_id)
                if stop_info:
                    stop = Stop(stop_id, stop_info['name'], stop_info['lat'], stop_info['lon'])
                    trip.stops.append((stop, stop_sequence))
        connected_trips[trip_id] = trip
    return connected_trips

def fetch_data(api_url, headers):
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error: Failed to fetch data. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

def build_stops_data(stops):
    stops_data = {}
    for stop in stops:
        stop_id = stop['stop_id']
        stop_name = stop['stop_name']
        stop_lat = stop['stop_lat']
        stop_lon = stop['stop_lon']
        stops_data[stop_id] = {
            'name': stop_name,
            'lat': stop_lat,
            'lon': stop_lon
        }
    return stops_data

def build_routes_data(routes):
    routes_data = {}
    for route in routes:
        route_id = route['route_id']
        route_short_name = route['route_short_name']
        route_long_name = route['route_long_name']
        routes_data[route_id] = {
            'route_short_name': route_short_name,
            'route_long_name': route_long_name
        }
    return routes_data


def build_stop_times_data(stop_times):
    stop_times_data = {}
    for stop_time in stop_times:
        trip_id = stop_time['trip_id']
        stop_id = stop_time['stop_id']
        stop_sequence = stop_time['stop_sequence']
        if trip_id not in stop_times_data:
            stop_times_data[trip_id] = []
        stop_times_data[trip_id].append((stop_id, stop_sequence))
        stop_times_data[trip_id].sort(key=lambda x: x[1])
    return stop_times_data

def build_trips_data(trips):
    trips_data = {}
    for trip in trips:
        route_id = trip['route_id']
        trip_id = trip['trip_id']
        trip_headsign = trip['trip_headsign']
        direction_id = trip['direction_id']
        block_id = trip['block_id']
        shape_id = trip['shape_id']
        trips_data[trip_id] = {
            'route_id': route_id,
            'trip_id': trip_id,
            'headsign': trip_headsign,
            'direction_id': direction_id,
            'block_id': block_id,
            'shape_id': shape_id
        }
    return trips_data

def save_stops_to_csv(stops_data, file_name):
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Stop ID', 'Stop Name', 'Stop Latitude', 'Stop Longitude'])
        for stop in stops_data:
            writer.writerow([stop['stop_id'], stop['stop_name'], stop['stop_lat'], stop['stop_lon']])


api_url_stops = "https://api.tranzy.ai/v1/opendata/stops"
api_url_stop_times = "https://api.tranzy.ai/v1/opendata/stop_times"
api_url_trips = "https://api.tranzy.ai/v1/opendata/trips"
api_url_routes = "https://api.tranzy.ai/v1/opendata/routes"

headers = {
    "Accept": "application/json",
    "X-API-KEY": "J0g4leUL612yf4gUCt9kh3k3UZ7WsAxF7rkZIOEz",
    "X-Agency-Id": "1"
}


stops = fetch_data(api_url_stops, headers)
stop_times = fetch_data(api_url_stop_times, headers)
trips = fetch_data(api_url_trips, headers)
routes = fetch_data(api_url_routes, headers)


stops_data = build_stops_data(stops)
stop_times_data = build_stop_times_data(stop_times)
trips_data = build_trips_data(trips)
routes_data = build_routes_data(routes)

csv_file_name = '../../data/iasi/iasi_all_stops_data.csv'
save_stops_to_csv(stops, csv_file_name)

connected_trips = connect_stops_to_trips(stops_data, stop_times_data, trips_data, routes_data)
for trip_id, trip in connected_trips.items():
    print(f"Trip ID: {trip.trip_id}, Route ID: {trip.route_id}, Route Short Name: {trip.route_short_name}, Route Long Name: {trip.route_long_name}, Trip Headsign: {trip.trip_headsign}")
    print("Stops:")
    for stop, sequence in trip.stops:
        print(f"Stop ID: {stop.stop_id}, Stop Name: {stop.stop_name}, Sequence: {sequence}")
    print()


