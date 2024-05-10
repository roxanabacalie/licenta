import random
from math import inf

from src.initial_solution import TransitNetwork
from src.visual_representation import draw_routes_mandl_network

pop_size = 100  # desired population size
elite_size = 1  # desired number of elite individuals
route_set_size = 8  # number of routes in the individual
t = 2  # tournament size for fitness
p_swap = 0.1  # probability of swapping an index in Uniform Crossover
p_ms = 0.8  # probability of doing small modification in Mutation
p_delete = 0.5  # probability of deleting the selected terminal in small modification
max_gen = 10  # maximum number of generations
P = []

Mandl_transit_network = TransitNetwork(15, "../data/mandl1_links.txt", "../data/mandl1_demand.txt")

def calculate_fitness(individual):
	fitness = 0
	total_demand_covered = 0
	for j in range(len(individual)):
		route = individual[j]
		for node1 in range(len(route)):
			for node2 in range(len(route)):
				total_demand_covered += Mandl_transit_network.demand[node1][node2]
		for i in range(len(route)-1):
			fitness += Mandl_transit_network.graph[route[i]][route[i+1]]
			fitness += (Mandl_transit_network.total_demand - total_demand_covered) * 0.5
	print(fitness)
	return 1/fitness


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
		#print(cumulative_prob, rand)
		if cumulative_prob >= rand:
			return index


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
			mutation_probabilities[index] = (1/ds[route_set[0]][route_set[len(route_set) - 1]]) / sum_ds
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
				individual[selected_route_index].remove(individual[selected_route_index][chosen_terminal])
		# add a new node based on probability 1-p_delete
		else:
			neighbors = []
			for node in range(Mandl_transit_network.number_of_vertices):
				if Mandl_transit_network.graph[chosen_terminal][node] > 0 and node not in individual[selected_route_index]:
					neighbors.append(node)
			if len(neighbors) != 0:
				individual[selected_route_index].append(random.choice(neighbors))
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
		individual[selected_route_index] = new_route
	return individual


def tournament_selection(population):
	best_individual = population[0]
	second_best_individual = population[1]
	for j in range(1, pop_size-1):
		next_individual = population[j]
		if calculate_fitness(next_individual) > calculate_fitness(best_individual):
			second_best_individual = best_individual
			best_individual = next_individual
		elif calculate_fitness(next_individual) > calculate_fitness(second_best_individual):
			second_best_individual = next_individual
	return best_individual, second_best_individual


for i in range(pop_size):
	P.append(Mandl_transit_network.find_initial_route_sets(8))


best = None
while max_gen > 0:
	for i in range(len(P)):
		if best is None or calculate_fitness(P[i]) > calculate_fitness(best):
			best = P[i]

	sorted_population = sorted(P, key=calculate_fitness, reverse=True)
	Q = sorted_population[:elite_size]

	for i in range(int((pop_size - elite_size) / 2)):
		Pa, Pb = tournament_selection(P)
		Ca, Cb = uniform_crossover(Pa, Pb)
		Q.append(mutation(Ca))
		Q.append(mutation(Cb))
	P = Q
	max_gen = max_gen - 1

print("Best", best)
print(P)
draw_routes_mandl_network(best)