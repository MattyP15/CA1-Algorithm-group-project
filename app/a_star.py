### IMPLEMENTATION OF THE A* ALGORITHM ###

import heapq
from haversine_formula import haversine_heuristic

class AStar:
    def __init__(self, graph, start_node, dest_node, heuristic=haversine_heuristic):
        # Contains all map data.
        self.graph = graph
        # Heuristic used to find g and h. Haverstine is used when dealing with long/lat coordinates.
        self.heuristic = heuristic
        # Initial node.
        self.start_node = start_node
        # Destination node.
        self.dest_node = dest_node

        # Priority queue of (f_score, node). f = g (cost so far) + heuristic
        self.frontier = [(self.heuristic(graph, start_node, dest_node), start_node)]

        # Cost of reaching current node from start node. Is set to zero because start node = current node at startup.
        self.g_score = {start_node: 0}
        # Maps each node to the one it came from.
        self.parent = {}
        # Set of nodes already visited by the algorithm.
        self.visited_nodes = set()

        # Track visited nodes in order for API and spread UI.
        # Not part of algorithm.
        self.visited_order = []
        # Track size of the frontier for testing and Benchmarking.
        # Not part of the algorithm.
        self.max_open_size = 1


    def run(self):
        graph = self.graph
        dest = self.dest_node
        frontier = self.frontier
        g_score = self.g_score
        parent = self.parent
        visited_nodes = self.visited_nodes

        # Keep looping until there are no more nodes to explore.
        while frontier:
            # Get node with the smallest f_score from 
            _, current = heapq.heappop(frontier)

            # Skip already visited nodes.
            if current in visited_nodes:
                continue
            visited_nodes.add(current)
            self.visited_order.append(current)

            # If destination reached, construct the final path.
            if current == dest:
                return self.reconstruct_path(current), g_score[current]

            # Explore neighbour nodes from current node. 
            for neighbour in graph.neighbors(current):
                # Ignore nodes we have already visited.
                if neighbour in visited_nodes:
                    continue

                # There may be multiple edges between two nodes. Use the shortest.
                edge_length = float("inf")
                for edge in graph[current][neighbour].values():
                    if edge["length"] < edge_length:
                        edge_length = edge["length"]

                # Distance from start to neighbour when going through current node.
                new_g = g_score[current] + edge_length

                # Keep current route only if it has a lower cost than the neighbour node.
                if new_g < g_score.get(neighbour, float("inf")):
                    g_score[neighbour] = new_g
                    parent[neighbour] = current

                    # Push neighbour node with new f_score onto frontier. Becomes new current node.
                    f_score = new_g + self.heuristic(graph, neighbour, dest)
                    heapq.heappush(frontier, (f_score, neighbour))
                    self.max_open_size = max(self.max_open_size, len(frontier))

        # No paths exists between start and dest node.
        return None, float("inf")

    # Reconstruct final path.
    def reconstruct_path(self, node):
        path = [node]
        while node in self.parent:
            node = self.parent[node]
            path.append(node)
        path.reverse()
        return path
        