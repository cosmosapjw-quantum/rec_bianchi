# PR-01B1-B3B3A regularized same-cell angular block

## Raw and collision-relevant moments

For frequency cell \(I_i\), let \(\mathsf S^{(\ell)}_{ii}\) denote the raw same-cell gain conductance.  The collision operator never needs this distributional quantity by itself.  Its same-cell contribution is

\[
\boxed{\mathcal D_{\ell i}=\frac{\mathsf S^{(\ell)}_{ii}-\mathsf S^{(0)}_{ii}}{\Pi_i}}.
\]

Equivalently,

\[
\boxed{\mathcal D_{\ell i}=\frac1{\Pi_i}\int_{I_i\times I_i}\!d\Phi\;[P_\ell(\mu)-1]}. 
\]

The coherent-forward part is proportional to \(\delta(1-\mu)\delta(x_t-x_s)\).  Since

\[
P_\ell(1)-1=0,
\]

it cancels exactly before discretization.  In particular

\[
\mathcal D_{0i}=0.
\]

## Forward endpoint coordinates

Write

\[
\mu=1-2s^2,\qquad x_t=u+v,\qquad x_s=u-v,
\]

and set

\[
v=s y.
\]

Then

\[
dx_tdx_s=2s\,du\,dy.
\]

The Maxwell--Jüttner structure factor carries the reciprocal narrow-width behavior, so the frequency integral has a finite \(s\to0\) limit.  Moreover, with \(t=\sqrt{1-\mu}=\sqrt2s\),

\[
P_\ell(1-t^2)-1=-\frac{\ell(\ell+1)}2t^2+O(t^4),
\]

and

\[
\frac12|d\mu|=t\,dt.
\]

Thus the omitted endpoint contribution below \(t_{\min}\) is \(O(t_{\min}^4)\), and no coherent delta needs numerical representation.

## Common-measure control variate

The v0.32 two-sided finite-volume Hummer block is used as an exact endpoint control variate:

\[
\boxed{
\mathcal D^{\rm exact}_{\ell i}=\mathcal D^{\rm Hummer}_{\ell i}+\int [P_\ell-1](K_{\rm exact}-K_{\rm Hummer}).
}
\]

This is an algebraic rearrangement of the same continuous integral, not posterior symmetrization or a fitted correction.

## Sign

For integer \(\ell\ge1\) and \(-1\le\mu\le1\), \(P_\ell(\mu)\le1\).  Since the scalar event measure is nonnegative,

\[
\boxed{\mathcal D_{\ell i}\le0.}
\]

The block is therefore a pure angular damping contribution.
