import importlib.util
import math
import sys
import threading
from pathlib import Path

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(ROOT / "app"))

def _load_module(relative_path):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

get_geo_data = _load_module("app/get_geo_data.py")
haversine_formula = _load_module("app/haversine_formula.py")  # for the search later
a_star = _load_module("app/a_star.py")

MAP_FILE = ROOT / "data" / "maps" / "exeter.graphml"

COORD_DECIMALS = 5


class Api:
    def __init__(self):
        self._graph = None              # the osmnx graph, loaded on first use
        self._lock = threading.Lock()   # pywebview runs each JS call in its own thread

    def _get_loaded_graph(self):
        with self._lock:
            if self._graph is None:
                
                self._graph = get_geo_data.load_data(MAP_FILE)
            return self._graph

    @staticmethod
    def _latlon(x, y):
        """osmnx stores x = longitude, y = latitude. Leaflet wants [lat, lon]."""
        return [round(y, COORD_DECIMALS), round(x, COORD_DECIMALS)]

    def get_graph(self):
        """Return the map as plain data the UI can draw.

        {
          "nodes": {"30792310": [lat, lon], ...},
          "edges": [{"u": 30792310, "v": 30792455, "length": 48.96,
                     "coords": [[lat, lon], [lat, lon], ...]}, ...],
          "bounds": [[south, west], [north, east]]
        }
        """
        graph = self._get_loaded_graph()

        nodes = {
            str(node_id): self._latlon(data["x"], data["y"])
            for node_id, data in graph.nodes(data=True)
        }

        edges = []
        seen = set()
        for u, v, data in graph.edges(data=True):
            
            pair = (min(u, v), max(u, v))
            if pair in seen:
                continue
            seen.add(pair)

            # Straight roads don't, so we just join the two end nodes.
            if "geometry" in data:
                coords = [self._latlon(x, y) for x, y in data["geometry"].coords]
            else:
                coords = [nodes[str(u)], nodes[str(v)]]

            edges.append({
                "u": u,
                "v": v,
                "length": round(float(data["length"]), 2),
                "coords": coords,
            })

        lats = [lat for lat, lon in nodes.values()]
        lons = [lon for lat, lon in nodes.values()]
        bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

        return {"nodes": nodes, "edges": edges, "bounds": bounds}

    def nearest_node(self, lat, lon):
        """Return the ID of the junction closest to a clicked point.

        A simple check of every node is fast enough for ~16,000 nodes, and it
        avoids needing scikit-learn (which osmnx.nearest_nodes requires).
        """
        graph = self._get_loaded_graph()

        # Over a city-sized area, longitude degrees are shorter than latitude
        # degrees by cos(latitude). Scaling by it makes the distance fair.
        lon_scale = math.cos(math.radians(lat))

        best_id = None
        best_dist = float("inf")
        for node_id, data in graph.nodes(data=True):
            d_lat = data["y"] - lat
            d_lon = (data["x"] - lon) * lon_scale
            dist = d_lat * d_lat + d_lon * d_lon   # no sqrt needed just to compare
            if dist < best_dist:
                best_id, best_dist = node_id, dist

        return best_id

    def find_path(self, start_node, end_node):
        graph = self._get_loaded_graph()
        search = a_star.AStar(graph, start_node, end_node)

        path, distance = search.run()
        return [self._latlon(graph.nodes[n]["x"], graph.nodes[n]["y"]) for n in path]



