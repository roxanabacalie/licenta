import sys
from math import inf
import numpy as np

class TransitNetwork:
    def __init__(self, vertices):
        self.number_of_vertices = vertices
        self.graph = [[inf for _ in range(vertices)] for _ in range(vertices)]
        self.demand = [[inf for _ in range(vertices)] for _ in range(vertices)]

    def printGraph(self):
        for node in range(self.number_of_vertices):
            print("")
            print("The neighbors of node " + str(node))
            for other_node in range(self.number_of_vertices):
                if self.graph[node][other_node] != 0 and self.graph[node][other_node] != inf:
                    print("The node " + str(other_node) + " at distance " + str(self.graph[node][other_node]))

    def printDemand(self):
        print("Demand Matrix")
        for node1 in range(self.number_of_vertices):
            for node2 in range(self.number_of_vertices):
                print(str(self.demand[node1][node2]), end=" ")
            print("")

    def min_distance_vertex(self, distances, sptSet):
        min_dist = sys.maxsize
        min_index = 0
        for u in range(self.number_of_vertices):
            if distances[u] < min_dist and u not in sptSet:
                min_dist = distances[u]
                min_index = u
        return min_index

    def dijkstra_algorithm(self, source):
        shortest_paths = [[] for _ in range(self.number_of_vertices)]

        sptSet = []
        distances = [inf] * self.number_of_vertices
        distances[source] = 0

        for neighbor in range(self.number_of_vertices):
            if self.graph[source][neighbor] > 0 and neighbor not in sptSet:
                distances[neighbor]= distances[source] + self.graph[source][neighbor]
                shortest_paths[neighbor].append(source)
        # update distance values of its adjacent vertices

        while len(sptSet) != self.number_of_vertices:
            u = self.min_distance_vertex(distances, sptSet)
            sptSet.append(u)
            for neighbor in range(self.number_of_vertices):
                if self.graph[u][neighbor]>0 and neighbor not in sptSet:
                    if(distances[u] + self.graph[u][neighbor] < distances[neighbor]):
                        distances[neighbor] = distances[u] + self.graph[u][neighbor]
                        shortest_paths[neighbor] = shortest_paths[u] + [u]
        for v in range(self.number_of_vertices):
            shortest_paths[v].append(v)
        return shortest_paths

def create_demand_matrix(file_path, number_of_nodes):
    demand_data = []
    with open(file_path, 'r') as file:
        next(file)
        for line in file:
            parts = line.strip().split(',')
            from_node = int(parts[0])
            to_node = int(parts[1])
            demand = int(parts[2])
            demand_data.append((from_node, to_node, demand))
    demand_matrix = np.zeros((number_of_nodes, number_of_nodes))
    for from_node, to_node, demand in demand_data:
        demand_matrix[from_node - 1][to_node - 1] = demand
    return demand_matrix

Mandl_transit_network = TransitNetwork(15)
#                   0  1   2    3    4    5    6    7    8    9   10   11   12   13   14
Mandl_transit_network.graph = \
                   [[0, 8, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf], #0
                   [8, 0, 2, 3, 6, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf],       #1
                   [inf, 2, 0, inf, inf, 3, inf, inf, inf, inf, inf, inf, inf, inf, inf],   #2
                   [inf, 3, inf, 0, 4, 4, inf, inf, inf, inf, inf, 10, inf, inf, inf],      #3
                   [inf, 6, inf, 4, 0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf],   #4
                   [inf, inf, 3, 4, inf, 0, inf, 2, inf, inf, inf, inf, inf, inf, 3],       #5
                   [inf, inf, inf, inf, inf, inf, 0, inf, inf, 7, inf, inf, inf, inf, 2],   #6
                   [inf, inf, inf, inf, inf, 2, 0, inf, inf, 8, inf, inf, inf, inf, 2],     #7
                   [inf, inf, inf, inf, inf, inf, inf, inf, 0, inf, inf, inf, inf, inf, 8], #8
                   [inf, inf, inf, inf, inf, inf, 7, 8, inf, 0, 5, inf, 10, 8, inf],        #9
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 5, inf, 10, 5, inf, inf],  #10
                   [inf, inf, inf, 1, inf, inf, inf, inf, inf, inf, 1, 0, inf, inf, inf],   #11
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 1, 5, inf, 0, 2, inf],     #12
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 8, inf, inf, 2, 0, inf],   #13
                   [inf, inf, inf, inf, inf, 3, 2, 2, 8, inf, inf, inf, inf, inf, 0],       #14
                   ]

Mandl_transit_network.demand = create_demand_matrix("mandl1_demand.txt", 15)
Mandl_transit_network.printGraph()
ds = [[] for _ in range(Mandl_transit_network.number_of_vertices)]
"""
for i in range(Mandl_transit_network.number_of_vertices):
    for j in range(Mandl_transit_network.number_of_vertices):
        if i != j:
            shortest_path = Mandl_transit_network.dijkstra_algorithm(i, j)
            for node1, node2 in shortest_path:
                ds[i][j] += Mandl_transit_network.demand[node1][node2]
"""
shortest_paths = Mandl_transit_network.dijkstra_algorithm(5)
print("Shortest paths: "+str(shortest_paths))

#def find_initial_route_sets(graph):
#    Y = []
#    m = 0
