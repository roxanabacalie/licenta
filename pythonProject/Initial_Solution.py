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

def create_adjacency_matrix(file_path, number_of_nodes):
    adjacency_matrix = np.zeros((number_of_nodes, number_of_nodes))
    with open(file_path, 'r') as file:
        next(file)  # Skip the header
        for line in file:
            parts = line.strip().split(',')
            from_node = int(parts[0]) - 1
            to_node = int(parts[1]) - 1
            travel_time = int(parts[2])
            adjacency_matrix[from_node][to_node] = travel_time
    return adjacency_matrix

Mandl_transit_network = TransitNetwork(15)
Mandl_transit_network.graph = \
                   [[0, 8, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf], #0
                   [8, 0, 2, 3, 6, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf],       #1
                   [inf, 2, 0, inf, inf, 3, inf, inf, inf, inf, inf, inf, inf, inf, inf],   #2
                   [inf, 3, inf, 0, 4, 4, inf, inf, inf, inf, inf, 10, inf, inf, inf],      #3
                   [inf, 6, inf, 4, 0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf],   #4
                   [inf, inf, 3, 4, inf, 0, inf, 2, inf, inf, inf, inf, inf, inf, 3],       #5
                   [inf, inf, inf, inf, inf, inf, 0, inf, inf, 7, inf, inf, inf, inf, 2],   #6
                   [inf, inf, inf, inf, inf, 2, inf, 0, inf, 8, inf, inf, inf, inf, 2],     #7
                   [inf, inf, inf, inf, inf, inf, inf, inf, 0, inf, inf, inf, inf, inf, 8], #8
                   [inf, inf, inf, inf, inf, inf, 7, 8, inf, 0, 5, inf, 10, 8, inf],        #9
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 5, 0, 10, 5, inf, inf],  #10
                   [inf, inf, inf, 10, inf, inf, inf, inf, inf, inf, 10, 0, inf, inf, inf],   #11
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 10, 5, inf, 0, 2, inf],     #12
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 8, inf, inf, 2, 0, inf],   #13
                   [inf, inf, inf, inf, inf, 3, 2, 2, 8, inf, inf, inf, inf, inf, 0],       #14
                   ]

Mandl_transit_network.graph=create_adjacency_matrix("mandl1_links.txt",15)
Mandl_transit_network.demand = create_demand_matrix("mandl1_demand.txt", 15)

ds = [[] for _ in range(Mandl_transit_network.number_of_vertices)]
shortest_paths = [[] for _ in range(Mandl_transit_network.number_of_vertices)]
for i in range(Mandl_transit_network.number_of_vertices):
    shortest_paths[i] = Mandl_transit_network.dijkstra_algorithm(i)
i=0
for row in shortest_paths:
    print(str(i)+': ' + ' '.join(map(str, row)))
    i=i+1
print("Shortest paths: "+str(shortest_paths))

def find_initial_route_sets(graph):
    Y = [] # the set of routes
    N = 8 # total number of routes in the solution

    # Calculate DS matrix
    ds = [[0 for _ in range(graph.number_of_vertices)] for _ in range(graph.number_of_vertices)]
    for i in range(graph.number_of_vertices):
        for j in range(graph.number_of_vertices):
            total_demand = 0
            for m in graph.dijkstra_algorithm(i)[j]:
                for n in graph.dijkstra_algorithm(i)[j]:
                    total_demand = total_demand + graph.demand[m][n]
            ds[i][j] = total_demand
    print(graph.demand)
    print("DS matrix:")
    i=0
    for row in ds:
        print(str(i)+': ' + ' '.join(map(str, row)))
        i=i+1
    m = 0

    while True:
        # Find pair of nodes with highest ds value
        max_ds = -1
        max_nodes = (-1, -1)
        for i in range(graph.number_of_vertices):
            for j in range(graph.number_of_vertices):
                if ds[i][j] > max_ds:
                    max_ds = ds[i][j]
                    max_nodes = (i, j)

        print(max_nodes)
        # Add shortest path between max_nodes to set Y
        shortest_path = shortest_paths[max_nodes[0]][max_nodes[1]]
        Y.append(shortest_path)

        print(shortest_path)

        m += 1
        if m == N:
            break

        # Update ds matrix after satisfying demands of the added route
        for i in range(graph.number_of_vertices):
            for j in range(graph.number_of_vertices):
                if i in shortest_path and j in shortest_path and i != j:
                    for k in range(graph.number_of_vertices):
                        for l in range(graph.number_of_vertices):
                            if k != l:
                                if i in shortest_paths[k][l] and j in shortest_paths[k][l] and ds[k][l]>0:
                                    #shortest_paths[k][l].remove()
                                    ds[k][l] -= graph.demand[i][j]
                                    if k==0 and l==12:
                                        print(k,l,i,j)
        print("DS matrix:")
        i = 0
        for row in ds:
            print(str(i) + ': ' + ' '.join(map(str, row)))
            i = i + 1


    return Y

    #a, b - terminals of the highest ds route
    #add shortest route between a and b to the set Y

print("Initial route sets: "+ str(find_initial_route_sets(Mandl_transit_network)))