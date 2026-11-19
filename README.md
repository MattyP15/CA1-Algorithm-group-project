# CA1-Algorithm-group-project
## Repo for ECM3428 – Algorithms That Changed The World Coursework, CA1: Algorithm Group Project. 

## Brief Description

### This project is a demonstration of the A* Algorithm, intended for an audience of end users situated in Exeter, trying to find an optimal walking/running route between two points in the Exeter metro area, without access to an internet connection.   

## Installation Instructions

setup from root:
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

to run:
       from root:
                 python main.py

## Saved routes (bookmarks)
OS Location 

| Windows | `%APPDATA%\ExeterRoutePlanner\bookmarks.json`<br>(usually `C:\Users\<username>\AppData\Roaming\ExeterRoutePlanner\`) |
| macOS | `~/Library/Application Support/ExeterRoutePlanner/bookmarks.json` |
| Linux | `$XDG_DATA_HOME/ExeterRoutePlanner/bookmarks.json`<br>(usually `~/.local/share/ExeterRoutePlanner/`) |

The folder is created the first time you save a bookmark.
To clear all bookmarks, delete `bookmarks.json`. If the file is damaged,
the app starts with an empty list instead of crashing.

Or, simply run the provided executable.

## Testing Instructions

## Algorithm Explanation

The main algorithm used in this program is the <b> A* Algorithm </b>. 
This algorithm calculates the optimal route between two nodes in a reasonable amount of time.
It does this by considering a heuristic when traversing the graph it operates on, to guide its efforts on the most effective prospects.

In this instance, we used a Haversine Distance heuristic, which is essentially a straight line / euclidian distance (therefore, admissable) heuristic between two longitude/latitude coordinates, with the added step of accounting for the earth's curvature using a great circle calculation.

After calculating this distance between two nodes, we are then able to use this to guide our A* algorithm.
We first initialise a priority queue of nodes, the starting node, and take each node's accumulated cost on the graph to be infinite, apart from the starting node - which has 0 cost.
We then loop through a process of:
1. If the queue is empty, return False and break
2. Remove the cheapest costing node (the easiest to reach) from the queue. This will be such that it has the cheapest heuristic cost
3. Mark this node as explored
4. If this node is the goal, then we return True and break.
5. Else, for all unexplored neighbours of the explored node, we:
    1. Take its accumulated cost to be the cost between the start node and current node, added with its current accumulated cost. 
    2. If this new accumulated cost is greater than the accumulated cost of the current node plus the cost of reaching the current node from the start node, set the accumulated cost of the neighbouring node to be equal to that of the current node plus the cost of the neighbouring node.
    3. Then, insert or update the neighbouring node's accumulated cost in priority queue with its new accumulated cost plus its heuristic cost.




## Test Cases and Summary of Results


## Limitations, Dependancies and Third Party Resources

### Packages, as shown in requirements.txt:

osmnx>=2.0
matplotlib
pywebview>=5.0
pyinstaller
pytest
cloudpickle-3.1.2 
joblib-1.6.0 
narwhals-2.28.0 
scikit-learn-1.9.1 
scipy-1.18.1 
threadpoolctl-3.8.0


### Limitations,

Data for this project was collected from OpenStreetMaps.org and may have some limited inaccuracies such as disconnected edges and nodes on the graph. However, this will not affect the quality of the demonstration of the algorithm in any way.

## Each member's contributions

Henry Riehl:
- Welcome Page.
- A* Algorithm implementation.
- Connection of disjointed graphs and pruning of small node pairs.

## Required acknowledgement of generative AI use


### vvv DELETE WHEN DONE vvv
• A README containing:
– the project title, selected algorithm, problem and intended users;
– installation, access and testing instructions;
– a concise explanation or pseudocode of the algorithm and its time and space complexity;
– the test cases used and a summary of the results;
– known limitations, dependencies and third-party resources;
– a statement of each member’s contributions; and
– the required acknowledgement of generative AI use.