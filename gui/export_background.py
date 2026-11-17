"""Download a simple map background (parks, water, rivers, buildings) once.

Run from the project root, with internet access:

    python -m gui.export_background
    python -m gui.export_background --no-buildings     # smaller file, no buildings

Saves data/maps/exeter_background.geojson.
The data comes from OpenStreetMap (© OpenStreetMap contributors, ODbL).
"""
import argparse
import json
import osmnx
from pathlib import Path
from shapely.geometry import mapping

ROOT= Path(__file__).resolve().parent.parent
GRAPH_FILE = ROOT / "data" / "maps" / "exeter.graphml"
OUT_FILE = ROOT / "data" / "maps" / "exeter_background.geojson"

TAGS= {
    "green": {
        "leisure": ["park", "garden", "pitch", "golf_course", "nature_reserve",
                    "recreation_ground", "playground", "common"],
        "landuse": ["grass", "forest", "meadow", "recreation_ground", "cemetery",
                    "allotments", "village_green", "orchard"],
        "natural": ["wood", "scrub", "grassland", "heath"],
    },
    "water": {"natural": ["water"], "landuse": ["reservoir", "basin"]},
    "river": {"waterway": ["river", "canal", "stream"]},
    "building": {"building": True},
}

SHAPES={
    "green": {"Polygon", "MultiPolygon"},
    "water": {"Polygon", "MultiPolygon"},
    "river": {"LineString", "MultiLineString"},
    "building": {"Polygon", "MultiPolygon"},
}

TOLERANCE={"green": 0.00004, "water": 0.00003, "river": 0.00003, "building": 0.00002}

def round_coords(value, decimals=5):
    if isinstance(value, (list, tuple)):
        return [round_coords(v, decimals) for v in value]
    return round(value, decimals)

def to_features(gdf, kind):
    features =[]
    for geometry in gdf.geometry:
        if geometry is None or geometry.is_empty or geometry.geom_type not in SHAPES[kind]:
            continue
        simple =geometry.simplify(TOLERANCE[kind], preserve_topology=True)
        if simple.is_empty:
            continue
        shape =mapping(simple)
        features.append({
            "type": "Feature",
            "properties": {"kind": kind},
            "geometry": {"type": shape["type"], "coordinates": round_coords(shape["coordinates"])},
        })
    return features

def main():
    parser= argparse.ArgumentParser(description="Download a simple map background once.")
    parser.add_argument("--no-buildings", action="store_true", help="leave buildings out")
    args =parser.parse_args()

    graph =osmnx.load_graphml(GRAPH_FILE)
    xs =[d["x"] for _, d in graph.nodes(data=True)]
    ys =[d["y"] for _, d in graph.nodes(data=True)]
    bbox =(min(xs), min(ys), max(xs), max(ys))     # (west, south, east, north)
    print(f"Area: {bbox}")

    kinds =["green", "water", "river"] + ([] if args.no_buildings else ["building"])
    features =[]
    for kind in kinds:
        print(f"Downloading {kind}…", end=" ", flush=True)
        try:
            gdf =osmnx.features_from_bbox(bbox, TAGS[kind])
        except osmnx._errors.InsufficientResponseError:
            print("none found")
            continue
        found =to_features(gdf, kind)
        features.extend(found)
        print(f"{len(found):,} shapes")

    OUT_FILE.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")),
        encoding="utf-8",
    )
    size_mb =OUT_FILE.stat().st_size / 1_000_000
    print(f"Saved {len(features):,} shapes to {OUT_FILE} ({size_mb:.1f} MB)")
    if size_mb > 15:
        print("That's large. If the app feels slow, run again with --no-buildings.")


if __name__ == "__main__":
    main()
