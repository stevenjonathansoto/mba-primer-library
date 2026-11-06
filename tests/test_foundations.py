import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_config import load_config
from check_site import CardParser
from check_legacy import check

class Foundations(unittest.TestCase):
    def test_legacy_contract(self):
        check()

    def test_coming_soon(self):
        p=CardParser()
        p.feed('<div class="primer-card coming-soon" id="card-test" data-status="coming-soon"><h3 class="card-title">Test</h3></div>')
        self.assertEqual(p.cards[0]['status'],'coming-soon')
        self.assertEqual(p.cards[0]['downloads'],[])

    def test_unsafe_config_rejected(self):
        baseline=load_config()
        for key,value in [('daily_request_cap',True),('monthly_budget_usd',-1),('public_requests_enabled','false'),('paid_generation_enabled',True)]:
            c=copy.deepcopy(baseline); c[key]=value
            with self.subTest(key=key),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'config.yaml'; p.write_text(json.dumps(c))
                with self.assertRaises(ValueError): load_config(p)

if __name__=='__main__': unittest.main()
