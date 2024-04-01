from math import inf


class Graph:
    def __init__(self, vertices):
        self.number_of_vertices = vertices
        self.graph = [[inf for _ in range(vertices)] for _ in range(vertices)]

    def printGraph(self):
        for node in range(self.number_of_vertices):
            print("")
            print("Vecinii nodului " + str(node))
            for other_node in range(self.number_of_vertices):
                if self.graph[node][other_node] != 0 and self.graph[node][other_node] != inf:
                    print("Nodul " + str(other_node) + " la distanta " + str(self.graph[node][other_node]))

    def min_distance(self, distances, sptSet):
        min_dist = inf
        for u in range(self.number_of_vertices):
            if(distances[u] < min_dist and u not in sptSet):
                min_dist = distances[u]
                min_index = u
        return min_index
    def dijkstra_algorithm(self, vertex):
        sptSet = []
        distances = [inf] * self.number_of_vertices
        distances[vertex] = 0
        while sptSet.size != self.number_of_vertices:
            u = self.min_distance(distances, sptSet)
            sptSet.append(u)
            for neighbor in self.graph[u]
                if neighbor != inf and neighbor !=0:
                    if(distances[u]+self.graph[u][neighbor]<distances[neighbor]):
                        distances[neighbor]=distances[u]+self.graph[u][neighbor]



Mandl_graph = Graph(15)
#                     1  2  3  4  5  6  7  8  9 1 11 12 13 14
Mandl_graph.graph=[[0, 8, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf], #
                   [8, 0, 2, 3, 6, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf], #1
                   [inf, 2, 0, inf, inf, 3, inf, inf, inf, inf, inf, inf, inf, inf, inf], #2
                   [inf, 3, inf, 0, 4, 4, inf, inf, inf, inf, inf, 10, inf, inf, inf], #3
                   [inf, 6, inf, 4, 0, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf], #4
                   [inf, inf, 3, 4, inf, 0, inf, 2, inf, inf, inf, inf, inf, inf, 3], #5
                   [inf, inf, inf, inf, inf, inf, 0, inf, inf, 7, inf, inf, inf, inf, 2], #6
                   [inf, inf, inf, inf, inf, 2, 0, inf, inf, 8, inf, inf, inf, inf, 2], #7
                   [inf, inf, inf, inf, inf, inf, inf, inf, 0, inf, inf, inf, inf, inf, 8], #8
                   [inf, inf, inf, inf, inf, inf, 7, 8, inf, 0, 5, inf, 10, 8, inf], #9
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 5, inf, 10, 5, inf, inf], #10
                   [inf, inf, inf, 1, inf, inf, inf, inf, inf, inf, 1, 0, inf, inf, inf], #11
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 1, 5, inf, 0, 2, inf], #12
                   [inf, inf, inf, inf, inf, inf, inf, inf, inf, 8, inf, inf, 2, 0, inf], #13
                   [inf, inf, inf, inf, inf, 3, 2, 2, 8, inf, inf, inf, inf, inf, 0], #14
                   ]
Mandl_graph.printGraph()




def find_initial_route_sets(graph):
    Y = []
    m = 0



