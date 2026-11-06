"""Bounded free source reachability checks; failures are review signals, not fact verdicts."""
import argparse
import concurrent.futures
import datetime as dt
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def public_url(url):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None,443):
        raise ValueError('only public HTTPS sources allowed')
    addresses=socket.getaddrinfo(parsed.hostname,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('non-public source address')
    return url

class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        public_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def probe(url):
    try:
        public_url(url)
        request=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'MBA-Library-Source-Monitor/1.0'})
        with urllib.request.build_opener(PublicRedirect()).open(request,timeout=8) as response:
            return {'url':url,'status':'reachable','http_status':response.status}
    except urllib.error.HTTPError as error:
        return {'url':url,'status':'missing' if error.code in (404,410) else 'unknown','http_status':error.code}
    except (ValueError,OSError) as error:
        return {'url':url,'status':'unknown','reason':type(error).__name__}

def urls():
    found=set()
    for path in ROOT.glob('*.docx'):
        with zipfile.ZipFile(path) as archive:
            for name in ('word/document.xml','word/_rels/document.xml.rels'):
                if name in archive.namelist():
                    text=archive.read(name).decode('utf-8')
                    found.update(re.findall(r'https://[^\s<>"\']+',text))
    # OOXML namespace/schema URLs are not bibliographic references.
    return sorted(u.replace('&amp;','&').rstrip('.,);') for u in found if 'schemas.' not in u and 'www.w3.org/' not in u and 'purl.org/' not in u)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--limit',type=int,default=30); p.add_argument('--offset',type=int,default=0); p.add_argument('--rotate',action='store_true')
    args=p.parse_args(); all_urls=urls(); limit=min(max(args.limit,0),100)
    if args.rotate and all_urls: args.offset=(dt.date.today().toordinal()//7*limit)%len(all_urls)
    batch=(all_urls+all_urls)[args.offset:args.offset+min(limit,len(all_urls))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(probe,batch))
    out=ROOT/'work/source-reachability.json'; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'total_unique_urls':len(all_urls),'offset':args.offset,'checked':len(results),'results':results},indent=2)+'\n',encoding='utf-8')
    print(f'Checked {len(results)} of {len(all_urls)} source URLs; results: {out}')
