# PR-05C2B/v0.64 research and optimization report

## Result

The stage closes as `PASS_EXPLICIT_CLOSURE_WITH_UNCERTAINTY`.  Nine one-macro
source-conditioned lanes (three redshifts by three locked Bianchi backgrounds)
converge with positive occupations and componentwise number, exact face-energy,
collision four-force, entropy and analytic-JVP gates.  This is not a
source-identical reconstruction of angular native radiation or a multi-macro
physical recombination trajectory.

## Blockers and dispositions

1. **Native angular rank:** one scalar original-HyRec boundary value cannot
   determine 26 directional values.  Isotropic and bounded maximum-entropy
   lifts are explicit positive closures; their missing-momentum uncertainty is
   retained.
2. **Face trace:** P0 is the production fallback.  Positivity-limited MUSCL is
   second-order in the smooth audit but remains non-production until its
   limiter/JVP semantics are frozen.
3. **Thermodynamic grid:** source-temperature faces and mode measures are exact,
   while conductances use a positive reciprocal closure.  Selected direct
   COM--KHW quadrature differs by up to 30.53%, so direct network compilation
   remains PR-05C2C.
4. **Stiffness:** the tested harmonic block was slower than the diagonal/AP
   baseline.  z~900 and z~1100 use diagonal-preconditioned GMRES; the
   cancellation-dominated z~1300 bounded reference uses chunked dense Jacobians.

## Performance changes

The unordered-pair collision action and JVP are vectorized.  Residual calls use
an action-only path; diagnostics are evaluated only at accepted/stalled states.
JVPs support batching and dense Jacobians are assembled in chunks.  Measured
single-thread speedups in the immutable artifact are 25.46x for the full action,
53.77x for action-only residual work, 35.11x for JVP, and 1.53x for dense
assembly.  Pair-loop implementations remain audit oracles.

A fresh repository profile disproved the earlier Git-bundle-test blocker
hypothesis: the full non-slow suite completes in about 21 seconds and the bundle
export test takes about 0.62 seconds.  The dominant fast-test cost is direct
exterior quadrature.  Expensive cold direct-network regeneration is therefore
separated from quick/CI verification and retained through immutable evidence
caches and hashes.

## Conventions and dimensions

Metric signature is `(-,+,+,+)`.  Frequency is ordinary Hz.  `c`, `h` and
`k_B` are explicit.  Cell mode measure has units m^-3, collision and transport
actions have occupation s^-1, number flux has m^-3 s^-1, and exact face energy
is `h nu_face` times number flux.  A pure representation crossing has zero atom
source; physical collision owns photon/atom four-force exchange.
