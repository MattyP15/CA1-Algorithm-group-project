import sys
from pathlib import Path

import networkx as nx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.common import load_map, reachable_core

@pytest.fixture(scope="session")
def exeter():
    # The full map, loaded once and shared by every test
    return reachable_core(load_map())

@pytest.fixture
def make_graph():
    # Builds small test graph
    def build(coords, edges, two_way=True):
        G = nx.MultiDiGraph()
        for node, (lat, lon) in coords.items():
            G.add_node(node, y=lat, x=lon)
        for u, v, length in edges:
            G.add_edge(u, v, length=length)
            if two_way:
                G.add_edge(v, u, length=length)
        return G
    return build