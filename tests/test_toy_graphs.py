# Small hand-made graphs where we know the right answer
import math
import pytest

from benchmarks.common import AStar
from benchmarks.heuristics import haversine, zero

LINE = {
    "A": (50.000, -3.5), 
    "B": (50.001, -3.5), 
    "C": (50.002, -3.5)
}

# Every test runs twice. Once with haversine, once with h=0

@pytest.fixture(params=[haversine, zero], ids=["haversine", "dijkstra"])
def h(request):
    return request.param

def test_straight_line(make_graph, h):
    G = make_graph(LINE, [("A", "B", 112), ("B", "C", 112)])
    path, cost = AStar(G, "A", "C", h).run()
    assert path == ["A", "B", "C"]
    assert cost == pytest.approx(224)

def test_takes_cheap_detour_not_expensive_direct_edge(make_graph, h):
    coords = {"A": (50.000, -3.5), "D": (50.001, -3.499), "C": (50.002, -3.5)}
    G = make_graph(coords, [("A", "C", 1000), ("A", "D", 160), ("D", "C", 160)])
    path, cost = AStar(G, "A", "C", h).run()
    assert path == ["A", "D", "C"]
    assert cost == pytest.approx(320)

def test_unreachable_goal(make_graph, h):
    coords = dict(LINE, Z=(50.010, -3.5))
    G = make_graph(coords, [("A", "B", 112), ("B", "C", 112)])
    path, cost = AStar(G, "A", "Z", h).run()
    assert path is None
    assert math.isinf(cost)

def test_start_is_goal(make_graph, h):
    G = make_graph(LINE, [("A", "B", 112)])
    path, cost = AStar(G, "A", "A", h).run()
    assert path == ["A"]
    assert cost == 0

def test_one_way_street(make_graph, h):
    # A -> B and B -> C are one-way. Going B to A means going via C
    G = make_graph(LINE, [("A", "B", 112), ("B", "C", 112), ("C", "A", 300)], two_way=False)
    path, _ = AStar(G, "B", "A", h).run()
    assert path == ["B", "C", "A"]

def test_parallel_edges_uses_shortest(make_graph, h):
    G = make_graph(LINE, [("A", "B", 500), ("A", "B", 112), ("B", "C", 112)])
    _, cost = AStar(G, "A", "C", h).run()
    assert cost == pytest.approx(224)

def test_two_equal_routes(make_graph, h):
    coords = {"A": (50.000, -3.5), "U": (50.001, -3.499), "L": (50.001, -3.501), "C": (50.002, -3.5)}
    G = make_graph(coords, [("A", "U", 150), ("U", "C", 150), ("A", "L", 150), ("L", "C", 150)])
    path, cost = AStar(G, "A", "C", h).run()
    assert cost == pytest.approx(300)
    assert path in (["A", "U", "C"], ["A", "L", "C"])

def test_stats_are_recorded(make_graph, h):
    G = make_graph(LINE, [("A", "B", 112), ("B", "C", 112)])
    search = AStar(G, "A", "C", h)
    search.run()
    assert search.visited_order[0] == "A"
    assert search.visited_order[-1] == "C"
    assert search.max_open_size >= 1