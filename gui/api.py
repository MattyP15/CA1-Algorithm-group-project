import importlib.util
import json
import os
import math
import sys
import threading
import time
import webview

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
landmarks = _load_module("app/landmarks.py")

MAP_FILE = ROOT / "data" / "maps" / "exeter.graphml"

COORD_DECIMALS = 5

ROAD_CLASSES = {
    "major": {"motorway", "motorway_link", "trunk", "trunk_link",
              "primary", "primary_link", "secondary", "secondary_link"},
    "medium": {"tertiary", "tertiary_link", "unclassified",
               "residential", "living_street"},
    "path": {"footway", "path", "steps", "pedestrian", "cycleway",
             "bridleway", "corridor"},

}
CLASS_RANK = {"major": 3, "medium": 2, "minor": 1, "path": 0}

def _bookmarks_file():
    """Bookmarks are stored in the OS-specific app data folder, not in the project files."""
    if sys.platform == "win32":          # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":       # macOS
        base = Path.home() / "Library" / "Application Support"
    else:                                # Linux and others
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    folder = base / "ExeterRoutePlanner"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "bookmarks.json"

class Api:
    def __init__(self):
        self._graph = None              # the osmnx graph, loaded on first use
        self._lock = threading.Lock()   # pywebview runs each JS call in its own thread
        self._bookmark_lock = threading.Lock()   # stops two saves overwriting each other
        self._landmarks_dict = None

    def quit(self):
        webview.windows[0].destroy()

    def _get_loaded_graph(self):
        with self._lock:
            if self._graph is None:
                
                self._graph = get_geo_data.load_data(MAP_FILE)
            return self._graph

    @staticmethod
    def _latlon(x, y):
        """osmnx stores x = longitude, y = latitude. Leaflet wants [lat, lon]."""
        return [round(y, COORD_DECIMALS), round(x, COORD_DECIMALS)]

    def _road_class(highway):
        types = highway if isinstance(highway, list) else [highway]
        best = "path"
        for road_type in types:
            road_class = "minor"                 
            for name, members in ROAD_CLASSES.items():
                if road_type in members:
                    road_class = name
            if CLASS_RANK[road_class] > CLASS_RANK[best]:
                best = road_class
        return best  

    def get_graph(self):
        
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

            
            if "geometry" in data:
                coords = [self._latlon(x, y) for x, y in data["geometry"].coords]
            else:
                coords = [nodes[str(u)], nodes[str(v)]]

            edges.append({
                "u": u,
                "v": v,
                "length": round(float(data["length"]), 2),
                "kind": self._road_class(data.get("highway", "")),
                "coords": coords,
            })

        lats = [lat for lat, lon in nodes.values()]
        lons = [lon for lat, lon in nodes.values()]
        bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

        return {"nodes": nodes, "edges": edges, "bounds": bounds}

    def nearest_node(self, lat, lon):
        
        graph = self._get_loaded_graph()


        
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

    def run_search(self, start_node, end_node):
        graph = self._get_loaded_graph()
        start_node, end_node = int(start_node), int(end_node)
        heuristic = haversine_formula.haversine_heuristic   

        search = a_star.AStar(graph, start_node, end_node)
        started = time.perf_counter()
        path, cost = search.run()
        time_ms = (time.perf_counter() - started) * 1000

        explored_at = {node: i for i, node in enumerate(search.visited_order)}

        steps = []
        for i, node in enumerate(search.visited_order):
            g = float(search.g_score[node])
            h = float(heuristic(graph, node, end_node))

            discovered = [
                n for n in graph.neighbors(node)
                if n in search.g_score and explored_at.get(n, math.inf) > i
            ]

            steps.append({
                "node": node,
                "parent": search.came_from.get(node),   # None for the start junction
                "g": round(g, 1),
                "h": round(h, 1),
                "f": round(g + h, 1),
                "discovered": discovered,
            })

            found = path is not None
        return {
            "found": found,
            "path": path if found else [],
            "cost": round(float(cost), 1) if found else None,
            "nodes_expanded": len(search.visited_order),
            "time_ms": round(time_ms, 2),
            "steps": steps,
        }

# Bookmarking feature 
    

    def _read_bookmarks(self):
        path = _bookmarks_file()
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []          # a damaged file shouldn't crash the app

    def _write_bookmarks(self, bookmarks):
        _bookmarks_file().write_text(json.dumps(bookmarks, indent=2), encoding="utf-8")

    def list_bookmarks(self):
        """Return all saved routes, newest first."""
        with self._bookmark_lock:
            return self._read_bookmarks()

    def save_bookmark(self, name, start_node, end_node, map_name="", stats=None):
        """Save a route and return the updated list (newest first)."""
        stats = stats or {}
        with self._bookmark_lock:
            bookmarks = self._read_bookmarks()
            bookmarks.insert(0, {
                "id": str(time.time_ns()),
                "name": str(name).strip()[:60] or "Untitled route",
                "start": int(start_node),
                "end": int(end_node),
                "map": str(map_name),
                "cost": stats.get("cost"),
                "nodes_expanded": stats.get("nodes_expanded"),
                "saved_at": time.strftime("%d %b %Y, %H:%M"),
            })
            self._write_bookmarks(bookmarks)
            return bookmarks

    def delete_bookmark(self, bookmark_id):
        """Delete one bookmark and return the updated list."""
        with self._bookmark_lock:
            bookmarks = [b for b in self._read_bookmarks() if b["id"] != bookmark_id]
            self._write_bookmarks(bookmarks)
            return bookmarks

    def get_landmarks(self):
        with self._lock:
            if self._graph is None:
                self._graph = get_geo_data.load_data(MAP_FILE)

            if self._landmarks_dict is None:
                node_names = landmarks.landmarks(self._graph)
                
                self._landmarks_dict = { str(node_id): name for node_id, name in node_names.items() }

            return(self._landmarks_dict)