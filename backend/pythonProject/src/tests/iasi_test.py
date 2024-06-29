from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.initial_solution import TransitNetwork

iasi_transit_network = TransitNetwork(
		191,
		"../../data/iasi/Iasi_links.txt",
		"../../data/iasi/Iasi_demand.txt"
	)

ga_iasi = GeneticAlgorithm(
	20,
	10,
	0.125,
	0.7,
						   0.4,
						   100,
						   iasi_transit_network,
						   4,
						   40,
						   60,
						   120)
ga_iasi.run_genetic_algorithm()

