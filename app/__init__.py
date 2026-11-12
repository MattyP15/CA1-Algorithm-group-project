from pathlib import Path

import get_geo_data
import osmnx
import networkx

graph_path = Path("data") / "maps" / "exeter_cathedral_proper.graphml"
exe_cathedral_graph = get_geo_data.load_data(graph_path)


print("Nodes:", len(exe_cathedral_graph.nodes))
print("Edges:", len(exe_cathedral_graph.edges))

print(
    "Weakly connected:",
    networkx.is_weakly_connected(exe_cathedral_graph)
)

G = exe_cathedral_graph

# 1. Check graph type
print(type(G))

# 2. Check node coordinates
node, data = next(iter(G.nodes(data=True)))

print("Node:", node)
print("Longitude:", data["x"])
print("Latitude:", data["y"])

# 3. Check edge distances
u, v, key, data = next(
    iter(G.edges(keys=True, data=True))
)

print("Edge length:", data["length"])

# 4. Check directed connectivity
print("Strongly connected:",
      networkx.is_strongly_connected(G))



    # Plotting the network of nodes and edges downloaded using osmnx
fig, ax = osmnx.plot_graph(
    exe_cathedral_graph,
    node_size=5,                    # Change these as appropriate for larger or smaller graphs
    edge_linewidth=0.8,             # Thinking of changing the colour of different edges to really visualise
    bgcolor="black",                # How the A* algorithm goes through these things and searches them
    show=True,
    close=False
)



