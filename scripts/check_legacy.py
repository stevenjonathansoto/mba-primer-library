"""Verify the original download and anchor compatibility contract."""
import hashlib
import json
import zipfile
from pathlib import Path
from check_site import CardParser

ROOT = Path(__file__).resolve().parents[1]

def check():
    inventory = json.loads((ROOT/'docs/legacy-inventory.json').read_text(encoding='utf-8'))
    parser = CardParser()
    parser.feed((ROOT/'index.html').read_text(encoding='utf-8'))
    cards = {c['id']:c for c in parser.cards}
    for entry in inventory:
        assert entry['id'] in cards, f"Lost anchor: {entry['id']}"
        for record in entry['files']:
            if not record['exists']:
                continue
            path = ROOT/record['path']
            assert path.exists(), f'Lost download: {path}'
            assert record['path'] in cards[entry['id']]['downloads'], f'Unlinked download: {path}'
            assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], f'Legacy file changed without audited migration: {path}'
            with zipfile.ZipFile(path) as archive:
                assert archive.testzip() is None, f'Corrupt Word archive: {path}'
                assert 'word/document.xml' in archive.namelist(), f'Invalid Word document: {path}'
    print('OK legacy anchors, links, checksums and Word archive integrity')

if __name__ == '__main__':
    check()
