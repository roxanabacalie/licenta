import random


def roulette_wheel_selection(probabilities):
	total = sum(probabilities)
	rand = random.random() * total
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
