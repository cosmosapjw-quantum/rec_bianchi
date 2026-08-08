# PR-05C2C1A direct compiler and characteristic-face formalism

## Scope and conventions

This bounded stage implements the nodal and characteristic parts of the v0.65
scalar theory contract. The metric convention is `(-,+,+,+)`. Frequency is
ordinary frequency in Hz and `c`, `h`, and `k_B` remain explicit. The local
atomic/collision operator is evaluated in the hydrogen tetrad; Bianchi geometry
enters only through `BackgroundSnapshot` characteristics.

## Direct thermodynamic nodes

For a thermodynamic context \(\vartheta=(T_{\rm H},n_{\rm H})\), every unordered
pair and same-cell block is compiled directly from the scalar COM--KHW event
kernel. The resulting nodal network has

\[
K_{AB}(\vartheta)=K_{BA}(\vartheta)\ge 0,
\]

and retains the exact v0.50 node at \(T=3000\,\mathrm K\),
\(n_{\rm H}=2.5\times10^8\,\mathrm{m}^{-3}\). State-independent source bytes and
each process-local thermodynamic context are content-hashed. Independent blocks
are reduced in a deterministic order; the pair-loop implementation remains the
audit oracle.

Inside a fixed-topology temperature cell the per-hydrogen scalar conductance is
interpolated in inverse temperature,

\[
\ln \widehat K_{AB}(T)=
 (1-\lambda)\ln \widehat K_{AB}(T_i)
 +\lambda\ln \widehat K_{AB}(T_{i+1}),
\]

while the independently supplied local density multiplies the microscopic
per-hydrogen rate. No global normalization is fitted.

## Characteristic angular solver

A scalar original-HyRec boundary datum is not inverted instantaneously into 26
directions. Instead, each positive-weight angular node is backtraced to a
prescribed red or blue face and evolved with the exact finite-tilt Bianchi
characteristic. For isotropic hydrogen-frame coefficients,

\[
\frac{df}{ds}=j_{\rm H}(s,\nu)-\chi_{\rm H}(s,\nu)f,
\]

piecewise-constant formal transfer preserves positivity. A face trace is
accepted only when every directional characteristic lands on the requested
ordinary-frequency face within the declared tolerance; otherwise the call fails
closed rather than inventing a frequency interpolation.

The source-derived evidence in this stage uses canonical scalar original-HyRec
boundary occupations and zero local source/opacity to isolate exact Bianchi free
transport. A smooth manufactured isotropic source is used only to verify
second-order interval refinement. A physical original-HyRec emissivity/opacity
adapter remains open.

## Conservative face trace

COM finite-volume traces use a common limited slope, so

\[
\frac{f_{i,L}+f_{i,R}}2=\bar f_i
\]

exactly. Fixed active limiter branches have analytic JVPs. Ties, zero crossings,
and upwind-direction switches are events requiring localization and integrator
restart. P0 remains the fail-safe production trace until the physical source
adapter and multi-macro refinement close.

## Preconditioner decision

The entropy-graph candidate preserves the constant-activity collision nullspace,
but on the locked physical z~1100 problem it increased both GMRES iterations and
wall time relative to the diagonal/AP baseline. It is therefore rejected as a
production selection in this stage. The theorem remains useful, but measured
improvement is mandatory before any preconditioner is promoted.

## Claim boundary

This stage establishes full direct nodal networks at z~900, 1100, and 1300; an
exact 3000 K anchor; selected withheld pair interpolation; exact characteristic
face traces; and a fixed-branch conservative face JVP. It does not claim full
withheld same-cell validation, a physical original-HyRec angular source adapter,
a selected scalable AP preconditioner, or a multi-macro trajectory.
