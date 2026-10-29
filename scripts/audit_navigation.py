"""Audit local native path assets and export a conservative regional pilot.

Reads installed game files and a read-only NPC coordinate export. Writes only
analysis artifacts, never SQL, TCD, EXEs or the running server's route CSV.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from navigation.graph import from_flags
from navigation.region import load_region
from navigation.tpf import read, PATH_HEIGHT

ROOT = Path(__file__).resolve().parents[1]


def summary(path, flags):
    known = set(flags)
    references = [(a,b) for a,f in flags.items() for b in f.neighbors if b not in known]
    expected_unit = int(path.stem.removeprefix('TFLAG'),16) & 0xffff
    return {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size, 'flags': len(flags),
            'directedReferences': sum(len(f.neighbors) for f in flags.values()),
            'unresolvedWithinFile': len(references),
            'unresolvedSameUnit': sum((b >> 16) == expected_unit for _,b in references),
            'selfReferences': sum(a in f.neighbors for a,f in flags.items()),
            'duplicateReferences': sum(len(f.neighbors)-len(set(f.neighbors)) for f in flags.values()),
            'foreignUnitIds': sum((ident >> 16) != expected_unit for ident in flags),
            'exactFieldRoundtrip': True}


def coverage(graph, position):
    nav = (position[0], position[1]+PATH_HEIGHT, position[2])
    ident = graph.nearest(nav)
    if ident is None:
        return {'status': 'no_nearby_native_flag'}
    return {'status': 'candidate_access_needs_collision_check', 'flagId': ident,
            'nativePosition': graph.positions[ident],
            'horizontalGap': math.hypot(nav[0]-graph.positions[ident][0],nav[2]-graph.positions[ident][2]),
            'verticalGapAfterSourceOffset': abs(nav[1]-graph.positions[ident][1])}


def draw_overview(path, graph, accepted, npcs, config):
    bounds = config['bounds']
    scale = 1.75
    width = (bounds['maxX']-bounds['minX'])*scale
    height = (bounds['maxZ']-bounds['minZ'])*scale
    def xy(p):
        return (40+(p[0]-bounds['minX'])*scale, 64+(bounds['maxZ']-p[2])*scale)
    def inside(p):
        return bounds['minX']<=p[0]<=bounds['maxX'] and bounds['minZ']<=p[2]<=bounds['maxZ']
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+80}" height="{height+150}" viewBox="0 0 {width+80} {height+150}">',
           '<rect width="100%" height="100%" fill="#f8fafc"/>',
           '<g font-family="Segoe UI,Arial,sans-serif" fill="#0f172a">',
           '<text x="40" y="27" font-size="20" font-weight="600">Yesode: ortak yol ağı incelemesi</text>',
           '<text x="40" y="49" font-size="12">Gri: mevcut aday bağlantılar · Yeşil: kabul edilen Kuznez ağı · Mavi: kaydedilen yürüyüş</text>']
    seen=set()
    for a,ends in graph.edges.items():
        for b in ends:
            pair=tuple(sorted((a,b)))
            if pair in seen or not inside(graph.positions[a]) or not inside(graph.positions[b]):
                continue
            seen.add(pair)
            x,y=xy(graph.positions[a]);xx,yy=xy(graph.positions[b])
            parts.append(f'<path d="M{x:.1f},{y:.1f} L{xx:.1f},{yy:.1f}" stroke="#cbd5e1" stroke-width=".5" opacity=".65"/>')
    lookup={n['id']:n['position'] for n in accepted['nodes']}
    for edge in accepted['edges']:
        p,q=lookup[edge['from']],lookup[edge['to']]
        x,y=xy(p);xx,yy=xy(q)
        color='#2563eb' if edge['from'].startswith('corridor:') else '#059669'
        parts.append(f'<path d="M{x:.1f},{y:.1f} L{xx:.1f},{yy:.1f}" stroke="{color}" stroke-width="3" fill="none"/>')
    for npc in npcs:
        p=(npc['x'],npc['y'],npc['z'])
        if inside(p):
            x,y=xy(p)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#9333ea" opacity=".7"/>')
    for entry in accepted['locations'].values():
        x,y=xy(entry['accessPosition'])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#1d4ed8" stroke="white" stroke-width="2"/>')
        parts.append(f'<text x="{x+9:.1f}" y="{y-7:.1f}" font-size="14" font-weight="600">{entry["displayName"]}</text>')
    parts += [f'<text x="40" y="{height+99}" font-size="12">Mor noktalar: veritabanındaki NPC konumları; henüz otomatik yol bağlantısı değildir.</text>',
              f'<text x="40" y="{height+121}" font-size="12">Yakın noktalar kendiliğinden birleştirilmez. Bu çıktı oyundaki rotaları değiştirmez.</text>', '</g></svg>']
    path.write_text('\n'.join(parts),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--region', default='yesode', choices=sorted(p.stem for p in (ROOT/'world/navigation').glob('*.json')))
    parser.add_argument('--output-dir',type=Path,default=ROOT/'runtime/navigation')
    parser.add_argument('--npc-export',type=Path,default=ROOT/'runtime/navigation-npcs.json')
    args=parser.parse_args()
    local=json.loads((ROOT/'runtime/local-game.json').read_text(encoding='utf-8-sig'))
    directory=Path(local['GameDirectory'])/'Path'
    config_path=ROOT/f'world/navigation/{args.region}.json'
    config=json.loads(config_path.read_text())
    if args.output_dir.resolve().is_relative_to(Path(local['GameDirectory']).resolve()):
        raise ValueError('Keep analysis output outside installed game')
    files=sorted(directory.glob(f"TFLAG{config['mapId']:04X}*.tpf"))
    target=f"TFLAG{config['mapId']:04X}{config['nativeUnit']}.tpf"
    rows=[];pilot=None
    for path in files:
        flags=read(path)
        rows.append(summary(path,flags))
        if path.name.upper()==target.upper():
            pilot=flags
    if pilot is None:
        raise ValueError('Pilot TPF file missing')
    graph,missing=from_flags(pilot)
    accepted_graph,accepted=load_region(ROOT,config_path)
    start=accepted['locations'][config['pilotJourney']['from']]['accessPosition']
    end=accepted['locations'][config['pilotJourney']['to']]['accessPosition']
    access=[coverage(graph,p) for p in (start,end)]
    candidate=[]
    if all('flagId' in a for a in access):
        candidate=graph.route(access[0]['flagId'],access[1]['flagId'])
    npcs=json.loads(args.npc_export.read_text(encoding='utf-8-sig')) if args.npc_export.exists() else []
    for npc in npcs:
        npc['nativeAccess']=coverage(graph,(npc['x'],npc['y'],npc['z']))
    components=graph.weak_components()
    report={'region':args.region,'mapId':config['mapId'],'mapFilesAreNotYesodeBoundary':True,
            'files':rows,'totalFlags':sum(r['flags'] for r in rows),
            'pilot':{'file':target,'flags':len(pilot),'usableDirectedEdges':sum(map(len,graph.edges.values())),
                     'unresolvedReferencesExcluded':len(missing),'weakComponents':len(components),
                     'largestComponentSizes':[len(c) for c in components[:10]],
                     'accessCandidates':access,'nativeRouteFound':bool(candidate),
                     'nativeRouteStatus':'candidate_needs_runtime_validation' if candidate else 'no_route_in_existing_pilot_links'},
            'npcAccessSummary':dict(Counter(n['nativeAccess']['status'] for n in npcs)),
            'acceptedNetwork':{'nodes':len(accepted_graph.positions),
                               'directedEdges':sum(map(len,accepted_graph.edges.values())),
                               'weakComponentSizes':accepted['weakComponentSizes'],
                               'candidateJunctions':accepted['candidateJunctions']},
            'runtimeModified':False}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for name,data in [('audit.json',report),('accepted-network.json',accepted),('npc-access-candidates.json',npcs)]:
        (args.output_dir/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    draw_overview(args.output_dir/'overview.svg',graph,accepted,npcs,config)
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))


if __name__=='__main__':
    main()
