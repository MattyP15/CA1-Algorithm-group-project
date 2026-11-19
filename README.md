# Exeter Route Planner: A* Pathfinding Demo

**ECM3428 - Algorithms That Changed The World, CA1: Algorithm Group Project**

## Brief Description

This project is a demonstration of the A* Algorithm, intended for an audience of end users situated in Exeter, trying to find an optimal walking/running route between two points in the Exeter metro area, without access to an internet connection.   

| | |
|---|---|
| **Algorithm** | A\* search with a haversine (great-circle distance) heuristic |
| **Problem** | Finding the shortest route between two points on a real street and footpath network |
| **Intended users** | People in Exeter planning a walk or run, including without an internet connection |
| **Map size** | 16,676 junctions (nodes) and 40,720 path segments (edges) |

---

## Contents

1. [Installation and Running](#installation-and-running)
2. [Using the app](#using-the-app)
3. [Running the tests](#running-the-tests)
4. [How the algorithm works](#how-the-algorithm-works)
5. [Test cases and summary of results](#test-cases-and-summary-of-results)
6. [Limitations, dependencies and third-party resources](#limitations-dependencies-and-third-party-resources)
7. [Saved routes (bookmarks)](#saved-routes-bookmarks)
8. [Each member's contributions](#each-members-contributions)
9. [Acknowledgement of generative AI use](#acknowledgement-of-generative-ai-use)

---

## Installation and Running

Requires Python 3.13. Run these commands from the project's root folder.

**Windows**

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

A window called **Exeter Route Planner** opens. Choose a start and end point on the map (or pick a landmark), and the app will animate the A\* search and draws the route.

---

## Using the app

1. **Get started.** Click "Get Started" on the welcome page.
2. **Choose a route.** Click the map once to set the start and again to set the end. Landmarks such as Exeter Cathedral, St Davids Station and Streatham Campus are labelled on the map to help.
3. **Run the search.** Click "Start Run". The map animates A\* as it works (Colour legend is located in the top right):

    | Colour on the map | Meaning |
    |---|---|
    | Explored | Junctions A\* has fully examined |
    | Frontier | Junctions found but not yet examined |
    | Exploring now | The junction being examined at this moment |
    | Route | The shortest route, drawn once the goal is reached |

4. **Control the playback.** Use the "Speed" slider, or "Pause", "Step" (one junction at a time), and "Finish" (jump to the results). The progress bar shows how many junctions have been explored.
5. **Watch the numbers.** While stepping, the sidebar shows "g" (distance so far) and "f = g + h" for the junction being explored. A\* always explored the junction with the lowest "f" next.
6. **Save the route.** Type a name under "Bookmarks" and click "Save". Click a saved route at any time to load it again later. See [Saved routes](#saved-routes-bookmarks) for where these are stored.
7. **Try another route.** Click "Reset".

The app works fully offline. The map data is stored in `data/maps/`.

---

## Running the tests

First activate the virtual environment, then from the root folder:

```bash
# 1. Correctness tests (Expect 26 passed, about 20 seconds)
python -m pytest tests -v

# 2. Benchmarks: Runs every heuristic on 60 random routes (roughly 1-2 minutes)
python -m benchmarks.run_benchmarks     # Add --quick for a short version

# 3. Convert results into tables and charts
python -m benchmarks.make_report
```

| Output | Contents |
|---|---|
| `results/runs.csv`, `results/scaling.csv` | Raw results, one row per search |
| `results/tables/summary.md` | Summary table, one row per heuristic |
| `results/tables/ghf_example.md` | The g, h, and f values for the first steps of one real search |
| `results/figures/*.png` | Charts and Maps of explored-areas |

---

## How the algorithm works

The main algorithm used in this program is the <b> A* Algorithm </b>. 
This algorithm calculates the optimal route between two nodes in a reasonable amount of time.
It does this by considering a heuristic when traversing the graph it operates on, to guide its efforts on the most effective prospects.

### The heuristic: haversine distance

In this instance, we used a Haversine Distance heuristic, which is essentially a straight line / euclidian distance (therefore, admissable) heuristic between two longitude/latitude coordinates, with the added step of accounting for the earth's curvature using a great circle calculation.

It is admissible because no walking route can be shorter than the straight line between its ends - meaning it never overestimates the distance left. This guarantees our A\* algorithm always returns the shortest route.

### Pseudocode

```text
A*(graph, start, goal, h):
    g[start] <- 0               # Every other node: g = infinity
    frontier <- priority queue containing (h(start, goal), start)
    visited <- empty set

    while frontier is not empty:
        current <- remove the node with the lowest f from frontier
        if current in visited: skip it
        add current to visited

        if current = goal:
            return the path from parent, and g[goal]

        for each neighbour of current not in visited:
            new_g <- g[current] + length of shortest edge(current, neighbour)
            if new_g < g[neighbour]:
                g[neighbour] <- new_g
                parent[neighbour] <- current
                add (new_g + h(neighbour, goal), neighbour) to frontier
        
    return no path, cost infinite   # Goal cannot be reached
```

### Time and space complexity

With V nodes, E edges, and a binary-heap priority queue:

| | Complexity | Why |
|---|---|---|
| **Time (Worst Case)** | O((V + E) log V) | Each node is expanded at most once. Each edge can add one entry to the heap at O(log V) per operation |
| **Space (Worst Case)** | O(V + E) | g-scores, previous-node records, and the visited set hold up to V entries. The heap can hold up to E entries |

The worst case is the same as Dijkstra's, which is what A\* becomes when h = 0. In practice, a heuristic is good when fewer nodes are expanded. On our map, haversine A\* expanded 3.5x fewer nodes than Dijkstra on average (see below).

---

## Test cases and summary of results

### Correctness tests: 26 / 26 passed

| Group | Tests | What is checked |
|---|---|---|
| **Hand-made graphs** (`tests/test_toy_graphs.py`) | 16 | Straight line, a cheap detour beating an expensive direct edge, unreachable goal, start equals goal, one-way streets, parallel edges (the shortest is used), tied routes, statistics recorded. Each test runs with haversine and with h = 0. |
| **Matches Dijkstra** (`tests/test_real_map.py`) | 3 | On 100 random Exeter routes, the route length equals NetworkX's independent Dijkstra implementation and equals the sum of the edges actually used. Haversine never expands more nodes than h = 0. |
| **Theory Checks** (`tests/test_real_map.py`) | 7 | Haversine never overestimates (admissible) and is consistent on every edge, weighted A\* never exceeds *w* x the optimal route length (w = 1.2, 1.5, 2, 3), Manhattan distance overestimates somewhere. |

### Benchmarks: Comparing heuristics

Every heuristic was run on the same 60 random routes on the full map. Times are the median of 5 runs. Memory was measured separately with `tracemalloc`.

| Heuristic | Avg nodes expanded | Median time | Avg peak memory | Shortest route found | Avg extra length |
|---|---|---|---|---|---|
| Dijkstra (h = 0) | 7,050 | 18.7 ms | 1,276 KB | 100% | 0% |
| **Haversine (ours)** | **1,999** | **9.3 ms** | **363 KB** | **100%** | **0%** |
| Manhattan | 970 | 5.0 ms | 186 KB | 8% | 1.6% |
| Weighted x1.2 | 1,012 | 3.6 ms | 183 KB | 28% | 0.3% |
| Weighted x1.5 | 595 | 1.6 ms | 116 KB | 8% | 2.7% |
| Weighted x2 | 433 | 1.4 ms | 87 KB | 2% | 5.3% | 
| Weighted x3 | 371 | 1.3 ms | 81 KB | 3% | 9.6% |

**What the comparisons are:**
- **Dijkstra (h = 0):** no estimate at all, the baseline
- **Manhattan:** north-south plus east-west distance. It is inadmissible (It overestimates diagonal paths), included to show what happens when the heuristic break the rule.
- **Weighted:** w x haversine, which trades route quality for speed.

**Key findings:**
1. Haversine expands 3.5x fewer nodes than Dijkstra and always finds the shortest route.
2. It is only about 2x faster, not 3.5x, because each estimate costs some trigonometry.
3. Memory falls by about 3.5x because most memory is the record kept for every explored node.
4. Inadmissible heuristics lose the guarantee. Manhattan found the shortest route only 8% of the time.
5. Weighted A\* is a tunable trade-off. x1.2 halves the work for routes only 0.3% longer. Beyond x2 there is little further speed gain.

Times depend on the computer used. Node counts, memory and route lengths do not.

---

## Limitations, dependencies and third-party resources

### Limitations

- **Map data quality.** OpenStreetMap data may have some limited inaccuracies such as disconnected edges and nodes on the graph.However, this will not affect the quality of the demonstration of the algorithm. The benchmarks also only used the 14,381 nodes that can all reach each other. 
- **Distance is the only cost.** The routes found are the shortest, not the quickest or easiest. Hills, surfaces and crossings are not added but were considered as an addition if time allowed.
- **The map is fixed.** It only covers the Exeter area as downloaded. New paths would need the map file to be regenerated.
- **The app uses haversine only.** The other heuristics are compared in the benchmarks only and not in the app itself.
- **Tested by sampling.** Real-map tests use random samples of routes, not every possible pair of points.

### Dependencies

Listed with exact versions in `requirements.txt`:

| Package | Used for |
|---|---|
| `osmnx` | Loading the OpenStreetMap graph, distance calculations |
| `networkx` | Graph functions in the tests and benchmarks, including Dijkstra as an independent check |
| `pywebview` | The desktop window that hosts the map interface |
| `scikit-learn` | Used by OSMnx to find the nearest map junction to each landmark |
| `shapely` | Building the map background in `gui/export_background.py` |
| `pandas` | Collecting benchmark results and building tables |
| `matplotlib` | Charts and maps in the test report |
| `pytest` | Running the tests |
| `tabulate` | Writing results tables as Markdown |

### Third-party resources

- **Map data** © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, available under the Open Database License (ODbL).
- **[Leaflet](https://leafletjs.com/)**, the map display library, bundled in `ui/lib/` under its BSD-2-Clause licence (`ui/lib/LEAFLET-LICENSE.txt`).
- **[OSMnx](https://osmnx.readthedocs.io/)** and **[NetworkX](https://networkx.org/)** for the graph data structures; NetworkX's Dijkstra is used as an independent check in the tests.

---

## Saved routes (bookmarks)

Bookmarks are saved locally:

| OS | Location |
|---|---|
| Windows | `%APPDATA%\ExeterRoutePlanner\bookmarks.json`<br>(usually `C:\Users\<username>\AppData\Roaming\ExeterRoutePlanner\`) |
| macOS | `~/Library/Application Support/ExeterRoutePlanner/bookmarks.json` |
| Linux | `$XDG_DATA_HOME/ExeterRoutePlanner/bookmarks.json`<br>(usually `~/.local/share/ExeterRoutePlanner/`) |

The folder is created the first time you save a bookmark.
To clear all bookmarks, delete `bookmarks.json`. If the file is damaged,
the app starts with an empty list instead of crashing.

---

## Each member's contributions

| Member | Contributions |
|---|---|
| **James Mann** | Data processing for graph; Data for landmarks; Initial haversine_formula; Contributed to README documentation |
| **Henry Riehl** | Welcome page; Loading of map data in the background; A* Algorithm implementation; Manual connection of disjointed graphs and pruning of small node pairs |
| **Pyae Phyo Thaw** | Initial project repo structure; GUI and UI; Animations; Offline functionality; Map display; Licence; UX features (Speed slider, Bookmarks) |
| **Carlin Barlow** | Test suite; benchmarking of heuristics; time and memory; results tables and charts |

---

## Acknowledgement of generative AI use


---

## Licence

Released under the MIT Licence. See [`LICENSE`](LICENSE).