# Activation checklist and current limits

This implementation is staged. The foundations and validation primitives do
not yet constitute an autonomous publishing pipeline. Do not enable paid
generation until provider integration, durable ledger transport, research
verification, rendered content CI and the controlled benchmark are complete.

## Repository protections

1. In Settings → Rules → Rulesets, create an active branch ruleset for main.
2. Require pull requests and status checks. Bootstrap with `library-checks`,
   which runs in foundation PR #2. Require branches to be up to date. Block
   force pushes and deletion. Apply rules to administrators without bypass.
   After #2 and #3 merge, require `browser-checks` before merging #4. Require
   `rendered-documents` before merging #5. The final rule requires all three.
   Retarget each dependent PR to main after its predecessor merges and rerun
   checks on the resulting head; never waive a missing check to merge a phase.
3. In Settings → General → Pull Requests, enable Allow auto-merge. Enable squash
   merge. Never use an immediate merge merely because no checks are reported.
4. In Settings → Actions → General, allow the checkout/setup-python actions.
   Default workflow permissions should remain read-only. Grant additional
   permissions only on the specific publishing workflow.
5. Configure Pages to serve main/root, preserving existing deployment settings.
   Verify a successful Pages deployment after each merge before announcing URLs.

## Future publishing credentials

Use a repository-scoped GitHub App with Contents and Pull requests write,
Issues write and Metadata read. Store `PR_APP_ID` as an Actions variable and
`PR_APP_PRIVATE_KEY` as an Actions secret; grant access only to this repository.
An alternative is `PR_BOT_TOKEN`, a fine-grained PAT restricted to this repo
with the same permissions and a short expiry. Never embed credentials in
source or command logs. PR creation must use the App/PAT so PR CI triggers;
the ordinary GITHUB_TOKEN alone does not provide that event behavior.

Provider secrets, model identifiers and pricing will be named by the chosen
adapter after official availability/pricing research. No provider is currently
selected. Do not add guessed API secrets or enable unsupported configuration.
Create a dedicated provider project; set the smallest available spending limit
and billing alerts. Application reservations supplement provider controls.

## Budget and benchmark

The default ceiling is $20/month, $5/primer, three requests/day. Benchmark funds
must be explicitly allocated before testing; no benchmark has run. Costs must
include reasoning/output tokens, retries, search and tools. Unknown costs retain
the full reservation. The SQLite primitive is atomic locally, but ephemeral
Actions disks are not a persistent shared ledger. Activation requires durable
ledger retrieval and atomic persistence plus workflow-wide serialization.

## Request and refresh policy

Edit `allowed_requesters` in config/agent.yaml to add club members through a PR.
Keep public_requests_enabled false until the public intake policy and caps have
been tested. The email link remains ssoto27@gsb.columbia.edu. Feedback must use
a separate label and never dispatch generation. Paid scheduled refresh remains
disabled; changing its flag alone intentionally fails validation while the
provider pipeline is incomplete. Retain Coming Soon for the two missing titles.

## Validation limits

Archive/checksum checks prove legacy preservation, not document rendering or
factual accuracy. Provenance validation checks evidence presence, hashes and
claim references, not semantic entailment or every uncited prose assertion.
No migrated package should be certified on this gate alone. Render each new
Word file to PDF, validate it with check_rendered.py and inspect all page images.
Never infer page count from Word's cached document properties.
