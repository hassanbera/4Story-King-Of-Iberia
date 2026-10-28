"""Build a connected ambient road graph from the 30 accepted Kuznez routes.

This reads a local read-only export, not SQL. No guessed cross-route shortcuts are
added: graph edges come only from adjacent points in an accepted route.
"""

import hashlib
import json
from collections import defaultdict, deque
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "yesode-live-routes.json"
GRAPH = ROOT / "yesode-graph.json"
MERGE_RADIUS = 1.0

rows = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
by_resident = defaultdict(list)
for row in rows:
    by_resident[int(row["id"])].append(row)
assert len(by_resident) == 30 and len(rows) == 120

points = []
route_edges = []
for resident_id, route in sorted(by_resident.items()):
    route.sort(key=lambda row: int(row["path"]))
    assert [row["path"] for row in route] == [1, 2, 3, 4]
    ordered = [
        (route[0]["spawn"], 0, resident_id, 0),
        *((row["position"], int(row["prob"]), resident_id, int(row["path"])) for row in route),
    ]
    indexes = []
    for position, probability, owner, order in ordered:
        indexes.append(len(points))
        points.append({"position": position, "stopProbability": probability, "resident": owner, "order": order})
    route_edges.extend(zip(indexes, indexes[1:]))

parent = list(range(len(points)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def union(a, b):
    a, b = find(a), find(b)
    if a != b:
        parent[b] = a


for i, first in enumerate(points):
    a = first["position"]
    for j in range(i + 1, len(points)):
        b = points[j]["position"]
        if abs(a[1] - b[1]) <= 1.0 and hypot(a[0] - b[0], a[2] - b[2]) <= MERGE_RADIUS:
            union(i, j)

clusters = defaultdict(list)
for i in range(len(points)):
    clusters[find(i)].append(i)

node_records = []
for root, members in clusters.items():
    positions = [points[i]["position"] for i in members]
    position = [round(sum(p[axis] for p in positions) / len(positions), 3) for axis in range(3)]
    node_records.append((root, position, max(points[i]["stopProbability"] for i in members), members))
node_records.sort(key=lambda row: (row[1][0], row[1][2], row[1][1]))
ids = {root: i for i, (root, _, _, _) in enumerate(node_records)}

edges = set()
for a, b in route_edges:
    x, y = ids[find(a)], ids[find(b)]
    if x != y:
        edges.add(tuple(sorted((x, y))))
edges = sorted(edges)

nodes = []
for node_id, (_, position, probability, members) in enumerate(node_records):
    nodes.append({
        "id": node_id,
        "mapId": 0,
        "position": position,
        "stopProbability": probability,
        "radius": 0.8,
        "sourceResidents": sorted({points[i]["resident"] for i in members}),
    })

adjacency = defaultdict(set)
for a, b in edges:
    adjacency[a].add(b)
    adjacency[b].add(a)
    p, q = nodes[a]["position"], nodes[b]["position"]
    if hypot(p[0] - q[0], p[2] - q[2]) > 40 or abs(p[1] - q[1]) > 12:
        raise RuntimeError(f"Unexpectedly long/different-height route edge: {a}-{b}")

seen = {0}
pending = deque([0])
while pending:
    for neighbor in adjacency[pending.popleft()]:
        if neighbor not in seen:
            seen.add(neighbor)
            pending.append(neighbor)
if len(seen) != len(nodes) or len(nodes) > 200:
    raise RuntimeError("Graph disconnected or too large for the legacy waypoint state")

graph = {
    "version": 1,
    "graphId": 1,
    "mapId": 0,
    "origin": "30 user-accepted Yesode routes; cluster positions within one horizontal unit",
    "sourceSha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest().upper(),
    "spawnIds": sorted(by_resident),
    "nodes": nodes,
    "edges": [{"from": a, "to": b} for a, b in edges],
}
GRAPH.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"nodes={len(nodes)} edges={len(edges)} connected=yes graph={GRAPH}")
