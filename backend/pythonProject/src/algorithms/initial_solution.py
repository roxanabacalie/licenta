import sys
from math import inf
import numpy as np
from src.algorithms.visual_representation import draw_routes_mandl_network

class TransitNetwork:
    def __init__(self, vertices, links_file_path, demand_file_path):
        self.number_of_vertices = vertices
        self.graph = self.create_adjacency_matrix(links_file_path)
        self.demand = self.create_demand_matrix(demand_file_path)
        self.total_demand = np.sum(self.demand)
        self.shortest_paths_matrix = self.precompute_all_pairs_shortest_paths()

    def print_graph(self):
        for node in range(self.number_of_vertices):
            print("\nThe neighbors of node " + str(node))
            for other_node in range(self.number_of_vertices):
                if self.graph[node][other_node] != 0 and self.graph[node][other_node] != inf:
                    print(f"The node {other_node} at distance {self.graph[node][other_node]}")

    def precompute_all_pairs_shortest_paths(self):
        all_pairs_shortest_paths = []
        for i in range(self.number_of_vertices):
            all_pairs_shortest_paths.append(self.dijkstra_algorithm(i))
        return all_pairs_shortest_paths

    def calculate_ds_matrix(self):
        ds = np.zeros((self.number_of_vertices, self.number_of_vertices))
        for i in range(self.number_of_vertices):
            for j in range(self.number_of_vertices):
                if i != j:
                    total_demand = sum(self.demand[m][n] for m in self.shortest_paths_matrix[i][j] for n in self.shortest_paths_matrix[i][j])
                    ds[i][j] = total_demand
        return ds

    def min_distance_vertex(self, distances, spt_set):
        min_dist = sys.maxsize
        min_index = 0
        for u in range(self.number_of_vertices):
            if distances[u] < min_dist and u not in spt_set:
                min_dist = distances[u]
                min_index = u
        return min_index

    def dijkstra_algorithm(self, source):
        shortest_paths = [[] for _ in range(self.number_of_vertices)]
        spt_set = []
        distances = np.full(self.number_of_vertices, np.inf)
        distances[source] = 0

        for neighbor in range(self.number_of_vertices):
            if self.graph[source][neighbor] > 0 and neighbor not in spt_set:
                distances[neighbor] = distances[source] + self.graph[source][neighbor]
                shortest_paths[neighbor].append(source)

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
            next(file)
            for line in file:
                parts = line.strip().split(',')
                from_node = int(parts[0]) - 1
                to_node = int(parts[1]) - 1
                travel_time = float(parts[2])
                adjacency_matrix[from_node][to_node] = travel_time
        return adjacency_matrix

    def find_initial_route_sets(self, route_set_size):
        already_deleted_paths = [[[] for _ in range(self.number_of_vertices)] for _ in range(self.number_of_vertices)]
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
            shortest_path = self.shortest_paths_matrix[max_nodes[0]][max_nodes[1]]
            Y.append(shortest_path)

            # Update ds matrix after satisfying demands of the added route
            for i in shortest_path:
                for j in shortest_path:
                    if i != j:
                        for k in range(self.number_of_vertices):
                            for l in range(self.number_of_vertices):
                                if k != l:
                                    if (i in self.shortest_paths_matrix[k][l]
                                            and j in self.shortest_paths_matrix[k][l]
                                            and ds[k][l] > 0 and (i, j) not in already_deleted_paths[k][l]):
                                        already_deleted_paths[k][l].append((i, j))
                                        ds[k][l] -= self.demand[i][j]
            m += 1
            if m == N:
                break

        # Identify unused nodes
        used_nodes = set()
        for route in Y:
            for node in route:
                used_nodes.add(node)
        unused_nodes = [node for node in range(self.number_of_vertices) if node not in used_nodes]

        # Add unused nodes to existing routes
        for unused_node in unused_nodes:
            best_route_index = -1
            best_demand = 0
            best_position = None
            for i, route in enumerate(Y):
                if self.demand[unused_node][route[0]] > best_demand:
                    best_route_index = i
                    best_demand = self.demand[unused_node][route[0]]
                    best_position = 0  # Insert at the beginning
                if self.demand[unused_node][route[-1]] > best_demand:
                    best_route_index = i
                    best_demand = self.demand[unused_node][route[-1]]
                    best_position = len(route)  # Insert at the end

            if best_position is not None:
                Y[best_route_index].insert(best_position, unused_node)

        print("Initial routes set:", Y)
        return Y