# Primer agent spec

Read `AGENTS.md` first for the primer template, card contract, and rules.

## What the agent does

1. **Create** a new primer when asked ("Create a primer on semiconductors &
   AI chips").
2. **Update** an existing primer when asked ("Update the solar primer"),
   refreshing what has gone stale without rewriting what's still right.
3. **Later, on a schedule:** find the stalest primers and open update PRs
   automatically, for human review.

Every run ends in a pull request, never a push to `main` (`main` is the live
site).

## Decision 1: where primer content lives (recommended: text source)

Today the only copy of each primer is a `.docx`. An agent can edit those with
`python-docx`, but every change is a binary blob nobody can review in a PR, and
styling drifts with each hand edit.

**Recommended:** make text the source of truth and generate the `.docx`.

```
primers/
  water-infrastructure.md        front matter + body in Markdown
  water-infrastructure/          images and any table data for that primer
scripts/
  build_primers.py               renders primers/*.md -> the .docx files
  check_site.py                  already exists
```

`build_primers.py` (python-docx) owns the template in `AGENTS.md`: title
block, Arial, navy `#1B3A6B` headings and table headers, `#404040` body,
`#F5F5F5` alternating rows, 13pt bold-caps section headings. Markdown `##`
headings become section headings; Markdown tables become styled tables. Then a
PR diff shows exactly which sentences and numbers changed.

Front matter carries everything the card needs, so cards can be generated
from it (coordinate with the UX workstream, see `docs/ux-brief.md` problem 3):

```yaml
---
title: Water Infrastructure
slug: water-infrastructure
categories: [infrastructure]          # subset of the 9 filter options
keywords: water infrastructure PFAS desalination utilities drinking water wastewater
description: The most essential and most underfunded sector in the global economy...
section_chips: [PFAS Remediation, Value Chain, Desalination, Water Utilities, Climate & Scarcity, Interview Starters]
read_time: 50
last_updated: May 2026
news_window: 2025-2026
output: water_infrastructure_primer_may2026.docx   # existing URL, never changes
---
```

**`output` stays fixed for existing primers** so shared download links keep
working (Pages has no redirects). New primers get a stable name without a
date, `<slug>_primer.docx`; freshness is shown by `last_updated`, not the
file name. Update the "File names" line in `AGENTS.md` once this lands.

**Migration (the first agent task):** extract each of the 25 `.docx` files
into `primers/<slug>.md` (section headings are the 13pt bold-caps paragraphs;
keep tables and images), rebuild with `build_primers.py`, and compare against
the original: same section list, word count within ~2%, same number of
tables and images. Commit the regenerated `.docx` only after comparing. Open
one PR for the builder plus 2-3 migrated primers first, so the template can be
reviewed before all 25 move.

If text source is rejected, the fallback is editing `.docx` files directly
with `python-docx`, keeping the same workflows below and putting a
section-by-section change summary in every PR description.

## Workflow A: create a primer

1. **Scope.** Confirm the title, the categories (from the 9), and the angle
   for an MBA reader (which roles and firms care about this industry). If the
   request is ambiguous, ask before researching.
2. **Research.** Prefer primary and authoritative sources: government and
   regulator data (EIA, IEA, FERC, DOE, the relevant ministry), company
   filings and investor decks, industry associations, and reputable financial
   press. Record the source for every figure as you go.
3. **Outline** to the template: Industry at a Glance, 5-8 topic sections,
   then the five fixed closing sections in order.
4. **Draft.** 5,000-7,000 words, 4-7 tables, dense with numbers, each one
   sourced and dated ("as of Q3 2026"). Interview starters are open,
   discussion-worthy questions, not trivia.
5. **Build** the `.docx`, add the card (or front matter), set `Last Updated`.
6. **Check.** Run `python scripts/check_site.py`; open the `.docx` and compare
   it to an existing primer.
7. **PR.** Description lists the sections, the main sources, anything you
   couldn't verify, and suggested related primers.

The two cards that already link to missing files (infrastructure investing,
semiconductors & AI chips) are good first runs of this workflow.

## Workflow B: update a primer

1. Read the whole current primer and note its `last_updated` and news window.
2. Refresh in this order: Current News & Market Dynamics (new window, e.g.
   `2026-2027`), the figures in Industry at a Glance, Key Players (M&A, exits,
   new entrants), Policy & Regulation, Future Outlook. Leave history and
   explanatory sections alone unless something is wrong.
3. Replace stale figures with sourced current ones; don't stack "as of 2025"
   and "as of 2026" numbers side by side.
4. Update REFERENCES (drop dead links, add new sources) and set `Last Updated`
   on both the primer title block and the card. Keep the output file name.
5. PR description: a section-by-section "what changed and why", and the
   claims you removed because you couldn't re-verify them.

## Quality bar (both workflows)

- No invented numbers, quotes, companies, deals, or sources. Unverifiable
  means it's cut or clearly marked as an estimate with its basis.
- Educational and neutral. No investment recommendations.
- References are consistent: publisher, title, date, URL, accessed date.
- Matches the template in `AGENTS.md` exactly; no new fonts or colors.

## Phase 2: scheduled updates

Once Workflow B works reliably by hand:

- A scheduled GitHub Action (monthly is plenty) that picks the 1-3 primers
  with the oldest `last_updated` (only those older than ~3 months), runs
  Workflow B through an LLM API with web access, rebuilds, runs
  `check_site.py`, and opens one PR per primer.
- The API key lives in GitHub Actions secrets, never in the repo (it's
  public).
- Guardrails: a cap on primers and tokens per run; if sources can't be
  fetched or checks fail, open nothing (or an issue explaining why) rather
  than a half-updated primer; never auto-merge.

## Suggested build order

1. `build_primers.py` + migrate 2-3 primers, compare output. (PR 1)
2. Migrate the rest; `check_site.py` still passes; cards generated from front
   matter if the UX work is ready. (PR 2)
3. Workflow A: write the two missing primers. (PR 3)
4. Workflow B: refresh the stalest primers (all are April/May 2026 today). (PR 4+)
5. Scheduled job. (last)
