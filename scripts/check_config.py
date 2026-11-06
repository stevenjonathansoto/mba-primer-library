"""Central configuration loader. JSON syntax is a strict YAML subset."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_config(path=ROOT / 'config/agent.yaml'):
    c = json.loads(path.read_text(encoding='utf-8'))
    for key in ('public_requests_enabled', 'scheduled_refresh_enabled', 'paid_generation_enabled', 'benchmark_approved'):
        if type(c.get(key)) is not bool:
            raise ValueError(f'{key}: expected boolean')
    if not c.get('allowed_requesters') or not all(isinstance(x,str) and x for x in c['allowed_requesters']):
        raise ValueError('allowed_requesters: expected nonempty logins')
    for key in ('daily_request_cap', 'monthly_budget_usd', 'max_cost_per_primer_usd', 'refresh_primers_per_month'):
        if type(c.get(key)) not in (int,float) or not 0 < c[key] < float('inf'):
            raise ValueError(f'{key}: expected finite positive limit')
    if c['max_cost_per_primer_usd'] > c['monthly_budget_usd']:
        raise ValueError('per-primer ceiling exceeds monthly budget')
    if c['validation']['max_pages'] > 10 or c['validation']['minimum_body_points'] < 11:
        raise ValueError('readability/page limits violate MVP requirements')
    if not c['budget']['fail_closed'] or not c['validation']['require_evidence']:
        raise ValueError('fail-closed and evidence policies are mandatory')
    if c['notifications']['request_label'] == c['notifications']['feedback_label']:
        raise ValueError('requests and feedback must use distinct labels')
    if c['paid_generation_enabled']:
        if not c['benchmark_approved'] or not c['models'] or not c['pricing']:
            raise ValueError('paid execution requires benchmark approval, models and pricing')
        raise ValueError('paid provider activation not yet implemented; execution blocked')
    if c['scheduled_refresh_enabled'] and not c['paid_generation_enabled']:
        raise ValueError('paid refresh requires paid generation activation')
    return c

if __name__ == '__main__':
    load_config()
    print('OK configuration; paid execution disabled')
