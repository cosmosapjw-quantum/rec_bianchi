# PR-05C2C1B2B1A / v0.70-P0 — accepted-state pseudo-transient infrastructure

## Recovery classification

The earlier v0.70-P0 transcript claimed a development bundle, but the durable
logs show that the build failed before
`pseudotransient_continuation.py` was created.  This branch reconstructs the P0
infrastructure from the verified v0.69 full bundle.  It does not inherit any
unwritten source from the failed attempt.

## Implemented contract

The module `trajectory.pseudotransient_continuation` supplies:

- a content-addressed accepted macro parent bound to history, background,
  thermodynamic-network, interface, branch, and event provenance;
- mixed log-positive and signed solver coordinates;
- exact left-nullspace projection for compatible linearized right-hand sides;
- a dense pseudo-transient reference equation

  \[
  M\frac{U^{(m+1)}-U^{(m)}}{\Delta\tau_m}
  +R(U^{(m+1)};U_n)=0;
  \]

- cancellation-safe normwise backward-error diagnostics using the local
  Jacobian/operator scale;
- deterministic restart bytes;
- one-shot macro commit and byte-exact discard/rollback semantics.

A pseudo-step is an internal nonlinear globalization step.  It does not mutate
or append the accepted original-HyRec history.  Only an explicit successful
macro transaction increments the history count by one.

## Verified P0 controls

The regression suite covers deterministic content hashes, mixed-variable
round trips, exact nullspace projection, a positive scalar problem with
`1e9` stiffness, a nonlinear Bose-activity root, deterministic restart, and
one-shot commit versus exact reject/rollback.

## Claim boundary

This is a development reference, not a sealed physical PR-05 completion.
It does **not** connect the durable Full Bianchi-HyRec residual/JVP, select a
production preconditioner, reconstruct the superseded v0.64 endpoints, or close
the nine-lane four-macro matrix.  The next evidence-bearing task is to connect
one source-derived `z~1100` Bianchi-II accepted parent to the physical residual
and shifted JVP while preserving the transaction contract.
