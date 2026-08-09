# PR-05C2C1B2B1C — safeguarded matrix-free continuation plan

1. Use the v0.71 `CoupledPhysicalContinuationAdapter` on the locked z~1100
   Bianchi-II accepted parent only.
2. Implement log-coordinate Newton--Krylov pseudo-transient steps using the
   shifted `LinearOperator`; do not assemble the 910x910 Jacobian in production.
3. Start with the diagonal/AP loss preconditioner already exposed by the coupled
   problem.  Add activity-nullspace RHS projection before any P/Q or Schur
   candidate.
4. Safeguard every step with physical gross, photon-number and positivity gates;
   use trust-region/backtracking when predicted and actual reductions disagree.
5. Generate residual-vs-pseudo-time, number-drift and Krylov-iteration plots.
6. Require one accepted physical macro and exact restart before extending to four
   macros.  Only then compare P/Q, atomic/native Schur, interface Schur and
   Krylov recycling.
7. Defer the Rust backend until Python residual/JVP and acceptance paths are
   reference-locked; Rust must reproduce residual/JVP and deterministic reduction
   before performance claims.
