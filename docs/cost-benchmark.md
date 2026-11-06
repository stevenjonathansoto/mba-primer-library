# Cost benchmark status

No paid calls made. Measured API cost for implementation: $0.
No per-primer benchmark, provider comparison or refresh cost has been measured.
Production models remain unselected; paid configuration fails closed.
The $20 configured monthly cap does not establish the provider account's
remaining balance, which is unknown. Do not report it as available funds.

Before activation, verify official pricing and tool compatibility on the day of
the run, allocate an explicit benchmark allowance, and record stage/provider/
model, input and output (including reasoning) tokens, search counts and charges,
retries, reserved cost, measured cost, validation results and final status.
Compare two configurations if the approved allowance permits. Preserve failed
attempt costs. Routine operation stays disabled until quality and cost pass.

## Candidate comparison, researched 2026-11-05

Official standard short-context pricing lists GPT-6.1 Sol at $2 input/$10
output per million tokens, GPT-6 Luna at $0.10/$0.50, and web search at
$0.01/call plus search-content tokens. Both models list Responses API web
search support. Recheck pricing, context tier and account access before use.

Sources: [pricing](https://developers.openai.com/api/docs/pricing),
[Sol capabilities](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Luna capabilities](https://developers.openai.com/api/docs/models/gpt-6-luna).

Hypothetical benchmark envelope, not measured performance: research 20k input,
10k output and eight searches; drafting 20k input/8k output; verification 30k
input/4k output. Input includes retrieved search text; output includes reasoning.
Sol research/verification plus Luna drafting estimates $0.326 per attempt;
all-Sol estimates $0.440. One complete retry doubles these estimates to $0.652
and $0.880. This excludes any unaccounted provider charges and is not a cost
guarantee. Reserve the configured $5 ceiling, not this illustrative estimate.
No candidate has passed quality benchmarking. Targeted-refresh costs are not
yet estimated because section sizes and evidence-fetch behavior are unmeasured.
