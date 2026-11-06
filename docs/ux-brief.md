# UX/UI refresh brief

Read `AGENTS.md` first for the deploy model, card contract, and rules.

## Goal

Make the library feel like a polished, fast, trustworthy resource a student
opens before a coffee chat or interview, and make it easy to keep growing past
27 primers without hand-editing counts and markup.

## Current state

- One file, `index.html` (~88KB): inline CSS, one inline `<script>`, 27 cards
  written out by hand. Google Fonts: Playfair Display (headings), DM Sans
  (body), DM Mono. Navy palette with a header of layered noise/grid/glow
  effects.
- Header, then a search strip (not sticky; scrolls away) with: free-text search (matches title,
  keywords, section chips, and description), a multi-select category dropdown
  with removable pills, and an A-Z / Recent sort toggle.
- Card grid: emoji category tag, title, expandable description ("Show more"),
  "Last Updated", section chips, Download button (`.docx`), and a copy-link
  anchor per card. Deep links (`#card-<slug>`) scroll to the card on load.
- "Request a Primer" opens a pre-filled email.
- One responsive breakpoint (`@media (max-width: 640px)`).

## Known problems

1. **Broken downloads.** `card-infrastructure-investing` and
   `card-semiconductors-ai-chips` look like normal cards but link to files
   that don't exist. Fix first; `scripts/check_site.py` fails on exactly
   these two today.
2. **Hardcoded count.** `const TOTAL = 27;` and the `27 documents` label must
   both be edited by hand whenever a card is added or removed. Derive from the
   DOM (or from card data).
3. **Cards are hand-written HTML.** Adding a primer means copying ~30 lines of
   markup and editing it in several places. This is the main thing that makes
   the primer agent fragile. Consider moving card data to one file (e.g.
   `primers.json`, or front matter on primer source files if the agent spec's
   text-source migration has happened) and rendering cards from it, either at
   build time or in the page's script. Keep a no-JS fallback in mind: a page
   that is blank without JavaScript is worse than today.
4. **Dead code.** `jumpToCard()` is written for "pairs chips" (related-primer
   links) that don't exist in the markup. Either build the feature (see below)
   or remove it.
5. **Download-only.** Every primer is a `.docx`, which is awkward on phones and
   gives no preview before downloading. Stale `README_solar.txt` in the root.
6. **Freshness isn't visible at a glance.** Everything says April or May 2026.
   Students can't tell whether a primer's news section is current.

## Ideas worth considering (pick, don't do all)

- Related primers: 2-3 "Pairs well with" chips per card using the existing
  `jumpToCard()` (e.g. Solar → Battery Storage, Transmission & Grid, Project
  Finance).
- A PDF alongside each `.docx`, or an in-page preview of the primer's
  "Industry at a Glance" and section list, so students can judge before
  downloading.
- Clearer freshness: a "Recently updated" filter or badge driven by `Last
  Updated`.
- Better mobile: the search strip, filter dropdown, and pills at 375px; tap
  targets of at least 44px.
- Accessibility: keyboard-operable dropdown and pills (they're `<div>`s with
  `onclick` today), visible focus states, `aria-expanded` on toggles, enough
  color contrast on muted text, `prefers-reduced-motion` for the card
  animations.
- Performance: the page is light, but check font loading (preconnect is
  already there) and keep it under ~150KB without primers.

## Constraints

- Must keep working as plain static files on GitHub Pages from `main`.
- No framework is required. If you introduce one or a build step, justify it
  in the PR, commit the built output or add a Pages workflow, and keep the
  local preview command in `AGENTS.md` accurate.
- Keep every field in the card contract (id, categories, keywords, read time,
  Last Updated, download link) and every existing download URL and
  `#card-<slug>` deep link working.
- Keep the Columbia / Energy & Infrastructure Club framing and the navy
  identity unless asked to rebrand. Keep the "Request a Primer" mailto.

## Done means

- `python scripts/check_site.py` passes (update the script in the same PR if
  you change the card markup or move card data).
- Search, every category filter (single and multiple), both sorts, Show more,
  copy-link, and deep links all work at desktop width and at 375px.
- Adding a primer touches one place (card data) plus the primer file.
- The PR description includes before/after screenshots at both widths.
