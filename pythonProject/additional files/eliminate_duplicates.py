def read_stations_file(file_path):
    stations = {}
    with open(file_path, 'r') as file:
        next(file)  # Skip header row
        for line in file:
            stop_id, stop_name, stop_lat, stop_lon = line.strip().split(',')
            stop_name = stop_name.strip()  # Remove leading/trailing whitespace
            stop_lat = float(stop_lat.strip())  # Convert latitude to float
            stop_lon = float(stop_lon.strip())  # Convert longitude to float
            # If station name already exists, skip it
            if stop_name not in stations:
                stations[stop_name] = (stop_id, stop_lat, stop_lon)
    return stations

def write_stations_file(stations, file_path):
    with open(file_path, 'w') as file:
        file.write("Stop ID,Stop Name,Stop Latitude,Stop Longitude\n")
        for stop_name, (stop_id, stop_lat, stop_lon) in stations.items():
            file.write(f"{stop_id},{stop_name},{stop_lat},{stop_lon}\n")

# Example usage
input_file = "../src/stops_data2.csv"
output_file = "../src/stops_data3.csv"

stations_data = read_stations_file(input_file)
write_stations_file(stations_data, output_file)