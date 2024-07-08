import csv


def read_travel_info():
    travel_times = []
    demands = []
    with open('data/Iasi/Iasi_links.txt', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            travel_times.append({
                'from': int(row[0]),
                'to': int(row[1]),
                'travel_time': int(row[2])
            })
    with open('data/Iasi/Iasi_demand.txt', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            demands.append(({
                'from': int(row[0]),
                'to': int(row[1]),
                'demand': int(row[2])
            }))

    return travel_times, demands

def update_links_file(filename, from_station, to_station, travel_time):
    print("Updating links file", from_station, to_station, travel_time)
    updated_lines = []

    with open(filename, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            if int(row[0]) == int(from_station) and int(row[1]) == int(to_station):
                row[2] = ' '+str(travel_time)
            updated_lines.append(','.join(row) + '\n')
    updated_lines.insert(0, ','.join(header) + '\n')

    with open(filename, 'w', newline='') as f:
        f.writelines(updated_lines)


def update_demands_file(filename, from_station, to_station, demand):
    print("Updating links file", from_station, to_station, demand)
    updated_lines = []

    with open(filename, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            if int(row[0]) == int(from_station) and int(row[1]) == int(to_station):
                row[2] = ' '+str(demand)
            updated_lines.append(','.join(row) + '\n')
    updated_lines.insert(0, ','.join(header) + '\n')

    with open(filename, 'w', newline='') as f:
        f.writelines(updated_lines)

def remove_link(filename, from_station, to_station):
    lines_to_keep = []

    with open(filename, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        lines_to_keep.append(','.join(header) + '\n')
        for row in csv_reader:
            if int(row[0]) != from_station or int(row[1]) != to_station:
                lines_to_keep.append(','.join(row) + '\n')

    with open(filename, 'w', newline='') as f:
        f.writelines(lines_to_keep)

def read_default_file():
    with open('default_file.txt', 'r') as f:
        return f.readline().strip()

def write_default_file(filepath):
    with open('default_file.txt', 'w') as f:
        f.write(filepath)