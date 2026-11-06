import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from monitor import plan_refresh

class MonitorTests(unittest.TestCase):
    def test_targeted_dependencies_and_cycles(self):
        r={'claims':[{'id':'a','verification':'supported','review_after':'2026-01-01','sections':['economics']},{'id':'b','verification':'supported','review_after':'2030-01-01','sections':['history']}], 'dependencies':{'economics':['summary','interview'],'summary':['economics']}}
        plan=plan_refresh(r,dt.date(2026,11,5),90)
        self.assertEqual(plan['sections'],['economics','interview','summary'])
        self.assertNotIn('history',plan['sections'])
