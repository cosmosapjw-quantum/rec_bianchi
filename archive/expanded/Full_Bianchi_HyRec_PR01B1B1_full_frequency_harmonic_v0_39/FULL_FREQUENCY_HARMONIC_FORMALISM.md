# PR-01B1-B1 full-frequency harmonic deposition audit

## Integrated kernel

For source cell `j`, the exact recoil correction is evaluated with the
same Sobol point as the no-recoil event:

\[
K^{\rm trial}_{\ell,ij}
=K^{\rm Hummer}_{\ell,ij}
+\langle w_e P_\ell(\mu_{\rm H})D_i(e)
-w_e^0P_\ell(\mu_{\rm H}^0)D_i(e^0)\rangle.
\]

The angle in the tally is the hydrogen-frame scattering angle. The
atomic cross section is still evaluated in the initial atom rest frame.

## Positive partition

Every microscopic outcome belongs to red exterior, one interior cell,
or blue exterior. The partitioned estimator is primary:

\[
\Gamma_j=K_{Rj}+\sum_iK_{ij}+K_{Bj}.
\]

An independently averaged total-rate estimator is retained only as a
quadrature diagnostic.

## Raw detailed-balance audit

The 17 source columns are integrated independently. Before any event
pairing, define

\[
C^{\rm raw}_{ij}=K^{\rm raw}_{i\leftarrow j}\Pi_j.
\]

Production microreversibility requires

\[
C^{\rm raw}_{ij}=C^{\rm raw}_{ji}
\]

within integration error. This stage finds a statistically significant
residual at roughly the 10^{-4} operator level. The symmetric reference

\[
S_{ij}=\tfrac12(C^{\rm raw}_{ij}+C^{\rm raw}_{ji})
\]

is stored only to show what the exact equilibrium null would be after
pairing; it is not accepted as a repair.

## Consequence

The current forward variables

\[
d^3p_i\,c(1-\boldsymbol\beta_i\cdot\boldsymbol n_i)\,d\Omega_i^*
\]

are not yet a demonstrated common measure under the PT event map. The
next stage must derive the invariant phase-space measure or its explicit
forward/reverse Jacobian before the full kernel can be released.
