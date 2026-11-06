"""Render and validate the actual learning edition, retaining every page for QA."""
import subprocess
from pathlib import Path
import fitz
from check_rendered import validate
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'work/learning-render';out.mkdir(parents=True,exist_ok=True)
for docx in (ROOT/'learn').glob('*.docx'):
    subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',str(out),str(docx)],check=True,timeout=120)
    pdf=out/(docx.stem+'.pdf');validate(docx,pdf)
    with fitz.open(pdf) as document:
        for i,page in enumerate(document):page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(out/f'{docx.stem}-page-{i+1}.png')
