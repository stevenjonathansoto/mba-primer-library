# MVP architecture and implementation record

Audit: 2026-11-05, baseline `6eb8642`. Read AGENTS.md, ux-brief.md and
primer-agent-spec.md in full. Inspected the HTML/CSS/JavaScript, checker,
tracked files, recent upload history and GitHub repository metadata.

## Current architecture

GitHub Pages serves committed static files from main according to repository
instructions. One 87,797-byte index contains CSS, JavaScript and 27 cards.
There are 25 root Word downloads. No generator, dependency manifest, Actions
workflow, content database or authentication exists. The baseline checker
fails on exactly the Infrastructure Investing and Semiconductors download
links. No open PRs were returned during audit. Main has no branch protection
or rulesets; auto-merge is disabled. Live deployment remains to be verified.

## Preserve

Keep all 25 document bytes and filenames, 27 card anchors, nine categories,
search, multi-category filters, sort, expanded descriptions, copy links,
Columbia framing, navy palette and maintainer email. Keep no-JavaScript content.
The only obsolete file identified by the existing handoff is README_solar.txt.

## Limitations and direction changes

Downloads have no web reading alternative. Counts are hardcoded; filters use
clickable divs; search has no accessible label. Catalog dates are April/May
2026, not verification dates. Source integrity cannot be inferred from a
document's references alone. Existing documents are legacy, not validated MVP
content. Financial facts and regulatory references need independent review.

The updated direction supersedes 5,000–7,000 words, word-count fidelity within
2%, mandatory fixed closing headings and the prohibition on auto-merge. New
primers target 7–9 rendered pages, never exceed 10 including references, and
use at least 11pt body text. Only checks-passing PRs may auto-merge. Public
paid intake and scheduled paid refresh start disabled.

## Target architecture

Retain static Pages. A deterministic Python build reads catalog metadata and
`primers/<slug>/research.json`, `primer.md`, `summary.md`, `interview.md`.
Research records source dates, retrieval evidence, stable claim IDs, units,
materiality, freshness, and dependent sections. Render HTML and Word from the
same content. Preserve originals during migration; label legacy content.

Research, editorial and verification stages share this evidence package.
Deterministic checks validate provenance and cross-format references; semantic
entailment still requires evidence review. Unsupported material claims block
publication. Model opinions alone never establish factual verification.

Serialize paid Actions across request and refresh workflows. Persist budget
reservations before a provider call, retain uncertain costs as reservations,
and reconcile measured usage. Fail closed on missing prices, ledger state,
credentials, benchmark approval or unsupported provider accounting. Issue
authors, not issue text, determine authorization. Feedback never runs paid work.

## Sequence and dependencies

1. Foundations: inventory, Coming Soon, accurate counts, configuration and docs.
2. CI: site/config/provenance tests; rendered pagination and typography gates.
3. Content: shared research, deterministic builders, limited audited migrations.
4. Provider stages and measured budgets; benchmark only with approved funding.
5. Authenticated requests, durable ledger, PR creation and publication callbacks.
6. Accessible reading, recruiting filters, related concepts and sources.
7. Free monitoring and targeted refresh dependency planning.
8. Browser, documents, authorization, concurrency and deployment validation.

Each phase should be a reviewable PR. Later PRs may depend on earlier branches
while repository settings prevent safe automatic merging.

## Risks, prerequisites and costs

No paid calls are authorized for the audit. The configured $20 monthly limit
is a ceiling, not a benchmark allowance. Models/prices must be checked against
official sources and benchmarked before enabling paid execution. Rendering
requires an actual Word-compatible renderer; XML page metadata is not proof.
Free source monitoring can report blocked/unknown responses, not infer false
facts from network errors. Maintain provider-side billing limits separately.

Maintainer must configure required checks, branch protection, auto-merge and
a scoped App/PAT that triggers PR CI. These settings are currently absent.
Secrets and provider billing configuration have not been inspected or assumed.
No successful remote CI, benchmark or production deployment is claimed here.
