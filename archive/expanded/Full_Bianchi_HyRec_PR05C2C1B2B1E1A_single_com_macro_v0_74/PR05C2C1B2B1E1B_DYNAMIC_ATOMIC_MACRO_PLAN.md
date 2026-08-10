# PR-05C2C1B2B1E1B dynamic atomic/native macro plan

## Objective

Advance the v0.73 accepted parent through one complete `z~1100` orthogonal
Bianchi-II canonical macro with dynamic atomic/native/history coupling.

## Required order

1. Reuse the v0.74 roundoff-aware COM solver and acceptance metrics unchanged.
2. Evaluate one-photon and canonical two-photon/Raman paired source rates at the
   trial endpoint.
3. Evolve the typed original-HyRec characteristic history transactionally;
   proposed nonlinear iterates may not mutate accepted history.
4. Recompute red/blue native occupations from the trial atomic/radiation state,
   rather than holding the v0.73 boundary fixed.
5. Use the dynamic Bianchi-II provider and localize any face-speed or branch
   event before the endpoint solve.
6. Commit exactly one accepted history slice only after every physical gate
   passes.

## Hard gates

- strict positivity without clipping
- gross residual, photon number and gross energy backward error below `1e-11`
- analytic JVP below `1e-8`
- photon--atom four-force and source-ownership closure
- event refinement and deterministic restart
- reject/rollback byte identity
- accepted-history count exactly `+1`

Preconditioner and Rust bake-offs remain deferred until this same full physical
residual path converges.
