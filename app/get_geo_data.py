import osmnx


if __name__ == "__main__":
    print("This is the get-geo-data.py file, not main")

def load_data(file):


    # Predownloaded OSM graph network of footpaths that one can walk
    # Very small for now, just around exeter cathedral.
    # Basic visualisation. TODO: More detailed visualisation, make sure compatable with larger graphs
    exeter_cathedral_graph = osmnx.load_graphml(
        'data\maps\exeter_cathedral_proper.graphml'
    )

    return exeter_cathedral_graph
    



