"""Optional Matplotlib overview of an existing offline navigation audit."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from navigation.tpf import read
from navigation.graph import from_flags

ROOT=Path(__file__).resolve().parents[1]


def main():
    output=ROOT/'runtime/navigation'
    report=json.loads((output/'audit.json').read_text())
    doc=json.loads((output/'accepted-network.json').read_text())
    npcs=json.loads((output/'npc-access-candidates.json').read_text())
    local=json.loads((ROOT/'runtime/local-game.json').read_text(encoding='utf-8-sig'))
    graph,_=from_flags(read(Path(local['GameDirectory'])/'Path'/report['pilot']['file']))
    lookup={n['id']:n['position'] for n in doc['nodes']}
    bounds=(min(p[0] for p in lookup.values())-25,max(p[0] for p in lookup.values())+25,
            min(p[2] for p in lookup.values())-18,max(p[2] for p in lookup.values())+18)
    inside=lambda p:bounds[0]<=p[0]<=bounds[1] and bounds[2]<=p[2]<=bounds[3]
    segments=[];seen=set()
    for start,ends in graph.edges.items():
        for end in ends:
            pair=tuple(sorted((start,end)))
            if pair not in seen and inside(graph.positions[start]) and inside(graph.positions[end]):
                p,q=graph.positions[start],graph.positions[end]
                segments.append([(p[0],p[2]),(q[0],q[2])]);seen.add(pair)
    fig,ax=plt.subplots(figsize=(10,10),dpi=145)
    fig.set_facecolor('#f8fafc');ax.set_facecolor('#f8fafc')
    ax.add_collection(LineCollection(segments,colors='#cbd5e1',linewidths=.45,alpha=.6,label='Mevcut aday bağlantılar'))
    for prefix,color,label in [('base:','#059669','Kuznez sakin ağı'),('corridor:','#2563eb','Tamamlanan Marad–Remings yolu')]:
        lines=[[(lookup[e['from']][0],lookup[e['from']][2]),(lookup[e['to']][0],lookup[e['to']][2])]
               for e in doc['edges'] if e['from'].startswith(prefix)]
        ax.add_collection(LineCollection(lines,colors=color,linewidths=2.5,label=label))
    for i,junction in enumerate(doc['candidateJunctions']):
        p,q=lookup[junction['from']],lookup[junction['to']]
        ax.plot([p[0],q[0]],[p[2],q[2]],color='#f97316',lw=2,ls='--',label='Doğrulanacak birleşimler' if not i else None)
    points=[n for n in npcs if inside((n['x'],n['y'],n['z']))]
    ax.scatter([n['x'] for n in points],[n['z'] for n in points],s=10,c='#9333ea',alpha=.7,label='NPC konumları')
    for entry in doc['locations'].values():
        x,_,z=entry['accessPosition']
        ax.scatter([x],[z],s=75,c='#1d4ed8',edgecolors='white',linewidth=1.3,zorder=6)
        ax.annotate(entry['displayName'],(x,z),xytext=(9,7),textcoords='offset points',fontsize=12,weight='bold',color='#0f172a')
    ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:]);ax.set_aspect('equal')
    ax.grid(alpha=.12);ax.set_xlabel('Dünya X');ax.set_ylabel('Dünya Z')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.10),fontsize=8,ncol=2)
    fig.suptitle('Yesode ortak yol ağı — ilk inceleme',x=.12,ha='left',y=.97,fontweight='bold',fontsize=16)
    fig.text(.12,.025,'Gri veri kesintisiz bir navmesh değildir. Turuncu birleşimler etkin değil.\nÇalışan oyun ve mevcut sakin rotaları değiştirilmedi.',fontsize=9,color='#475569')
    fig.subplots_adjust(bottom=.10,top=.86,left=.12,right=.96)
    fig.savefig(output/'overview.png',facecolor=fig.get_facecolor());plt.close(fig)
    print(output/'overview.png')


if __name__=='__main__':
    main()
