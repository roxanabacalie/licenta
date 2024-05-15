import requests
import networkx as nx
import matplotlib.pyplot as plt

def save_graph(graph, file_name):
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)

    pos = nx.spring_layout(graph)

    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig(file_name, bbox_inches="tight")
    plt.close(fig)

def draw_stops(stops):
    G = nx.Graph()

    for stop in stops:
        stop_id = stop['stop_id']
        stop_name = stop['stop_name']
        stop_lat = stop['stop_lat'] * 10000
        stop_lon = stop['stop_lon'] * 10000
        G.add_node(stop_id, label=stop_name, pos=(stop_lon, stop_lat))

    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'label')
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=30, node_color="skyblue", font_size=5, font_color="black")
    plt.show()

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
        # Send GET request to the API endpoint with headers
        response = requests.get(api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
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


connected_trips = connect_stops_to_trips(stops_data, stop_times_data, trips_data, routes_data)
for trip_id, trip in connected_trips.items():
    print(f"Trip ID: {trip.trip_id}, Route ID: {trip.route_id}, Route Short Name: {trip.route_short_name}, Route Long Name: {trip.route_long_name}, Trip Headsign: {trip.trip_headsign}")
    print("Stops:")
    for stop, sequence in trip.stops:
        print(f"Stop ID: {stop.stop_id}, Stop Name: {stop.stop_name}, Sequence: {sequence}")
    print()


