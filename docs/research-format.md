# Shared research contract

Store each audited industry in `primers/<slug>/`: `research.json`, `primer.md`,
`summary.md`, `interview.md`, and an `evidence/` folder. Legacy HTML reading
copies are not migrated research packages.

The JSON root has `slug`, `title`, `version`, `last_verified`, `status`,
`sources`, `claims`, `dependencies` and `refresh_history`. Sources have stable
IDs, publisher, title, publication/retrieval ISO dates, HTTPS URL, an evidence
file path and its SHA-256 digest. Retain only legally permissible evidence
excerpts, not wholesale copyrighted reports. Claims have stable IDs, text,
source IDs, exact evidence excerpt, verification status, materiality, stable
versus time-sensitive classification, last_verified, review_after and dependent
sections. Quantitative claims additionally need value, unit and as_of.

Use `[claim:stable-id]` markers in all three Markdown formats. Reference IDs
must resolve to the same claim across formats. Section dependencies map changed
sections to affected summaries and interview answers; the refresh planner
computes their transitive closure and preserves all other sections.

Publication requires `status: verified`, all claims supported, valid evidence
hashes and excerpts, consistent dates/units, complete mandatory sections and
an actual rendered document within ten pages. Structural validation is only one
gate. A verifier must examine semantic entailment and detect unsupported prose,
contradictions and important omitted qualifications. If that cannot be established,
keep the package unpublished and explain what needs evidence.

## Migration order

Start with Water Infrastructure, Solar Energy and AI & Power Demand. For each,
map the original sections, tables and key financial topics to a coverage matrix;
triage every quantitative/policy/transaction assertion to a primary source.
Preserve verified fundamentals, remove unsupported material, and draft all three
formats from the reviewed claims. Plan 7–9 pages including references before
writing. Keep 11pt body text and the Arial/navy visual identity. Render and inspect
every page before any replacement is proposed. The original download remains
available throughout; use a separate validated edition initially.

Then migrate the other 22 available industries, ordered by source availability,
recruiting relevance and review urgency. The inventory is authoritative for
original filenames and anchors. Infrastructure Investing and Semiconductors
remain Coming Soon until normal authorized generation is operational.

Current migration status: zero verified packages. Reading conversion preserves
legacy text/tables/figures but neither verifies facts nor condenses documents.
