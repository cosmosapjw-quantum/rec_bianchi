# Same-context science/code audit (not a separate native reviewer)

1. Channel orientation: pair loop uses γ down + collision up ⇒ A=β(ε−ΔE). Triangle uses γ up+γ up+collision down ⇒ A_tri=β(ΔE20−ε1−ε2) ⇒ -A1−A2. Verified both signs directly from 26 positive channel rates at all 6 source conditions.
2. Exact thermodynamic relation derived with the original Kirchhoff source representation, Wolfram FullSimplify=0; numeric cross-read 24/24 <1e-65. Sign reversal test: J3 gap positive ⇒ A3 negative; J6 gap negative ⇒ A6 positive.
3. Source invariance: byte SHA pinned, old FAIL7/8 unchanged; no out-of-grid T nor extrapolated collision data; para/ortho separate and 2→0 present in both; original A and q unmodified.
4. Nine-state generator Q has nonnegative off diagonal, each column sums zero. 6/6 stationary populations positive and normalized; componentwise absolute residual <1e-65. Formal σ term is (x−y)log(x/y)≥0; source model nonzero, synthetic equal-energy reference <1e-65. Positivity is of the synthetic channel-marked CTMC, **not a physical heat/entropy claim**.
5. Independent NumPy float64 9×9 matrix assembly plus Decimal100 raw literals agrees with 90-digit mpmath within specified pointwise gates. Single model family; no native fresh-context blind reviewer.
6. No real CDMS 2011-v2 independent .cat/.egy/.par or reduction recipe. The source originally has distinct printed energies/frequencies; assigning which was measured cannot be inferred from synthetic cycle affinities. Full spectroscopy remains HOLD. No new strong no-go/novel general theorem.
7. Figure visual audit: saved-only, no connected gaps, two sample collider density scenarios, y axis explicitly formal per molecule. Adjusted legend scientific notation without changing data. No continuous-T implication.

Review status: `PASS_SCOPED_SAME_CONTEXT`, native R6/C9 review `NOT_RUN_TOOL_NOT_EXPOSED`.
