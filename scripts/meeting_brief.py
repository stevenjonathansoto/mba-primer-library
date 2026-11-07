"""Render the same quick-reference briefing for each industry."""

from html import escape
import json
from pathlib import Path


BRIEFS = json.loads(
    (Path(__file__).resolve().parents[1] / "docs" / "meeting-briefs.json")
    .read_text(encoding="utf-8")
)


def render_meeting_brief(slug):
    brief = BRIEFS[slug]
    figures = "".join(
        f'<li><strong>{escape(value)}</strong><span>{escape(label)}</span></li>'
        for value, label in brief["figures"]
    )
    trends = "".join(
        f'<li><strong>{escape(label)}.</strong> {escape(text)}</li>'
        for label, text in brief["trends"]
    )
    players, roles = map(escape, brief["players"])
    return f'''<div class="meeting-brief">
  <p class="meeting-summary">{escape(brief["summary"])}</p>
  <section><h2>Key figures</h2><ul class="meeting-figures">{figures}</ul></section>
  <section><h2>What to watch</h2><ul class="meeting-trends">{trends}</ul></section>
  <section><h2>Who matters</h2><p><strong>{players}.</strong> {roles}</p></section>
  <section class="meeting-question"><h2>Ask in a meeting</h2><p>{escape(brief["question"])}</p></section>
</div>'''
