import random
from copy import deepcopy
from math import inf

from src.initial_solution import TransitNetwork
from src.visual_representation import draw_routes_mandl_network

pop_size = 16  # desired population size
elite_size = 4  # desired number of elite individuals
route_set_size = 8  # number of routes in the individual
t = 10  # tournament size for fitness
p_swap = 0.125  # probability of swapping an index in Uniform Crossover
p_ms = 0.7  # probability of doing small modification in Mutation
p_delete = 0.4  # probability of deleting the selected terminal in small modification
max_gen = 100  # maximum number of generations
P = []

Mandl_transit_network = TransitNetwork(15, "../data/mandl1_links.txt", "../data/mandl1_demand.txt")


def calculate_fitness(individual):
	fitness = 0
	total_demand_covered = 0
	fulfilled_demands = []
	for j in range(len(individual)):
		route = individual[j]
		for node1_index in range(len(route)):
			for node2_index in range(len(route)):
				node1 = route[node1_index]
				node2 = route[node2_index]
				nodes_pair = (node1, node2)
				if nodes_pair not in fulfilled_demands:
					total_demand_covered += Mandl_transit_network.demand[node1][node2]
					fulfilled_demands.append(nodes_pair)
		for idx in range(len(route) - 1):
			fitness += Mandl_transit_network.graph[route[idx]][route[idx + 1]]
	fitness += (Mandl_transit_network.total_demand - total_demand_covered) * 0.5
	# print(fitness)
	return 1 / fitness


# swap the routes of that position based on probability Pswap
def uniform_crossover(a, b):
	for j in range(route_set_size):
		rand = random.random()
		if rand < p_swap:
			temp = a[j]
			a[j] = b[j]
			b[j] = temp
	return a, b


def roulette_wheel_selection(probabilities):
	rand = random.random()
	cumulative_prob = 0
	for index, prob in enumerate(probabilities):
		cumulative_prob += prob
		# print(cumulative_prob, rand)
		if cumulative_prob >= rand:
			return index


def is_subsequence(subsequence, individual):
	for route in individual:
		if route != subsequence:
			len_sub = len(subsequence)
			for i in range(len(route) - len_sub + 1):
				if route[i:i + len_sub] == subsequence:
					return True
	return False


def mutation(individual):
	# calculate mutation probabilities

	ds = Mandl_transit_network.calculate_ds_matrix()
	mutation_probabilities = [0 for _ in range(len(individual))]
	sum_ds = 0
	for route_set in individual:
		if ds[route_set[0]][route_set[len(route_set) - 1]] != 0:
			sum_ds += 1 / ds[route_set[0]][route_set[len(route_set) - 1]]
	index = 0
	for route_set in individual:
		if ds[route_set[0]][route_set[len(route_set) - 1]] == 0:
			mutation_probabilities[index] = inf
		else:
			mutation_probabilities[index] = (1 / ds[route_set[0]][route_set[len(route_set) - 1]]) / sum_ds
		index += 1

	# select a route based on roulette wheel selection
	selected_route_index = roulette_wheel_selection(mutation_probabilities)

	rand = random.random()
	# small modification
	if rand < p_ms:
		# choose a terminal
		chosen_terminal = random.choice([0, len(individual[selected_route_index]) - 1])
		rand = random.random()

		# delete the terminal based on a probability p_delete
		if rand < p_delete:
			if len(individual[selected_route_index]) > 2:
				new_route = individual[selected_route_index]
				new_route.remove(new_route[chosen_terminal])
				if new_route not in individual and not is_subsequence(new_route, individual):
					individual[selected_route_index].remove(individual[selected_route_index][chosen_terminal])
		# add a new node based on probability 1-p_delete
		else:
			neighbors = []
			for node in range(Mandl_transit_network.number_of_vertices):
				if Mandl_transit_network.graph[chosen_terminal][node] > 0 and node not in individual[
					selected_route_index]:
					neighbors.append(node)
			if len(neighbors) != 0:
				new_route = individual[selected_route_index]
				new_route.append(random.choice(neighbors))
				if new_route not in individual and not is_subsequence(new_route, individual):
					individual[selected_route_index] = new_route
	# big modification
	else:
		# choose a terminal
		chosen_terminal = random.choice([0, len(individual) - 1])

		# choose a new terminal using roulette wheel selection
		sum_ds = 0
		new_terminal_probabilities = [0 for _ in range(Mandl_transit_network.number_of_vertices)]
		for node in range(Mandl_transit_network.number_of_vertices):
			sum_ds += ds[chosen_terminal][node]
		for node in range(Mandl_transit_network.number_of_vertices):
			new_terminal_probabilities[node] = ds[chosen_terminal][node] / sum_ds
		new_terminal = roulette_wheel_selection(new_terminal_probabilities)

		# the new route is the shortest path between the chosen terminal and the new terminal
		new_route = Mandl_transit_network.dijkstra_algorithm(chosen_terminal)[new_terminal]
		if new_route not in individual and not is_subsequence(new_route, individual):
			individual[selected_route_index] = new_route
	return individual


def tournament_selection(population, tournament_size):
	tournament_population = random.sample(population, tournament_size)
	best_individual = tournament_population[0]
	second_best_individual = tournament_population[1]
	for j in range(1, tournament_size - 1):
		next_individual = tournament_population[j]
		if calculate_fitness(next_individual) > calculate_fitness(best_individual):
			second_best_individual = best_individual
			best_individual = next_individual
		elif calculate_fitness(next_individual) > calculate_fitness(second_best_individual):
			second_best_individual = next_individual
	return best_individual, second_best_individual


def genetic_algorithm(population, max_generations, tournament_size):
	best = deepcopy(population[0])

	while max_generations > 0:

		current_best = deepcopy(max(population, key=calculate_fitness))

		if calculate_fitness(current_best) > calculate_fitness(best):
			best = deepcopy(current_best)

		print("Generation:", max_generations, best, "Best Fitness:", calculate_fitness(best))

		sorted_population = [deepcopy(individual) for individual in
							 sorted(population, key=calculate_fitness, reverse=True)]
		Q = [deepcopy(individual) for individual in sorted_population[:elite_size]]

		for idx in range(int((pop_size - elite_size) / 2)):
			parent1, parent2 = tournament_selection(population, tournament_size)
			child1, child2 = uniform_crossover(parent1[:], parent2[:])
			Q.append(deepcopy(mutation(child1)))
			Q.append(deepcopy(mutation(child2)))

		population = [deepcopy(individual) for individual in Q]
		max_generations = max_generations - 1

	print("Best", best)
	print(population)
	draw_routes_mandl_network(best)

	print("Fitness initial " + str(calculate_fitness(Mandl_transit_network.find_initial_route_sets(8))))
	print("Fitness final " + str(calculate_fitness(best)))


for i in range(pop_size):
	P.append(Mandl_transit_network.find_initial_route_sets(8))

genetic_algorithm(P, max_gen, t)
