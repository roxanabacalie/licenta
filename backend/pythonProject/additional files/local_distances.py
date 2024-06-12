import random
from geopy.distance import geodesic as GD
import csv

def calculate_distance(coord1, coord2):
    return GD(coord1, coord2).km

# Citeste datele din fisier intr-o lista
with open('../src/stops_data_consecutive_ids.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    stops_data = list(reader)

# Parcurge lista de doua ori pentru a calcula distantele si cererile intre statii
with open('../data/iasi/Iasi_links.txt', 'w') as txtfile:
    with open('../data/iasi/Iasi_demand.txt', 'w') as txtfile2:
        txtfile.write("from, to, travel_time\n")
        txtfile2.write("from, to, demand\n")

        for row1 in stops_data:
            for row2 in stops_data:
                stop1_coords = (float(row1['Stop Latitude']), float(row1['Stop Longitude']))
                stop2_coords = (float(row2['Stop Latitude']), float(row2['Stop Longitude']))

                # Calculeaza distanta intre statii
                distance = calculate_distance(stop1_coords, stop2_coords)
                demand = random.randint(0, 1000)

                # Scrie rezultatul in fisierele text
                txtfile.write(f"{row1['Stop ID']}, {row2['Stop ID']}, {distance}\n")
                txtfile2.write(f"{row1['Stop ID']}, {row2['Stop ID']}, {demand}\n")

print("Procesul de generare a fisierelor Iasi_links.txt si Iasi_demand.txt a fost finalizat.")
