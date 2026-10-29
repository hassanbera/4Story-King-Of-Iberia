"""Reusable directed A* graph; edges must be supplied from evidence.

Never joins nearby points automatically. No dependency on monster IDs, BYTE
waypoint limits, the number of residents, or a particular region.
"""
import heapq
import itertools
import math


class Graph:
    def __init__(self):
        self.positions = {}
        self.edges = {}

    def add_node(self, ident, position):
        position = tuple(position)
        if len(position) != 3 or not all(math.isfinite(v) for v in position):
            raise ValueError('Invalid navigation position')
        if ident in self.positions and self.positions[ident] != position:
            raise ValueError('Conflicting navigation ID')
        self.positions[ident] = position
        self.edges.setdefault(ident, set())

    def add_edge(self, start, end, *, bidirectional=False):
        if start not in self.positions or end not in self.positions or start == end:
            raise ValueError('Invalid navigation edge')
        self.edges[start].add(end)
        if bidirectional:
            self.edges[end].add(start)

    def nearest(self, position, *, max_horizontal=6, max_vertical=2):
        candidates = []
        for ident, p in self.positions.items():
            horizontal = math.hypot(position[0] - p[0], position[2] - p[2])
            if horizontal <= max_horizontal and abs(position[1] - p[1]) <= max_vertical:
                candidates.append((math.dist(position, p), ident))
        if not candidates:
            return None
        return min(candidates, key=lambda item: item[0])[1]

    def route(self, start, end):
        if start not in self.positions or end not in self.positions:
            raise ValueError('Unknown route endpoint')
        order = itertools.count()
        queue = [(0, next(order), start)]
        cost = {start: 0.0}
        previous = {}
        closed = set()
        while queue:
            _, _, current = heapq.heappop(queue)
            if current in closed:
                continue
            if current == end:
                route = [end]
                while route[-1] != start:
                    route.append(previous[route[-1]])
                return list(reversed(route))
            closed.add(current)
            for neighbor in sorted(self.edges[current], key=str):
                candidate = cost[current] + math.dist(self.positions[current], self.positions[neighbor])
                if candidate < cost.get(neighbor, math.inf):
                    previous[neighbor] = current
                    cost[neighbor] = candidate
                    heuristic = math.dist(self.positions[neighbor], self.positions[end])
                    heapq.heappush(queue, (candidate + heuristic, next(order), neighbor))
        return []

    def weak_components(self):
        neighbors = {n: set(v) for n, v in self.edges.items()}
        for start, ends in self.edges.items():
            for end in ends:
                neighbors[end].add(start)
        unseen = set(neighbors)
        components = []
        while unseen:
            seed = min(unseen, key=str)
            reached = {seed}
            todo = [seed]
            unseen.remove(seed)
            while todo:
                for neighbor in neighbors[todo.pop()]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        reached.add(neighbor)
                        todo.append(neighbor)
            components.append(reached)
        return sorted(components, key=len, reverse=True)


def from_flags(flags):
    graph = Graph()
    for ident, flag in flags.items():
        graph.add_node(ident, flag.position)
    missing = []
    for ident, flag in flags.items():
        for neighbor in flag.neighbors:
            if neighbor not in flags:
                missing.append((ident, neighbor))
            elif neighbor != ident:
                graph.add_edge(ident, neighbor)
    return graph, missing
