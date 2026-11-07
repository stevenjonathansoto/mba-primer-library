"""A quiet reading layout: brief first, detail only when requested."""
import html
from learning_visuals import VISUALS
from meeting_brief import BRIEFS, render_meeting_brief
from urllib.parse import quote

def page(data,slug,full,toc,questions,evidence,rich):
    intro,models,drivers,*additional,lesson=data['brief']
    def lines(text):
        result=[]
        for item in text.split('|'):
            label,separator,body=item.strip().partition(' — ')
            result.append('<li><strong>'+html.escape(label)+'</strong>'+(' — '+rich(body) if separator else '')+'</li>')
        return ''.join(result)
    visual_config=data.get('visuals',{})
    intro_visual=VISUALS.get(visual_config.get('intro'),'')
    correction_title=quote(data['title']+' learning edition')
    meeting = render_meeting_brief(slug) if slug in BRIEFS else ''
    if meeting:
        meeting += '<h2 class="meeting-more">How it works</h2>'
    depth=''
    for title,body in additional:
        visual=VISUALS.get(visual_config.get('sections',{}).get(title),'')
        depth+='<section class="brief-section"><h2>'+html.escape(title)+'</h2>'+visual+'<ul class="driver-list">'+lines(body)+'</ul></section>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(data['title'])} | Energy Library</title><link rel="stylesheet" href="../assets/reader.css"><link rel="stylesheet" href="../assets/learn.css?v=meeting-brief"></head><body><a class="skip" href="#learning">Skip to content</a>
<header class="learn-header"><a class="back" href="../index.html#card-{slug}">← Library</a><h1>{html.escape(data['title'])}</h1><p class="dek">{html.escape(data.get('subtitle','How the industry works. What drives its returns.'))}</p></header>
<main id="learning" class="learning"><nav class="format-nav" aria-label="Learning formats"><a id="tab-brief" href="#brief">Brief</a><a id="tab-full" href="#full">Full primer</a><a id="tab-interview" href="#interview">Interview prep</a></nav>
<section id="brief" class="format-panel" aria-labelledby="tab-brief">{meeting or '<p class="reading-time">5 MIN READ</p>'}<p class="brief-intro">{rich(intro[1])}</p>{intro_visual}<div class="brief-layout"><div><section class="brief-section"><h2>{models[0]}</h2><ul class="model-list">{lines(models[1])}</ul></section><section class="brief-section"><h2>{drivers[0]}</h2><ul class="driver-list">{lines(drivers[1])}</ul></section></div></div><div class="brief-depth">{depth}</div><div class="remember"><h2>{lesson[0]}</h2><p>{rich(lesson[1])}</p></div></section>
<section id="full" class="format-panel long-read" aria-labelledby="tab-full"><div class="reading-tools"><span>FULL PRIMER</span><a href="{slug}.docx" download>Download Word</a></div><details class="contents"><summary>Contents</summary><nav aria-label="Primer contents">{toc}</nav></details>{full}</section>
<section id="interview" class="format-panel interview" aria-labelledby="tab-interview"><h2>Interview prep</h2><p class="muted">Start with industry basics, then explore business economics and investment judgment.</p>{questions}<details class="networking"><summary>Coffee chat questions</summary><ul>{''.join('<li>'+html.escape(q)+'</li>' for q in data['networking'])}</ul></details></section>
<details id="evidence" class="evidence-register"><summary>Sources &amp; edition notes <span>{len(data['sources'])} sources</span></summary><p>Sources reviewed {data['reviewed']}. Examples are hypothetical; investment frameworks are editorial analysis.</p>{evidence}<p>{html.escape(data['scope'])}</p></details></main><footer>Educational material · AI-assisted · <a href="https://github.com/stevenjonathansoto/mba-primer-library/issues/new?labels=feedback&amp;title={correction_title}">Report a correction</a></footer><script src="../assets/learn.js" defer></script></body></html>'''
