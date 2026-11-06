"""Conservative structural provenance gate; never claims semantic verification."""
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

def require(condition, message):
    if not condition: raise ValueError(message)

def validate(folder):
    research=json.loads((folder/'research.json').read_text(encoding='utf-8'))
    require(research.get('status')=='verified','research must be verified before publishing')
    sources=research['sources']; claims=research['claims']
    require(bool(sources) and bool(claims),'sources and claims required')
    source_map={s['id']:s for s in sources}
    require(len(source_map)==len(sources),'duplicate source IDs')
    for source in sources:
        for key in ('publisher','title','url','published','retrieved','evidence_path','sha256'):
            require(bool(source.get(key)),f'missing source {key}')
        require(source['url'].startswith('https://'),'source URL must use HTTPS')
        for field in ('published','retrieved'): dt.date.fromisoformat(source[field])
        evidence=(folder/source['evidence_path']).resolve()
        require(evidence.is_relative_to(folder.resolve()),'evidence path escapes primer')
        require(hashlib.sha256(evidence.read_bytes()).hexdigest()==source['sha256'],'evidence hash mismatch')
    ids=set()
    for claim in claims:
        require(claim['id'] not in ids,'duplicate claim ID'); ids.add(claim['id'])
        require(claim.get('verification')=='supported','unsupported claim blocks publication')
        require(bool(claim.get('source_ids')),'claim requires sources')
        require(all(s in source_map for s in claim['source_ids']),'unknown claim source')
        require(bool(claim.get('evidence_excerpt')),'claim needs evidence excerpt')
        require(any(claim['evidence_excerpt'] in (folder/source_map[s]['evidence_path']).read_text(encoding='utf-8') for s in claim['source_ids']),'excerpt absent from evidence')
        if claim.get('quantitative'):
            require(all(claim.get(k) is not None for k in ('value','unit','as_of')),'quantitative claim needs value, unit and date')
            dt.date.fromisoformat(claim['as_of'])
        require(claim.get('sections'),'claim needs dependent sections for targeted refresh')
    for name in ('primer','summary','interview'):
        content=(folder/f'{name}.md').read_text(encoding='utf-8')
        require(not re.search(r'\b(TODO|TBD|lorem ipsum)\b|\[citation needed\]',content,re.I),'placeholder text')
        refs=set(re.findall(r'\[claim:([a-z0-9-]+)\]',content))
        require(bool(refs) and refs<=ids,f'{name}: missing/unknown claim references')
        require('## References' in content,f'{name}: references section required')
        if name=='summary': require(600<=len(content.split())<=900,'brief must contain 600–900 words')
        if name=='interview': require(10<=len(re.findall(r'^### Q\d+',content,re.M))<=15,'interview requires 10–15 questions')
    return research

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    folders=sorted((root/'primers').glob('*/research.json'))
    for path in folders: validate(path.parent)
    print(f'OK provenance structure: {len(folders)} research packages; legacy documents not certified')
