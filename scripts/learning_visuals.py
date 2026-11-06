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
