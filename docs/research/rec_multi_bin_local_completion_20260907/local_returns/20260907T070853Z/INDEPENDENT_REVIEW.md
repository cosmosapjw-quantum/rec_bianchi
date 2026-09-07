STATUS: PASS — scoped independent read-only scientific/source review.
Reviewer: Codex subagent /root/scientific_review, requested profile cuhg_terra_guide.
No numerical command, rendering, mutation, external service query, or nested review was performed by the reviewer.

Exact checkout verified: 9195f94bf308806ae6e9070f6175b500a1c2ef53,
tree 98577a94604efff77c24b89ee3a56a99fd478f16, clean.

- verify_nullspace.py:30-108 correctly defines four independent left invariants, proves the energy row is their stated combination, and pairs exact rational rank-3 witnesses with separate rounded-stencil residuals. Observed witnesses: base [0,1,16], hires [0,1,34].
- verify_nullspace.py:110-130 uses the required count derivative beta*(dC-C*dn/nH) and makes the omitted term a failing diagnostic.
- verify_nullspace.py:132-167 constructs W^-1 L^T, checks all four right-null vectors, and independently checks four stationary-family tangents. Family derivatives agree with the stated (kappa,p,q,A) parameterization.
- verify_nullspace.py:170-199 adds exactly y0,y2,y3,y4 for both tables and reads: 16 comparisons, with frozen precision and central-difference checks.
- run_local.py:190-201 selects only supplement under --only supplement and does not invoke the original seven-group runner. The observed process receipt records only that lane, exit 0, no timeout, all four TestIDs PASS.
- plot_supplement.py:23-40,43-88 consumes saved RESULT.json, PROCESS.json, ADDITIONAL_JVP.csv; it imports no study/test module and launches no test subprocess. The receipt binds the three inputs to the same execution commit/tree and declares both original and supplement tests unreplayed.

CONCERN: none in the bounded scientific/source scope.
FAIL: none.
NOT_TESTED: independent numerical replay, full solver behavior, physical REC split/provider admission, original PR79 artifact recovery and historical-plot visual review.
NO_PASS_REC_PHYSICAL_SPLIT; physical_source_authenticated=false; provider_admitted=false.
