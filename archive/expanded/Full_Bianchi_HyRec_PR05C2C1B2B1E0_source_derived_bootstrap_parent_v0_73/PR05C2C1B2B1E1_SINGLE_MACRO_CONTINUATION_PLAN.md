# PR-05C2C1B2B1E1 single-macro continuation plan

## Objective

Advance the v0.73 source-derived bootstrap parent through exactly one canonical
`z~1100` Bianchi-II macro interval.

## Required execution order

1. Load and validate the v0.73 parent and all provenance hashes.
2. Use the dynamic Bianchi-II provider at every internal evaluation.
3. Couple one-/two-photon/Raman source, native characteristic transport,
   nonlinear COM collision and red/blue interface ledgers.
4. Use safeguarded pseudo-transient/Newton continuation without mutating the
   accepted history during internal iterations.
5. Localize every face-speed, topology, limiter and branch event.
6. Commit exactly one history slice only after all physical gates pass.

## Hard gates

- strict positivity without clipping
- gross residual, photon number and exact face energy below `1e-11`
- analytic JVP below `1e-8`
- photon--atom four-force and source ownership closure
- reject/rollback byte identity and deterministic restart
- accepted history count exactly `+1`

Preconditioner bake-off is permitted only after the same parent/residual path is
established.  Rust remains parity-only until the Python reference converges.
