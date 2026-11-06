"""Atomic local ledger primitive. Production must supply durable shared storage.

SQLite transactions serialize reservations; no provider call belongs inside
this module. Missing ledgers fail closed unless explicitly initialized.
"""
import datetime as dt
import sqlite3
from decimal import Decimal

def micros(value):
    d=Decimal(str(value))
    if not d.is_finite() or d<0: raise ValueError('invalid cost')
    return int((d*1000000).to_integral_value(rounding='ROUND_CEILING'))

class Ledger:
    def __init__(self,path,initialize=False):
        if not initialize and not path.is_file(): raise ValueError('missing ledger; spending blocked')
        self.db=sqlite3.connect(path,timeout=30,isolation_level=None)
        if initialize:
            self.db.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, requester TEXT NOT NULL, reserved INTEGER NOT NULL, actual INTEGER, status TEXT NOT NULL, usage TEXT)')

    def reserve(self,run_id,requester,config,amount,now=None):
        if requester not in config['allowed_requesters'] and not config['public_requests_enabled']:
            raise ValueError('unauthorized requester')
        now=now or dt.datetime.now(dt.timezone.utc)
        stamp=now.astimezone(dt.timezone.utc).isoformat()
        value=micros(amount)
        if value<=0 or value>micros(config['max_cost_per_primer_usd']): raise ValueError('invalid reservation')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if self.db.execute("SELECT count(*) FROM runs WHERE status='overrun'").fetchone()[0]:
                raise ValueError('unresolved overrun; spending blocked')
            count=self.db.execute('SELECT count(*) FROM runs WHERE substr(timestamp,1,10)=?',(stamp[:10],)).fetchone()[0]
            total=self.db.execute('SELECT coalesce(sum(coalesce(actual,reserved)),0) FROM runs WHERE substr(timestamp,1,7)=?',(stamp[:7],)).fetchone()[0]
            if count>=config['daily_request_cap']: raise ValueError('daily cap reached')
            if total+value>micros(config['monthly_budget_usd']): raise ValueError('monthly budget exhausted')
            self.db.execute('INSERT INTO runs VALUES (?,?,?,?,NULL,?,NULL)',(run_id,stamp,requester,value,'reserved'))
            self.db.execute('COMMIT')
        except Exception:
            self.db.execute('ROLLBACK'); raise

    def reconcile(self,run_id,amount,usage):
        import json
        value=micros(amount)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT reserved,status FROM runs WHERE id=?',(run_id,)).fetchone()
            if not row or row[1]!='reserved': raise ValueError('unknown or finalized run')
            status='overrun' if value>row[0] else 'complete'
            self.db.execute('UPDATE runs SET actual=?,status=?,usage=? WHERE id=?',(value,status,json.dumps(usage),run_id))
            self.db.execute('COMMIT')
        except Exception:
            self.db.execute('ROLLBACK'); raise
        if status=='overrun': raise ValueError('provider exceeded reservation; halt paid operations')
