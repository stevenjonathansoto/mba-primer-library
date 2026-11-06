"""Keep static email/issue intake in sync with centralized policy."""
import argparse
import re
from urllib.parse import quote
from check_config import ROOT,load_config

def sync(check=False):
    config=load_config()
    if config['public_requests_enabled']:
        url='https://github.com/stevenjonathansoto/mba-primer-library/issues/new?labels='+quote(config['notifications']['request_label'])
    else:
        url='mailto:'+config['maintainer_email']+'?subject=Primer%20Request&amp;body='+quote('Industry:\nSpecific focus:\nRecruiting relevance:\nAdditional context:\n')
    path=ROOT/'index.html'; old=path.read_text(encoding='utf-8')
    new,count=re.subn(r'<a href="[^"]+" class="btn-request">',lambda _:f'<a href="{url}" class="btn-request">',old)
    if count!=1: raise ValueError('Expected exactly one Request a Primer link')
    if check and new!=old: raise ValueError('Intake link differs from config; run scripts/sync_intake_links.py')
    if not check: path.write_text(new,encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); args=p.parse_args(); sync(args.check)
