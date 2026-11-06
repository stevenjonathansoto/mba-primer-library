"""Lossless text/table/image web views of legacy Word files, not verified migrations."""
import base64
import html
import json
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT=Path(__file__).resolve().parents[1]

def paragraph_html(p,document):
    text=html.escape(p.text)
    sizes=[r.font.size.pt for r in p.runs if r.font.size]
    heading=bool(text) and ((sizes and max(sizes)>=13 and p.text.upper()==p.text) or (p.style is not None and p.style.name.startswith('Heading')))
    tag='h2' if heading else 'p'
    rendered=f'<{tag}>{text}</{tag}>' if text else ''
    for blip in p._p.xpath('.//a:blip'):
        rid=blip.get(qn('r:embed'))
        if rid:
            part=document.part.related_parts[rid]
            if part.content_type not in ('image/png','image/jpeg','image/gif'):
                raise ValueError(f'Unsupported legacy image: {part.content_type}')
            part_name=str(part.partname).lstrip('/')
            rendered+=f'<figure><img data-docx-part="{html.escape(part_name)}" data-mime="{part.content_type}" alt="Legacy document figure; see adjacent caption and original Word document"><noscript>Enable JavaScript to view this figure or download the original Word document.</noscript></figure>'
    return rendered

def build():
    inventory=json.loads((ROOT/'docs/legacy-inventory.json').read_text(encoding='utf-8'))
    out=ROOT/'read'; out.mkdir(exist_ok=True)
    for entry in inventory:
        if entry['status']!='legacy': continue
        doc=Document(ROOT/entry['downloads'][0]); blocks=[]
        for child in doc.element.body.iterchildren():
            if child.tag==qn('w:p'): blocks.append(paragraph_html(Paragraph(child,doc),doc))
            elif child.tag==qn('w:tbl'):
                table=Table(child,doc); rows=[]
                for i,row in enumerate(table.rows):
                    tag='th' if i==0 else 'td'
                    cells=''.join(f'<{tag}'+(' scope="col"' if i==0 else '')+'>'+''.join(paragraph_html(p,doc) for p in cell.paragraphs)+f'</{tag}>' for cell in row.cells)
                    rows.append('<tr>'+cells+'</tr>')
                blocks.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table"><table>'+''.join(rows)+'</table></div>')
        title=html.escape(entry['title'].strip()); slug=entry['id'][5:]
        related=[x for x in inventory if x['id']!=entry['id'] and set(x['category'].split())&set(entry['category'].split())][:3]
        links=' · '.join(f'<a href="../index.html#{x["id"]}">{html.escape(x["title"].strip())}</a>' for x in related)
        page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | MBA Energy Library</title><link rel="stylesheet" href="../assets/reader.css"></head>
<body data-document="../{entry['downloads'][0]}"><a class="skip" href="#content">Skip to primer</a><header><nav><a href="../index.html#{entry['id']}">← Library</a> <a href="../{entry['downloads'][0]}" download>Download original Word</a></nav><p>Columbia Business School · Energy &amp; Infrastructure Club</p><h1>{title}</h1><p class="status">Legacy edition · Not independently reverified</p><p>This is an automated reading copy of the original document, dated {html.escape(entry['updated'].replace('Last Updated:','').strip())}. Its claims, forecasts and references have not passed the new verification standard. Original figures and wording are retained; consult current primary sources before relying on dated information.</p><p>AI-assisted site implementation. Last verified: not yet verified. <a href="https://github.com/stevenjonathansoto/mba-primer-library/issues/new?labels=feedback&amp;title=Feedback%3A%20{slug}">Report an issue</a></p><p id="figure-status" role="status"></p></header>
<main id="content">{''.join(blocks)}</main><footer><h2>Related industries</h2><p>{links}</p><p>Educational material, not investment advice.</p></footer><script src="../assets/reader.js" defer></script></body></html>'''
        (out/f'{slug}.html').write_text(page,encoding='utf-8',newline='\r\n')
    print('Built 25 legacy reading copies; no documents reverified or overwritten')

if __name__=='__main__': build()
