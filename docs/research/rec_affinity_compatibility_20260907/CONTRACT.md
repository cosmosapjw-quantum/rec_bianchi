# REC fixed-map affinity compatibility

Objective: accept PR77 from its existing exact-source CI evidence, then determine
whether its conservative log-control read can give a negative derivative of the
same discrete atom/photon entropy. This is a manufactured research diagnostic.

Base: `4125f7f39b29b710ad6ca673520ae46a426b564f`.
Tree: `bc5d7f0dbf477ccb693084dd9cd72e4e54bde25e`.
Allowed additions: this directory only, including code, evidence and closeout.
Protected: all prior files, production `src/`, existing tests, workflow, BASS,
fixtures, original results, tolerances, physical/provider admission and branches.

Use the original PR77 two-node map and both existing `compose` read kinds.
Keep nodal f=(1,1/15), a=1 s^-1, nH=8 m^-3, H=4 s^-1 and atomic total 9/16.
Parameterize xu/xg=exp(eta)/8, with eta in {-1/4,-1/8,-1/16,0,1/16,1/4}.
Binary64 z is the exact numerical input for independent Decimal references.
References use rational map coefficients; their binary64 representation error
is included in the already chosen 4096*epsilon*(1+abs(reference)) allowance.

Acceptance: (1) 12 API cases versus 80/120-digit independently written primal
references, reference stability <1e-70; (2) both number and energy ledgers;
(3) eta=-1/8: log-control entropy rate < -1e-5 s^-1, matched chi rate >1e-5;
(4) independent entropy directional difference along the actual count-state
vector field at h=(2^-8,2^-12,2^-16) seconds: successive errors decrease >100x,
last absolute error <1e-11 s^-1. These thresholds precede execution.

No PR77 test rerun, original BASS replay, actual time integration, provider,
moving map, high-resolution map selection or source promotion is performed.
One independent read-only review covers the scientific and implementation axes.
Within-scope evidence-driven repair is allowed. Preserve first failures.
Keep NO_PASS_REC_PHYSICAL_SPLIT and all physical/provider flags false.

The newest owner instructions take precedence over the historical root
REC-NEXT-03 handoff, which is a different work unit. Global policy was read at
0ea20a921bf48f15840ed70d6b4b796296501257. This thread performs the scientific
derivation and executable diagnostic; the user requests local Codex only for
capabilities unavailable here. No such local requirement is assumed.
