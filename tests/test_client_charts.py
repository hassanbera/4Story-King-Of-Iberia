import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from navigation.client_charts import Reader,npcs


class ClientChartTests(unittest.TestCase):
    def test_mfc_ansi_unicode_strings_and_truncation(self):
        self.assertEqual(Reader(b'\x05Marad').string(),'Marad')
        self.assertEqual(Reader(b'\xff\xfe\xff\x01A\x00').string(),'A')
        with self.assertRaises(ValueError):Reader(b'\x08abc').string()

    def test_npc_identity_and_position_fields_match_source_layout(self):
        raw=struct.pack('<H',1)+struct.pack('<IH',20058,33)+b'\x05Marad\x07Trainer'
        raw+=bytes([0,0,1,1,0,1,1,0,0,0,1,0])+struct.pack('<4IHI',0,0,0,0,0,100)
        raw+=struct.pack('<10fB',0,5366,95,4661,1,2,1,1,1,1,0)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'npc.tcd';path.write_bytes(raw)
            result=npcs(path)
        self.assertEqual(result[0]['name'],'Marad')
        self.assertEqual(result[0]['position'],[5366,95,4661])
        self.assertEqual(result[0]['country'],1)

    def test_tour_covers_every_exported_npc_once_and_portals_are_distinguished(self):
        tour=json.loads((ROOT/'docs/navigation/YESODE_TOUR_STOPS.json').read_text(encoding='utf-8'))
        rows=[n for t in tour['tours'] for n in t['stops']+t['optional']]
        self.assertEqual(len(rows),tour['npcCount'])
        self.assertEqual(len({n['id'] for n in rows}),len(rows))
        self.assertEqual(sum('Portal' in n['name'] for n in rows),tour['portalNpcCount'])
        self.assertEqual(len(tour['portalArrivals']),6)
        self.assertTrue(any(n['name']=='Remings' for n in rows))
        for n in rows:
            x,y,z=n['position']
            self.assertTrue(5120<=x<6144 and 4096<=z<5120)


if __name__=='__main__':unittest.main()
