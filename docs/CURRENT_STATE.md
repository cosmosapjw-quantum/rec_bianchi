# Current state

- Durable local stage: **PR-05C2C1B2B1E1A / v0.74**.
- Status: `PASS_PR05C2C1B2B1E1A_SOURCE_CONDITIONED_SINGLE_COM_MACRO_ROUNDOFF_LIMITED_ROOT_ATOMIC_HISTORY_COUPLING_OPEN`.
- The v0.73 provenance-locked source-derived parent remains the only admissible
  production parent for this lane.  The q=1 operator fixture, raw arrays without
  provenance, stale v0.64 endpoints and direct native-to-COM remaps remain
  forbidden.
- v0.74 evaluates the orthogonal Bianchi-II geometry at the dynamic macro
  endpoint and solves the bounded 35-state by 26-direction COM nonlinear Bose
  collision plus conservative frequency-transport backward-Euler subproblem.
- The raw residual is `5.4748e-20`.  The cancellation-amplified net/state
  diagnostic remains `7.0045e-6`, but the gross-event backward error is
  `3.1925e-17` and the raw residual is `1.1232e-3` of an explicit conservative
  floating-point roundoff bound.  Acceptance therefore uses gross backward
  error, the explicit roundoff bound and independent number/energy ledgers;
  the large net/state diagnostic is retained rather than hidden.
- Photon number is restored along a common Bose chemical-activity direction by
  a maximum relative correction `1.3439e-11`; this is an internal conservation
  restoration, not a fit or free external normalization.  The final number
  residual is `1.4080e-16`, gross-energy backward error `3.6540e-19`, pair-loop
  action parity `2.0467e-9`, minimum occupation `7.2780e-15`, and collision free
  energy is nonincreasing.
- No interior red/blue boundary-speed zero occurs in this macro.  Two directions
  on each side lie exactly on the initial branch tie and are resolved by the
  endpoint branch; future eventful stages must continue to localize interior
  roots explicitly.
- Claim boundary: this is a **source-conditioned COM collision--transport
  subblock root**.  Native red/blue boundary occupations are held at their
  v0.73 values; one-/two-photon/Raman atomic populations, native characteristic
  history and accepted-history storage are not evolved.  No history slice is
  appended and no full coupled macro endpoint is claimed.
- The uploaded background solver remains provider-validated only for the
  expanding orthogonal Bianchi-II pilot.  All other family/tilt branches remain
  fail-closed or registry/smoke-only.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain unaffected.
- Next: **PR-05C2C1B2B1E1B dynamic atomic/native/history macro on the same
  z~1100 Bianchi-II parent and residual path**.
