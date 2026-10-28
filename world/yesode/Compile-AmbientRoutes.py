"""Validate editable *-graph.json region files and emit the server's route CSV."""

import json
from collections import deque
from math import hypot, isfinite
from pathlib import Path

root = Path(__file__).resolve().parent
sources = sorted(root.glob("*-graph.json"))
if not sources:
    raise SystemExit("No region graph JSON files found")

graphs = []
graph_ids = set()
spawn_ids = set()
for source in sources:
    graph = json.loads(source.read_text(encoding="utf-8"))
    graph_id = graph["graphId"]
    map_id = graph["mapId"]
    residents = graph["spawnIds"]
    nodes = graph["nodes"]
    edges = graph["edges"]
    if not isinstance(graph_id, int) or not 1 <= graph_id <= 65535 or graph_id in graph_ids:
        raise ValueError(f"Duplicate or invalid graph ID: {source}")
    graph_ids.add(graph_id)
    if not isinstance(map_id, int) or not 0 <= map_id <= 65535:
        raise ValueError(f"Invalid map ID: {source}")
    if not residents or len(residents) != len(set(residents)) or any(not isinstance(r, int) or not 0 <= r <= 65535 or r in spawn_ids for r in residents):
        raise ValueError(f"Invalid or duplicate spawn binding: {source}")
    spawn_ids.update(residents)
    if not 3 <= len(nodes) <= 200 or [n["id"] for n in nodes] != list(range(len(nodes))):
        raise ValueError(f"Node IDs must be contiguous 0..N-1: {source}")

    for node in nodes:
        position = node["position"]
        if len(position) != 3 or not all(isinstance(v, (int, float)) and isfinite(v) for v in position):
            raise ValueError(f"Invalid position at map {map_id} node {node['id']}")
        if not 0 <= node["stopProbability"] <= 100 or not 0 <= node["radius"] <= 3:
            raise ValueError(f"Invalid stop/radius at map {map_id} node {node['id']}")

    adjacency = {n["id"]: set() for n in nodes}
    seen_edges = set()
    for edge in edges:
        a, b = edge["from"], edge["to"]
        if not isinstance(a, int) or not isinstance(b, int) or a == b or a not in adjacency or b not in adjacency:
            raise ValueError(f"Invalid edge on map {map_id}: {edge}")
        pair = tuple(sorted((a, b)))
        if pair in seen_edges:
            raise ValueError(f"Duplicate edge on map {map_id}: {pair}")
        seen_edges.add(pair)
        p, q = nodes[a]["position"], nodes[b]["position"]
        if hypot(p[0] - q[0], p[2] - q[2]) > 40 or abs(p[1] - q[1]) > 12:
            raise ValueError(f"Long or steep edge on map {map_id}: {pair}")
        adjacency[a].add(b)
        adjacency[b].add(a)

    reached = {0}
    queue = deque([0])
    while queue:
        for neighbor in adjacency[queue.popleft()]:
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    if len(reached) != len(nodes):
        raise ValueError(f"Disconnected graph on map {map_id}")
    graphs.append(graph)

lines = ["# Ambient route graph v2: N,graph,map,id,x,y,z,stop_probability,radius; E,graph,from,to; R,spawn,graph"]
for graph in sorted(graphs, key=lambda item: item["graphId"]):
    graph_id = graph["graphId"]
    map_id = graph["mapId"]
    for node in graph["nodes"]:
        x, y, z = node["position"]
        lines.append(f'N,{graph_id},{map_id},{node["id"]},{x:.3f},{y:.3f},{z:.3f},{node["stopProbability"]},{node["radius"]:.2f}')
    for edge in graph["edges"]:
        lines.append(f'E,{graph_id},{edge["from"]},{edge["to"]}')
    for spawn_id in graph["spawnIds"]:
        lines.append(f'R,{spawn_id},{graph_id}')

output = root / "AmbientRoutes.csv"
output.write_text("\n".join(lines) + "\n", encoding="ascii")
print(f"maps={len(graphs)} nodes={sum(len(g['nodes']) for g in graphs)} edges={sum(len(g['edges']) for g in graphs)} output={output}")
