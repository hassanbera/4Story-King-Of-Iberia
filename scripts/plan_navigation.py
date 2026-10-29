"""Plan between named regional access points without touching a running game."""
import argparse
import json
import math
from pathlib import Path

from navigation.region import load_region

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default='yesode', choices=sorted(p.stem for p in (ROOT/'world/navigation').glob('*.json')))
    parser.add_argument('--from', dest='start', required=True)
    parser.add_argument('--to', dest='end', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    graph, document = load_region(ROOT, ROOT / f'world/navigation/{args.region}.json')
    locations = document['locations']
    if args.start not in locations or args.end not in locations:
        raise SystemExit('Unknown location; available: ' + ', '.join(locations))
    path = graph.route(locations[args.start]['node'], locations[args.end]['node'])
    result = {'region': args.region, 'from': args.start, 'to': args.end,
              'status': 'planned_from_evidenced_edges' if path else 'no_verified_route',
              'nodes': path, 'positions': [graph.positions[n] for n in path],
              'length': sum(math.dist(graph.positions[a], graph.positions[b]) for a,b in zip(path,path[1:])),
              'runtimeInstalled': False}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('nodes','positions')}, indent=2))
    return 0 if path else 2


if __name__ == '__main__':
    raise SystemExit(main())
