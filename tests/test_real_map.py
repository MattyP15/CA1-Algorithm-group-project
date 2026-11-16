# Correctness Checks on the real Exeter Map
import networkx as nx
import pytest

from benchmarks.common import AStar, random_routes
from benchmarks.heuristics import haversine, manhattan, weighted, zero

def path_length(G, path):
    return sum(min(d["length"] for d in G[u][v].values()) for u, v in zip(path, path[1:]))

@pytest.mark.parametrize("h", [haversine, zero], ids=["haversine", "dijkstra"])
def test_matches_dijkstra(exeter, h):
    for start, goal in random_routes(exeter, 100, seed=1):
        path, cost = AStar(exeter, start, goal, h).run()
        assert cost == pytest.approx(nx.dijkstra_path_length(exeter, start, goal, weight="length"))
        assert path[0] == start and path[-1] == goal
        assert path_length(exeter, path) == pytest.approx(cost) # Check reported cost is real

def test_haversine_never_expands_more_than_dijkstra(exeter):
    for start, goal in random_routes(exeter, 30, seed=2):
        a = AStar(exeter, start, goal, haversine); a.run()
        d = AStar(exeter, start, goal, zero); d.run()
        assert len(a.visited_order) <= len(d.visited_order)

@pytest.mark.parametrize("w", [1.2, 1.5, 2.0, 3.0])
def test_weighted_within_w_times_optimal(exeter, w):
    # Weighted A* is never worse than w times the best path
    for start, goal in random_routes(exeter, 30, seed=3):
        _, cost = AStar(exeter, start, goal, weighted(w)).run()
        best = nx.dijkstra_path_length(exeter, start, goal, weight="length")
        assert cost <= w * best + 1e-6

def true_distances_to(G, goal):
    # Real shortest distance from every node to goal (Dijkstra on the reversed map)
    return nx.single_source_dijkstra_path_length(G.reverse(copy=False), goal, weight="length")

def test_haversine_is_admissible(exeter):
    # Never overestimates the real remaining distance
    for _, goal in random_routes(exeter, 5, seed=4):
        for node, real in true_distances_to(exeter, goal).items():
            assert haversine(exeter, node, goal) <= real + 1e-6

def test_haversine_is_consistent(exeter):
    for _, goal in random_routes(exeter, 3, seed=5):
        for u, v, data in exeter.edges(data=True):
            assert haversine(exeter, u, goal) <= data["length"] + haversine(exeter, v, goal) + 1e-6

def test_manhattan_overestimates_somewhere(exeter):
    # Expected: Manhattan is not admissible. There are some nodes where it overestimates
    _, goal = random_routes(exeter, 1, seed=6)[0]
    real = true_distances_to(exeter, goal)
    assert any(manhattan(exeter, n, goal) > d + 1e-6 for n, d in real.items())