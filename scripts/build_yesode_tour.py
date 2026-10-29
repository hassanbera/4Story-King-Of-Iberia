"""Build a Yesode walking checklist from current client names and terrain regions.

Stop ordering is an exploration itinerary, not a claim of collision-free edges.
Does not change any game files or database rows.
"""
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import struct

from navigation.client_charts import regions,npcs,minimaps,portals,maps

ROOT=Path(__file__).resolve().parents[1]
OPTIONAL_NAMES={'Chest','Treasure Chest','Arrow','&&&','Participants',"Jack O' Lantern",'Expert',
                'Rice Cake Virtuoso','Weaver','Altar of origin','Tera','Beauty','Cherry','Gilda','Schoki',
                'Yvaine','Christmas Tree','Fire Starter','Game (normal crystal)','Game (small crystal)'}
TOURS=[
 ('R01','Kuznez Outpost — meydan, satıcılar ve kapı',[2]),
 ('R02','Marad → Remings → Brendel — eğitim vadisi',[1]),
 ('R03','Soldier Canyon — Blue, Koral ve Reep',[8]),
 ('R04','Ancient City Yarsk — portal ve yerleşim',[9]),
 ('R05','Liberator Hill ve Knight’s Cape — Wess ve doğu eğitim kampı',[10,11]),
 ('R06','Central Elixia → Evergreen Forest → Sacred Grove',[18,6,7,0]),
 ('R07','Sarnis ve Eastern Elixia',[5,16]),
 ('R08','Grasnoya Forest ve Ruler Forest',[3,4]),
 ('R09','Morabia Frontier Post ve Morabia Fort',[12,13]),
 ('R10','Canyon of Secrets, Gravestone ve kalan sınır durakları',[15,14,19,20,21,22]),
]


def walk_order(rows,start):
    remaining=list(rows);ordered=[]
    while remaining:
        item=min(remaining,key=lambda n:math.dist(n['position'],start))
        ordered.append(item);remaining.remove(item);start=item['position']
    return ordered,start


def main():
    local=json.loads((ROOT/'runtime/local-game.json').read_text(encoding='utf-8-sig'))
    game=Path(local['GameDirectory']);tcd=game/'Tcd'
    region=regions(tcd/'TRegion.tcd');mini=minimaps(tcd/'TMinimap.tcd');map_info=maps(tcd/'TMAP.tcd')
    portal_names=portals(tcd/'TPortal.tcd');people=npcs(tcd/'TNPC00000405.tcd')
    if map_info[0]['transform'] != (1,1,1,0,0,0,0,0,0) or mini[0x405]['world']!=4:
        raise ValueError('Review map transform/Yesode map selection before generating a tour')
    town=[r for r in region.values() if r['id']>>16==0 and r['name']=='Yesode - Kuznez outpost']
    if len(town)!=1:raise ValueError('Ambiguous Kuznez region')
    unit_index=(town[0]['id']>>8)&255
    terrain=game/f"Data/MAP/EM{map_info[0]['resource']}_{unit_index}.tmu"
    data=terrain.read_bytes();height_count,=struct.unpack_from('<I',data)
    side=math.isqrt(height_count)-1
    offset=4+height_count*4
    region_count,=struct.unpack_from('<I',data,offset);offset+=4
    if side!=512 or height_count!=513*513 or region_count!=side*side or offset+region_count>len(data):
        raise ValueError('Terrain region prefix differs from inspected source layout')
    region_grid=data[offset:offset+region_count]
    db=json.loads((ROOT/'runtime/yesode-server-npcs.json').read_text(encoding='utf-8-sig'))
    db_by_id={r['wID']:r for r in db}
    grouped=defaultdict(list)
    for npc in people:
        x,y,z=npc['position']
        if not 5120<=x<6144 or not 4096<=z<5120:raise ValueError('NPC outside Yesode unit')
        area=region_grid[int((z-4096)//2)*side+int((x-5120)//2)]
        npc['regionId']=(unit_index<<8)|area
        npc['area']=region.get(npc['regionId'],{}).get('name','Sınır / bölge etiketi yok')
        npc['optional']=npc['name'] in OPTIONAL_NAMES or npc['id'] not in db_by_id
        npc['serverPresent']=npc['id'] in db_by_id
        npc['databaseDelta']=None if npc['id'] not in db_by_id else math.dist(npc['position'],[db_by_id[npc['id']][k] for k in ('x','y','z')])
        npc['visitAsLandmark']=area in (4,7,14) and npc['name'] in ('Chest','Sack','Barrel','Stone','Gravestone')
        grouped[area].append(npc)
    tours=[];covered=set();start=next(n['position'] for n in people if n['name']=='Marad')
    for code,title,areas in TOURS:
        stops=[];extras=[]
        for area in areas:
            rows=[n for n in grouped[area] if n['id'] not in covered]
            core=[n for n in rows if not n['optional'] or n['visitAsLandmark']]
            if code=='R01':
                first=next(n for n in core if n['name']=='Marad');stops.append(first);core.remove(first);start=first['position']
            if code=='R02':
                first=next(n for n in core if n['name']=='Remings');stops.append(first);core.remove(first);start=first['position']
            ordered,start=walk_order(core,start);stops+=ordered
            extras += [n for n in rows if n not in stops]
            covered.update(n['id'] for n in rows)
        tours.append({'id':code,'title':title,'stops':stops,'optional':extras,'geometryStatus':'itinerary_only_not_a_verified_path'})
    if covered!={n['id'] for n in people}:raise ValueError('Unassigned Yesode NPC records')
    marad=next(n for n in people if n['name']=='Marad')
    remings=next(n for n in people if n['name']=='Remings')
    previous=marad
    for tour in tours:
        targets=list(tour['stops'])
        if tour['id']=='R01':previous=marad
        if tour['id']=='R02':previous=marad
        if tour['id']=='R03':previous=remings
        if not targets or previous['id']!=targets[0]['id']:targets.insert(0,previous)
        if tour['id']=='R01':targets.append(marad)
        if tour['id']=='R02':targets.append(remings)
        tour['legs']=[{'fromId':a['id'],'fromName':a['name'],'fromArea':a['area'],
                       'toId':b['id'],'toName':b['name'],'toArea':b['area']}
                      for a,b in zip(targets,targets[1:]) if a['id']!=b['id']]
        previous=targets[-1]
    arrivals=json.loads((ROOT/'runtime/yesode-server-portals.json').read_text(encoding='utf-8-sig'))
    for arrival in arrivals:
        p=portal_names.get(arrival['wPortalID'])
        if not p or p['portalRegion']!=4:raise ValueError('Unexpected portal region')
        arrival['name']=p['name']
    sources=[tcd/n for n in ('TRegion.tcd','TNPC00000405.tcd','TMinimap.tcd','TPortal.tcd','TMAP.tcd')]+[terrain]
    document={'version':1,'scope':{'mapId':0,'worldId':4,'unit':'0405','bounds':[5120,6144,4096,5120]},
              'npcCount':len(people),'npcMatchedInDb':sum(n['serverPresent'] for n in people),
              'portalNpcCount':sum('Portal' in n['name'] for n in people),'portalArrivals':arrivals,
              'tours':tours,'runtimeModified':False,
              'sources':[{'file':str(p.relative_to(game)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}
    out=ROOT/'docs/navigation';out.mkdir(exist_ok=True)
    (out/'YESODE_TOUR_STOPS.json').write_text(json.dumps(document,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (out/'YESODE_NPC_CHECKLIST.csv').open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.writer(file);writer.writerow(['tour','order','npc_id','name','title','area','x','z','height_y','optional','server_present','db_position_delta'])
        for tour in tours:
            for i,n in enumerate(tour['stops']+tour['optional'],1):
                x,y,z=n['position'];writer.writerow([tour['id'],i,n['id'],n['name'],n['title'],n['area'],round(x,2),round(z,2),round(y,2),n['optional'],n['serverPresent'],n['databaseDelta']])
    text=['# Yesode gezi ve yol kayıt rehberi','',
          '**Bu bir durak ve keşif sırası listesidir; durakların arasındaki düz çizgi güvenli güzergâh değildir.** Normal görünen yolları, merdivenleri ve köprüleri izle. Geçiş yoksa zıplayıp zorlamak yerine kaydı duraklat ve hangi iki durak arasında kaldığını bildir.','',
          'Önce R01 ve R02 ile başla; 3x hızı kısa bir düz yolda denemeden bütün haritaya çıkma. Meydanlarda ve dar merdivenlerde normal hıza dön. NPC’nin 1–3 adım önüne yaklaşmak yeterli; içine girmeye veya konuşmaya gerek yok.','',
          '- Başlatıcı: **4Story King Of Iberia - Haritalama**.',
          '- **Ctrl+Shift+F8:** normal / 3x hız.',
          '- **Ctrl+Shift+F9:** kayıt duraklat / sürdür. Alt-tab, ara verme veya ışınlanmadan önce duraklat.',
          '- Portalların yanına yürü; bu gezide portalı kullanıp ışınlanma. Işınlanma bir yürüyüş bağlantısı oluşturmaz.',
          '- Oyun haritasının altındaki koordinatla **X ve Z** sütunlarını karşılaştır. **Y** yüksekliktir; üst kattaki NPC’lerde merdiven bulman gerektiğini anlamaya yardım eder.',
          '- Gidiş tamamlanınca aynı yolu normal biçimde geri yürümek, ters yönü de sınamamıza yardımcı olur. Tek gidişin ters yönde de geçerli olduğu varsayılmaz.','',
          f"Kapsam: istemci Yesode birimindeki **{len(people)} NPC kaydı**, {document['npcMatchedInDb']} sunucu eşleşmesi, **{document['portalNpcCount']} portal NPC kaydı** ve **{len(arrivals)} portal varış kaydı**. Etkinlik/nesne kayıtları görünmeyebilir. Sadece ilk iki turu bitirmek de kullanılabilir kayıt sağlar; hepsini tek oturumda yapman gerekmiyor.",'',
          '## Tur özeti','', '| Tur | Bölge / amaç | Ana durak | İsteğe bağlı |','|---|---|---:|---:|']
    for tour in tours:text.append(f"| {tour['id']} | {tour['title']} | {len(tour['stops'])} | {len(tour['optional'])} |")
    for tour in tours:
        text += ['',f"## {tour['id']} — {tour['title']}",'',
                 'Sıra, yakın durakları aynı turda toplar. Aradaki yürünebilir yolu sen seçiyorsun; henüz otomatik engel kontrolüyle doğrulanmış bir yol tarifi değildir.','',
                 '**İsim isim yürüme sırası:**','']
        for i,leg in enumerate(tour['legs'],1):
            start_name=leg['fromName'] if leg['fromName'] not in ('Passage Portal','Chest','Jin') else f"{leg['fromName']} ({leg['fromArea']})"
            end_name=leg['toName'] if leg['toName'] not in ('Passage Portal','Chest','Jin') else f"{leg['toName']} ({leg['toArea']})"
            text.append(f"{i}. **{start_name}** → **{end_name}**")
        text += ['','**Durak koordinatları:**','', '| Tamam | No | NPC / durak | Görevi | X | Z | Y |','|---|---|---|---|---:|---:|---:|']
        for i,n in enumerate(tour['stops'],1):
            x,y,z=n['position'];role='Portal' if n['type']==8 else n['title'] if n['title']!='_' else 'Bölge işareti / nesne'
            text.append(f"| [ ] | {tour['id']}-{i:02} | {n['name']} | {role} | {x:.1f} | {z:.1f} | {y:.1f} |")
        if tour['id']=='R02':text += ['','Bu tura başlamadan Marad’ın yanına dön. Remings → Sallisar → Brendel sonrası eğitim kamplarına geçerken vadinin görünen yolunu kullan; yamaçtan kestirme yapma. Gerekirse Remings’e geri dön.']
        if tour['id']=='R08':text += ['','Ruler Forest hedefleri nehrin karşı kıyısında kalıyorsa köprü yolunu izle. Yüzerek geçişi normal yürüyüş bağlantısı saymayacağız. Nesneler görünmüyorsa koordinat yakınındaki normal yol yeterlidir.']
        if tour['id']=='R09':text += ['','**Morabia’da Y sütununa dikkat:** bazı NPC’ler duvar, teras veya üst kattadır. Hızlıca aşağı atlama; merdiven/normal giriş kullan.']
        if tour['optional']:
            text += ['','İsteğe bağlı / etkinlik / özel nesne kayıtları — görünmüyorlarsa aramak için turu bırakma:','']
            for n in tour['optional']:
                x,y,z=n['position'];text.append(f"- {n['name']} — {n['title']} — X {x:.1f}, Z {z:.1f} (kayıt {n['id']}).")
    text += ['','## Portal durakları','',
             'Aşağıdaki tablo **varış koordinatlarını** listeler; altı ayrı portal modeli var demek değildir. Kuznez’in iki farklı varış kaydı vardır. Görünür portal NPC’leri ana turlarda ayrıca yer alır.','',
             '| Kod | Varış kaydı | Ad | X | Z | Y |','|---|---:|---|---:|---:|---:|']
    for i,p in enumerate(arrivals,1):text.append(f"| P{i:02} | {p['wPortalID']} | {p['name']} | {p['x']:.1f} | {p['z']:.1f} | {p['y']:.1f} |")
    text += ['','## Ana portal bölgeleri arasında yürüyüş denemeleri','',
             'Bunlar ayrıca keşfedilecek bağlantılardır; tamamının geçilebilir olduğu iddia edilmiyor. Portalları kullanmadan, yollar üzerinden git.','',
             '1. **Passage Portal (Kuznez)** → **Passage Portal (Sarnis)**.',
             '2. **Passage Portal (Kuznez)** → **Marad** → **Remings** → **Blue** → **Koral** → **Reep** → **Passage Portal (Yarsk)**.',
             '3. **Passage Portal (Yarsk)** → **Gap** → **Panashi** → **Passage Portal (Sarnis)**.',
             "4. **Passage Portal (Yarsk)** → **Wess** → **Jin (Knight’s Cape)** → **Bronx** → **Gimmlet** → **Killie** → **Passage Portal (Morabia)**.",
             '5. **Passage Portal (Sarnis)** → **Laim** → **Ricky** → **Morabia** → **Passage Portal (Morabia Fort)**.',
             '6. **Passage Portal (Morabia Fort)** → **Kronan** → **Space-time Portal (Canyon of Secrets)**.','',
             '## Kaynak ve sınırlar','',
             'İsim ve görünen koordinatlar kurulu kaynak istemcinin NPC dosyasından; alt bölge adları TRegion ile mevcut harita biriminin gerçek bölge ızgarasından okundu. Portal varışları mevcut veritabanıyla eşleştirildi. Sunucu ve istemcide farklı konumlu bazı NPC kayıtları var; bu rehber görüntülenen istemci konumunu kullanır. Tam JSON ve CSV listesi bu dosyanın yanındadır. Ham chart ve TMU dosyaları değiştirilmedi.','',
             'Hız ve zemin bayrakları hata yakalamaya yardım eder; kayıtlar yine aday koridorlardır. NPC’lerin normal hızda bu yolları tamamladığı ayrıca doğrulanır.']
    (out/'YESODE_WALKING_TOUR.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    runtime=ROOT/'runtime/navigation';runtime.mkdir(exist_ok=True)
    # Height/region prefix is decoded for a schematic overview, not collision baking.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    import numpy as np
    heights=np.frombuffer(data,dtype='<f4',count=height_count,offset=4).reshape(side+1,side+1)
    figure,axis=plt.subplots(figsize=(12,12),dpi=140)
    terrain_image=LightSource(azdeg=315,altdeg=45).shade(heights,cmap=plt.cm.gist_earth,vert_exag=1,dx=2,dy=2,blend_mode='soft')
    axis.imshow(terrain_image,extent=[5120,6144,4096,5120],origin='lower',alpha=.55)
    palette=plt.get_cmap('tab10')
    for i,tour in enumerate(tours):
        stops=tour['stops'];color=palette(i)
        axis.scatter([n['position'][0] for n in stops],[n['position'][2] for n in stops],s=22,c=[color],edgecolors='white',linewidths=.35,label=f"{tour['id']} {tour['title'].split(' — ')[0]}")
        if stops:
            x=sum(n['position'][0] for n in stops)/len(stops);z=sum(n['position'][2] for n in stops)/len(stops)
            label_color={'R07':'#9d266f','R09':'#6b6d00','R10':'#008899'}.get(tour['id'],color)
            label_offset=(8,-25) if tour['id']=='R07' else (8,7)
            axis.annotate(tour['id'],(x,z),xytext=label_offset,textcoords='offset points',weight='bold',fontsize=11,color=label_color,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none','pad':2})
    for i,p in enumerate(arrivals,1):
        axis.scatter(p['x'],p['z'],marker='D',c='#dc2626',s=52,edgecolors='white',linewidths=.8,zorder=8)
        offset=(-38,13) if i==1 else (-38,-16) if i==2 else (8,10)
        axis.annotate(f'P{i:02}',(p['x'],p['z']),xytext=offset,textcoords='offset points',fontsize=9,weight='bold',color='#991b1b',bbox={'facecolor':'white','alpha':.85,'edgecolor':'none','pad':1})
    axis.set_xlim(5120,6144);axis.set_ylim(4096,5120);axis.set_aspect('equal');axis.grid(alpha=.18)
    axis.set_xlabel('Dünya X');axis.set_ylabel('Dünya Z')
    axis.set_title('Yesode — NPC ve portal keşif durakları',loc='left',weight='bold',pad=16)
    axis.legend(loc='upper center',bbox_to_anchor=(.5,-.07),ncol=2,fontsize=8,frameon=False)
    figure.text(.12,.025,'Noktalar hedefleri gösterir; aralarında güvenli yol çizilmiş değildir. Kırmızı elmaslar portal varış kayıtlarıdır.',fontsize=9)
    figure.subplots_adjust(bottom=.24,top=.94,left=.10,right=.97)
    figure.savefig(runtime/'yesode-tour.png');plt.close(figure)
    print(json.dumps({'npcs':len(people),'mainStops':sum(len(t['stops']) for t in tours),'optionalStops':sum(len(t['optional']) for t in tours),'portalNpcs':document['portalNpcCount'],'portalArrivals':len(arrivals),'guide':str(out/'YESODE_WALKING_TOUR.md')},indent=2))


if __name__=='__main__':
    main()
