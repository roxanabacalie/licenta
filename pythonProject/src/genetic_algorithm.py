from random import random


pop_size = 100 # desired population size
elite_size = 1 # desired number of elite individuals
route_set_size = 8 # number of routes in the individual
t = 2 # tournament size for fitness
p_swap = 0.1 # probability of swapping an index in Uniform Crossover
p_ms = 0.8 # probability of doing small modification in Mutation
p_delete = 0.5 # probability of deleting the selected terminal in small modification
max_gen = 10 #maximum number of generations
P = []

demand_matrix = [[0 for _ in range(10)] for _ in range(10)] #TODO
def calculate_fitness(individual):
	fitness = 0
	for i in range(len(individual)):
		route = individual[i]
		for node1 in range(len(route)):
			for node2 in range(len(route)):
				fitness += demand_matrix[node1][node2]

def uniform_crossover(a, b):
	for i in range(route_set_size):
		rand = random.random()
		if rand >= p_swap:
			temp = a[i]
			a[i] = b[i]
			b[i] = temp
	return a, b

def mutation(individual):
	pass

def tournament_selection(population):
	best = population[0]
	for i in range(1, pop_size):
		next = population[i]
		if calculate_fitness(next) > calculate_fitness(best):
			best = next
	return best

for i in range(pop_size):
	P.append(initial_route_set(route_set_size))

best = None
while(max_gen>0):
	for i in range (len(P)):
		if best = None or calculate_fitness(P[i]) > calculate_fitness(Best):
			best = P[i]

	Q = # the eliteSize fittest individuals in P, breaking ties at random
	for i in range((pop_size - elite_size)/2):
		Pa = tournament_selection(P)
		Pb = tournament_selection(P)
		Ca,Cb = uniform_crossover(Pa, Pb)
		Q.append(Mutation(Ca))
		Q.append(Mutation(Cb))
	P = Q
	max_gen = max_gen - 1



