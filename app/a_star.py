#Take inputs from get_user_inputs
#Using selected heuristic, given at start up of program (we'll implement euclidian distance first)
#Apply a* algorithm to graph from get-geo-data.py to find shortest route from start to end

#IDEAS:
# Colour in the paths that are currently being explored by the algorithm with a colour correspondant to 
# what stage the algoritm is considering

# Make the program wait like half a second between steps in the algorithm to slow it down so visualisation works

# At the end, highlight the shortest path and maybe output the list of nodes in console.

import heapq
from haversine_formula import haversine_heuristic


class AStar:

    def __init__(self, graph, start_node, dest_node):
        self.graph = graph
        self.start_node = start_node
        self.dest_node = dest_node

        # priority queue of (f_score, node). f = g (cost so far) + heuristic
        self.open_set = [(haversine_heuristic(graph, start_node, dest_node), start_node)]

        # cost of reaching current node from start node. Is set to zero because start node = current node at startup.
        self.g_score = {start_node: 0}
        self.came_from = {}
        self.visited = set()
        self.visited_order = []

    def run(self):
        graph = self.graph
        dest = self.dest_node
        open_set = self.open_set
        g_score = self.g_score
        came_from = self.came_from
        visited = self.visited

        while open_set:

            # get node with the smallest f_score
            _, current = heapq.heappop(open_set)

            # skip already visited nodes
            if current in visited:
                continue
            visited.add(current)
            self.visited_order.append(current)

            # destination reached. Walk backwards through came_from to rebuild the path
            if current == dest:
                return self.reconstruct_path(current), g_score[current]

            for neighbour in graph.neighbors(current):
                # ignore nodes we have already visited
                if neighbour in visited:
                    continue

                # there may be multiple edges between two nodes. Use the shortest
                edge_length = float("inf")
                for edge in graph[current][neighbour].values():
                    if edge["length"] < edge_length:
                        edge_length = edge["length"]

                # distance from start to neighbour when going through current node
                new_g = g_score[current] + edge_length

                # compare new_g with the neighbour's best known g
                if new_g < g_score.get(neighbour, float("inf")):
                    g_score[neighbour] = new_g
                    came_from[neighbour] = current

                    f_score = new_g + haversine_heuristic(graph, neighbour, dest)
                    heapq.heappush(open_set, (f_score, neighbour))

        # open set is empty and destination was never reached
        return None, float("inf")

    def reconstruct_path(self, node):
        path = [node]
        while node in self.came_from:
            node = self.came_from[node]
            path.append(node)
        path.reverse()
        return path
        