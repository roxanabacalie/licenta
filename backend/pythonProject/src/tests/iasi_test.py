from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.initial_solution import TransitNetwork

iasi_transit_network = TransitNetwork(
		191,
		"../../data/iasi/Iasi_links.txt",
		"../../data/iasi/Iasi_demand.txt"
	)

ga_iasi = GeneticAlgorithm(
	60,
	10,
	0.7,
	0.7,
	0.4,
	100,
	iasi_transit_network,
	5,
	35,
	60,
	120,
	None)
ga_iasi.run_genetic_algorithm()

