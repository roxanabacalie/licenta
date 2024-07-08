file_name = 'iasi_filtered_stops_data.csv'
num_stations_to_keep = 40
selected_stations = []

with open(file_name, 'r', encoding='utf-8') as file:
    next(file)
    for i, line in enumerate(file):
        if i >= num_stations_to_keep:
            break
        station_id = line.strip().split(',')[0]
        selected_stations.append(station_id)

output_stops_file = '30stops.txt'

stops_header = 'Stop ID,Stop Name,Stop Latitude,Stop Longitude\n'

with open(output_stops_file, 'w', encoding='utf-8') as file:
    file.write(stops_header)
    for station_id in selected_stations:
        with open(file_name, 'r', encoding='utf-8') as orig_file:
            next(orig_file)
            for line in orig_file:
                if line.startswith(station_id):
                    file.write(line)
                    break

print(f'S-au selectat și scris în fișierul {output_stops_file} primele {num_stations_to_keep} stații.')

links_file = 'Iasi_links.txt'
output_links_file = 'Iasi_30stops_links.txt'

with open(links_file, 'r', encoding='utf-8') as in_file, \
     open(output_links_file, 'w', encoding='utf-8') as out_file:

    out_file.write('from,to,travel_time\n')

    for line in in_file:
        from_station, to_station, travel_time = line.strip().split(',')
        from_station_str = str(from_station).strip()
        to_station_str = str(to_station).strip()

        if from_station_str in selected_stations and to_station_str in selected_stations:
            out_file.write(f'{from_station_str},{to_station_str},{travel_time}\n')

print(f'S-au selectat și scris în fișierul {output_links_file} link-urile care conectează primele {num_stations_to_keep} stații.')


demands_file = 'Iasi_demand.txt'
output_demands_file = 'Iasi_30stops_demand.txt'
demands_header = 'from,to,demand\n'

with open(demands_file, 'r', encoding='utf-8') as in_file, \
     open(output_demands_file, 'w', encoding='utf-8') as out_file:
    out_file.write(demands_header)
    for line in in_file:
        from_station, to_station, demand = line.strip().split(',')
        from_station_str = str(from_station).strip()
        to_station_str = str(to_station).strip()
        demand_str = str(demand).strip()
        if from_station_str in selected_stations and to_station_str in selected_stations:
            out_file.write(f'{from_station_str},{to_station_str},{demand_str}\n')