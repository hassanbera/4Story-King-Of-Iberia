"""Build a common regional graph from explicitly evidenced corridors."""
import hashlib
import json
import math
from pathlib import Path

from .graph import Graph


def source_file(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Region source must be a file inside this repository')
    return path


def load_region(root: Path, config_path: Path):
    config = json.loads(config_path.read_text())
    if config['policy']['autoJoinNearbyNodes'] or config['policy']['recordedWalkDirection'] != 'forward':
        raise ValueError('Unsupported region evidence policy')
    graph = Graph()
    evidence = []
    sources = []
    last_nodes = {}
    for entry in config['baseGraphs']:
        path = source_file(root, entry['file']); sources.append(path)
        base = json.loads(path.read_text())
        if base['mapId'] != config['mapId']:
            raise ValueError('Base graph map mismatch')
        prefix = f"base:{entry['id']}:"
        for node in base['nodes']:
            graph.add_node(prefix+str(node['id']), node['position'])
        for edge in base['edges']:
            a,b = prefix+str(edge['from']),prefix+str(edge['to'])
            graph.add_edge(a,b,bidirectional=entry['bidirectional'])
            evidence.append({'from':a,'to':b,'bidirectional':entry['bidirectional'],'source':'accepted_base_graph'})
    for entry in config['corridors']:
        path = source_file(root, entry['file']); sources.append(path)
        walk = json.loads(path.read_text())
        if walk['mapId'] != config['mapId'] or walk['directions'] != ['forward']:
            raise ValueError('Corridor map/direction needs explicit support')
        prefix = f"corridor:{entry['id']}:"
        for i, position in enumerate(walk['waypoints']):
            graph.add_node(prefix+str(i),position)
            if i:
                a,b = prefix+str(i-1),prefix+str(i)
                graph.add_edge(a,b)
                evidence.append({'from':a,'to':b,'bidirectional':False,'source':'recorded_player_walk_soldier_reached_destination'})
        last_nodes[prefix+'last'] = prefix+str(len(walk['waypoints'])-1)
    for edge in config['verifiedConnections']:
        if not edge.get('evidence'):
            raise ValueError('Junction needs explicit evidence before activation')
        graph.add_edge(edge['from'], edge['to'], bidirectional=edge['bidirectional'])
        evidence.append(edge)
    locations = {}
    for key, location in config['locations'].items():
        entry = dict(location)
        entry['node'] = last_nodes.get(entry['node'],entry['node'])
        if entry['node'] not in graph.positions:
            raise ValueError('Location points at an unknown node')
        entry['accessPosition'] = graph.positions[entry['node']]
        locations[key] = entry
    # Review suggestions only: these pairs are deliberately NOT graph edges.
    junctions = []
    for a, p in graph.positions.items():
        if not a.startswith('base:'):
            continue
        for b, q in graph.positions.items():
            if b.startswith('corridor:') and math.hypot(p[0]-q[0], p[2]-q[2]) <= 4 and abs(p[1]-q[1]) <= 1:
                junctions.append({'from': a, 'to': b, 'distance': math.dist(p,q), 'status': 'unverified_not_traversable'})
    document = {'version': 1, 'region': config['region'], 'mapId': config['mapId'],
                'nodes': [{'id': k, 'position': p} for k,p in graph.positions.items()],
                'edges': evidence, 'locations': locations, 'candidateJunctions': junctions,
                'weakComponentSizes': [len(c) for c in graph.weak_components()],
                'sources': [{'file': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                            for p in sources]}
    return graph, document
