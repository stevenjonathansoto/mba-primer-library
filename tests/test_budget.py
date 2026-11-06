import copy
import datetime as dt
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from budget import Ledger
from check_config import load_config

class BudgetTests(unittest.TestCase):
    def test_atomic_monthly_ceiling(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.db'; Ledger(path,True).db.close()
            config=copy.deepcopy(load_config()); config['daily_request_cap']=10
            def run(i):
                ledger=Ledger(path)
                try:
                    ledger.reserve(str(i),'stevenjonathansoto',config,5)
                    return True
                except ValueError: return False
                finally: ledger.db.close()
            with ThreadPoolExecutor(max_workers=6) as pool:
                self.assertEqual(sum(pool.map(run,range(8))),4)

    def test_unauthorized_missing_and_unknown_cost(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.db'
            with self.assertRaises(ValueError): Ledger(path)
            ledger=Ledger(path,True)
            with self.assertRaises(ValueError): ledger.reserve('a','outsider',load_config(),5)
            with self.assertRaises(ValueError): ledger.reserve('a','stevenjonathansoto',load_config(),float('nan'))
            ledger.db.close()

    def test_uncertain_runs_keep_reservation(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=Ledger(Path(d)/'ledger.db',True); config=load_config()
            for i in range(3): ledger.reserve(str(i),'stevenjonathansoto',config,5)
            with self.assertRaises(ValueError): ledger.reserve('4','stevenjonathansoto',config,5)
            ledger.reconcile('0',1.25,{'provider':'mock','input_tokens':100})
            with self.assertRaises(ValueError): ledger.reconcile('0',0,{})
            ledger.db.close()
