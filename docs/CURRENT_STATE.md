# Current state

- Durable local stage: **PR-05C2C1B2B1B / v0.71**.
- Status: `PASS_P0_FALSE_CONVERGENCE_GATE_FIXED_PHYSICAL_RESIDUAL_JVP_CONNECTED_MATRIX_FREE_CONTINUATION_OPEN`.
- The reconstructed v0.70 generic pseudo-transient acceptance metric used an
  absolute scale floor of one.  For the locked `z~1100` Bianchi-II occupations
  (`O(1e-18)`), this suppresses the reported error by an arbitrary change of
  units and falsely passes the canonical parent at zero outer iterations.
- v0.71 replaces that floor with a state-relative scale and keeps the existing
  physical hard gate `max(gross backward error, photon-number residual)`.
- At the canonical `1.708369384e9 s` step, the legacy metric is `3.893e-15`, but
  the corrected generic error is `5.143e2`; physical gross and number residuals
  are both `1`.  The largest parent-state step passing the `1e-11` physical gate
  is only `1.288e-6 s`.
- The durable coupled residual, physical-variable analytic JVP and shifted
  matrix-free `LinearOperator` are connected.  Its finite-difference JVP
  residual is `3.49e-10`.
- No canonical macro convergence, preconditioner selection, Rust speedup, or
  multi-macro trajectory is claimed.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain unaffected.
- Next: **PR-05C2C1B2B1C safeguarded matrix-free continuation on the single
  `z~1100` Bianchi-II parent**, followed by measured preconditioner selection.
- Rust remains deferred until the Python physical residual/JVP and accepted
  trajectory are reference-locked.
