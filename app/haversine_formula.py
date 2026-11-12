import osmnx

def haversine_heuristic(graph, current_node, dest_node):

    
    current_lat = graph.nodes[current_node]["y"]
    current_lon = graph.nodes[current_node]["x"]

    
    dest_lat = graph.nodes[dest_node]["y"]
    dest_lon = graph.nodes[dest_node]["x"]

    
    distance = osmnx.distance.great_circle(
        current_lat,
        current_lon,
        dest_lat,
        dest_lon
    )

    return distance