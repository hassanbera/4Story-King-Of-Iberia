"""Prepare one soldier chart/SQL candidate; never modifies the running game."""
import hashlib
import json
import math
from pathlib import Path
import struct

from tmon_chart import parse

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def main():
    config = json.loads((ROOT / 'world/yesode/soldiers/caelen.json').read_text())
    points = config['waypoints']
    if not 5 <= len(points) <= 190:
        raise ValueError('Expected a bounded recorded soldier walk')
    for a, b in zip(points, points[1:]):
        if math.hypot(a[0]-b[0], a[2]-b[2]) > 10 or abs(a[1]-b[1]) > 5:
            raise ValueError('Do not bridge missing ground samples with guessed waypoints')
    local = json.loads((ROOT / 'runtime/local-game.json').read_text(encoding='utf-8-sig'))
    chart = Path(local['GameDirectory']) / 'Tcd/TMon.tcd'
    original = chart.read_bytes()
    records = parse(original)
    ident = config['id']
    assert ident not in records and all(i in records for i in range(32600, 32630))
    base = records[config['clientTemplate']]
    assert base['obj'] == 1005220 and base['title'] == ''
    raw = bytearray(base['raw'])
    struct.pack_into('<H', raw, 0, ident)
    equip = [0] * 19
    equip[14] = base['equip'][14]  # Accepted human male face/portrait.
    for slot, item in config['equipment'].items():
        equip[int(slot)] = item
    struct.pack_into('<19H', raw, base['equip_offset'], *equip)
    struct.pack_into('<4H', raw, base['skill_offset'], 726, 0, 0, 0)
    # Rewrite variable strings after patching fixed offsets, from right to left.
    for start, end, text in ((base['name_start'], base['name_end'], config['name']),
                             (4, base['name_start'], config['title'])):
        encoded = text.encode('ascii')
        assert len(encoded) < 255
        raw[start:end] = bytes([len(encoded)]) + encoded
    candidate = struct.pack('<H', len(records) + 1) + original[2:] + raw
    checked = parse(candidate)
    assert len(checked) == len(records) + 1
    assert all(checked[i]['raw'] == r['raw'] for i, r in records.items())
    assert checked[ident]['equip'] == tuple(equip)
    assert checked[ident]['title'] == config['title']
    out = ROOT / 'runtime/soldier-caelen'
    out.mkdir(exist_ok=True)
    (out / 'TMon.candidate.tcd').write_bytes(candidate)
    (out / 'TMon.before.tcd').write_bytes(original)
    manifest = {'id': ident, 'chartPath': str(chart), 'beforeSha256': sha(original),
                'candidateSha256': sha(candidate), 'unchangedExistingRecords': len(records)}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))

    # Clone established friendly humanoid warrior behavior, without copying loot.
    # Attribute 1/level 1 exists in the current DB; no new combat balance is added.
    points = config['waypoints']
    values = ',\n'.join(f"({ident},{i},{x},{y},{z},0,0)" for i, (x,y,z) in enumerate(points, 1))
    x,y,z = points[0]
    sql = f"""SET XACT_ABORT ON;
IF (SELECT COUNT(*) FROM dbo.TMONSTERCHART WHERE wID BETWEEN 32600 AND 32629) <> 30
    THROW 51000, 'Expected 30 accepted residents', 1;
IF EXISTS(SELECT 1 FROM dbo.TMONSTERCHART WHERE wID={ident}) OR
   EXISTS(SELECT 1 FROM dbo.TMONSPAWNCHART WHERE wID={ident}) OR
   EXISTS(SELECT 1 FROM dbo.TMAPMONCHART WHERE wSpawnID={ident} OR wMonID={ident}) OR
   EXISTS(SELECT 1 FROM dbo.TSPAWNPATHCHART WHERE wSpawnID={ident})
    THROW 51000, 'Soldier IDs already occupied', 1;
IF NOT EXISTS(SELECT 1 FROM dbo.TMONATTRCHART WHERE wID=1 AND bLevel=1)
    THROW 51000, 'Level 1 attribute missing', 1;
IF (SELECT COUNT(*) FROM dbo.TITEMCHART WHERE wItemID IN (121,1021,4601,4602,4603,4604,4605)
    AND bLevel=1 AND bItemCountry=1 AND (dwClassID & 1)=1) <> 7
    THROW 51000, 'Derion warrior starter equipment changed', 1;
IF NOT EXISTS(SELECT 1 FROM dbo.TNPCCHART WHERE wID=20058 AND ABS(fPosX-5366.22)<0.1 AND ABS(fPosZ-4661.17)<0.1)
 OR NOT EXISTS(SELECT 1 FROM dbo.TNPCCHART WHERE wID=20065 AND ABS(fPosX-5477.82)<0.1 AND ABS(fPosZ-4775.8)<0.1)
    THROW 51000, 'Route anchors changed', 1;
DECLARE @before int=(SELECT CHECKSUM_AGG(BINARY_CHECKSUM(*)) FROM dbo.TMONSTERCHART WHERE wID BETWEEN 32600 AND 32629);
BEGIN TRANSACTION;
SELECT * INTO #soldier FROM dbo.TMONSTERCHART WHERE wID={config['serverTemplate']};
IF @@ROWCOUNT <> 1 THROW 51000, 'Warrior template missing', 1;
UPDATE #soldier SET wID={ident},szName='{config['name']}',szName2='{config['name']}',bClass=0,
 bLevel=1,wMonAttr=1,fSize=0.77,bRoamProb=100,wSkill1=726,wSkill2=0,wSkill3=0,wSkill4=0;
INSERT dbo.TMONSTERCHART SELECT * FROM #soldier;
SELECT * INTO #spawn FROM dbo.TMONSPAWNCHART WHERE wID=32600;
UPDATE #spawn SET wID={ident},fPosX={x},fPosY={y},fPosZ={z},bRoamType=6;
INSERT dbo.TMONSPAWNCHART SELECT * FROM #spawn;
INSERT dbo.TMAPMONCHART(wSpawnID,wMonID,bEssential,bLeader,bProb) VALUES({ident},{ident},1,1,100);
INSERT dbo.TSPAWNPATHCHART(wSpawnID,bPathID,fPosX,fPosY,fPosZ,bProb,fRadius) VALUES
{values};
IF @before <> (SELECT CHECKSUM_AGG(BINARY_CHECKSUM(*)) FROM dbo.TMONSTERCHART WHERE wID BETWEEN 32600 AND 32629)
 THROW 51000, 'Existing residents changed', 1;
COMMIT;
"""
    (out / 'install.sql').write_text(sql)
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
