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
            return f'<a class="claim" href="#source-{m[1]}" aria-label="Evidence for {m[1]}">[{m[1]}]</a>'
        return re.sub(r'\[([a-z-]+)\]',citation,html.escape(text))
    def table(rows):
        return '<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable analysis table"><table>'+''.join('<tr>'+''.join(f'<{"th scope=col" if i==0 else "td"}>{rich(cell)}</{"th" if i==0 else "td"}>' for cell in row)+'</tr>' for i,row in enumerate(rows))+'</table></div>'
    brief_parts=[]
    for title,body in data['brief']:
        if body.startswith('1. '):
            numbered,tail=body.split('For banking',1)
            items=re.split(r'\b[1-5]\. ',numbered)[1:]
            text='<ol>'+''.join('<li>'+rich(item.strip())+'</li>' for item in items)+'</ol><p>'+rich('For banking'+tail)+'</p>'
        else:text='<p>'+rich(body)+'</p>'
        brief_parts.append(f'<section><h3>{html.escape(title)}</h3>{text}</section>')
    brief=''.join(brief_parts)
    full=''.join(f'<section><h3 id="full-{s["id"]}">{html.escape(s["title"])}</h3>'+''.join('<p>'+rich(p)+'</p>' for p in s['paragraphs'])+(table(s['table']) if 'table' in s else '')+'</section>' for s in data['full'])
    toc=''.join(f'<a href="#full-{s["id"]}">{html.escape(s["title"])}</a>' for s in data['full'])
    questions=''.join(f'<details class="question"><summary><span>Q{i:02} </span>{html.escape(q)}</summary><div><p>{rich(a)}</p><p class="followup"><strong>Go deeper:</strong> {html.escape(f)}</p></div></details>' for i,(q,a,f) in enumerate(data['questions'],1))
    evidence=''.join(f'<details id="source-{s["id"]}" class="evidence"><summary>{html.escape(s["publisher"])} · {html.escape(s["title"])}</summary><p><strong>Supported assertion:</strong> {html.escape(s["claim"])}</p><p><strong>Evidence excerpt:</strong> “{html.escape(s["excerpt"])}”</p><p>Source date: {html.escape(s["date"] or "Not stated on reviewed page")}. Reviewed: {data["reviewed"]}. Affects: {", ".join(s["sections"])}.</p><a href="{html.escape(s["url"],quote=True)}">Open primary source ↗</a></details>' for s in data['sources'])
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']} · Learn | MBA Energy Library</title><link rel="stylesheet" href="../assets/reader.css"><link rel="stylesheet" href="../assets/learn.css"></head><body><a class="skip" href="#learning">Skip to learning formats</a>
<header class="learn-header"><nav><a href="../index.html#card-{slug}">← All industries</a><a href="{slug}.docx" download>Download this primer ↗</a></nav><p class="eyebrow">COLUMBIA BUSINESS SCHOOL · ENERGY &amp; INFRASTRUCTURE CLUB</p><h1>{data['title']}</h1><p class="dek">The economics of essential service: capital recovery, operating performance and investment judgment.</p><div class="chips"><span>Infrastructure</span><span>Utilities</span><span>Project finance</span></div><p class="review-meta">Sources reviewed {data['reviewed']} · {len(sources)} primary sources · <a href="#evidence">Inspect evidence</a></p><p class="related-top">Related: <a href="../read/project-finance.html">Project Finance</a> · <a href="../read/private-equity-in-energy-infrastructure.html">Infrastructure PE</a></p></header>
<main id="learning" class="learning"><details class="scope-note"><summary>About this edition and its sources</summary><p>{html.escape(data['scope'])} <a href="../read/{slug}.html">Read the archived May 2026 edition</a>.</p></details>
<nav class="format-nav" aria-label="Learning formats"><a id="tab-brief" href="#brief">Quick Brief <small>5-minute overview</small></a><a id="tab-full" href="#full">Full Primer <small>Economics &amp; analysis</small></a><a id="tab-interview" href="#interview">Interview Prep <small>{len(data['questions'])} model answers</small></a></nav>
<section id="brief" class="format-panel" aria-labelledby="tab-brief"><div class="panel-heading"><p class="eyebrow">01 / GET ORIENTED</p><h2>The industry in five minutes</h2></div><div class="takeaway"><strong>The central question</strong><p>How does an essential service become reliable cash flow—and at what cost to customers and investors?</p></div>{brief}<div class="flow" aria-label="Simplified water value chain"><span>Source</span><b aria-hidden="true">→</b><span>Treat</span><b aria-hidden="true">→</b><span>Distribute</span><b aria-hidden="true">→</b><span>Collect &amp; reuse</span></div><p class="next"><a href="#full">Explore the full primer →</a><a href="#interview">Prepare for the conversation →</a></p></section>
<section id="full" class="format-panel" aria-labelledby="tab-full"><div class="panel-heading"><p class="eyebrow">02 / BUILD DEPTH</p><h2>Water infrastructure economics</h2><p>Source-linked facts, explicit assumptions and worked financial examples.</p></div><details class="contents"><summary>Jump to a section</summary><nav aria-label="Primer contents">{toc}</nav></details>{full}<p><a href="{slug}.docx" download>Download this edition as Word</a></p></section>
<section id="interview" class="format-panel" aria-labelledby="tab-interview"><div class="panel-heading"><p class="eyebrow">03 / PREPARE YOUR ANSWERS</p><h2>From industry knowledge to investment judgment</h2><p>Open a question for a model answer, its assumptions and a follow-up. Questions are editorial examples, not attributed to employers.</p></div>{questions}<h3>Networking and coffee chat questions</h3><ul>{''.join('<li>'+html.escape(q)+'</li>' for q in data['networking'])}</ul></section>
<section id="evidence" class="evidence-register" aria-labelledby="evidence-heading"><h2 id="evidence-heading">Sources and evidence</h2><p>Inline references link to the specific supported assertion below. Worked examples and investment frameworks are editorial analysis. Review dates record the source check, not a guarantee that policy or company facts remain unchanged.</p>{evidence}</section></main><footer><p>AI-assisted educational material, not investment advice. <a href="https://github.com/stevenjonathansoto/mba-primer-library/issues/new?labels=feedback&amp;title=Water%20learning%20edition">Report an issue</a></p></footer><script src="../assets/learn.js" defer></script></body></html>'''
    out=ROOT/'learn';out.mkdir(exist_ok=True)
    (out/f'{slug}.html').write_text(page,encoding='utf-8',newline='\n')
    if word: build_word(data,out/f'{slug}.docx')

def build_word(data,path):
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc=Document()
    normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(11)
    normal.paragraph_format.space_after=Pt(7)
    for section in doc.sections:
        section.top_margin=section.bottom_margin=Inches(.7)
        section.left_margin=section.right_margin=Inches(.75)
    for name in ['Title','Heading 1','Heading 2']:
        style=doc.styles[name];style.font.name='Arial';style.font.size=Pt(26 if name=='Title' else 13);style.font.color.rgb=RGBColor.from_string('1B3A6B')
        for border in style.element.findall('.//'+qn('w:pBdr')):border.getparent().remove(border)
    doc.add_paragraph('Water Infrastructure','Title')
    doc.add_paragraph('MBA Industry Primer | Infrastructure and Utilities')
    doc.add_paragraph('Columbia Business School | Sources reviewed '+data['reviewed'])
    doc.add_paragraph(data['scope'])
    for s in data['full']:
        doc.add_heading(s['title'],1)
        for p in s['paragraphs']:doc.add_paragraph(p)
        if 'table' in s:
            t=doc.add_table(rows=0,cols=len(s['table'][0]));t.style='Table Grid'
            for i,row in enumerate(s['table']):
                cells=t.add_row().cells
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
