"""Convert one explicitly recorded local walk into a bounded soldier route.

Prepares JSON only. Does not update SQL or restart the game.
"""
import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def distance(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def convert(rows, start, end):
    points = [[float(v) for v in row[2:5]] for row in rows if int(row[1]) == 0]
    # Use a completed start-to-end walk, not the player's approach to Marad.
    start_hits = [i for i, p in enumerate(points) if distance(p, start) <= 6]
    if not start_hits:
        raise ValueError('No recorded point within six units of Marad start')
    end_hits = [i for i, p in enumerate(points) if i > start_hits[0] and distance(p, end) <= 6]
    if not end_hits:
        raise ValueError('No completed walk to Remings yet')
    finish = end_hits[-1]
    begin = min((i for i in start_hits if i < finish), key=lambda i: distance(points[i], start))
    section = points[begin:finish + 1]
    if len(section) < 5:
        raise ValueError('Too few movement samples')
    for a, b in zip(section, section[1:]):
        if distance(a, b) > 10 or abs(a[1] - b[1]) > 5:
            raise ValueError('Discontinuous walk; do not bridge jumps/teleports or recording gaps')
    kept = [section[0]]
    for p in section[1:]:
        if distance(p, kept[-1]) >= 2 or abs(p[1] - kept[-1][1]) >= .6:
            kept.append(p)
    if distance(kept[-1], section[-1]) > .1:
        kept.append(section[-1])
    if not 5 <= len(kept) <= 190:
        raise ValueError('Route exceeds bounded waypoint count or is too short')
    assert all(distance(a, b) <= 10 for a, b in zip(kept, kept[1:]))
    return [[round(v, 4) for v in p] for p in kept]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'runtime/soldier-caelen/walk-candidate.json')
    args = parser.parse_args()
    config = json.loads((ROOT / 'world/yesode/soldiers/caelen.json').read_text())
    with args.csv.open(newline='') as stream:
        rows = list(csv.reader(stream))
    config['waypoints'] = convert(rows, config['waypoints'][0], config['anchors']['end']['position'])
    config['routeStatus'] = 'recorded_player_walk_requires_soldier_replay'
    config['positionEvidence'] = 'Explicit Marad-to-Remings player walk captured by opt-in RouteSurvey; no terrain-height interpolation.'
    args.output.write_text(json.dumps(config, indent=2) + '\n')
    print(f"Prepared {len(config['waypoints'])} recorded ground waypoints: {args.output}")


if __name__ == '__main__':
    main()
