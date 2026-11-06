import json
import unittest
from pathlib import Path
from html.parser import HTMLParser
from docx import Document
ROOT=Path(__file__).resolve().parents[1]

class ReaderParser(HTMLParser):
    def __init__(self): super().__init__(); self.text=[]; self.images=0; self.tables=0
    def handle_data(self,data): self.text.append(data)
    def handle_starttag(self,tag,attrs):
        self.images+=tag=='img'; self.tables+=tag=='table'

class ReaderTests(unittest.TestCase):
    def test_original_text_tables_and_images_preserved(self):
        for entry in json.loads((ROOT/'docs/legacy-inventory.json').read_text(encoding='utf-8')):
            if entry['status']!='legacy': continue
            with self.subTest(primer=entry['id']):
                p=ReaderParser(); p.feed((ROOT/'read'/f'{entry["id"][5:]}.html').read_text(encoding='utf-8'))
                text=' '.join(p.text); doc=Document(ROOT/entry['downloads'][0])
                for paragraph in doc.paragraphs:
                    if paragraph.text: self.assertIn(paragraph.text,text)
                self.assertEqual(p.tables,len(doc.tables))
                self.assertEqual(p.images,len(doc.inline_shapes))
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                if paragraph.text: self.assertIn(paragraph.text,text)
