import json
import re
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, text): self.parts.append(text)

class LearningPreviewTests(unittest.TestCase):
    def test_content_lengths_and_draft_status(self):
        data=json.loads((ROOT/'content/water-infrastructure.json').read_text(encoding='utf-8'))
        self.assertEqual(data['status'], 'source-reviewed-learning-edition')
        words=sum(len(p.split()) for _,p in data['brief'])
        self.assertTrue(600 <= words <= 900, words)
        self.assertTrue(10 <= len(data['questions']) <= 15)
        self.assertTrue(all(len(answer.split()) >= 30 for _,answer,_ in data['questions']))

    def test_full_document_preserved_with_unique_navigation_targets(self):
        data=json.loads((ROOT/'content/water-infrastructure.json').read_text(encoding='utf-8'))
        page=(ROOT/'learn/water-infrastructure.html').read_text(encoding='utf-8')
        b=Text(); b.feed(page)
        self.assertEqual(len(data['sources']),6)
        sources={s['id'] for s in data['sources']}
        for section in data['full']:
            for paragraph in section['paragraphs']:
                self.assertTrue(set(re.findall(r'\[([a-z-]+)\]',paragraph)) <= sources)
        ids=re.findall(r'\bid="([^"]+)"',page)
        self.assertEqual(len(ids),len(set(ids)))
        for target in re.findall(r'href="#([^"]+)"',page): self.assertIn(target,ids)
        self.assertIn('Sources reviewed 2026-11-06', page)
        self.assertIn('../read/water-infrastructure.html',page)

if __name__ == '__main__': unittest.main()
