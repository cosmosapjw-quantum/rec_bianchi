# PR-05C2C1B2B1 accepted-state pseudo-transient/micro-macro continuation

## Entry gate

PR-05C2C1B2B0 proves that the v0.64 cached endpoints cannot seed a physical
backward-Euler multi-macro trajectory under the durable operator.  Reconstruct
from source-conditioned accepted states; do not repair the cached endpoints by
fitting a normalization or inventing a parent.

## C1. Accepted-state registry

Define a typed state containing the canonical HyRec history hash, electron and
atomic state, angle/frequency occupation, background snapshot, direct network
node/interpolation provenance, interface accumulators, and event branch.
A macro attempt must carry an immutable parent hash.

## C2. Pseudo-transient globalization

For each canonical macro residual \(R(U;U_n)=0\), solve a sequence

\[
 M\frac{U^{(m+1)}-U^{(m)}}{\Delta\tau_m}+R(U^{(m+1)};U_n)=0,
\]

with adaptive pseudo-time \(\Delta\tau_m\).  Use trust-region or safeguarded
backtracking when the Newton model is not predictive.  A pseudo-step is an
internal nonlinear iteration and must not append canonical radiation history.

## C3. AP/nullspace preconditioner bake-off

Compare diagonal/AP, activity `P/Q`, atomic/native Schur, interface Schur,
low-ell/high-ell, and recycled Krylov candidates on the same accepted-state
path.  Record original residual, Newton/Krylov counts, setup/reuse cost, wall
time, peak RSS, and conservation drift.  Select only a wall-time improvement
with exact activity nullspace and entropy metric preserved.

## C4. Canonical macro transaction

A successful macro endpoint commits exactly one history slice.  Rejected
pseudo-steps, rejected macros, and event rollback preserve parent bytes exactly.
Frequency-speed, topology, limiter, and owner changes localize the earliest root
and restart the nonlinear controller.

## C5. Completion matrix

Run at least four canonical intervals in all nine lanes
`z~900,1100,1300 x II, VI_h, VI_-1/9`.  Require gross backward and algebraic
residuals below `1e-11`, analytic JVP below `1e-8`, strict positivity, photon
number, exact face energy, redshift work, physical four-force, zero pure-interface
atom source, nonpositive collision free energy, event/tolerance refinement,
deterministic restart, and FLRW reduction.

PASS enters PR-06.  Failure without fitted repair remains a bounded blocker.
