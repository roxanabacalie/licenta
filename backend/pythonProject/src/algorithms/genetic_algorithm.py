import random
from copy import deepcopy
from math import inf

import numpy as np

from src.algorithms.initial_solution import TransitNetwork
from src.algorithms.visual_representation import draw_routes_mandl_network

pop_size = 16  # desired population size
elite_size = 4  # desired number of elite individuals
route_set_size = 8 # number of routes in the individual
t = 10  # tournament size for fitness
p_swap = 0.125  # probability of swapping an index in Uniform Crossover
p_ms = 0.7  # probability of doing small modification in Mutation
p_delete = 0.4  # probability of deleting the selected terminal in small modification
max_gen = 100  # maximum number of generations
P = []

Mandl_transit_network = TransitNetwork(15, "../../data/mandl/mandl1_links.txt", "../../data/mandl/mandl1_demand.txt")
Iasi_transit_network = TransitNetwork(191, "../../data/iasi/Iasi_links.txt", "../../data/iasi/Iasi_demand.txt")


# Maximizing the demand coverage by considering the total passenger demand satisfied by the routes.
# Minimizing the travel cost by summing the weights of the edges used in the routes.
# Penalizing the solution for any demand that remains uncovered.
def calculate_fitness(individual, transit_network):
	fitness = 0
	total_travel_cost = 0
	total_demand_covered = 0
	fulfilled_demands = []
	direct_connections_demand = 0
	one_change_connections_demand = 0
	node_to_routes = {node: [] for node in range(transit_network.number_of_vertices)}
	for route_index, route in enumerate(individual):
		for node in route:
			node_to_routes[node].append(route_index)
	try:
		# calculate covered demand and total route set travel_cost
		for route in individual:
			for node1 in route:
				for node2 in route:
					if node1 != node2 and (node1, node2) not in fulfilled_demands:
						total_demand_covered += transit_network.demand[node1][node2]
						fulfilled_demands.append((node1, node2))
			total_travel_cost += sum(transit_network.graph[route[i]][route[i + 1]] for i in range(len(route) - 1))
		# penalty for the total demand that is not covered by the routes in the individual.
		#fitness += (transit_network.total_demand - total_demand_covered) * 0.4
		fitness += total_travel_cost
		# Calculate number of direct connections and connections with one change

		for i in range(transit_network.number_of_vertices):
			for j in range(i + 1, transit_network.number_of_vertices):
				routes_i = set(node_to_routes[i])
				routes_j = set(node_to_routes[j])
				if routes_i & routes_j:
					direct_connections_demand += transit_network.demand[i][j]
				else:
					common_node_found = False
					for route_i in routes_i:
						for route_j in routes_j:
							if set(individual[route_i]) & set(individual[route_j]):
								common_node_found = True
								break
						if common_node_found:
							break
					if common_node_found:
						one_change_connections_demand += transit_network.demand[i][j]

	except IndexError as e:
		print("IndexError ", e)
		print("Problematic individual:", individual)
	fitness -= (direct_connections_demand * 0.001)
	fitness -= (one_change_connections_demand * 0.0005)
	print("demand uncovered", transit_network.total_demand - total_demand_covered)
	print("total travel cost", total_travel_cost)
	print("direct connections demand", direct_connections_demand)
	print("one change connections", one_change_connections_demand)
	return 1 / fitness


# swap the routes of that position based on probability Pswap
def uniform_crossover(parent_a, parent_b):
	# Create deep copies to avoid modifying the original parents
	a, b = deepcopy(parent_a), deepcopy(parent_b)
	for j in range(route_set_size):
		if random.random() < p_swap:
			a[j], b[j] = b[j], a[j]
	return a, b


def roulette_wheel_selection(probabilities):
	total = sum(probabilities)
	rand = random.random() * total  # scale random number to the total sum of probabilities
	cumulative_prob = 0
	for index, prob in enumerate(probabilities):
		cumulative_prob += prob
		if cumulative_prob >= rand:
			return index


def is_subsequence(subsequence, individual):
	len_sub = len(subsequence)
	for route in individual:
		if route != subsequence:
			for idx in range(len(route) - len_sub + 1):
				if route[idx:idx + len_sub] == subsequence:
					return True
	return False


def mutation(individual, transit_network):
	# calculate mutation probabilities
	ds = transit_network.calculate_ds_matrix()
	mutation_probabilities = np.zeros(len(individual))
	sum_ds = 0
	for route_set in individual:
		first = route_set[0]
		last = route_set[-1]
		if ds[first][last] != 0:
			sum_ds += 1 / ds[first][last]

	for index, route_set in enumerate(individual):
		first = route_set[0]
		last = route_set[-1]
		if ds[first][last] == 0:
			mutation_probabilities[index] = inf
		else:
			mutation_probabilities[index] = (1 / ds[route_set[0]][route_set[len(route_set) - 1]]) / sum_ds

	# select a route based on roulette wheel selection
	selected_route_index = roulette_wheel_selection(mutation_probabilities)
	# choose a terminal of the selected route randomly.
	chosen_terminal = random.choice([0, len(individual[selected_route_index]) - 1])

	# small modification
	if random.random() < p_ms:
		# choose a terminal

		new_route = deepcopy(individual[selected_route_index])
		# delete the terminal based on a probability p_delete
		if random.random() < p_delete:
			if len(new_route) > 2:
				del new_route[chosen_terminal]
		# add a new node based on probability 1-p_delete
		else:
			neighbors = [node for node in range(transit_network.number_of_vertices)
						 if transit_network.graph[chosen_terminal][node] > 0 and node not in new_route]
			if neighbors:
				new_route.append(random.choice(neighbors))

		if new_route not in individual and not is_subsequence(new_route, individual):
			individual[selected_route_index] = new_route
	# big modification
	else:
		# choose a new terminal using roulette wheel selection
		sum_ds = 0
		new_terminal_probabilities = [0 for _ in range(transit_network.number_of_vertices)]
		for node in range(transit_network.number_of_vertices):
			sum_ds += ds[chosen_terminal][node]
		for node in range(transit_network.number_of_vertices):
			new_terminal_probabilities[node] = ds[chosen_terminal][node] / sum_ds
		new_terminal = roulette_wheel_selection(new_terminal_probabilities)

		# the new route is the shortest path between the chosen terminal and the new terminal
		new_route = transit_network.shortest_paths_matrix[chosen_terminal][new_terminal]
		if new_route not in individual and not is_subsequence(new_route, individual):
			individual[selected_route_index] = new_route
	return individual


def tournament_selection(population, tournament_size, transit_network):
	tournament_population = random.sample(population, tournament_size)
	fitness_scores = [(individual, calculate_fitness(individual, transit_network)) for individual in tournament_population]
	# Sort by fitness in descending order (higher fitness is better)
	fitness_scores.sort(key=lambda x: x[1], reverse=True)
	# Return the top two individuals
	return fitness_scores[0][0], fitness_scores[1][0]


def genetic_algorithm(population, max_generations, tournament_size, transit_network):
	best = deepcopy(population[0])
	best_fitness = calculate_fitness(best, transit_network)
	generations_without_improvement = 0
	convergence_threshold = 20

	while max_generations > 0 and generations_without_improvement < convergence_threshold:
		population_fitness = [calculate_fitness(individual, transit_network) for individual in population]
		current_best_index = max(range(len(population)), key=lambda i: population_fitness[i])
		current_best = population[current_best_index]
		current_best_fitness = population_fitness[current_best_index]

		if current_best_fitness > best_fitness:
			best = current_best
			best_fitness = current_best_fitness
			generations_without_improvement = 0
		else:
			generations_without_improvement += 1

		print("Generation:", max_generations, best, "Best Fitness:", best_fitness)
		included_nodes = set().union(*map(set, best)) if best else set()
		missing_nodes = 191- len(included_nodes)
		print("Nodes included:", included_nodes)
		print("Number of nodes not included:", missing_nodes)
		elite_indices = sorted(range(len(population)), key=lambda i: population_fitness[i], reverse=True)[:elite_size]
		elite_population = [population[i] for i in elite_indices]

		q = deepcopy(elite_population)

		for idx in range(int((pop_size - elite_size) / 2)):
			parent1, parent2 = tournament_selection(population, tournament_size, transit_network)
			child1, child2 = uniform_crossover(parent1[:], parent2[:])
			q.append(deepcopy(mutation(child1, transit_network)))
			q.append(deepcopy(mutation(child2, transit_network)))

		population = [deepcopy(individual) for individual in q]
		max_generations = max_generations - 1

	print("Best individual", best)
	print("Population", population)
	print("Fitness initial " + str(calculate_fitness(transit_network.find_initial_route_sets(route_set_size), transit_network)))
	print("Fitness final " + str(calculate_fitness(best, transit_network)))

'''
for i in range(pop_size):
	P.append(Mandl_transit_network.find_initial_route_sets(8))
genetic_algorithm(P, max_gen, t, Mandl_transit_network)
'''

'''
route_set = Mandl_transit_network.find_initial_route_sets(8);
route_set[0]=[0,1,2]
route_set[1]=[1,2,3]
route_set[2]=[2,3,4]
route_set[3]=[3,4,5]
route_set[4]=[6,7,8]
route_set[5]=[9,10,11]
route_set[6]=[12,13,14]
route_set[7]=[0,12,14]
for i in range(pop_size):
	P.append(route_set)
genetic_algorithm(P, max_gen, t, Mandl_transit_network)
'''

for i in range(50,100,5):
	x = Iasi_transit_network.find_initial_route_sets(i)
	print("Nr routes", i, "fitnesss", calculate_fitness(x, Iasi_transit_network))
	included_nodes = set().union(*map(set, x)) if x else set()
	missing_nodes = 191 - len(included_nodes)
	print("Number of nodes not included:", missing_nodes)

#P_Iasi = []
#for i in range(pop_size):
#	P_Iasi.append(x)
#genetic_algorithm(P_Iasi, max_gen, t, Iasi_transit_network)

