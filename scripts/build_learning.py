"""Render reusable static learning pages from source-linked editorial content."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def build(path,word=False):
    data=json.loads(path.read_text(encoding='utf-8')); slug=path.stem
    sources={s['id']:s for s in data['sources']}
    def rich(text):
        def citation(m):
            if m[1] not in sources: raise ValueError('Unknown source claim '+m[1])
            return f'<a class="claim" href="#source-{m[1]}" aria-label="Evidence for {m[1]}">[{list(sources).index(m[1])+1}]</a>'
        return re.sub(r'\[([a-z-]+)\]',citation,html.escape(text))
    def table(rows):
        return '<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable analysis table"><table>'+''.join('<tr>'+''.join(f'<{"th scope=col" if i==0 else "td"}>{rich(cell)}</{"th" if i==0 else "td"}>' for cell in row)+'</tr>' for i,row in enumerate(rows))+'</table></div>'
    full=''.join(f'<section><h3 id="full-{s["id"]}">{html.escape(s["title"])}</h3>'+''.join('<p>'+rich(p)+'</p>' for p in s['paragraphs'])+(table(s['table']) if 'table' in s else '')+'</section>' for s in data['full'])
    toc=''.join(f'<a href="#full-{s["id"]}">{html.escape(s["title"])}</a>' for s in data['full'])
    question_items=[]
    for i,(q,a,f) in enumerate(data['questions']):
        lead=data.get('question_takeaways',['']*len(data['questions']))[i]
        question_items.append(f'<details class="question"><summary>{html.escape(q)}</summary><div><p class="answer-lead">{rich(lead)}</p><p>{rich(a)}</p><p class="followup"><strong>Follow-up:</strong> {html.escape(f)}</p></div></details>')
    groups=data.get('question_groups',[{'title':'Questions','questions':list(range(len(question_items)))}])
    indices=[i for group in groups for i in group['questions']]
    if sorted(indices)!=list(range(len(question_items))):raise ValueError('Question groups must contain each question exactly once')
    questions=''.join('<section class="question-group"><h3>'+html.escape(group['title'])+'</h3>'+''.join(question_items[i] for i in group['questions'])+'</section>' for group in groups)
    evidence=''.join(f'<details id="source-{s["id"]}" class="evidence"><summary>{html.escape(s["publisher"])} · {html.escape(s["title"])}</summary><p><strong>Supported assertion:</strong> {html.escape(s["claim"])}</p><p><strong>Evidence excerpt:</strong> “{html.escape(s["excerpt"])}”</p><p>Source date: {html.escape(s["date"] or "Not stated on reviewed page")}. Reviewed: {data["reviewed"]}. Affects: {", ".join(s["sections"])}.</p><a href="{html.escape(s["url"],quote=True)}">Open primary source ↗</a></details>' for s in data['sources'])
    from learning_layout import page as render_page
    page=render_page(data,slug,full,toc,questions,evidence,rich)
    out=ROOT/'learn';out.mkdir(exist_ok=True)
    (out/f'{slug}.html').write_text(page,encoding='utf-8',newline='\n')
    if word: build_word(data,out/f'{slug}.docx')

def build_word(data,path):
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc=Document()
    for section in doc.sections:
        section.page_width=Inches(8.5);section.page_height=Inches(11)
    normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(11)
    normal.paragraph_format.space_after=Pt(7)
    for section in doc.sections:
        section.top_margin=section.bottom_margin=Inches(.7)
        section.left_margin=section.right_margin=Inches(.75)
    for name in ['Title','Heading 1','Heading 2']:
        style=doc.styles[name];style.font.name='Arial';style.font.size=Pt(26 if name=='Title' else 13);style.font.color.rgb=RGBColor.from_string('1B3A6B')
        for border in style.element.findall('.//'+qn('w:pBdr')):border.getparent().remove(border)
    doc.styles['Title'].font.color.rgb=RGBColor(0,0,0)
    doc.add_paragraph(data['title'],'Title')
    doc.add_paragraph('MBA Industry Primer | '+data.get('category','Infrastructure and Utilities'))
    doc.add_paragraph('Columbia Business School | Sources reviewed '+data['reviewed'])
    doc.add_paragraph(data['scope'])
    for s in data['full']:
        doc.add_heading(s['title'],1)
        for p in s['paragraphs']:doc.add_paragraph(p)
        if 'table' in s:
            t=doc.add_table(rows=0,cols=len(s['table'][0]));t.style='Table Grid'
            for i,row in enumerate(s['table']):
                cells=t.add_row().cells
                for cell in cells:
                    for side in ['top','left','bottom','right']:
                        borders=cell._tc.get_or_add_tcPr().find(qn('w:tcBorders'))
                        if borders is None:
                            borders=OxmlElement('w:tcBorders');cell._tc.get_or_add_tcPr().append(borders)
                        edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
                    if i>0 and i%2==0:
                        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F5F5F5');cell._tc.get_or_add_tcPr().append(shade)
                for cell,value in zip(cells,row):
                    cell.text=value
                    if i==0:
                        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'1B3A6B');cell._tc.get_or_add_tcPr().append(shade)
                        for run in cell.paragraphs[0].runs:run.font.color.rgb=RGBColor(255,255,255);run.bold=True
                if i==0:
                    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    doc.add_heading('Sources and evidence',1)
    for s in data['sources']:
        doc.add_paragraph('['+s['id']+'] '+s['publisher']+'. '+s['title']+'. Source date: '+(s['date'] or 'not stated')+'. Reviewed '+data['reviewed']+'. '+s['url'])
        doc.add_paragraph('Supports: '+s['claim'])
    doc.add_paragraph('AI-assisted educational material. Hypothetical examples are not forecasts or investment advice.')
    doc.save(path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--word',action='store_true');args=p.parse_args()
    for path in sorted((ROOT/'content').glob('*.json')):build(path,args.word)
