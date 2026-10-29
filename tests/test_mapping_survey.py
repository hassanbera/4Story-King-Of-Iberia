import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from navigation.survey import extract


def row(i,position_x,**changes):
    value={'tick_ms':i*70,'map_id':0,'x':position_x,'y':95,'z':0,'ground_y':95,
           'jump':0,'fall':0,'swim':0,'ghost':0,'dead':0,'blocked':0,'on_foot':1,
           'focused':1,'frame_ms':16,'speed_setting':3,'event':0,'candidate':1}
    value.update(changes)
    return value


class SurveyTelemetryTests(unittest.TestCase):
    def test_grounded_threefold_survey_is_retained_as_candidate_only(self):
        result=extract([row(i,i) for i in range(8)])
        self.assertEqual(len(result['segments']),1)
        self.assertFalse(result['segments'][0]['verifiedForNpc'])
        self.assertEqual(result['segments'][0]['directions'],['forward'])

    def test_fall_splits_paths_without_bridging_the_drop(self):
        rows=[row(i,i) for i in range(6)]+[row(6,6,fall=1,candidate=0)]
        rows += [row(i,100+i,y=70,ground_y=70) for i in range(7,13)]
        result=extract(rows)
        self.assertEqual(len(result['segments']),2)
        self.assertIn('air_obstacle_or_nonfoot',result['breakReasons'])

    def test_pause_event_and_teleport_never_create_long_edges(self):
        rows=[row(i,i) for i in range(6)]+[row(i,100+i,event=1) for i in range(6,12)]
        result=extract(rows)
        self.assertEqual(len(result['segments']),2)
        self.assertIn('discontinuity',result['breakReasons'])

    def test_ground_focus_and_frame_checks_are_independent_of_candidate_flag(self):
        for changes in ({'focused':0},{'frame_ms':200},{'ground_y':20},{'x':'nan'},{'map_id':1}):
            self.assertEqual(extract([row(i,i,**changes) for i in range(8)])['segments'],[])


if __name__=='__main__':
    unittest.main()
