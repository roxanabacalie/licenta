import json

def extract_directions_info(file_path):
    print("sal")
    with open(file_path, 'r') as file:
        data = json.load(file)

    if 'routes' in data and len(data['routes']) > 0:
        print("routes")
        route = data['routes'][0]
        if 'legs' in route and len(route['legs']) > 0:
            print("legs")
            leg = route['legs'][0]

            distance = leg['distance']['value']
            duration = leg['duration']['value']
            duration_in_traffic = leg['duration_in_traffic']['value'] if 'duration_in_traffic' in leg else 'N/A'

            result = {
                'distance': distance,
                'duration': duration,
                'duration_in_traffic': duration_in_traffic,
                'start_id': data.get('start_id', 'N/A'),
                'stop_id': data.get('stop_id', 'N/A')
            }

            return result
        else:
            raise ValueError("No legs found in the provided JSON data.")
    else:
        raise ValueError("No routes found in the provided JSON data.")


file_path = "../../data/iasi/directions/directions_1_3.json"
result = extract_directions_info(file_path)
print(result)