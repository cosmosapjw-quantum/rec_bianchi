# PR-05C2C1B2B1E source-derived accepted-parent reconstruction plan

## Objective

Construct one physical accepted parent at `z~1100`, Bianchi II from the previous
accepted atomic/radiation history.  Do not reuse the operator-verification
fixture or cached v0.64 endpoints.

## Required state

- accepted HyRec history bytes and index
- electron and real/virtual atomic populations
- angle-frequency occupation
- dynamic `BackgroundSnapshotSequence` from the validated provider
- direct thermodynamic-network provenance
- red/blue interface accumulators
- limiter/upwind/event branch
- one-/two-photon/Raman source registry

## Transaction

1. Read an immutable accepted parent prefix.
2. Advance internal microsteps with dynamic background interpolation.
3. Reject/rollback without mutating accepted history.
4. Localize every branch/face-speed/topology event.
5. Commit exactly one canonical history slice only after all physical gates pass.

## Hard gates

- evidence class `SOURCE_DERIVED_ACCEPTED`
- all provenance hashes exact
- strict positivity without clipping
- photon number and exact face energy below `1e-11`
- source ownership and photon--atom four-force closure
- deterministic restart and rollback byte identity
- accepted history count `+1`
- no preconditioner or Rust selection until this parent exists
