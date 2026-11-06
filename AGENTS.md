# AGENTS.md

Standing instructions for coding agents (Codex and others) working in this
repo. Read this first, then the brief for whichever workstream you were asked
to do.

## What this is

The **MBA Industry Primer Library**: a static site that lists industry primers
(Word documents) for Columbia Business School MBA students, built around the
CBS Energy & Infrastructure Club. Each primer is a ~5,000-7,000 word briefing
on one industry, written to get a student interview-ready fast.

## How it ships

- **GitHub Pages serves this repo from `main`. Every merge to `main` is live,
  and the repo is public.**
- Never push directly to `main`. Work on a branch and open a pull request.
- No build step today: `index.html` and the `.docx` files are served exactly
  as committed. If you add a build step, the site must still work when served
  as static files from Pages, and the built output must be committed (or
  produced by a GitHub Actions Pages workflow you add in the same PR).

## Layout

```
index.html          the whole site: inline CSS, one inline <script>, 27 cards
*.docx              the primers, all in the repo root (25 today)
scripts/            check_site.py (consistency checks; run before every PR)
docs/               workstream briefs (see below)
README_solar.txt    stale note from an earlier upload; safe to remove
```

## Workstreams

- **UX/UI refresh**: read [`docs/ux-brief.md`](docs/ux-brief.md).
- **Primer agent** (create new primers and update existing ones on request,
  later on a schedule): read [`docs/primer-agent-spec.md`](docs/primer-agent-spec.md).

## Card contract

Each primer is one card in `index.html`. Today's markup (keep these fields
through any redesign, even if the markup changes):

```html
<div id="card-water-infrastructure" class="primer-card"
     data-category="infrastructure"
     data-title="water infrastructure PFAS desalination utilities"
     data-read-time="50">
  <div class="card-banner"></div>
  <div class="card-body">
    <div class="card-tags"><span class="card-tag">🏗️ Infrastructure</span></div>
    <h3 class="card-title">Water Infrastructure</h3>
    <div class="card-desc">
      <span class="card-desc-text">One- to three-sentence pitch...</span>
      <button class="read-more-btn" onclick="toggleDesc(this)">Show more</button>
    </div>
    <div class="card-updated">Last Updated: <strong>May 2026</strong></div>
    <div class="card-sections">
      <span class="section-chip">Value Chain</span> ... 
    </div>
    <div class="card-footer">
      <a href="water_infrastructure_primer_may2026.docx" download class="btn-download">...</a>
    </div>
  </div>
</div>
```

- `id`: `card-<lowercase-slug>`, unique. Other links and `jumpToCard()` use it.
- `data-category`: **space-separated** list of tags. Each tag must be one of
  the filter options in the page's dropdown (`toggleFilter('...')`): `energy`,
  `infrastructure`, `materials`, `decarbonization`, `finance`, `technology`,
  `geopolitics`, `policy`, `agriculture`. Multi-tag values like
  `finance infrastructure` are intentional. Adding a category means adding a
  filter option too.
- `data-title`: search keywords, lowercase, space-separated. Not shown.
- `data-read-time`: minutes, as a number (45-55 today).
- `card-tag`: emoji plus label, one per category (e.g. `⚡ Energy`,
  `📊 Finance`, `🏗️ Infrastructure`, `🏭 Decarbonization`, `💻 Technology`,
  `⛏️ Materials`, `🏛️ Policy`, `🌏 Geopolitics`, `🌾 Agriculture`).
- `Last Updated`: `<Month> <YYYY>`, and it must change whenever the primer's
  content changes.
- Download link: a file that exists in the repo.

## Primer format

Every primer follows the same template. Match it for new primers and keep it
when updating old ones.

**Title block:** industry name in large bold capitals, then
`MBA Industry Primer | <Category>` and `Columbia Business School | <Month YYYY>`.

**Opening:** `INDUSTRY AT A GLANCE`, a dense, number-backed overview.

**Body:** 5-8 topic-specific sections, headings in bold capitals. Common ones:
History & Origins, Market Structure & Value Chain, Key Players & Competitive
Landscape, Global Geography, Politics/Policy & Regulation, Industry Trends &
Technology Innovation. Use whatever the industry needs (e.g. the water primer
has a PFAS section; AI & Power Demand has a Hyperscalers section).

**Closing sections, always present and in this order:**
1. `CURRENT NEWS & MARKET DYNAMICS (<YYYY>-<YYYY>)`
2. `INVESTMENT, FINANCE & CAREER ANGLES`
3. `FUTURE OUTLOOK`
4. `INTERVIEW CONVERSATION STARTERS`
5. `REFERENCES`

**Visual identity:** Arial throughout. Navy `#1B3A6B` for headings, table
header fills and accents; dark gray `#404040` body text; light gray `#F5F5F5`
alternating table rows. Section headings 13pt bold caps; title ~24-28pt.
Typical primer: 4-7 tables and a few images.

**File names:** existing names are irregular (`solar_energy_industry_primer.docx`,
`water_infrastructure_primer_may2026.docx`, `onshore_wind_industry_primer_final.docx`).
Do not rename existing files without a plan for old links: Pages has no
redirects, and people share direct download URLs. New primers use
`<slug>_primer_<mon><yyyy>.docx` (e.g. `semiconductors_primer_nov2026.docx`)
unless the primer agent spec has moved to stable names by then.

## Rules

- **Every factual claim and every number needs a source** listed in
  REFERENCES. Never invent figures, quotes, companies, or deals. If you can't
  verify something, leave it out or mark it clearly as an estimate with its
  basis.
- Date-stamp honestly: "Current News" covers the period it says it covers, and
  `Last Updated` on the card matches the primer's title block.
- Keep the site static and dependency-light. No backend, no secrets, no API
  keys in the repo (it is public). Any API key a workflow needs goes in GitHub
  Actions secrets.
- Keep download URLs that already work working.
- The "Request a Primer" button is a `mailto:` to the maintainer. Leave it
  unless asked.
- This is an educational resource, not investment advice. Keep that tone.

## Verify before opening a PR

```bash
python scripts/check_site.py        # must pass (see Known issues for today's baseline)
python -m http.server 8000          # then open http://localhost:8000
```

Check the page at desktop width and at ~375px phone width, try search, every
category filter, and sort, and click a few Download buttons. For primer
changes, open the generated `.docx` and compare it against an existing primer
for template and styling.

## Known issues (as of November 2026)

- Two cards link to primers that don't exist, so their Download buttons 404:
  `card-infrastructure-investing` →
  `infrastructure_investing_industry_primer_may2026.docx`, and
  `card-semiconductors-ai-chips` →
  `semiconductors_ai_chips_industry_primer_may2026.docx`.
  `check_site.py` fails on exactly these two today. Fix by writing the primers
  or by marking the cards as coming soon (and teaching the checker about that
  state).
- Every primer is stamped April or May 2026, so the "Current News" sections
  are about six months old.
