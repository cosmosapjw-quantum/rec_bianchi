# Validation of the attached uniform-measure first probe

| Item | Status | Evidence / limit |
|---|---|---|
| Exact pasted source and fixed baseline | PASS | IDENTITY.json; original numerical probe byte-identical to supplied block |
| Syntax / installed dependencies / original import paths | PASS | SYNTAX_ENVIRONMENT.log, actual exit 0 |
| Process completion and coverage | PASS | PROCESS.json actual exit 0; RESULT 288 moment rows / 8 discrete oracle comparisons / 6 direct references |
| Weak source and density JVP; signed decomposition | PASS | Runtime assertions; saved decomposition residuals in SAVED_ANALYSIS.json |
| Fixed uniform hat measure and twofold rescaling | PASS | Runtime assertions: total 20, first moment 10, positive mu, 2*C2=C, unchanged weak moments |
| Conditional chi moment bound | PASS | All stored chi cases within envelope plus unchanged binary64 allowance; no analytic JVP-bound claim |
| Observed convergence behavior | BOUNDED_OBSERVATION | LOCAL_SLOPES.csv retains irregular slopes; affine primal roundoff slopes are not convergence orders |
| Saved-only final four plots | PASS | POSTPROCESS02_PROCESS.json, unchanged input hashes, VISUAL_REVIEW.json |
| Independent scientific/source review | PASS_WITH_CLAIM_LIMITS | INDEPENDENT_REVIEW.md; no independent numerical replay |
| Original 7+4 tests | NOT_RERUN | Prior accepted evidence remains separate |
| Physical measure/provider, full solver, atomic continuum | NOT_TESTED | NO_PASS_REC_PHYSICAL_SPLIT and both admission flags false |
