# PR-05C2C1B2B1B/v0.71 physical acceptance-gate formalism

## Scope

This stage audits one locked accepted parent at `z~1100` on the actual
`Bianchi_II_large_shear` background.  It does not claim a converged physical
canonical macro.  The coupled backward-Euler residual is

\[
R(f;f_n)=f-f_n-\Delta t\,[C_{\rm Bose}(f)+L_\nu(f)+S_{\rm interface}].
\]

Metric signature is `(-,+,+,+)`, frequency is ordinary Hz, and `c,h,k_B` remain
explicit in the inherited physical operators.

## Defect

The reconstructed v0.70 generic backward error used the dimensionless scale
`max(|f_i|,1)`.  In the locked lane, occupations are about `1e-18`; therefore
`|J|max(|f|,1)` is not invariant under a harmless change of occupation units and
can suppress the reported error by about eighteen orders of magnitude.

## Corrected generic scale

Let

\[
s_i=\max\left(|f_i|,\sqrt{\epsilon_{\rm mach}}\,\|f\|_\infty\right).
\]

The generic normwise diagnostic is

\[
\epsilon_{\rm gen}
=\max_i\frac{|R_i|}{\max[s_i,(|J|s)_i]}.
\]

There is no absolute unit floor.  Under a consistent variable rescaling
`f=s y`, `R_y=R_f/s`, this diagnostic is invariant.

## Problem-specific macro acceptance

The physical solver retains two independent hard gates:

\[
\epsilon_{\rm gross}
=\frac{\|R\|_\infty}{\max(\|f\|_\infty,\|f_n\|_\infty,
\|\Delta t C\|_\infty,\|\Delta t L\|_\infty)},
\]

and the componentwise photon-number ledger residual
`epsilon_N`.  A candidate passes only when

\[
\max(\epsilon_{\rm gross},\epsilon_N)\le10^{-11}
\]

and every physical occupation is strictly positive.

## Matrix-free shifted JVP

For pseudo-time `Delta tau` and diagonal mass `M`,

\[
G(f)=M\frac{f-f^m}{\Delta\tau}+R(f;f_n),
\qquad
G'(f)v=M\frac{v}{\Delta\tau}+R'(f)v.
\]

The production-facing interface exposes the latter as a SciPy `LinearOperator`;
a dense Jacobian is assembled only for this bounded audit.

## Locked result

- canonical physical step: `1.70836938432170534e+09 s`
- legacy generic metric: `3.89331917263591647e-15`
- corrected generic metric: `5.14281469031761389e+02`
- physical gross error: `1.00000000000000000e+00`
- photon-number error: `1.00000000000000000e+00`
- largest parent-state step passing the `1e-11` gate: `1.28800433098080934e-06 s`
- canonical/gated-step ratio: `1.32636928559144675e+15`

The initial parent is therefore rejected.  No macro convergence is inherited or
manufactured.
