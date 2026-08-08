# Current state

- Durable stage: **PR-05C2B / v0.64**.
- Status: `PASS_EXPLICIT_CLOSURE_WITH_UNCERTAINTY_OPTIMIZED_CANONICAL_MACRO_REFERENCE_PR05C2C_NEXT`.
- Nine source-conditioned one-macro lanes (`z~1300,1100,900` × Bianchi II,
  class-B `VI_h`, exceptional `VI_-1/9`) close positivity, gross backward error,
  photon number, exact face energy, entropy, four-force and analytic-JVP gates.
- Native angular data and source-temperature conductances are explicit
  noncanonical closures with quantified uncertainty, not source-identical
  reconstructions.  Direct selected-pair disagreement reaches about 30.5%.
- Vectorized action/JVP and action-only residual paths reduce the principal
  Python collision cost by roughly 25x--54x in the locked benchmark.
- The full non-slow repository suite completes in about 20 seconds.  Slow
  scientific coverage is recorded in 15 fingerprint-bound file receipts
  covering 36 tests; the receipt-aware aggregate verifier closes 224 fast plus
  36 slow tests and exits zero in about 25 seconds.
- The previously suspected Git-bundle test is not the bottleneck.  The repaired
  harness removes node-level process churn and invalidates every slow receipt
  whenever scientific code, tests, canonical inputs or numerical evidence
  change.
- PR-05 remains in progress.  Next: **PR-05C2C direct thermodynamic network
  family and native angular evolution**, followed by multi-macro trajectory and
  PR-06 FLRW history parity.
