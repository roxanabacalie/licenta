import random
from copy import deepcopy
from math import inf

import numpy as np

from src.algorithms.initial_solution import TransitNetwork
from src.algorithms.visual_representation import draw_routes_mandl_network

class GeneticAlgorithm:
	def __init__(self, pop_size, tournament_size, p_swap, p_ms, p_delete, max_generations, transit_network, elite_size, route_set_size):
		self.pop_size = pop_size
		self.tournament_size = tournament_size
		self.p_swap = p_swap
		self.p_ms = p_ms
		self.p_delete = p_delete
		self.max_generations = max_generations
		self.transit_network = transit_network
		self.elite_size = elite_size
		self.route_set_size = route_set_size
		self.population = []
		self.best_individual = None
		self.best_fitness = -inf

	def initialize_population(self):
		initial_individual = self.transit_network.find_initial_route_sets(self.route_set_size)
		print("Initial individual: ", initial_individual)
		direct_connections_demand, one_change_connections_demand, two_changes_connections_demand, unsatisfied_demand = self.calculate_demands(initial_individual)
		print("d0", direct_connections_demand * 100 / (self.transit_network.total_demand/2), '%')
		print("d1", one_change_connections_demand * 100 / (self.transit_network.total_demand/2), '%')
		print("d2", two_changes_connections_demand * 100 / (self.transit_network.total_demand/2), '%')
		print("dun", unsatisfied_demand * 100 / (self.transit_network.total_demand/2), '%')
		#print("direct connections demand", direct_connections_demand)
		#print("one change connections", one_change_connections_demand)
		#print("two change connections", two_changes_connections_demand)
		#print("unsatisfied demand", unsatisfied_demand)
		for _ in range(self.pop_size):
			self.population.append(deepcopy(initial_individual))

	def calculate_demands(self, individual):
		node_to_routes = {node: [] for node in range(self.transit_network.number_of_vertices)}

		for route_index, route in enumerate(individual):
			for node in route:
				node_to_routes[node].append(route_index)

		direct_connections_demand = 0
		one_change_connections_demand = 0
		two_change_connections_demand = 0
		total_demand = self.transit_network.total_demand

		direct_connections = []
		one_change_connections = []
		two_change_connections = []
		unsatisfied_pairs = []

		for i in range(self.transit_network.number_of_vertices):
			for j in range(i + 1, self.transit_network.number_of_vertices):
				demand_ij = self.transit_network.demand[i][j]
				if demand_ij > 0:
					routes_i = set(node_to_routes[i])
					routes_j = set(node_to_routes[j])
					if routes_i & routes_j:
						direct_connections_demand += demand_ij
						direct_connections.append((i, j))
					else:
						one_change = False
						for route_i in routes_i:
							for route_j in routes_j:
								if set(individual[route_i]) & set(individual[route_j]):
									one_change_connections_demand += demand_ij
									one_change_connections.append((i, j))
									one_change = True
									break
							if one_change:
								break
						if not one_change:
							two_change = False
							for route_i in routes_i:
								for node in individual[route_i]:
									if not two_change:
										routes_mid = set(node_to_routes[node])
										for route_j in routes_j:
											if routes_mid & set(individual[route_j]):
												two_change_connections_demand += demand_ij
												two_change_connections.append((i, j))
												two_change = True
												break
								if two_change:
									break
					if not (routes_i & routes_j) and not one_change and not two_change:
						unsatisfied_pairs.append((i, j, demand_ij))

		unsatisfied_demand = total_demand/2 - (
				direct_connections_demand + one_change_connections_demand + two_change_connections_demand)
		#print("direct connections", direct_connections)
		#print("one change connections", one_change_connections)
		#print("two-change connections", two_change_connections)
		#print("unsatisfied connections", unsatisfied_pairs)
		return direct_connections_demand, one_change_connections_demand, two_change_connections_demand, unsatisfied_demand

	# Maximizing the demand coverage by considering the total passenger demand satisfied by the routes.
	# Minimizing the travel cost by summing the weights of the edges used in the routes.
	# Penalizing the solution for any demand that remains uncovered.
	def calculate_fitness(self, individual):
		fitness = 0
		total_travel_cost = 0
		total_demand_covered = 0
		fulfilled_demands = []

		try:
			# Calculate covered demand and total route set travel_cost
			for route in individual:
				for node1 in route:
					for node2 in route:
						if node1 != node2 and (node1, node2) not in fulfilled_demands:
							total_demand_covered += self.transit_network.demand[node1][node2]
							fulfilled_demands.append((node1, node2))
				total_travel_cost += sum(
					self.transit_network.graph[route[i]][route[i + 1]] for i in range(len(route) - 1))

			# Calculate number of direct connections and connections with one change
			direct_connections_demand, one_change_connections_demand, two_changes_connections_demand, unsatisfied_demand = self.calculate_demands(individual)
			fitness -= (direct_connections_demand * 0.015)
			fitness -= (one_change_connections_demand * 0.0005)
			fitness -= (two_changes_connections_demand * 0.0001)
			fitness += unsatisfied_demand * 0.1

		except IndexError as e:
			print("IndexError ", e)
			print("Problematic individual:", individual)

		fitness += total_travel_cost

		return 1 / fitness

	# swap the routes of that position based on probability Pswap
	def uniform_crossover(self, parent_a, parent_b):
		# Create deep copies to avoid modifying the original parents
		a, b = deepcopy(parent_a), deepcopy(parent_b)
		for j in range(self.route_set_size):
			if random.random() < self.p_swap:
				a[j], b[j] = b[j], a[j]
		return a, b

	def roulette_wheel_selection(self, probabilities):
		total = sum(probabilities)
		rand = random.random() * total  # scale random number to the total sum of probabilities
		cumulative_prob = 0
		for index, prob in enumerate(probabilities):
			cumulative_prob += prob
			if cumulative_prob >= rand:
				return index

	def is_subsequence(self, subsequence, individual):
		len_sub = len(subsequence)
		for route in individual:
			if route != subsequence:
				for idx in range(len(route) - len_sub + 1):
					if route[idx:idx + len_sub] == subsequence:
						return True
		return False

	def mutation(self, individual):
		# calculate mutation probabilities
		ds = self.transit_network.calculate_ds_matrix()
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
		selected_route_index = self.roulette_wheel_selection(mutation_probabilities)
		# choose a terminal of the selected route randomly.
		chosen_terminal = random.choice([0, len(individual[selected_route_index]) - 1])

		# small modification
		if random.random() < self.p_ms:
			# choose a terminal

			new_route = deepcopy(individual[selected_route_index])
			# delete the terminal based on a probability p_delete
			if random.random() < self.p_delete:
				if len(new_route) > 2:
					del new_route[chosen_terminal]
			# add a new node based on probability 1-p_delete
			else:
				neighbors = [node for node in range(self.transit_network.number_of_vertices)
							 if self.transit_network.graph[chosen_terminal][node] > 0 and node not in new_route]
				if neighbors:
					new_route.append(random.choice(neighbors))

			if new_route not in individual and not self.is_subsequence(new_route, individual):
				individual[selected_route_index] = new_route
		# big modification
		else:
			# choose a new terminal using roulette wheel selection
			sum_ds = 0
			new_terminal_probabilities = [0 for _ in range(self.transit_network.number_of_vertices)]
			for node in range(self.transit_network.number_of_vertices):
				sum_ds += ds[chosen_terminal][node]
			for node in range(self.transit_network.number_of_vertices):
				new_terminal_probabilities[node] = ds[chosen_terminal][node] / sum_ds
			new_terminal = self.roulette_wheel_selection(new_terminal_probabilities)

			# the new route is the shortest path between the chosen terminal and the new terminal
			new_route = self.transit_network.shortest_paths_matrix[chosen_terminal][new_terminal]
			if new_route not in individual and not self.is_subsequence(new_route, individual):
				individual[selected_route_index] = new_route
		return individual

	def tournament_selection(self):
		tournament_population = random.sample(self.population, self.tournament_size)
		fitness_scores = [(individual, self.calculate_fitness(individual)) for individual in tournament_population]
		# Sort by fitness in descending order (higher fitness is better)
		fitness_scores.sort(key=lambda x: x[1], reverse=True)
		# Return the top two individuals
		return fitness_scores[0][0], fitness_scores[1][0]
	'''
	def run_genetic_algorithm(self):
		self.initialize_population()
		best = deepcopy(self.population[0])
		best_fitness = self.calculate_fitness(best)
		generations_without_improvement = 0
		convergence_threshold = 20
		max_generations_copy = self.max_generations
		while max_generations_copy > 0 and generations_without_improvement < convergence_threshold:
			population_fitness = [self.calculate_fitness(individual) for individual in self.population]
			current_best_index = max(range(len(self.population)), key=lambda i: population_fitness[i])
			current_best = self.population[current_best_index]
			current_best_fitness = population_fitness[current_best_index]

			if current_best_fitness > best_fitness:
				best = current_best
				best_fitness = current_best_fitness
				generations_without_improvement = 0
			else:
				generations_without_improvement += 1

			print()
			print("Generation:", max_generations_copy, best, "Best Fitness:", best_fitness)
			included_nodes = set().union(*map(set, best)) if best else set()
			missing_nodes = 191 - len(included_nodes)
			print("Nodes included:", included_nodes)
			print("Number of nodes not included:", missing_nodes)
			elite_indices = sorted(range(len(self.population)), key=lambda i: population_fitness[i], reverse=True)[
							:self.elite_size]
			elite_population = [self.population[i] for i in elite_indices]

			q = deepcopy(elite_population)

			for idx in range(int((self.pop_size - self.elite_size) / 2)):
				parent1, parent2 = self.tournament_selection()
				child1, child2 = self.uniform_crossover(parent1[:], parent2[:])
				q.append(deepcopy(self.mutation(child1)))
				q.append(deepcopy(self.mutation(child2)))

			population = [deepcopy(individual) for individual in q]
			max_generations_copy = max_generations_copy - 1

		print("Best individual", best)
		print("Population", self.population)
		print("Fitness initial " + str(
			self.calculate_fitness(self.transit_network.find_initial_route_sets(self.route_set_size))))
		print("Fitness final " + str(self.calculate_fitness(best)))
		'''

	def run_genetic_algorithm(self):
		self.initialize_population()
		best_individual = deepcopy(self.population[0])
		best_fitness = self.calculate_fitness(best_individual)
		generations_without_improvement = 0
		convergence_threshold = 80

		for generation in range(self.max_generations):
			# Calculate fitness for the current population
			population_fitness = [self.calculate_fitness(individual) for individual in self.population]
			current_best_index = max(range(len(self.population)), key=lambda i: population_fitness[i])
			current_best = self.population[current_best_index]
			current_best_fitness = population_fitness[current_best_index]

			# Update the best individual if the current best is better
			if current_best_fitness > best_fitness:
				best_individual = deepcopy(current_best)
				best_fitness = current_best_fitness
				generations_without_improvement = 0
			else:
				generations_without_improvement += 1

			print()
			print()
			print(f"Generation: {generation}, Best Fitness: {best_fitness}")
			included_nodes = set().union(*map(set, best_individual)) if best_individual else set()
			missing_nodes = self.transit_network.number_of_vertices - len(included_nodes)
			print(f"Nodes included: {included_nodes}")
			print(f"Number of nodes not included: {missing_nodes}")
			direct_connections_demand, one_change_connections_demand, two_changes_connections_demand, unsatisfied_demand = self.calculate_demands(best_individual)
			print("d0", direct_connections_demand * 100 / (self.transit_network.total_demand/2), '%')
			print("d1", one_change_connections_demand * 100 / (self.transit_network.total_demand/2), '%')
			print("d2", two_changes_connections_demand*100/(self.transit_network.total_demand/2), '%')
			print("dun", unsatisfied_demand*100/(self.transit_network.total_demand/2), '%')
			print("direct connections demand", direct_connections_demand)
			print("one change connections", one_change_connections_demand)


			# Create the next generation
			elite_indices = sorted(range(len(self.population)), key=lambda i: population_fitness[i], reverse=True)[
							:self.elite_size]
			elite_population = [self.population[i] for i in elite_indices]

			new_population = deepcopy(elite_population)

			for _ in range(int((self.pop_size - self.elite_size) / 2)):
				parent1, parent2 = self.tournament_selection()
				child1, child2 = self.uniform_crossover(parent1[:], parent2[:])
				new_population.append(self.mutation(child1))
				new_population.append(self.mutation(child2))

			self.population = deepcopy(new_population)

			# Check for convergence
			if generations_without_improvement >= convergence_threshold:
				break

		print("Best individual", best_individual)
		print("Fitness initial",
			  self.calculate_fitness(self.transit_network.find_initial_route_sets(self.route_set_size)))
		print("Fitness final", best_fitness)


Mandl_transit_network = TransitNetwork(15, "../../data/mandl/mandl1_links.txt", "../../data/mandl/mandl1_demand.txt")
Iasi_transit_network = TransitNetwork(191, "../../data/iasi/Iasi_links.txt", "../../data/iasi/Iasi_demand.txt")
ga = GeneticAlgorithm(16, 10, 0.125, 0.7, 0.4, 400, Mandl_transit_network, 4, 8)
ga.run_genetic_algorithm()


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

'''
for i in range(50,100,5):
	x = Iasi_transit_network.find_initial_route_sets(i)
	print("Nr routes", i, "fitnesss", calculate_fitness(x, Iasi_transit_network))
	included_nodes = set().union(*map(set, x)) if x else set()
	missing_nodes = 191 - len(included_nodes)
	print("Number of nodes not included:", missing_nodes)
'''
#P_Iasi = []
#for i in range(pop_size):
#	P_Iasi.append(x)
#genetic_algorithm(P_Iasi, max_gen, t, Iasi_transit_network)

