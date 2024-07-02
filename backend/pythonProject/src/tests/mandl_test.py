from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.initial_solution import TransitNetwork


gawip_individual4=[
	[0, 1, 2, 5, 7, 9, 10, 11, 3, 4],
	[0, 1, 4, 3, 5, 7, 9, 12, 13],
	[8, 14, 6, 9, 13, 12, 10, 11, 3, 1, 0],
	[12, 13, 9, 6, 14, 5, 2, 1, 0]
]

gawip_individual6=[
	[0, 1, 2, 5, 7, 9, 10, 12],
	[0, 1, 4, 3, 5, 7, 9, 12, 13],
	[4, 1, 2, 5, 3, 11, 10, 9, 6, 14, 8],
	[0, 1, 2, 5, 14, 6, 9, 13, 12, 10, 11, 3, 4],
	[8, 14, 5, 2, 1, 0],
	[0, 1, 3, 11, 10, 12, 13, 9, 7, 14, 6]
]

gawip_individual7=[
	[0, 1, 2, 5, 7, 9, 10, 12, 13],
	[10, 12, 13, 9, 7, 5, 3, 4, 1, 2],
	[13, 12, 10, 9, 6, 14, 7, 5, 3, 4, 1, 0],
	[8, 14, 5, 2, 1, 0],
	[8, 14, 5, 2, 1, 3, 11, 10, 12, 13, 9],
	[0, 1, 2, 5, 14, 6, 9, 13, 12, 10, 11, 3, 4],
	[8, 14, 6, 9, 10, 11, 3, 1, 0]
]

gawip_individual8 = [
		[0, 1, 2, 5, 7, 9, 10, 12],
		[2, 1, 4, 3, 5, 7, 9, 10, 12],
		[8, 14, 5, 2, 1, 0],
		[8, 14, 7, 5, 2, 1, 3, 11, 10, 9, 13, 12],
		[11, 10, 12, 13, 9, 6, 14, 7, 5, 3, 4, 1, 0],
		[0, 1, 2, 5, 14, 6, 9, 13, 12, 10, 11, 3, 4],
		[8, 14, 5, 3, 11, 10, 12, 13, 9, 7],
		[8, 14, 6, 9, 10, 11, 3, 1, 0]
]

mandl_transit_network = TransitNetwork(
		15,
		"../../data/mandl/mandl1_links.txt",
		"../../data/mandl/mandl1_demand.txt"
	)

ga4 = GeneticAlgorithm(
		16,
		10,
		0.125,
		0.7,
		0.4,
		100,
		mandl_transit_network,
		4,
		4,
		1,
		50
	)

ga6 = GeneticAlgorithm(
		16,
		10,
		0.125,
		0.7,
		0.4,
		100,
		mandl_transit_network,
		4,
		6,
		1,
		50
	)

ga7 = GeneticAlgorithm(
		16,
		10,
		0.125,
		0.7,
		0.4,
		400,
		mandl_transit_network,
		4,
		7,
		1,
		50
	)

ga8 = GeneticAlgorithm(
		16,
		10,
		0.125,
		0.7,
		0.4,
		100,
		mandl_transit_network,
		4,
		8,
		1,
		50
	)


print("GAWIP 4 rute")
fitness = ga4.calculate_fitness(gawip_individual4)
(d0, d1, d2, dun, ATT) = ga4.calculate_characteristics(gawip_individual4)
trl = ga4.calculate_trl(gawip_individual4)
print("fitness", fitness)
print("d0", d0, '%')
print("d1", d1, '%')
print("d2", d2, '%')
print("dun", dun, '%')
print("ATT", ATT)
print("TRL", trl)


print("\nGAWIP 6 rute")
fitness = ga6.calculate_fitness(gawip_individual6)
(d0, d1, d2, dun, ATT) = ga6.calculate_characteristics(gawip_individual6)
trl = ga6.calculate_trl(gawip_individual6)
print("fitness", fitness)
print("d0", d0, '%')
print("d1", d1, '%')
print("d2", d2, '%')
print("dun", dun, '%')
print("ATT", ATT)
print("TRL", trl)


print("\nGAWIP 7 rute")
fitness = ga7.calculate_fitness(gawip_individual7)
(d0, d1, d2, dun, ATT) = ga7.calculate_characteristics(gawip_individual7)
trl = ga7.calculate_trl(gawip_individual7)
print("fitness", fitness)
print("d0", d0, '%')
print("d1", d1, '%')
print("d2", d2, '%')
print("dun", dun, '%')
print("ATT", ATT)
print("TRL", trl)

print("\nGAWIP 8 rute")
fitness = ga8.calculate_fitness(gawip_individual8)
(d0, d1, d2, dun, ATT) = ga8.calculate_characteristics(gawip_individual8)
trl = ga8.calculate_trl(gawip_individual8)
print("fitness", fitness)
print("d0", d0, '%')
print("d1", d1, '%')
print("d2", d2, '%')
print("dun", dun, '%')
print("ATT", ATT)
print("TRL", trl)

print("\nGA 4 rute")
ga4.run_genetic_algorithm()

print("\nGA 6 rute")
ga6.run_genetic_algorithm()


print("\nGA 7 rute")
ga7.run_genetic_algorithm()

print("\nGA 8 rute")
ga8.run_genetic_algorithm()
p