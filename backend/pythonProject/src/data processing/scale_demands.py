import numpy as np


def scale_demand(demand, min_new=5, max_new=1000):
	min_old = min(demand)
	max_old = max(demand)
	# Apply linear scaling to the demand values
	scaled_demand = [(d - min_old) / (max_old - min_old) * (max_new - min_new) + min_new for d in demand]
	# Round to nearest multiple of 5
	scaled_demand = [round(d / 5) * 5 for d in scaled_demand]
	return scaled_demand


# Read the TXT file
input_file = '../../data/iasi/Iasi_demand.txt'
with open(input_file, 'r') as file:
	lines = file.readlines()

# Skip the header line
header = lines[0]
lines = lines[1:]

# Parse the data
data = []
from_nodes = []
to_nodes = []
demands = []

for line in lines:
	parts = line.strip().split(',')
	from_node = int(parts[0])
	to_node = int(parts[1])
	demand = int(parts[2])

	from_nodes.append(from_node)
	to_nodes.append(to_node)
	demands.append(demand)

# Scale the demand values
scaled_demands = scale_demand(demands)

# Write the scaled data to a new TXT file
output_file = 'scaled_demands.txt'
with open(output_file, 'w') as file:
	# Write the header
	file.write(header)
	# Write the scaled data
	for from_node, to_node, demand in zip(from_nodes, to_nodes, scaled_demands):
		file.write(f"{from_node}, {to_node}, {demand}\n")

print("Demands have been scaled and saved to", output_file)
