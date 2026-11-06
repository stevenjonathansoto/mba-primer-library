"""Semantic HTML diagrams: readable without JavaScript and in print."""

VALUE_CHAIN = '''<figure class="learning-visual value-chain" aria-labelledby="chain-caption">
<figcaption id="chain-caption"><strong>Follow the water</strong><span>A simplified service chain</span></figcaption>
<ol class="water-flow">
<li><strong>Source</strong><span>Water enters the system</span></li>
<li><strong>Treat</strong><span>Prepare it for use</span></li>
<li><strong>Deliver</strong><span>Network → customer</span></li>
<li><strong>Collect &amp; treat</strong><span>Wastewater → discharge or reuse</span></li>
</ol>
<p class="visual-note">Locate the business: utilities operate assets; contractors and suppliers build, equip, or service them. Ownership and payment arrangements vary.</p>
</figure>'''

CASH_FLOW = '''<figure class="learning-visual cash-flow" aria-labelledby="cash-caption">
<figcaption id="cash-caption"><strong>Higher costs shrink the debt cushion</strong><span>Hypothetical annual cash flows · $ millions</span></figcaption>
<div class="cash-row"><div class="cash-label"><strong>Base case</strong><span>$12m available</span></div><div class="cash-track"><span class="debt" style="width:66.6667%">$8m debt</span><span class="cushion" style="width:33.3333%">$4m cushion</span></div><p>$12m ÷ $8m = <strong>1.50× coverage</strong></p></div>
<div class="cash-row"><div class="cash-label"><strong>Costs rise $2m</strong><span>$10m available</span></div><div class="cash-track"><span class="debt" style="width:66.6667%">$8m debt</span><span class="cushion" style="width:16.6667%">$2m</span><span class="lost" style="width:16.6666%">−$2m</span></div><p>$10m ÷ $8m = <strong>1.25× coverage</strong></p></div>
<p class="visual-note">The debt payment stays fixed. A $2m cost increase halves the cushion from $4m to $2m. Hatched area: cash lost to higher costs. Both bars use the same $12m scale.</p>
</figure>'''

PROJECT_CAPITAL = '''<figure class="learning-visual project-capital" aria-labelledby="capital-caption">
<figcaption id="capital-caption"><strong>Who funds the solar project</strong><span>Hypothetical initial funding · $100 million total</span></figcaption>
<div class="capital-sources"><div><strong>Lenders</strong><span>$70m debt</span><small>Principal and interest due</small></div><div><strong>Shareholders</strong><span>$30m equity</span><small>Residual value and losses</small></div></div>
<p class="flow-arrow" aria-hidden="true">↓</p><div class="project-entity"><strong>Solar Project Company</strong><span>Combines the funding and signs the project agreements</span></div>
<p class="flow-arrow" aria-hidden="true">↓</p><p class="visual-note">Funds construction and equipment, development and financing costs, and contingency. The 70/30 mix is an assumption, not an industry benchmark.</p></figure>'''

PROJECT_WATERFALL = '''<figure class="learning-visual project-waterfall" aria-labelledby="waterfall-caption">
<figcaption id="waterfall-caption"><strong>Where one year of electricity payments goes</strong><span>Hypothetical cash bridge · $ millions</span></figcaption>
<ol class="payment-flow"><li><span>Cash collected</span><strong>$18m</strong></li><li><span>Operating costs</span><strong>−$4m</strong></li><li><span>Taxes and other pre-debt adjustments</span><strong>−$2m</strong></li><li class="subtotal"><span>Available for debt service</span><strong>$12m</strong></li><li><span>Principal and interest</span><strong>−$8m</strong></li><li class="subtotal"><span>Residual before further restrictions</span><strong>$4m</strong></li></ol>
<p class="visual-note">This example leaves $4m after debt service. Reserves or distribution tests may retain some or all of it; it is not a promised dividend.</p></figure>'''

PROJECT_RISK = '''<figure class="learning-visual project-risk" aria-labelledby="risk-caption">
<figcaption id="risk-caption"><strong>Who must respond when an assumption fails</strong><span>Illustrative allocation questions for the solar project</span></figcaption>
<dl class="risk-map"><div><dt>Late completion → contractor</dt><dd>Does the completion remedy cover the project’s lost cash?</dd></div><div><dt>Low output → operator or equipment provider</dt><dd>Who fixes the problem, and who funds the gap meanwhile?</dd></div><div><dt>Late payment → electricity buyer</dt><dd>Can the project meet debt payments before collection?</dd></div></dl>
<p class="visual-note">Actual responsibility follows the signed contracts. Any uncovered loss remains a risk to project cash and its capital providers.</p></figure>'''

VISUALS={'water-chain':VALUE_CHAIN,'water-cash':CASH_FLOW,'project-capital':PROJECT_CAPITAL,'project-waterfall':PROJECT_WATERFALL,'project-risk':PROJECT_RISK}
