"""Build verified research packages into a staging directory, never overwrite legacy files.

Supported Markdown: headings, paragraphs, bullet lists and pipe tables. HTML is
escaped. Publication still requires rendered/visual and semantic review gates.
"""
import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from check_research import validate
from check_rendered import validate as validate_rendered

def blocks(text):
    lines=text.splitlines(); i=0
    while i<len(lines):
        line=lines[i].strip(); i+=1
        if not line: continue
        if line=='## References': break
        if line.startswith('#'):
            match=re.fullmatch(r'(#{1,3}) (.+)',line)
            if not match: raise ValueError('Unsupported heading syntax')
            yield ('heading',len(match[1]),match[2]); continue
        if line.startswith('|'):
            rows=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i+=1
            cells=[[c.strip() for c in r.strip('|').split('|')] for r in rows]
            if len(cells)<2 or not all(re.fullmatch(r':?-{3,}:?',c) for c in cells[1]): raise ValueError('Invalid pipe table')
            cells.pop(1)
            if any(len(row)!=len(cells[0]) for row in cells): raise ValueError('Inconsistent table columns')
            yield ('table',cells); continue
        if line.startswith('- '): yield ('bullet',line[2:]); continue
        paragraph=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ')):
            paragraph.append(lines[i].strip()); i+=1
        yield ('paragraph',' '.join(paragraph))

def build(folder,output,render=False):
    research=validate(folder)
    for key in ('title','slug','last_verified','category','version'):
        if not research.get(key): raise ValueError(f'missing research {key}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',research['slug']): raise ValueError('invalid slug')
    output.mkdir(parents=True,exist_ok=True)
    sources={s['id']:(i+1,s) for i,s in enumerate(research['sources'])}
    claims={c['id']:c for c in research['claims']}
    def citations(text):
        def replace(match):
            return '['+','.join(str(sources[s][0]) for s in claims[match[1]]['source_ids'])+']'
        return re.sub(r'\[claim:([a-z0-9-]+)\]',replace,text)
    references=[f"[{n}] {s['publisher']}. {s['title']}. Published {s['published']}; retrieved {s['retrieved']}. {s['url']}" for n,s in sources.values()]
    doc=Document(); normal=doc.styles['Normal']; normal.font.name='Arial'; normal.font.size=Pt(11); normal.font.color.rgb=RGBColor.from_string('404040')
    normal.paragraph_format.space_after=Pt(6)
    for section in doc.sections:
        section.top_margin=section.bottom_margin=Inches(.7); section.left_margin=section.right_margin=Inches(.75)
    for name in ['Title','Heading 1','Heading 2','Heading 3']:
        style=doc.styles[name]; style.font.name='Arial'; style.font.color.rgb=RGBColor.from_string('1B3A6B'); style.font.size=Pt(26 if name=='Title' else 13)
    doc.add_paragraph(research['title'].upper(),'Title')
    doc.add_paragraph('MBA Industry Primer | '+research['category'])
    doc.add_paragraph('Columbia Business School | Verified '+research['last_verified'])
    doc.add_paragraph('AI-assisted educational material. Sources and verification dates are listed below.')
    for name in ('primer','summary','interview'):
        rendered=[]
        for block in blocks((folder/f'{name}.md').read_text(encoding='utf-8')):
            kind=block[0]
            if kind=='table':
                rows=[[citations(cell) for cell in row] for row in block[1]]
                rendered.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table"><table>'+''.join('<tr>'+''.join(f'<{"th" if i==0 else "td"}>'+html.escape(cell)+f'</{"th" if i==0 else "td"}>' for cell in row)+'</tr>' for i,row in enumerate(rows))+'</table></div>')
                if name=='primer':
                    table=doc.add_table(rows=0,cols=len(rows[0])); table.style='Table Grid'
                    for i,row in enumerate(rows):
                        cells=table.add_row().cells
                        for cell,text in zip(cells,row):
                            cell.text=text
                            shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'1B3A6B' if i==0 else ('F5F5F5' if i%2 else 'FFFFFF')); cell._tc.get_or_add_tcPr().append(shade)
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.font.size=Pt(11)
                                    if i==0: run.bold=True; run.font.color.rgb=RGBColor(255,255,255)
                        if i==0:
                            repeat=OxmlElement('w:tblHeader'); table.rows[0]._tr.get_or_add_trPr().append(repeat)
            else:
                text=citations(block[-1]); tag=f'h{min(block[1]+1,4)}' if kind=='heading' else 'p'
                rendered.append(f'<{tag}>'+('• ' if kind=='bullet' else '')+html.escape(text)+f'</{tag}>')
                if name=='primer': doc.add_paragraph(text,'Heading '+str(min(block[1],3)) if kind=='heading' else ('List Bullet' if kind=='bullet' else None))
        rendered.append('<h2>References</h2>'+''.join('<p>'+html.escape(ref)+'</p>' for ref in references))
        nav=' · '.join(f'<a href="{n}.html">{label}</a>' for n,label in [('summary','Five-minute briefing'),('primer','Full primer'),('interview','Interview preparation')])
        page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(research['title'])+'</title><link rel="stylesheet" href="../../assets/reader.css"></head><body><header><h1>'+html.escape(research['title'])+'</h1><nav>'+nav+'</nav><p>AI-assisted · Last verified '+html.escape(research['last_verified'])+'</p></header><main>'+''.join(rendered)+'</main></body></html>'
        (output/f'{name}.html').write_text(page,encoding='utf-8')
    doc.add_heading('References',level=1)
    for ref in references: doc.add_paragraph(ref)
    docx_path=output/(research['slug']+'_primer.docx'); doc.save(docx_path)
    manifest={'slug':research['slug'],'rendered':False,'publishable':False,'requires':['semantic evidence review','visual page review'],'docx_sha256':hashlib.sha256(docx_path.read_bytes()).hexdigest()}
    if render:
        subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',str(output),str(docx_path)],check=True,timeout=120)
        pdf=docx_path.with_suffix('.pdf'); validate_rendered(docx_path,pdf)
        manifest['rendered']=True; manifest['pdf_sha256']=hashlib.sha256(pdf.read_bytes()).hexdigest()
    (output/'validation.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('folder',type=Path); p.add_argument('--output',type=Path,required=True); p.add_argument('--render',action='store_true')
    args=p.parse_args(); print(json.dumps(build(args.folder,args.output,args.render)))
