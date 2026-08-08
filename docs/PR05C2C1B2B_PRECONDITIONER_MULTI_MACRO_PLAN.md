# PR-05C2C1B2B — measured preconditioner and multi-macro closure

## Entry result

PR-05C2C1B2A/v0.68 locks the canonical October-2012 integrated-bin table,
threshold/process registry and real--virtual two-photon/Raman matrix
coefficients for all 311 virtual states.  It also provides a positive scalar
paired-action contract with LTE/Planck null and analytic JVP, while preserving
the claim boundary that this paired decomposition is not separately stored by
original HyRec.

## B2B.1 Physical characteristic coupling

Combine the source-identical virtual-spike and real--virtual coefficients with
the exact finite-tilt Bianchi characteristic solver.  Keep physical gain and
loss in paired nonnegative form.  Required gates:

- no scalar-to-angular instantaneous inversion;
- source/opacity ownership exactly once;
- LTE/Planck and FLRW scalar limits;
- positive occupation without clipping;
- photon number, exact face energy, redshift work and physical four-force;
- analytic full residual/JVP, including fixed characteristic stencils;
- event localization at frequency-speed, topology, limiter and owner changes.

## B2B.2 Measured preconditioner bake-off

Compare the following on identical locked problems:

1. diagonal/AP baseline;
2. activity-nullspace `P/Q` split;
3. atomic/native Schur block;
4. interface Schur block;
5. low-ell exact plus high-ell relaxation;
6. recycled Krylov subspace between neighboring temperature/macro nodes.

For every candidate record original residual, Newton and Krylov iterations,
setup/reuse time, solve and total wall time, peak RSS, and factorization reuse.
A candidate is selected only if total wall time improves without changing the
Bose entropy metric, activity nullspace, positivity or conservation gates.

## B2B.3 Multi-macro trajectories

Run at least four canonical `DLNA` macro intervals in the nine independent
lanes

```text
z~900, 1100, 1300
x Bianchi II, class-B VI_h, exceptional VI_-1/9.
```

Every successful macro commits exactly one accepted history slice.  Rejected
attempts and event rollback preserve the parent bytes exactly.  Required gates:

- gross backward and algebraic residuals below `1e-11`;
- analytic JVP below `1e-8`;
- strict positivity without clipping;
- photon number and exact face energy;
- cosmological redshift work;
- physical photon--atom four-force and zero pure-interface atom source;
- nonpositive collision free-energy production;
- event-time and tolerance refinement;
- deterministic restart and fixed-local-state geometry firewall;
- componentwise FLRW reduction.

## Exit decision

PASS enters PR-06 full FLRW `x_e(z)`/visibility/source/Jacobian parity.  A
preconditioner that lowers iterations but increases wall time is rejected.  A
trajectory that requires fitted normalization, hidden angular lifting or
mutation of rejected history remains a bounded blocker.
