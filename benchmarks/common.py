# Shared helpers for tests and benchmarks

import random
import sys
from pathlib import Path

import networkx as nx
import osmnx as ox

# Project root folder
ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "app"))
from a_star import AStar

MAP_FILE = ROOT / "data" / "maps" / "exeter.graphml"
RESULTS = ROOT / "results"
CATHEDRAL = (50.7226, -3.5299) # (Lat, Lon)

def load_map(path=MAP_FILE):
    return ox.load_graphml(path)

def reachable_core(graph):
    # Keep only the biggest group of nodes that can all reach each other
    biggest = max(nx.strongly_connected_components(graph), key=len)
    return graph.subgraph(biggest).copy()

def straight_line(graph, a, b):
    na, nb = graph.nodes[a], graph.nodes[b]
    return ox.distance.great_circle(na["y"], na["x"], nb["y"], nb["x"])

def random_routes(graph, count, seed=42):
    # Seeded for consistent testing
    rng = random.Random(seed)
    nodes = sorted(graph.nodes)
    return [tuple(rng.sample(nodes, 2)) for _ in range(count)]

def nearest_node(graph, lat, lon):
    return min(graph.nodes, key=lambda n: (graph.nodes[n]["y"] - lat)**2 + (graph.nodes[n]["x"] - lon)**2)

def cut_down_map(graph, radius_m):
    # Everything within radius_m metres of the cathedral
    centre = nearest_node(graph, *CATHEDRAL)
    small = ox.truncate.truncate_graph_dist(graph, centre, radius_m)
    return reachable_core(small)