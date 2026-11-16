# Turns results/runs.csv and results/scaling.csv into table and charts
# python -m benchmarks.make_report
# Outputs go to results/tables/ and results/figures/

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd

from benchmarks.common import AStar, RESULTS, load_map, random_routes, reachable_core
from benchmarks.heuristics import HEURISTICS, haversine

TABLES = RESULTS / "tables"
FIGURES = RESULTS / "figures"

# One fixed colour per heuristic, used in every chart
COLOURS = {
    "Dijkstra (h=0)": "#2a78d6",  # blue
    "Haversine": "#eb6834",       # orange
    "Manhattan": "#1baf7a",       # aqua
    "Weighted x1.2": "#eda100",   # yellow
    "Weighted x1.5": "#e87ba4",   # pink
    "Weighted x2": "#6250d6",     # violet
    "Weighted x3": "#008300",     # green
}

plt.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 16,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 150
})

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGURES / f"{name}.png")
    plt.close(fig)
    print(f" figures/{name}.png")


# Tables
def summary_table(runs):
    table = runs.groupby("heuristic", sort=False).agg(
        avg_nodes_expanded=("nodes_expanded", "mean"),
        median_time_ms=("runtime_ms", "median"),
        avg_peak_open_set=("max_open_size", "mean"),
        avg_peak_memory_kb=("peak_mem_kb", "mean"),
        pct_routes_optimal=("matches_optimal", lambda s: 100 * s.mean()),
        avg_extra_cost_pct=("excess_pct", "mean"),
    ).round(1)
    table.to_csv(TABLES / "summary.csv")
    (TABLES / "summary.md").write_text(table.to_markdown())
    print(table.to_string())
    return table

def ghf_table(graph):
    # First few steps of one search, to explain f = g + h on a slide
    start, goal = random_routes(graph, 1, seed=7)[0]
    search = AStar(graph, start, goal, haversine)
    search.run()
    rows = []
    for step, node in enumerate(search.visited_order[:8], start=1):
        g = search.g_score[node]
        h = haversine(graph, node, goal)
        rows.append({
            "step": step,
            "node": str(node),
            "g (m so far)": round(g, 1),
            "h (m estimate left)": round(h, 1),
            "f = g + h": round(g + h, 1)
        })
    table = pd.DataFrame(rows)
    (TABLES / "ghf_example.md").write_text(table.to_markdown(index=False))


# Charts
def nodes_vs_distance(runs):
    fig, ax = plt.subplots(figsize=(10, 6))
    runs = runs.copy()
    runs["distance_band"] = pd.cut(runs["straight_line_m"], bins=6)
    for name in ["Dijkstra (h=0)", "Haversine", "Manhattan", "Weighted x2"]:
        part = runs[runs["heuristic"] == name]
        by_band = part.groupby("distance_band", observed=True).agg(x=("straight_line_m", "median"), y=("nodes_expanded", "median"))
        ax.plot(by_band["x"], by_band["y"], marker="o", lw=2, color=COLOURS[name], label=name)
        ax.annotate(name, (by_band["x"].iloc[-1], by_band["y"].iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=12)
    d = runs[runs.heuristic == "Dijkstra (h=0)"].nodes_expanded.mean()
    h = runs[runs.heuristic == "Haversine"].nodes_expanded.mean()
    ax.set_title(f"Haversine expands {d / h:.1f}x fewer nodes than Dijkstra")
    ax.set_xlabel("Straight-line distance from start to goal (m)")
    ax.set_ylabel("Nodes expanded (median)")
    ax.legend(frameon=False)
    save(fig, "nodes_vs_distance")

def runtime_boxplot(runs):
    fig, ax = plt.subplots(figsize=(11, 6))
    names = list(HEURISTICS)
    data = [runs[runs.heuristic == n]["runtime_ms"] for n in names]
    box = ax.boxplot(data, patch_artist=True, showfliers=False, medianprops={"color": "black", "linewidth": 2})
    for patch, n in zip(box["boxes"], names):
        patch.set_facecolor(COLOURS[n])
        patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(names) + 1), [n.replace(" ", "\n", 1) for n in names], fontsize=11)
    ax.set_ylabel("Run time per route (ms)")
    ax.set_title("Run time per heuristic (60 routes, full Exeter map)")
    save(fig, "runtime_boxplot")

def weighted_tradeoff(runs):
    weighted = runs[runs["weight"] >= 1].groupby("weight").agg(nodes=("nodes_expanded", "mean"), extra=("excess_pct", "mean"))
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    left.plot(weighted.index, weighted["nodes"], marker="o", lw=2, color="#2a78d6")
    left.set_title("Higher w: fewer nodes expanded")
    left.set_xlabel("Weight w (h = w x haversine)")
    left.set_ylabel("Nodes expanded (mean)")
    right.plot(weighted.index, weighted["extra"], marker="o", lw=2, color="#eb6834")
    right.set_title("Higher w: more extra cost")
    right.set_xlabel("Weight w (h = w x haversine)")
    right.set_ylabel("Extra distance vs best route (%)")
    save(fig, "weighted_tradeoff")

def scaling(scale):
    fig, ax = plt.subplots(figsize=(10, 6))
    for name in scale["heuristic"].unique():
        part = scale[scale.heuristic == name].groupby("map_nodes")["runtime_ms"].median()
        ax.plot(part.index, part.values, marker="o", lw=2, color=COLOURS[name], label=name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Nodes in map (log scale)")
    ax.set_ylabel("Median run time (ms, log scale)")
    ax.set_title("Run time grows with map size")
    ax.legend(frameon=False)
    save(fig, "scaling")

def explored_maps(graph):
    # Same route, three heuristics. Check to see which nodes each one looked at
    start, goal = random_routes(graph, 40, seed=8)[0]
    names = ["Dijkstra (h=0)", "Haversine", "Weighted x2"]
    searches = {}
    for n in names:
        s = AStar(graph, start, goal, HEURISTICS[n][0])
        s.run()
        searches[n] = s

    # Zoom every panel to the area Dijkstra explored
    xs = [graph.nodes[v]["x"] for v in searches[names[0]].visited_order]
    ys = [graph.nodes[v]["y"] for v in searches[names[0]].visited_order]
    pad_x, pad_y = (max(xs) - min(xs)) * 0.05, (max(ys) - min(ys)) * 0.05

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    for ax, n in zip(axes, names):
        s = searches[n]
        ox.plot_graph(graph, ax=ax, show=False, close=False, node_size=0, edge_color="#cccccc", edge_linewidth=0.4, bgcolor="white")
        ex = s.visited_order
        ax.scatter([graph.nodes[v]["x"] for v in ex], [graph.nodes[v]["y"] for v in ex],
                   c=range(len(ex)), cmap="viridis", s=4, zorder=3)
        path = s.reconstruct_path(goal)
        ax.plot([graph.nodes[v]["x"] for v in path], [graph.nodes[v]["y"] for v in path], color="#e34948", lw=3, zorder=4)
        ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
        ax.set_title(f"{n}\n{len(ex):,} nodes expanded", fontsize=15)
    fig.suptitle("On the same route, a better heuristic searches a smaller area "
                 "(colour = order explored, red = route)", fontsize=17)
    save(fig, "explored_maps")

if __name__ == "__main__":
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    runs = pd.read_csv(RESULTS / "runs.csv")
    scale = pd.read_csv(RESULTS / "scaling.csv")
    full = reachable_core(load_map())

    summary_table(runs)
    ghf_table(full)
    nodes_vs_distance(runs)
    runtime_boxplot(runs)
    weighted_tradeoff(runs)
    scaling(scale)
    explored_maps(full)
