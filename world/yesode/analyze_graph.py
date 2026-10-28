import json
from collections import defaultdict
from math import hypot
from pathlib import Path

rows = json.loads((Path(__file__).parent / 'yesode-live-routes.json').read_text(encoding='utf-8-sig'))
by_resident = defaultdict(list)
for row in rows:
    by_resident[row['id']].append(row)

points = []
links = []
for resident_id, route in sorted(by_resident.items()):
    route.sort(key=lambda row: row['path'])
    indexes = []
    for order, position in enumerate([route[0]['spawn']] + [row['position'] for row in route]):
        indexes.append(len(points))
        points.append((resident_id, order, position))
    links.extend(zip(indexes, indexes[1:]))


def analyze(radius):
    parent = list(range(len(points)))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = root(a), root(b)
        if a != b:
            parent[b] = a

    for i, (_, _, a) in enumerate(points):
        for j in range(i + 1, len(points)):
            b = points[j][2]
            if abs(a[1] - b[1]) <= 2 and hypot(a[0] - b[0], a[2] - b[2]) <= radius:
                union(i, j)

    clusters = defaultdict(list)
    for i in range(len(points)):
        clusters[root(i)].append(i)
    graph = defaultdict(set)
    for a, b in links:
        x, y = root(a), root(b)
        if x != y:
            graph[x].add(y)
            graph[y].add(x)

    visited = set()
    components = []
    for node in clusters:
        if node in visited:
            continue
        todo = [node]
        component = set()
        while todo:
            current = todo.pop()
            if current in component:
                continue
            component.add(current)
            todo.extend(graph[current] - component)
        visited.update(component)
        components.append(component)
    components.sort(key=len, reverse=True)
    print(f'radius={radius} nodes={len(clusters)} edges={sum(map(len, graph.values())) // 2} components={len(components)} sizes={[len(c) for c in components[:10]]}')


for radius in (1, 2, 3, 4, 5, 6, 8, 10):
    analyze(radius)
