import osmnx

# Predownloaded OSM graph network of footpaths that one can walk
# Very small for now, just around exeter cathedral.
# Basic visualisation. TODO: More detailed visualisation, make sure compatable with larger graphs
exeter_cathedral_graph = osmnx.load_graphml(
    'data\maps\exeter_cathedral_proper.graphml'
)

print("Nodes:", len(exeter_cathedral_graph.nodes))
print("Edges:", len(exeter_cathedral_graph.edges))




# Plotting the network of nodes and edges downloaded using osmnx
fig, ax = osmnx.plot_graph(
    exeter_cathedral_graph,
    node_size=5,                    # Change these as appropriate for larger or smaller graphs
    edge_linewidth=0.8,             # Thinking of changing the colour of different edges to really visualise
    bgcolor="black",                # How the A* algorithm goes through these things and searches them
    show=True,
    close=False
)

ax.set_title("Exeter Cathedral")



