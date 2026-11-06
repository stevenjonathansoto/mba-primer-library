import json
import re
import unittest
from pathlib import Path
from docx import Document

ROOT=Path(__file__).resolve().parents[1]

class ProjectLearningTests(unittest.TestCase):
    def test_project_cross_format_integrity(self):
        data=json.loads((ROOT/'content/project-finance.json').read_text(encoding='utf-8'))
        page=(ROOT/'learn/project-finance.html').read_text(encoding='utf-8')
        doc=Document(ROOT/'learn/project-finance.docx')
        paragraphs={p.text for p in doc.paragraphs}
        self.assertIn('Project Finance',paragraphs)
        self.assertNotIn('Water Infrastructure',paragraphs)
        for section in data['full']:
            for paragraph in section['paragraphs']:self.assertIn(paragraph,paragraphs)
        tables=[[[c.text for c in row.cells] for row in t.rows] for t in doc.tables]
        self.assertEqual(tables,[s['table'] for s in data['full'] if 'table' in s])
        source_ids={s['id'] for s in data['sources']}
        texts=[p for _,p in data['brief']]+[p for s in data['full'] for p in s['paragraphs']]+[a for _,a,_ in data['questions']]
        for text in texts:self.assertTrue(set(re.findall(r'\[([a-z-]+)\]',text))<=source_ids)
        self.assertEqual(sorted(i for g in data['question_groups'] for i in g['questions']),list(range(12)))
        self.assertEqual(len(data['question_takeaways']),len(data['questions']))
        self.assertTrue(700<=sum(len(p.split()) for _,p in data['brief'])<=1100)
        self.assertNotIn('Follow the water',page)
        self.assertIn('title=Project%20Finance%20learning%20edition',page)
        self.assertNotIn('../read/project-finance.html',page)

if __name__=='__main__':unittest.main()
