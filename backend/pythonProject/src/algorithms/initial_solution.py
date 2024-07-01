import sys
import numpy as np


class TransitNetwork:
    # Initializarea obiectului TransitNetwork
    def __init__(self, vertices, links_file_path, demand_file_path):
        self.number_of_vertices = vertices
        self.graph = self.create_adjacency_matrix(links_file_path)
        self.demand = self.create_demand_matrix(demand_file_path)
        self.total_demand = np.sum(self.demand)
        self.shortest_paths_matrix = self.precompute_all_pairs_shortest_paths()

    # Precalcularea celor mai scurte drumuri intre toate perechile de noduri
    def precompute_all_pairs_shortest_paths(self):
        all_pairs_shortest_paths = []
        for i in range(self.number_of_vertices):
            all_pairs_shortest_paths.append(self.dijkstra_algorithm(i))
        return all_pairs_shortest_paths

    # Calcularea matricei DS (demand satisfaction)
    def calculate_ds_matrix(self):
        ds = np.zeros((self.number_of_vertices, self.number_of_vertices))
        for i in range(self.number_of_vertices):
            for j in range(self.number_of_vertices):
                if i != j:
                    total_demand = sum(
                        self.demand[m][n] for m in self.shortest_paths_matrix[i][j]
                        for n in self.shortest_paths_matrix[i][j]
                    )
                    ds[i][j] = total_demand
        return ds

    # Gasirea nodului cu cea mai mica distanta care nu este inca in spt_set
    def min_distance_vertex(self, distances, spt_set):
        min_dist = sys.maxsize
        min_index = 0
        for u in range(self.number_of_vertices):
            if distances[u] < min_dist and u not in spt_set:
                min_dist = distances[u]
                min_index = u
        return min_index

    # Implementarea algoritmului Dijkstra pentru gasirea celui mai scurt drum de la un nod sursa
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

    # Crearea matricei de cereri (demand) dintr-un fisier
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

    # Crearea matricei de adiacenta (graph) dintr-un fisier
    def create_adjacency_matrix(self, file_path):
        adjacency_matrix = np.full((self.number_of_vertices, self.number_of_vertices), np.inf)
        np.fill_diagonal(adjacency_matrix, 0)

        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                parts = line.strip().split(',')
                from_node = int(parts[0]) - 1
                to_node = int(parts[1]) - 1
                travel_time = float(parts[2])
                adjacency_matrix[from_node][to_node] = travel_time
        return adjacency_matrix

    # Gasirea setului initial de rute
    def find_initial_route_sets(self, route_set_size):
        already_deleted_paths = [[[] for _ in range(self.number_of_vertices)] for _ in range(self.number_of_vertices)]
        routes_set = []  # the set of routes
        routes_number = route_set_size  # total number of routes in the solution
        ds = self.calculate_ds_matrix()
        m = 0
        while m < routes_number:
            # Gasirea perechii de noduri cu cea mai mare valoare DS
            max_ds = -1
            max_nodes = (-1, -1)
            for i in range(self.number_of_vertices):
                for j in range(self.number_of_vertices):
                    if ds[i][j] > max_ds:
                        max_ds = ds[i][j]
                        max_nodes = (i, j)

            # Adaugarea celui mai scurt drum intre max_nodes la setul de rute
            shortest_path = self.shortest_paths_matrix[max_nodes[0]][max_nodes[1]]

            # Verificarea daca ruta depaseste 40 de statii
            if len(shortest_path) > 40:
                middle_index = len(shortest_path) // 2
                part1 = shortest_path[:middle_index + 1]
                part2 = shortest_path[middle_index:]
                routes_set.append(part1)
                routes_set.append(part2)
            else:
                routes_set.append(shortest_path)

            # Actualizarea matricei DS dupa satisfacerea cererilor rutei adaugate
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

        # Identificarea nodurilor neutilizate
        used_nodes = set()
        for route in routes_set:
            for node in route:
                used_nodes.add(node)
        unused_nodes = [node for node in range(self.number_of_vertices) if node not in used_nodes]
        for unused_node in unused_nodes:
            self.process_unused_node(unused_node, routes_set)
        used_nodes = set()
        for route in routes_set:
            for node in route:
                used_nodes.add(node)
        unused_nodes = [node for node in range(self.number_of_vertices) if node not in used_nodes]
        print(unused_nodes)
        print("Initial routes set:", routes_set)
        return routes_set

    # Procesarea unui nod neutilizat pentru a-l adauga la setul de rute
    def process_unused_node(self, unused_node, routes_set):
        routes_with_demand = []
        for route in routes_set:
            route_demand = sum(self.demand[unused_node][route[i]] for i in range(len(route)))
            routes_with_demand.append((route, route_demand))
        routes_with_demand_sorted = sorted(routes_with_demand, key=lambda x: x[1], reverse=True)
        node_routes_number = 0
        for route, demand in routes_with_demand_sorted:
            if node_routes_number < 5:
                best_position = None
                best_travel_time = float('inf')

                # Verificarea inserarii la inceputul rutei
                if self.graph[unused_node][route[0]] != float('inf'):
                    best_position = 0
                    best_travel_time = self.graph[unused_node][route[0]]

                # Verificarea inserarii la sfarsitul rutei
                if self.graph[unused_node][route[-1]] != float('inf'):
                    if self.graph[unused_node][route[-1]] < best_travel_time:
                        best_position = len(route)
                        best_travel_time = self.graph[unused_node][route[-1]]

                # Verificarea inserarii in mijlocul rutei
                for k in range(1, len(route) - 1):
                    if (self.graph[unused_node][route[k]] != float('inf')
                            and self.graph[route[k - 1]][unused_node] != float('inf')):
                        travel_time = self.graph[unused_node][route[k]] + self.graph[route[k - 1]][unused_node]
                        if travel_time < best_travel_time:
                            best_travel_time = travel_time
                            best_position = k

                # Inserarea nodului la cea mai buna pozitie gasita
                if best_position is not None:
                    route.insert(best_position, unused_node)
                    node_routes_number += 1
