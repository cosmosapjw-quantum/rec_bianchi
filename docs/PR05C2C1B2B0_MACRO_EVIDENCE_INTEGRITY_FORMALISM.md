# PR-05C2C1B2B0 macro-evidence integrity formalism

## Conventions

The metric signature is `(-,+,+,+)`.  Ordinary frequency is measured in Hz;
`c`, `h`, and `k_B` remain explicit.  Photon occupation is dimensionless and the
semidiscrete collision-plus-frequency-transport action has units `s^-1`.

## Necessary backward-Euler parent condition

For a recorded endpoint \(f_\star>0\), recorded timestep \(\Delta t>0\), and the
durable semidiscrete action \(\mathcal A[f_\star]\), backward Euler requires

\[
 f_\star-f_n-\Delta t\,\mathcal A[f_\star]=0.
\]

The parent is therefore unique:

\[
 \boxed{f_n=f_\star-\Delta t\,\mathcal A[f_\star]}.
\]

For every component with \(\mathcal A_i[f_\star]>0\), strict positivity requires

\[
 \Delta t < \frac{f_{\star i}}{\mathcal A_i[f_\star]}.
\]

Hence a recorded endpoint is inconsistent with every strictly-positive parent
whenever any component of the implied parent is nonpositive.  This test needs
neither the missing nonlinear-worker source nor a guessed parent state.

## Durable-operator reconstruction

The audit uses the recorded v0.64 thermodynamic node, density, canonical macro
step, final occupation, v0.48 background characteristic, durable v0.50 network,
and the current v0.64 explicit thermodynamic network family.  It evaluates both
declared angular-boundary alternatives:

1. isotropic lift;
2. outward reduced-flux maximum-entropy lift.

The collision action dominates the contradiction; switching between these
boundary closures does not change the minimum implied parent in float64.

## Result

All nine recorded lanes fail under both closures.  Between 235 and 340 of 910
components have nonpositive implied parents.  The recorded canonical macro
steps exceed the strict-positivity upper bound by factors between
\(2.7599\times10^9\) and \(3.8840\times10^9\).

This does not corrupt the immutable v0.64 bytes, the v0.65 scalar theory, or the
v0.66--v0.68 direct-node and source adapters.  It does supersede the nine v0.64
macro-convergence rows as evidence for a physical accepted macro step.

## Solver implication

The next nonlinear stage must start from a source-conditioned accepted state and
construct the path with adaptive microsteps or pseudo-transient continuation.
Preconditioner selection against the superseded endpoints is not meaningful.
Every accepted canonical macro must retain positivity, conservation, rollback,
and history-commit gates independently.
