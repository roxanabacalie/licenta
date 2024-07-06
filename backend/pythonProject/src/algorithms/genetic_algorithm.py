import json
import random
from copy import deepcopy
from datetime import datetime
from math import inf
import numpy as np
from matplotlib import pyplot as plt

from db_management.ga_runs import update_percent_complete
from src.algorithms.genetic_algorithm_helpers import roulette_wheel_selection, is_subsequence


class GeneticAlgorithm:
	# Initializarea parametrilor algoritmului genetic
	def __init__(
			self,
			pop_size,
			tournament_size,
			p_swap, p_ms,
			p_delete,
			max_generations,
			transit_network,
			elite_size,
			route_set_size,
			time_unit_factor,
			unsatisfied_factor,
			run_id

	):
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
		self.time_unit_factor = time_unit_factor  # 1 for minutes, 60 for seconds
		self.unsatisfied_factor = unsatisfied_factor
		self.individual_characteristics_values = {}
		self.total_route_length_values = {}
		self.run_id = None

	# Initializarea populatiei cu seturi de rute initiale
	def initialize_population(self):
		initial_individual = self.transit_network.find_initial_route_sets(self.route_set_size)
		print("Initial individual: ", initial_individual)
		for _ in range(self.pop_size):
			self.population.append(deepcopy(initial_individual))

	# Calcularea lungimii totale a rutelor
	def calculate_trl(self, route_set):
		route_set_key = tuple(tuple(route) for route in route_set)
		if route_set_key in self.total_route_length_values:
			return self.total_route_length_values[route_set_key]

		total_route_length = 0
		for route in route_set:
			edges = [(route[i], route[i + 1]) for i in range(len(route) - 1)]
			total_route_length += np.sum(
				[self.transit_network.graph[node_from][node_to] for node_from, node_to in edges])

		self.total_route_length_values[route_set_key] = total_route_length
		return total_route_length

	# Calcularea caracteristicilor pentru un individ (set de rute)
	def calculate_characteristics(self, individual):
		individual_key = tuple(tuple(route) for route in individual)
		if individual_key in self.individual_characteristics_values:
			return self.individual_characteristics_values[individual_key]

		node_to_routes = {node: [] for node in range(self.transit_network.number_of_vertices)}
		for route_index, route in enumerate(individual):
			for node in route:
				node_to_routes[node].append(route_index)

		direct_connections_demand = 0
		one_change_connections_demand = 0
		two_changes_connections_demand = 0
		total_demand = self.transit_network.total_demand
		total_demand_time = 0
		direct_travel_times = {}



		# Pasul 1: Calcularea timpilor de calatorie directi
		for i in range(self.transit_network.number_of_vertices):
			for j in range(i + 1, self.transit_network.number_of_vertices):
				demand_ij = self.transit_network.demand[i][j]
				routes_i = set(node_to_routes[i])
				routes_j = set(node_to_routes[j])

				if routes_i & routes_j:

					direct_travel_time = self.calculate_direct_travel_time(individual, i, j, routes_i & routes_j)
					if direct_travel_time != float('inf'):
						direct_connections_demand += demand_ij
						direct_travel_times[(min(i, j), max(i, j))] = direct_travel_time
						total_demand_time += demand_ij * direct_travel_time

		# Pasul 2: Calcularea timpilor de calatorie cu o schimbare si doua schimbari folosind timpii de calatorie directi
		for i in range(self.transit_network.number_of_vertices):
			for j in range(i + 1, self.transit_network.number_of_vertices):
				demand_ij = self.transit_network.demand[i][j]

				if (min(i, j), max(i, j)) in direct_travel_times:
					continue

				min_one_change_time, one_change_node = self.calculate_one_change_time(
					individual, i, j, node_to_routes, direct_travel_times)
				if one_change_node:
					one_change_connections_demand += demand_ij
					total_demand_time += demand_ij * min_one_change_time

				else:
					min_two_change_time = self.calculate_two_change_time(
						individual, i, j, node_to_routes, direct_travel_times)
					if min_two_change_time < float('inf'):
						two_changes_connections_demand += demand_ij
						total_demand_time += demand_ij * min_two_change_time

					else:
						total_demand_time += demand_ij * self.unsatisfied_factor * self.time_unit_factor

		unsatisfied_demand = (total_demand / 2 - (
				direct_connections_demand + one_change_connections_demand + two_changes_connections_demand))
		avg_travel_time = (2 * total_demand_time) / self.transit_network.total_demand
		d0 = direct_connections_demand * 100 / (self.transit_network.total_demand / 2)
		d1 = one_change_connections_demand * 100 / (self.transit_network.total_demand / 2)
		d2 = two_changes_connections_demand * 100 / (self.transit_network.total_demand / 2)
		dun = unsatisfied_demand * 100 / (self.transit_network.total_demand / 2)

		characteristics = (d0, d1, d2, dun, avg_travel_time)
		self.individual_characteristics_values[individual_key] = characteristics
		return characteristics

	# Calcularea fitness-ului pentru un individ
	def calculate_fitness(self, individual):
		d0, d1, d2, dun, avg_travel_time = self.calculate_characteristics(individual)
		total_route_length = self.calculate_trl(individual)
		fitness = 1 / (0.01 * avg_travel_time)
		return fitness

	# Calcularea timpului de calatorie directa
	def calculate_direct_travel_time(self, individual, i, j, common_routes):
		min_travel_time = float('inf')
		for route in common_routes:
			route_nodes = individual[route]
			if i in route_nodes and j in route_nodes:
				idx_i = route_nodes.index(i)
				idx_j = route_nodes.index(j)
				travel_time = sum(
					self.transit_network.graph[route_nodes[k]][route_nodes[k + 1]]
					for k in range(min(idx_i, idx_j), max(idx_i, idx_j)))
				min_travel_time = min(min_travel_time, travel_time)
		return min_travel_time

	# Calcularea timpului de calatorie cu o schimbare
	def calculate_one_change_time(self, individual, i, j, node_to_routes, direct_travel_times):
		routes_i = set(node_to_routes[i])
		routes_j = set(node_to_routes[j])
		min_one_change_time = float('inf')
		one_change_node = None

		for route_i in routes_i:
			for route_j in routes_j:
				common_nodes = set(individual[route_i]) & set(individual[route_j])
				for common_node in common_nodes:
					travel_time = (
							direct_travel_times.get(
								(min(i, common_node), max(i, common_node)),
								self.transit_network.graph[i][common_node]
							) +
							direct_travel_times.get(
								(min(common_node, j), max(common_node, j)),
								self.transit_network.graph[common_node][j]
							) +
							5 * self.time_unit_factor
					)
					if travel_time < min_one_change_time:
						min_one_change_time = travel_time
						one_change_node = common_node

		return min_one_change_time, one_change_node

	# Calcularea timpului de calatorie cu doua schimbari
	def calculate_two_change_time(self, individual, i, j, node_to_routes, direct_travel_times):
		routes_i = set(node_to_routes[i])
		routes_j = set(node_to_routes[j])
		min_two_change_time = float('inf')

		for route_i in routes_i:
			for node in individual[route_i]:
				routes_mid = set(node_to_routes[node])
				for route_j in routes_j:
					common_nodes_mid = routes_mid & set(individual[route_j])
					for common_node_mid in common_nodes_mid:
						travel_time = (
								direct_travel_times.get(
									(min(i, node), max(i, node)),
									self.transit_network.graph[i][node]
								) +
								direct_travel_times.get(
									(min(node, common_node_mid), max(node, common_node_mid)),
									self.transit_network.graph[node][common_node_mid]
								) +
								direct_travel_times.get(
									(min(common_node_mid, j), max(common_node_mid, j)),
									self.transit_network.graph[common_node_mid][j]
								) +
								10 * self.time_unit_factor
						)
						min_two_change_time = min(min_two_change_time, travel_time)

		return min_two_change_time

	# Interschimbarea rutelor bazat pe probabilitatea Pswap
	def uniform_crossover(self, parent_a, parent_b):
		a, b = deepcopy(parent_a), deepcopy(parent_b)
		for j in range(self.route_set_size):
			if random.random() < self.p_swap:
				a[j], b[j] = b[j], a[j]
		return a, b

	# Mutatia unui individ
	def mutation(self, individual):
		# Calcularea probabilitatilor de mutatie
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

		# Selectarea unei rute pe baza selectiei de tip ruleta
		selected_route_index = roulette_wheel_selection(mutation_probabilities)
		# Alegerea unui terminal din ruta la intamplare
		chosen_terminal = random.choice([0, len(individual[selected_route_index]) - 1])

		# Modificare mica
		if random.random() < self.p_ms:
			new_route = deepcopy(individual[selected_route_index])
			# Stergerea terminalului pe baza probabilitatii p_delete
			if random.random() < self.p_delete:
				if len(new_route) > 2:
					del new_route[chosen_terminal]
			# Adaugarea unui nod pe baza probabilitatii 1-p_delete
			else:
				neighbors = [
					node for node in range(self.transit_network.number_of_vertices)
					if self.transit_network.graph[individual[selected_route_index][chosen_terminal]][node] != np.inf and node not in new_route
				]
				if neighbors:
					neighbor = random.choice(neighbors)
					if chosen_terminal == 0:
						new_route.insert(0, neighbor)
					else:
						new_route.append(neighbor)

			if new_route not in individual and not is_subsequence(new_route, individual):
				individual[selected_route_index] = new_route
		# Modificare mare
		else:
			sum_ds = 0
			new_terminal_probabilities = [0 for _ in range(self.transit_network.number_of_vertices)]
			for node in range(self.transit_network.number_of_vertices):
				sum_ds += ds[individual[selected_route_index][chosen_terminal]][node]
			for node in range(self.transit_network.number_of_vertices):
				new_terminal_probabilities[node] = ds[individual[selected_route_index][chosen_terminal]][node] / sum_ds
			new_terminal = roulette_wheel_selection(new_terminal_probabilities)
			# Noua ruta este cel mai scurt drum dintre terminalul ales si noul terminal
			new_route = self.transit_network.shortest_paths_matrix[individual[selected_route_index][chosen_terminal]][new_terminal]
			if new_route not in individual and not is_subsequence(new_route, individual):
				individual[selected_route_index] = new_route
		return individual

	# Selectia de tip turneu
	def tournament_selection(self):
		tournament_population = random.sample(self.population, self.tournament_size)
		fitness_scores = [(individual, self.calculate_fitness(individual)) for individual in tournament_population]
		fitness_scores.sort(key=lambda x: x[1], reverse=True)
		return fitness_scores[0][0], fitness_scores[1][0]

	# Rularea algoritmului genetic
	def run_genetic_algorithm(self):
		fitness_history = []
		self.initialize_population()
		best_individual = deepcopy(self.population[0])
		best_fitness = self.calculate_fitness(best_individual)
		generations_without_improvement = 0
		convergence_threshold = 20

		for generation in range(self.max_generations):
			# Calcularea fitness-ului pentru fiecare individ din populatia curenta
			population_fitness = [self.calculate_fitness(individual) for individual in self.population]
			current_best_index = max(range(len(self.population)), key=lambda i: population_fitness[i])
			current_best = self.population[current_best_index]
			current_best_fitness = population_fitness[current_best_index]

			# Calcularea celui mai bun individ
			if current_best_fitness > best_fitness:
				best_individual = deepcopy(current_best)
				best_fitness = current_best_fitness
				generations_without_improvement = 0
			else:
				generations_without_improvement += 1
			fitness_history.append(best_fitness)

			included_nodes = set().union(*[set(route) for route in best_individual]) if best_individual else set()
			missing_nodes = self.transit_network.number_of_vertices - len(included_nodes)

			print()
			print()
			print(f"Generation: {generation+1}")
			print(f"Best Fitness: {best_fitness}")
			print(f"Best individual: {best_individual}")
			print(f"Number of nodes not included: {missing_nodes}")
			d0, d1, d2, dun, avg_travel_time = self.calculate_characteristics(best_individual)
			print("d0", d0, '%')
			print("d1", d1, '%')
			print("d2", d2, '%')
			print("dun", dun, '%')
			print("ATT", avg_travel_time)
			print("TRL", self.calculate_trl(best_individual))

			update_percent_complete(generation, self.run_id)

			'''
			socketio.emit('generation_update', {
				'generation': generation + 1,
				'best_fitness': best_fitness
			})
			'''
			# Crearea noii generatii
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

			# Verificarea indeplinirii conditiei de convergenta
			if generations_without_improvement >= convergence_threshold:
				break

		print("\n\nRezultatul aplicarii algoritmului genetic")
		print("Best individual", best_individual)
		d0, d1, d2, dun, att = self.calculate_characteristics(best_individual)
		print("d0", d0, '%')
		print("d1", d1, '%')
		print("d2", d2, '%')
		print("dun", dun, '%')
		print("ATT", att)
		print("TRL", self.calculate_trl(best_individual))
		print("Fitness final", best_fitness)

		# Generare nume fișier cu data și ora curente
		current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"ga_results_{current_time}.json"

		results = {
			"best_individual": best_individual,
			"d0": d0,
			"d1": d1,
			"d2": d2,
			"dun": dun,
			"att": att,
			"trl": self.calculate_trl(best_individual),
			"final_fitness": best_fitness
		}

		with open(filename, 'w') as file:
			json.dump(results, file, indent=4)
		# Afisarea valorilor fitnessului pe un grafic
		plt.plot(fitness_history)
		plt.xlabel('Generații')
		plt.ylabel('Fitness')
		plt.title('Evoluția  fitness-ului')
		plt.show()
		return filename

