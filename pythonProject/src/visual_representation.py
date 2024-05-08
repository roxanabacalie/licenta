import networkx as nx
import matplotlib.pyplot as plt

from src.initial_solution import TransitNetwork

G = nx.Graph()
node_positions = {}
with open("../data/mandl1_nodes.txt", "r") as file:
    next(file)
    for line in file:
        node, lat, lon, _ = map(float, line.strip().split(","))
        G.add_node(node-1)
        node_positions[node-1] = (lon, lat)

with open("../data/mandl1_links.txt", "r") as file:
    next(file)
    for line in file:
        from_node, to_node, weight = map(int, line.strip().split(","))
        G.add_edge(from_node-1, to_node-1, weight=weight)



routes = [[1, 2, 3, 4], [2, 3, 4, 5]]
MG = nx.MultiGraph(G)
nx.draw(G, pos=node_positions, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_color="black")
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos=node_positions, edge_labels=labels)
colors = ['red', 'green', 'blue', 'yellow', 'gray', 'pink', 'purple', 'orange']
offset = 0.0

Mandl_transit_network = TransitNetwork(15, "../data/mandl1_links.txt", "../data/mandl1_demand.txt")
routes = Mandl_transit_network.find_initial_route_sets(8)
for i, route in enumerate(routes):
    for j in range(len(route) - 1):
        u, v = route[j], route[j + 1]
        nx.draw_networkx_edges(
            MG,
            node_positions,
            edgelist=[(u, v)],
            edge_color=colors[i],
            width=2,
            alpha=0.5,
            connectionstyle=f"arc3,rad={offset}",
        )
        # Incrementarea offsetului pentru fiecare muchie
        offset += 0.05

plt.show()
