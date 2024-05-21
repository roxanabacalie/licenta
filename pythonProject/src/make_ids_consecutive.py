import csv

# Read data from the CSV file into a list
with open('stops_data3.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    stops_data = list(reader)

# Generate consecutive IDs starting from 1 and update the data
id_mapping = {}  # Dictionary to store the mapping between old IDs and new consecutive IDs
new_id = 1
for stop in stops_data:
    old_id = stop['Stop ID']
    id_mapping[old_id] = new_id
    stop['Stop ID'] = str(new_id)  # Update the ID to be consecutive starting from 1
    new_id += 1

# Write the updated data to a new CSV file
with open('stops_data_consecutive_ids.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Stop ID', 'Stop Name', 'Stop Latitude', 'Stop Longitude']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(stops_data)

print("Process of updating IDs in stops_data3.csv has been completed.")
