import sys
from math import inf
import numpy as np


class TransitNetwork:
    def __init__(self, vertices, links_file_path, demand_file_path):
        self.number_of_vertices = vertices
        self.graph = self.create_adjacency_matrix(links_file_path)
        self.demand = self.create_demand_matrix(demand_file_path)

    def print_graph(self):
        for node in range(self.number_of_vertices):
            print("")
            print("The neighbors of node " + str(node))
            for other_node in range(self.number_of_vertices):
                if self.graph[node][other_node] != 0 and self.graph[node][other_node] != inf:
                    print("The node " + str(other_node) + " at distance " + str(self.graph[node][other_node]))

    def calculate_ds_matrix(self):
        ds = [[0 for _ in range(self.number_of_vertices)] for _ in range(self.number_of_vertices)]
        for i in range(self.number_of_vertices):
            for j in range(self.number_of_vertices):
                total_demand = 0
                for m in self.dijkstra_algorithm(i)[j]:
                    for n in self.dijkstra_algorithm(i)[j]:
                        total_demand = total_demand + self.demand[m][n]
                ds[i][j] = total_demand
        return ds

    # method that returns the index of the vertex at a minimum distance
    def min_distance_vertex(self, distances, spt_set):
        min_dist = sys.maxsize
        min_index = 0
        for u in range(self.number_of_vertices):
            if distances[u] < min_dist and u not in spt_set:
                min_dist = distances[u]
                min_index = u
        return min_index

    # dijkstra's algorithm that returns the shortest paths from a source to all vertices
    def dijkstra_algorithm(self, source):
        shortest_paths = [[] for _ in range(self.number_of_vertices)]

        spt_set = []
        distances = [inf] * self.number_of_vertices
        distances[source] = 0

        for neighbor in range(self.number_of_vertices):
            if self.graph[source][neighbor] > 0 and neighbor not in spt_set:
                distances[neighbor] = distances[source] + self.graph[source][neighbor]
                shortest_paths[neighbor].append(source)
        # update distance values of its adjacent vertices

        while len(spt_set) != self.number_of_vertices:
            u = self.min_distance_vertex(distances, spt_set)
            spt_set.append(u)
            for neighbor in range(self.number_of_vertices):
                if self.graph[u][neighbor] > 0 and neighbor not in spt_set:
                    if distances[u] + self.graph[u][neighbor] < distances[neighbor]:
                        distances[neighbor] = distances[u] + self.graph[u][neighbor]
                        shortest_paths[neighbor] = shortest_paths[u] + [u]
        for v in range(self.number_of_vertices):
            shortest_paths[v].append(v)
        return shortest_paths

    def create_demand_matrix(self, file_path):
        demand_data = []
        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                parts = line.strip().split(',')
                from_node = int(parts[0])
                to_node = int(parts[1])
                demand = int(parts[2])
                demand_data.append((from_node, to_node, demand))
        demand_matrix = np.zeros((self.number_of_vertices, self.number_of_vertices))
        for from_node, to_node, demand in demand_data:
            demand_matrix[from_node - 1][to_node - 1] = demand
        return demand_matrix

    def create_adjacency_matrix(self, file_path):
        adjacency_matrix = np.zeros((self.number_of_vertices, self.number_of_vertices))
        with open(file_path, 'r') as file:
            next(file)  # Skip the header
            for line in file:
                parts = line.strip().split(',')
                from_node = int(parts[0]) - 1
                to_node = int(parts[1]) - 1
                travel_time = int(parts[2])
                adjacency_matrix[from_node][to_node] = travel_time
        return adjacency_matrix

    def find_initial_route_sets(self, route_set_size):
        shortest_paths = [[] for _ in range(self.number_of_vertices)]
        for i in range(self.number_of_vertices):
            shortest_paths[i] = self.dijkstra_algorithm(i)
        already_deleted_paths = [[[] for _ in range(self.number_of_vertices)] for _ in
                                 range(self.number_of_vertices)]

        Y = []  # the set of routes
        N = route_set_size  # total number of routes in the solution

        # Calculate DS matrix
        ds = self.calculate_ds_matrix()

        m = 0

        while True:
            # Find pair of nodes with highest ds value
            max_ds = -1
            max_nodes = (-1, -1)
            for i in range(self.number_of_vertices):
                for j in range(self.number_of_vertices):
                    if ds[i][j] > max_ds:
                        max_ds = ds[i][j]
                        max_nodes = (i, j)

            # Add shortest path between max_nodes to set Y
            shortest_path = shortest_paths[max_nodes[0]][max_nodes[1]]
            Y.append(shortest_path)

            m += 1
            if m == N:
                break

            # Update ds matrix after satisfying demands of the added route
            for i in range(self.number_of_vertices):
                for j in range(self.number_of_vertices):
                    if i in shortest_path and j in shortest_path and i != j:
                        for k in range(self.number_of_vertices):
                            for l in range(self.number_of_vertices):
                                if k != l:
                                    if (i in shortest_paths[k][l] and j in shortest_paths[k][l] and ds[k][l] > 0 and
                                            (i, j) not in already_deleted_paths[k][l]):
                                        already_deleted_paths[k][l].append((i, j))
                                        ds[k][l] -= self.demand[i][j]
        return Y


Mandl_transit_network = TransitNetwork(15, "../data/mandl1_links.txt", "../data/mandl1_demand.txt")
print("Initial route sets: " + str(Mandl_transit_network.find_initial_route_sets(8)))
