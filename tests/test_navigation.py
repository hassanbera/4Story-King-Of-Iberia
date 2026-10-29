import json
import math
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from navigation.graph import Graph, from_flags
from navigation.region import load_region
from navigation.tpf import Flag, decode, encode


class NativePathReaderTests(unittest.TestCase):
    def test_source_layout_roundtrip_and_unresolved_reference_is_quarantined(self):
        flags={10:Flag((1.0,2.3,3.0),(11,999)),11:Flag((2.0,2.3,3.0),(10,))}
        decoded=decode(encode(flags))
        self.assertEqual(encode(decoded),encode(flags))
        graph,missing=from_flags(decoded)
        self.assertEqual(missing,[(10,999)])
        self.assertEqual(graph.route(10,11),[10,11])
        self.assertNotIn(999,graph.positions)

    def test_truncated_adjacency_and_trailing_data_are_rejected(self):
        raw=encode({10:Flag((1,2,3),(11,))})
        with self.assertRaises(ValueError):
            decode(raw[:-1])
        with self.assertRaisesRegex(ValueError,'trailing'):
            decode(raw+b'X')

    def test_duplicate_ids_and_nan_are_rejected(self):
        record=struct.pack('<IfffI',10,1,2,3,0)
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            decode(struct.pack('<I',2)+record+record)
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            decode(struct.pack('<I',1)+struct.pack('<IfffI',10,1,math.nan,3,0))


class SharedPlannerTests(unittest.TestCase):
    def test_detour_uses_only_explicit_edges_and_does_not_invent_shortcut(self):
        graph=Graph()
        for key,pos in {'start':(0,0,0),'corner':(0,0,4),'end':(4,0,4),'nearby':(.1,0,0)}.items():
            graph.add_node(key,pos)
        graph.add_edge('start','corner')
        graph.add_edge('corner','end')
        self.assertEqual(graph.route('start','end'),['start','corner','end'])
        self.assertEqual(graph.route('start','nearby'),[])
        self.assertEqual(graph.route('end','start'),[])

    def test_large_graph_is_not_limited_to_existing_monster_waypoint_byte(self):
        graph=Graph()
        for i in range(301):
            graph.add_node(i,(i,0,0))
            if i:
                graph.add_edge(i-1,i)
        self.assertEqual(len(graph.route(0,300)),301)

    def test_ground_and_bridge_layers_are_not_confused_by_nearest_lookup(self):
        graph=Graph()
        graph.add_node('ground',(0,0,0))
        graph.add_node('bridge',(0,12,0))
        self.assertEqual(graph.nearest((0,12.3,0)), 'bridge')
        self.assertIsNone(graph.nearest((0,6,0)))

    def test_actual_region_reuses_walk_and_preserves_unverified_junctions(self):
        graph,doc=load_region(ROOT,ROOT/'world/navigation/yesode.json')
        start=doc['locations']['marad']['node'];end=doc['locations']['remings']['node']
        planned=graph.route(start,end)
        recorded=json.loads((ROOT/'world/yesode/soldiers/caelen.json').read_text())['waypoints']
        self.assertEqual([list(graph.positions[n]) for n in planned],recorded)
        self.assertEqual(graph.route(end,start),[])
        self.assertTrue(doc['candidateJunctions'])
        for junction in doc['candidateJunctions']:
            self.assertEqual(graph.route(junction['from'],junction['to']),[])


if __name__=='__main__':
    unittest.main()
