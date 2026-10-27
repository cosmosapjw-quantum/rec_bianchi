# C6 — implementation verification from the actual bounded pass

The C5 primary processes performed the changed-surface tests as part of their actual feature path. This stage reads and interprets their saved results; it does not rerun a successful primary.

| Surface | Actual verification | Result |
|---|---|---|
| HD exact coherence | Synthetic coherent source at50/100/200K |3/3 exact analytic zeros |
| HD mismatch sign | Positive gaps/frequencies on opposite sides of coherence |2/2 correct opposite I,D signs |
| HD invalid/domain handling | Zero/negative gaps, lower energy, frequency, temperature; NaN/Inf; unsupported T; boolean; binary64 exponent overflow |13/13 rejected as intended |
| Original HD source/colliders | Source byte roundtrip, separate colliderIDs2/3 and54 rate literals unchanged, original35Hz gate unchanged |3/3 PASS |
| Actual HD calculations |8 lines×3 fixed nodes; independent Decimal80 values |24/24 PASS |
| Exact represented-history identities |1240 direct-vs-jump retimings and313 direct-vs-Peano chords, exact inclusion |1553/1553 PASS |
| Source binding | Original query/source/cell/sample and old geometric anchor witnesses |313/313 PASS |
| History finite controls | Affine/nonuniform, both hinge directions, starts/targets, zeros, cancellation, domain/grid/sample rejection and mutations |30/30 PASS |
| Causal domain |313 right requests, of which301 available and12 outsideprefix |301 executed;12 explicit skips |
| Actual omitted-jump mutation | Every nonzero crossed-knot remainder |614/614 detected |

HD controls total21; history controls total30. The history invalid final endpoint is rejected even for zero step. A zero step at a valid boundary returns zero without an exterior derivative. Multi-jump cancellation is tested with a nonzero absolute envelope, and a flat source is not required to show a spurious nonzero mutation.

## Execution evidence

HD `raw/primary001/targeted_run.stdout.txt` lists every control and the final summary; stderr is empty. The bounded receipt records exit0, no timeout and no spawn error. History `evidence/primary001.stdout.txt` records `TARGETED_CONTROLS_PASS30` and the actual summary; `plot001.stdout.txt` confirms saved-output PNG/PDF generation. Both history stderr files are empty and both receipts record exit0.

The runtime interruption before implementation produced a transport/input-path failure and was repaired by exact retrieval. No scientific primary failed or was repeated. The separate packaging helper was checked with one synthetic file fixture; its0.177543 measured CPU seconds are metadata/packaging cost, not scientific validation.

## Coverage boundary

The tests target the newly implemented formulas, source binding, directional and causal behavior. Earlier54-rate detailed-balance,24LTE, native/RHS, IVP, Ks and GEO computations were not rerun. Scientific scope and finite-precision interpretation are considered in C7/C8; independent code/raw/figure judgment is C9. Original source gating and physical epsilon remain unchanged.

