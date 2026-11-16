from pathlib import Path
import osmnx


if __name__ == "__main__":
    print("This is the get-geo-data.py file, not main")

def load_data(file):

    graph_path = Path(file)
    exeter_graph = osmnx.load_graphml(graph_path)

    return exeter_graph
    



