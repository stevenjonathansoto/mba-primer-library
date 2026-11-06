"""Validate local HTML links, anchors and static assets without network access."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1]

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.ids=set(); self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: raise ValueError('duplicate HTML id: '+a['id'])
            self.ids.add(a['id'])
        for key in ('href','src'):
            if a.get(key): self.links.append(a[key])

def check():
    pages={}
    for path in [ROOT/'index.html',*sorted((ROOT/'read').rglob('*.html')),*sorted((ROOT/'learn').rglob('*.html'))]:
        parsed=Links(); parsed.feed(path.read_text(encoding='utf-8')); pages[path.resolve()]=parsed
    for path,parsed in pages.items():
        for link in parsed.links:
            url=urlsplit(link)
            if url.scheme or url.netloc: continue
            target=(path.parent/unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(ROOT) or not target.is_file(): raise ValueError(f'{path.name}: broken internal link {link}')
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                raise ValueError(f'{path.name}: broken anchor {link}')
    print(f'OK internal links and anchors across {len(pages)} HTML pages')

if __name__=='__main__': check()
