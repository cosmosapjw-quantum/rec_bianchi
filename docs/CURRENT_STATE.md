# Current state

- Durable local stage: **PR-05C2C1B2B0 / v0.69**.
- Status: `PASS_BOUNDED_NO_GO_V064_RECORDED_MACRO_ENDPOINTS_INCONSISTENT_WITH_DURABLE_BACKWARD_EULER_OPERATOR_CONTINUATION_SOLVER_REQUIRED`.
- The immutable v0.64 artifact bytes remain durable, but its nine recorded
  canonical-macro endpoints are not reusable as accepted trajectory evidence:
  every endpoint implies a nonpositive backward-Euler parent under the durable
  operator and recorded timestep.
- The contradiction holds for both isotropic and outward maximum-entropy native
  boundary closures.  Between 235 and 340 of 910 state components are
  nonpositive; recorded timesteps exceed the strict-positivity bound by
  `2.76e9`--`3.88e9`.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters are unaffected.
- Preconditioner selection and multi-macro claims are reset to an accepted-state
  path.  Cached v0.64 endpoints must not be chained or used as nonlinear
  predictors.
- Next: **PR-05C2C1B2B1 accepted-state pseudo-transient/micro-macro
  continuation**, followed by the measured preconditioner bake-off and nine-lane
  four-or-more-macro evidence.
