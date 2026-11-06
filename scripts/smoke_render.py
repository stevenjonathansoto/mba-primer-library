"""CI integration fixture: exercise a real renderer without publishing sample content."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_research_builder import ResearchBuilderTests
from build_primers import build
from check_rendered import validate as validate_rendered
import fitz

root=Path('work/render-smoke'); root.mkdir(parents=True,exist_ok=True)
folder=ResearchBuilderTests().fixture(root)
manifest=build(folder,root/'staged',render=True)
assert manifest['rendered'] and not manifest['publishable']
pdf=fitz.open(root/'staged/synthetic_primer.pdf')
for number,page in enumerate(pdf,1): page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(root/f'page-{number}.png')
oversized=fitz.open()
for _ in range(11): oversized.insert_pdf(pdf,from_page=0,to_page=0)
overflow=root/'overflow.pdf'; oversized.save(overflow); oversized.close()
try:
    validate_rendered(root/'staged/synthetic_primer.docx',overflow)
except AssertionError as error:
    assert 'limit is 10' in str(error)
else:
    raise AssertionError('Eleven-page PDF was incorrectly accepted')
print('Real Word-to-PDF rendering passed; sample remains unpublished')
