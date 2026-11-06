"""Authenticate issue metadata before any generation or reservation."""
import json
import os
from pathlib import Path
from check_config import load_config

def decide(event,config):
    issue=event.get('issue',{})
    labels={x['name'] for x in issue.get('labels',[])}
    policy=config['notifications']
    if policy['feedback_label'] in labels or policy['request_label'] not in labels:
        return {'status':'ignored','reason':'Not a generation request','paid_calls':0}
    author=issue.get('user',{}).get('login')
    if not author or (author not in config['allowed_requesters'] and not config['public_requests_enabled']):
        return {'status':'rejected','reason':'Issue author is not an authorized requester. Please email the maintainer.','paid_calls':0}
    if not config['paid_generation_enabled']:
        return {'status':'blocked','reason':'Paid generation is disabled pending provider integration, durable budget storage, source verification and an approved benchmark. No API resources used.','paid_calls':0}
    raise ValueError('No production provider adapter is activated')

if __name__=='__main__':
    result=decide(json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8')),load_config())
    Path('intake-result.json').write_text(json.dumps(result),encoding='utf-8')
    print(json.dumps(result))
