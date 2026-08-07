# Current scientific state — PR-05B3 / v0.61

PR-04 is complete at the source-conditioned split-domain operator-contract
level. PR-05A locks the primitive rate/schema layer, PR-05B1 fixes the
source-identifiable rank-one local DAE, and PR-05B2 closes the exact accepted
characteristic-history replacement contract. PR-05B3 now performs the first
actual compressed-term owner transition.

## PASS results

- Scalar `Dfplus`/`Dfplus_Ly` feedback has an XOR owner registry. Exactly one of
  `CANONICAL_CALLBACK` and `TYPED_CHARACTERISTIC_HISTORY` may be active.
- The typed characteristic history is the sole active Python production owner
  after componentwise canonical parity; the canonical callback remains only as
  an isolated audit oracle.
- Canonical and typed incoming fields, native RHS, 313-state solution, electron
  rate, outgoing virtual/line/average fields, append candidate and conservation
  ledgers agree exactly at `z~1300,1100,900`.
- Maximum analytic shifted-IJacobian discrepancy:
  `2.12624465852112292e-16`.
- Maximum frozen-coefficient backward-Euler backward error:
  `4.00610954024109673e-12`.
- Minimum physical population: `4.86080925682533631e-16`.
- Accepted-step transactions commit exactly once. Duplicate commit/discard is
  rejected; restart, rollback and rejected-step history are byte-exact.
- Future endpoints, nonmonotone accepted grids and unlocalized characteristic
  stencil switches fail closed.
- Photon number and redshift-energy work close componentwise; pure
  characteristic propagation has zero atom source.
- Interface-off v0.60 feedback parity and fixed-local-state Bianchi II,
  class-B `VI_h`, and exceptional `VI_-1/9` firewalls are exact.

## Ownership boundary

Only the scalar history owner has changed. Canonical Sobolev Ly-alpha escape,
native `A1s` diffusion and completed/Schur `Tvv` remain active and owned by
original HyRec. They may not be removed until an independently complete
replacement closes residual, Jacobian, conservation and restart gates in the
same bounded stage.

## Claim boundary

PR-05B3 proves a typed, causal, transaction-safe scalar history owner inside the
Python production residual. It does not claim an adaptive physical trajectory,
a native-derived COM interior trajectory, full FLRW `x_e(z)` parity,
visibility-function parity or CMB parity.

The next stage is **PR-05C canonical-output-grid adaptive short trajectory**.
Its critical architecture is fixed canonical original-HyRec history macro
intervals with adaptive internal DAE/collision microsteps; accepted history is
committed only once at a successful canonical macro endpoint.
