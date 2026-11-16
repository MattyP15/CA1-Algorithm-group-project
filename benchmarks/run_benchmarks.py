# Runs the experiments and saves raw results as CSV files in results/
# python -m benchmarks.run_benchmarks (Full run: A few minutes)
# python -m benchmarks.run_benchmarks --quick (A small run to check it works)

import argparse
import statistics
import time
import tracemalloc

import networkx as nx
import pandas as pd

from benchmarks.common import AStar, RESULTS, cut_down_map, load_map, random_routes, reachable_core, straight_line
from benchmarks.heuristics import HEURISTICS

# Run one search several times. Returns the last search object, median time in ms, and peak memory in KB
def measure(graph, start, goal, heuristic, repeats):
    times = []
    for _ in range(repeats):
        search = AStar(graph, start, goal, heuristic)
        t0 = time.perf_counter()
        search.run()
        times.append((time.perf_counter() - t0) * 1000)

    # Memory is measured in a seperate run because tracemalloc slows code down
    tracemalloc.start()
    AStar(graph, start, goal, heuristic).run()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return search, statistics.median(times), peak / 1024

def run_experiment(graph, routes, heuristics, repeats, map_name):
    rows= []
    for route_id, (start, goal) in enumerate(routes):
        optimal = nx.dijkstra_path_length(graph, start, goal, weight="length")
        for name, (heuristic, weight) in heuristics.items():
            search, time_ms, mem_kb = measure(graph, start, goal, heuristic, repeats)
            path, cost = search.reconstruct_path(goal), search.g_score[goal]
            rows.append({
                "map": map_name,
                "map_nodes": len(graph),
                "route_id": route_id,
                "start": start,
                "goal": goal,
                "straight_line_m": straight_line(graph, start, goal),
                "heuristic": name,
                "weight": weight,
                "cost_m": cost,
                "optimal_m": optimal,
                "excess_pct": 100 * (cost - optimal) / optimal,
                "matches_optimal": abs(cost - optimal) < 1e-6,
                "path_nodes": len(path),
                "nodes_expanded": len(search.visited_order),
                "max_open_size": search.max_open_size,
                "runtime_ms": time_ms,
                "peak_mem_kb": mem_kb,
            })
        print(f" {map_name}: route {route_id + 1}/{len(routes)} done")
    return rows

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    routes_main, routes_scaling, repeats = (5, 3, 1) if args.quick else (60, 20, 5)
    RESULTS.mkdir(exist_ok=True)
    full = reachable_core(load_map())

    # Experiment 1: Every heuristic on the full Exeter map
    rows = run_experiment(full, random_routes(full, routes_main), HEURISTICS, repeats, "Exeter (Full)")
    pd.DataFrame(rows).to_csv(RESULTS / "runs.csv", index=False)

    # Experiment 2: How it scales with map size
    scaling_heuristics = {k: HEURISTICS[k] for k in ["Dijkstra (h=0)", "Haversine", "Weighted x2"]}
    rows = []
    for radius in [250, 500, 1000, 2000, 3000, 5000]:
        small = cut_down_map(full, radius)
        rows += run_experiment(small, random_routes(small, routes_scaling, seed=radius), scaling_heuristics, repeats, f"{radius} m")
    pd.DataFrame(rows).to_csv(RESULTS / "scaling.csv", index=False)
    print("Saved results/runs.csv and results/scaling.csv")