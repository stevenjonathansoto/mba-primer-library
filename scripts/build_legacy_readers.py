"""Lossless text/table/image web views of legacy Word files, not verified migrations."""
import html
import json
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT=Path(__file__).resolve().parents[1]
UPDATED_READERS = {'project-finance', 'water-infrastructure'}


def legacy_learning_page(entry, title, slug, blocks):
    """Wrap the archived document in the learning reader without editing it."""
    document = html.escape('../' + entry['downloads'][0], quote=True)
    edition = html.escape(entry['updated'].removeprefix('Last Updated:').strip())
    contents = []
    brief = []
    interview = []
    full = []
    current_heading = ''
    for block in blocks:
        heading = re.match(r'<h2>(.*?)</h2>', block)
        plain_heading = re.match(r'<p>(INDUSTRY AT A GLANCE|INTERVIEW CONVERSATION STARTERS|REFERENCES)</p>', block)
        if plain_heading:
            block = f'<h2>{plain_heading[1]}</h2>' + block[plain_heading.end():]
            heading = plain_heading
        if heading:
            current_heading = html.unescape(heading[1]).strip().upper()
            anchor = f'full-section-{len(contents) + 1}'
            contents.append(f'<a href="#{anchor}">{heading[1]}</a>')
            block = block.replace('<h2>', f'<h3 id="{anchor}">', 1).replace('</h2>', '</h3>', 1)
        elif current_heading in {'INDUSTRY AT A GLANCE', 'INTERVIEW CONVERSATION STARTERS'}:
            paragraph = re.match(r'<p>.*?</p>', block, re.S)
            if paragraph:
                target = brief if current_heading == 'INDUSTRY AT A GLANCE' else interview
                target.append(paragraph[0])
        full.append(block)
    if not brief or not interview:
        raise ValueError(f'Missing opening or interview material in {slug}')
    # Wrap groups for the shared primer spacing rules while preserving every block.
    body = ''.join(full)
    body = re.sub(r'(<h3 id="full-section-\d+">)', r'</section><section>\1', '<section>' + body) + '</section>'
    body = body.removeprefix('<section></section>')
    starters = ''.join(f'<li>{paragraph}</li>' for paragraph in interview)
    feedback = f'https://github.com/stevenjonathansoto/mba-primer-library/issues/new?labels=feedback&amp;title=Feedback%3A%20{slug}'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | Energy &amp; Infrastructure Industry Library</title><link rel="stylesheet" href="../assets/reader.css"><link rel="stylesheet" href="../assets/learn.css?v=reader-spacing"></head>
<body class="legacy-learning" data-document="{document}"><a class="skip" href="#learning">Skip to content</a>
<header class="learn-header"><a class="back" href="../index.html#{entry['id']}">← Library</a><h1>{title}</h1><p class="dek">{edition} edition · Market figures reflect the original edition.</p></header>
<main id="learning" class="learning"><nav class="format-nav" aria-label="Learning formats"><a id="tab-brief" href="#brief">Brief</a><a id="tab-full" href="#full">Full primer</a><a id="tab-interview" href="#interview">Interview prep</a></nav>
<section id="brief" class="format-panel long-read" aria-labelledby="tab-brief"><h2>Industry at a glance</h2>{''.join(brief)}</section>
<section id="full" class="format-panel long-read" aria-labelledby="tab-full"><div class="reading-tools"><span>FULL PRIMER</span><a href="{document}" download>Download Word</a></div><details class="contents"><summary>Contents</summary><nav aria-label="Primer contents">{''.join(contents)}</nav></details><p id="figure-status" role="status"></p>{body}</section>
<section id="interview" class="format-panel interview" aria-labelledby="tab-interview"><h2>Interview prep</h2><p class="muted">Use these conversation starters from the {edition} edition to practice explaining an industry driver in your own words. Check the date of any figures you plan to quote.</p><ol class="legacy-starters">{starters}</ol></section></main>
<footer>Educational material · <a href="{feedback}">Report an issue</a></footer><script src="../assets/reader.js" defer></script><script src="../assets/learn.js" defer></script></body></html>'''

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
        if slug not in UPDATED_READERS:
            page = legacy_learning_page(entry, title, slug, blocks)
            (out/f'{slug}.html').write_text(page, encoding='utf-8', newline='\n')
            continue
        related=[x for x in inventory if x['id']!=entry['id'] and set(x['category'].split())&set(entry['category'].split())][:3]
        links=' · '.join(f'<a href="../index.html#{x["id"]}">{html.escape(x["title"].strip())}</a>' for x in related)
        page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | MBA Energy Library</title><link rel="stylesheet" href="../assets/reader.css"></head>
<body data-document="../{entry['downloads'][0]}"><a class="skip" href="#content">Skip to primer</a><header><nav><a href="../index.html#{entry['id']}">← Library</a> <a href="../{entry['downloads'][0]}" download>Download original Word</a></nav><p>Columbia Business School · Energy &amp; Infrastructure Club</p><h1>{title}</h1><p class="status">Legacy edition · Not independently reverified</p><p>This is an automated reading copy of the original document, dated {html.escape(entry['updated'].replace('Last Updated:','').strip())}. Its claims, forecasts and references have not passed the new verification standard. Original figures and wording are retained; consult current primary sources before relying on dated information.</p><p>AI-assisted site implementation. Last verified: not yet verified. <a href="https://github.com/stevenjonathansoto/mba-primer-library/issues/new?labels=feedback&amp;title=Feedback%3A%20{slug}">Report an issue</a></p><p id="figure-status" role="status"></p></header>
<main id="content">{''.join(blocks)}</main><footer><h2>Related industries</h2><p>{links}</p><p>Educational material, not investment advice.</p></footer><script src="../assets/reader.js" defer></script></body></html>'''
        (out/f'{slug}.html').write_text(page,encoding='utf-8',newline='\r\n')
    print('Built 23 beta learning readers and two archive readers; original Word files preserved')

if __name__=='__main__': build()
