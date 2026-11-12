import osmnx as ox

def haversine_heuristic(graph, current_node, dest_node):

    
    current_lat = G.nodes[current_node]["y"]
    current_lon = G.nodes[current_node]["x"]

    
    dest_lat = G.nodes[dest_node]["y"]
    dest_lon = G.nodes[dest_node]["x"]

    
    distance = ox.distance.great_circle(
        current_lat,
        current_lon,
        dest_lat,
        dest_lon
    )

    return distance