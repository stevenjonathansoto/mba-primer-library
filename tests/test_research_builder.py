import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from docx import Document
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_research import validate
from build_primers import build,blocks

class ResearchBuilderTests(unittest.TestCase):
    def fixture(self,root):
        folder=root/'synthetic'; folder.mkdir()
        evidence='Synthetic test evidence: illustrative revenue equals price times volume.'
        (folder/'evidence.txt').write_text(evidence,encoding='utf-8')
        research={'title':'Synthetic test fixture','slug':'synthetic','category':'Test','version':1,'last_verified':'2026-11-05','status':'verified','sources':[{'id':'s1','publisher':'Test fixture','title':'Synthetic evidence','url':'https://example.com/test','published':'2026-01-01','retrieved':'2026-11-05','evidence_path':'evidence.txt','sha256':hashlib.sha256(evidence.encode()).hexdigest()}],'claims':[{'id':'revenue','verification':'supported','source_ids':['s1'],'evidence_excerpt':evidence,'sections':['economics']}]}
        (folder/'research.json').write_text(json.dumps(research),encoding='utf-8')
        primer='\n'.join('## '+heading+'\nSynthetic explanation. [claim:revenue]\n' for heading in ['Executive summary','Fundamentals and value chain','Market landscape','Industry economics','Investment and financing','Policy and outlook','Recruiting applications'])
        (folder/'primer.md').write_text(primer+'\n| Driver | Meaning |\n| --- | --- |\n| Price | Hypothetical |\n\n## References\n',encoding='utf-8')
        summary='\n'.join('## '+heading+'\n'+' '.join(['Synthetic']*85)+' [claim:revenue]\n' for heading in ['Overview','Value chain','Business models','Financial drivers','Market dynamics','Trends','Recruiting takeaways'])
        (folder/'summary.md').write_text(summary+'\n## References\n',encoding='utf-8')
        interview='\n'.join(f'### Q{i} Illustrative question\n'+' '.join(['Synthetic']*32)+' [claim:revenue]\n' for i in range(1,11))
        interview+='\n'.join('## '+heading+'\nSynthetic explanation. [claim:revenue]\n' for heading in ['Key concepts','Industry debates','Networking questions','Misconceptions'])
        (folder/'interview.md').write_text(interview+'\n## References\n',encoding='utf-8')
        return folder

    def test_three_outputs_and_staging_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); folder=self.fixture(root); out=root/'staged'
            manifest=build(folder,out)
            self.assertFalse(manifest['publishable']); self.assertFalse(manifest['rendered'])
            for name in ('primer','summary','interview'): self.assertTrue((out/f'{name}.html').exists())
            doc=Document(out/'synthetic_primer.docx')
            self.assertEqual(doc.styles['Normal'].font.size.pt,11)
            self.assertEqual(len(doc.tables),1)
            self.assertIn('[1]',(out/'primer.html').read_text(encoding='utf-8'))

    def test_tampered_or_unsupported_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            folder=self.fixture(Path(d)); (folder/'evidence.txt').write_text('tampered')
            with self.assertRaisesRegex(ValueError,'hash mismatch'): validate(folder)

    def test_unknown_claim_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            folder=self.fixture(Path(d)); p=folder/'primer.md'; p.write_text(p.read_text().replace('claim:revenue','claim:invented'))
            with self.assertRaisesRegex(ValueError,'unknown claim'): validate(folder)

    def test_malformed_table_blocks(self):
        with self.assertRaises(ValueError): list(blocks('| A | B |\n| --- | --- |\n| bad |'))

    def test_missing_required_sections_block(self):
        with tempfile.TemporaryDirectory() as d:
            folder=self.fixture(Path(d)); p=folder/'primer.md'
            p.write_text(p.read_text().replace('## Policy and outlook','## Other topic'))
            with self.assertRaisesRegex(ValueError,'missing required topic'): validate(folder)
