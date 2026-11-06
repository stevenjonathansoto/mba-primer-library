"""Validate a Word document and its freshly rendered PDF; requires PyMuPDF/python-docx.

Caller must render this exact DOCX immediately before invocation. Page images
still require visual review; geometry checks cannot establish perfect layout.
"""
import argparse
from pathlib import Path

def validate(docx_path,pdf_path):
    import fitz
    from docx import Document
    doc=Document(docx_path)
    assert pdf_path.stat().st_mtime>=docx_path.stat().st_mtime,'PDF predates Word file'
    normal=doc.styles['Normal'].font.size
    assert normal is not None and normal.pt>=11,'Normal body font must be explicit and at least 11pt'
    paragraphs=list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells: paragraphs.extend(cell.paragraphs)
    for paragraph in paragraphs:
        for run in paragraph.runs:
            if not run.text.strip(): continue
            size=run.font.size or paragraph.style.font.size or normal
            assert size.pt>=11,'Text below 11pt'
    pdf=fitz.open(pdf_path)
    assert 1<=len(pdf)<=10,f'{len(pdf)} rendered pages; limit is 10'
    for page in pdf:
        assert page.get_text().strip(),'empty rendered page'
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    assert fitz.Rect(span['bbox']) in page.rect,'text extends beyond page'
    print(f'OK {len(pdf)} rendered pages; visual clipping/table review still required')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('docx',type=Path); p.add_argument('pdf',type=Path)
    args=p.parse_args(); validate(args.docx,args.pdf)
