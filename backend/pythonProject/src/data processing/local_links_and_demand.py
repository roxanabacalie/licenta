import json
import os
from db_management import routes


def extract_directions_info():
    for i in range (1, 192):
        for j in range(i+1, 192):
            if i!=j:
                file_path1 = f"../../data/iasi/directions/directions_{i}_{j}.json"
                file_path2 = f"../../data/iasi/directions/directions_{j}_{i}.json"
                if not os.path.exists(file_path1):
                    print(f"File not found: {file_path1}")
                    continue
                if not os.path.exists(file_path2):
                    print(f"File not found: {file_path2}")
                    continue

                with open(file_path1, 'r') as file1:
                    data1 = json.load(file1)
                with open(file_path2, 'r') as file2:
                    data2 = json.load(file2)

                if 'routes' in data1 and len(data1['routes']) > 0 and 'routes' in data1 and len(data1['routes']) > 0:
                    route1 = data1['routes'][0]
                    route2 = data2['routes'][0]
                    if 'legs' in route1 and len(route1['legs']) > 0 and 'legs' in route2 and len(route2['legs']) > 0:
                        leg1 = route1['legs'][0]
                        leg2 = route2['legs'][0]
                        distance1 = leg1['distance']['value']
                        distance2 = leg2['distance']['value']
                        duration1 = leg1['duration']['value']
                        duration2 = leg2['duration']['value']
                        duration_in_traffic1 = leg1['duration_in_traffic']['value'] if 'duration_in_traffic' in leg1 else 'N/A'
                        duration_in_traffic2 = leg2['duration_in_traffic']['value'] if 'duration_in_traffic' in leg2 else 'N/A'
                        start_id = data1.get('start_id', 'N/A')
                        stop_id = data1.get('stop_id', 'N/A')
                        actual_time = (duration1 + duration2)/2
                        demand = (int(10000 * abs(duration1 - duration_in_traffic1) / distance1) + int(10000 * abs(duration2 - duration_in_traffic2) / distance2))/2
                        routes.insert_route(int(start_id), int(stop_id), duration1, duration_in_traffic1, distance1, actual_time, demand)
                        routes.insert_route(int(stop_id), int(start_id), duration2, duration_in_traffic2, distance2, actual_time, demand)
                    else:
                        raise ValueError("No legs found in the provided JSON data.")
                else:
                    raise ValueError("No routes found in the provided JSON data.")


def route_pruning():
    for i in range(1, 192):
        for j in range(i + 1, 192):
            for k in range(j + 1, 192):
                time_i_j = routes.get_route_time(i, j)
                time_i_k = routes.get_route_time(i, k)
                time_j_k = routes.get_route_time(j, k)
                max_time = 0
                a, b = 0, 0
                coef = 0.95

                if time_i_k > time_j_k:
                    if time_i_k > time_i_j:
                        max_time = time_i_k
                        a, b = i, k
                    else:
                        max_time = time_i_j
                        a, b = i, j
                else:
                    if time_j_k > time_i_j:
                        max_time = time_j_k
                        a, b = j, k
                    else:
                        max_time = time_i_j
                        a, b = i, j

                time_sum = time_i_j + time_j_k + time_i_k
                if max_time > (time_sum - max_time) * coef:
                    routes.update_medium_time(a, b, -1)
                    print("Deleted", a, b, "because of ", i, j, k)



def write_data_to_files():
    for i in range(1,192):
        for j in range(i+1,192):
            aux = routes.get_route_time(i, j)
            routes.update_actual_time(i,j,routes.get_route_medium_time(i,j))
            routes.update_actual_time(j,i,routes.get_route_medium_time(i,j))
            routes.update_medium_time(i,j,aux)
            routes.update_medium_time(j,i,aux)
            print(i,j)


    for i in range(1,192):
        for j in range(i+1,192):
            if routes.get_route_time(i,j) != -1:
                routes.update_actual_time(i,j, routes.get_route_medium_time(i,j))
                routes.update_actual_time(j,i, routes.get_route_medium_time(i,j))

    with open('../../data/iasi/Iasi_links.txt', 'w') as txtfile:
        txtfile.write("from, to, travel_time\n")

    with open('../../data/iasi/Iasi_demand.txt', 'w') as txtfile2:
        txtfile2.write("from, to, demand\n")

    for i in range(1, 192):
        for j in range(1, 192):
            if i != j:
                travel_time = routes.get_route_time(i, j)
                demand = routes.get_route_demand(i, j)

                with open('../../data/iasi/Iasi_links.txt', 'a') as txtfile:
                    if travel_time != -1:
                        txtfile.write(f"{i}, {j}, {travel_time}\n")

                with open('../../data/iasi/Iasi_demand.txt', 'a') as txtfile2:
                    txtfile2.write(f"{i}, {j}, {demand}\n")

                print(i, j)

def filter_travel_times(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    header = lines[0]
    data_lines = lines[1:]

    filtered_lines = [header]
    for line in data_lines:
        from_stop, to_stop, travel_time = map(int, line.strip().split(','))
        if travel_time <= 300:
            filtered_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(filtered_lines)


extract_directions_info()
route_pruning()
write_data_to_files()
filter_travel_times('../../data/iasi/Iasi_links.txt')
