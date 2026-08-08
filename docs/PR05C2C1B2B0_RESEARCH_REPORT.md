# PR-05C2C1B2B0 research report

## Result

The missing v0.64 worker source could not be recovered from the filesystem, Git
object graph, immutable artifact, or delivery bundles.  A parent-independent
backward-Euler audit was therefore used.  All nine recorded endpoint/timestep
pairs imply a nonpositive parent under the durable operator, for both isotropic
and maximum-entropy boundary closures.

## Evidence classification

- v0.64 artifact and NPZ bytes: **DURABLE_VERIFIED**.
- v0.64 structural operator implementation and compact tests: retained.
- v0.64 nine-lane canonical-macro convergence claim: **SUPERSEDED / NOT
  REUSABLE**.
- v0.65 scalar theory and v0.66--v0.68 network/source adapters: **UNAFFECTED**.
- physical multi-macro trajectory: **OPEN**.

## Root cause

The immediate root cause is not merely a poor preconditioner.  The recorded
endpoint, recorded canonical timestep, and durable right-hand side do not define
a positive backward-Euler parent.  Because the expensive worker source and
accepted parent states are absent, the old numerical path cannot be replayed or
used as a continuation seed.

## Numerical implication

The durable direct network is extremely stiff and cancellation dominated.  A
plain large-step log-variable Newton solve is not an acceptable recovery path.
The next stage must use an accepted-state continuation strategy and measure
preconditioners only on that reconstructed path.

## External solver basis

PETSc provides pseudo-transient continuation for steady ODE/DAE residuals,
Newton trust-region methods, and backtracking line searches.  These are candidate
globalization mechanisms, not automatic scientific validation.  Positivity,
number, exact face energy, redshift work, four-force, and accepted-history
transaction gates remain project-owned.
