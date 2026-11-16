# Heuristics to compare. All take (graph, node, goal) and return metres.
import osmnx as ox

from benchmarks.common import AStar
from haversine_formula import haversine_heuristic as haversine

def zero(graph, node, goal): return 0.0

def manhattan(graph, node, goal):
    # North-South distance + East-West distance
    a, b = graph.nodes[node], graph.nodes[goal]
    north_south = ox.distance.great_circle(a["y"], a["x"], b["y"], a["x"])
    east_west = ox.distance.great_circle(b["y"], a["x"], b["y"], b["x"])
    return north_south + east_west

def weighted(w):
    # Makes a heuristic that is w times haversine.
    def h (graph, node, goal): return w * haversine(graph, node, goal)
    return h

# Name -> (Heuristic function, Weight). Order is the same as chart colour order
HEURISTICS = {
    "Dijkstra (h=0)": (zero, 0.0),
    "Haversine": (haversine, 1.0),
    "Manhattan": (manhattan, None),
    "Weighted x1.2": (weighted(1.2), 1.2),
    "Weighted x1.5": (weighted(1.5), 1.5),
    "Weighted x2": (weighted(2.0), 2.0),
    "Weighted x3": (weighted(3.0), 3.0),
}