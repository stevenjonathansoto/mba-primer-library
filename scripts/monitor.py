"""Free deterministic review queue. Network probes are opt-in and never use LLMs."""
import argparse
import datetime as dt
import json
from pathlib import Path
from check_config import load_config

ROOT=Path(__file__).resolve().parents[1]

def plan_refresh(research,today,review_days):
    affected=set(); reasons=[]
    for claim in research.get('claims',[]):
        due=claim.get('review_after')
        checked=claim.get('last_verified')
        stale=(due and dt.date.fromisoformat(due)<=today) or (checked and (today-dt.date.fromisoformat(checked)).days>=review_days)
        if stale or claim.get('verification')!='supported':
            affected.update(claim.get('sections',[]))
            reasons.append({'claim_id':claim['id'],'reason':'review due' if stale else 'unsupported','materiality':claim.get('materiality','unknown')})
    dependencies=research.get('dependencies',{})
    pending=list(affected)
    while pending:
        for dependent in dependencies.get(pending.pop(),[]):
            if dependent not in affected: affected.add(dependent); pending.append(dependent)
    return {'sections':sorted(affected),'reasons':reasons,'preserve_other_sections':True}

def report(today):
    config=load_config(); queue=[]
    for item in json.loads((ROOT/'docs/legacy-inventory.json').read_text(encoding='utf-8')):
        if item['status']=='coming-soon': continue
        date=dt.datetime.strptime(item['updated'].replace('Last Updated:','').strip(),'%B %Y').date()
        queue.append({'slug':item['id'][5:],'status':'legacy-unverified','age_days':(today-date).days,'reason':'Initial source audit required; age is measured from month start, not verification date'})
    for path in sorted((ROOT/'primers').glob('*/research.json')):
        research=json.loads(path.read_text(encoding='utf-8'))
        queue.append({'slug':path.parent.name,'status':'structured','plan':plan_refresh(research,today,config['refresh']['review_after_days'])})
    return {'as_of':today.isoformat(),'paid_calls':0,'scheduled_paid_refresh_enabled':config['scheduled_refresh_enabled'],'queue':queue}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--date',type=dt.date.fromisoformat,default=dt.datetime.now(dt.timezone.utc).date()); parser.add_argument('--output',type=Path,default=Path('work/monitor.json'))
    args=parser.parse_args(); args.output.parent.mkdir(parents=True,exist_ok=True)
    result=report(args.date); args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f"Review queue: {len(result['queue'])}; paid calls: 0; output: {args.output}")
