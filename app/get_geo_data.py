from pathlib import Path
import osmnx


if __name__ == "__main__":
    print("This is the get-geo-data.py file, not main")

MANUAL_CONNECTIONS = [
    (205498489, 25375594, "primary"),
]

def connect(graph, u, v, road_type, two_way=True):
    length = osmnx.distance.great_circle(
        graph.nodes[u]["y"], graph.nodes[u]["x"],
        graph.nodes[v]["y"], graph.nodes[v]["x"],
    )
    graph.add_edge(u, v, length=length, highway=road_type)
    if two_way:
        graph.add_edge(v, u, length=length, highway=road_type)

def load_data(file):
    graph_path = Path(file)
    exeter_graph = osmnx.load_graphml(graph_path)

    for u, v, road_type in MANUAL_CONNECTIONS:
        connect(exeter_graph, u, v, road_type)

    exeter_graph = osmnx.truncate.largest_component(exeter_graph, strongly=False)

    return exeter_graph
    



