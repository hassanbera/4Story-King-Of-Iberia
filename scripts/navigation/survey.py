"""Read local survey telemetry into forward-only corridor candidates.

Candidate samples are not declared safe for NPCs. Gaps, air movement, pause
events, bridge-height ambiguity, other maps and non-foot movement split paths.
"""
import math

FLAGS=('jump','fall','swim','ghost','dead','blocked')


def extract(rows):
    segments=[];current=[];previous=None;reasons={};total=0
    def finish(reason):
        nonlocal current,previous
        if len(current)>=5:
            segments.append(current)
        current=[];previous=None
        reasons[reason]=reasons.get(reason,0)+1
    for row in rows:
        total+=1
        try:
            point=tuple(float(row[k]) for k in ('x','y','z'))
            ground=float(row['ground_y']);tick=int(row['tick_ms']);event=int(row['event'])
            if not all(math.isfinite(v) for v in (*point,ground)):
                raise ValueError('nonfinite')
            if int(row['map_id'])!=0:
                finish('other_map');continue
            if any(int(row[k])!=0 for k in FLAGS) or int(row['on_foot'])!=1:
                finish('air_obstacle_or_nonfoot');continue
            if int(row['focused'])!=1 or int(row['frame_ms'])>150 or int(row['frame_ms'])<0:
                finish('focus_or_frame_gap');continue
            if int(row['candidate'])!=1 or abs(point[1]-ground)>1:
                finish('ground_not_confirmed');continue
        except (ValueError,TypeError,KeyError,OverflowError):
            finish('malformed_sample');continue
        if previous:
            old_tick,old_event,old_point=previous
            horizontal=math.hypot(point[0]-old_point[0],point[2]-old_point[2])
            if event!=old_event or not 0<=tick-old_tick<=1000 or horizontal>4 or abs(point[1]-old_point[1])>1.5:
                finish('discontinuity')
        if not current or math.hypot(point[0]-current[-1][0],point[2]-current[-1][2])>=.4 or abs(point[1]-current[-1][1])>=.2:
            current.append(point)
        previous=(tick,event,point)
    finish('end_of_recording')
    return {'samples':total,'breakReasons':reasons,
            'segments':[{'id':i,'directions':['forward'],'positions':points,
                         'length':sum(math.dist(a,b) for a,b in zip(points,points[1:])),
                         'status':'player_ground_traversal_candidate','verifiedForNpc':False}
                        for i,points in enumerate(segments)]}
