# PR-01C BackgroundSnapshot frame-adapter closure

## Stable interface

The local recombination and Ly-alpha collision kernel receives physical
orthonormal-frame data only:

\[
\mathcal B=
\{H,q,\sigma_{ab},N_{ab},A_a,R_a,
\beta_{\rm H}^a,D_0\beta_{\rm H}^a\}.
\]

All rates are in s^-1. Primitive chart state classes are confined to the
adapter layer.

## Normal-frame photon characteristic

For a unit direction \(e^a\),

\[
\mathcal R_n=D_0\ln\nu_n
=-H-\sigma_{ab}e^ae^b,
\]

\[
\begin{aligned}
D_0e^a={}&
-\left(\sigma^a{}_be^b
-e^a\sigma_{bc}e^be^c\right)
+(R\times e)^a
\\
&-\left[\mathcal P^a(e)
-e^ae_b\mathcal P^b(e)\right],
\end{aligned}
\]

\[
\mathcal P^a(e)
=A^a-(A\cdot e)e^a
+\epsilon^a{}_{bc}e^b(N e)^c.
\]

## Exact hydrogen-frame adapter

\[
\mathcal D_{\rm H}
=\Gamma_{\rm H}(1-\beta_{\rm H}\cdot e_n),
\]

\[
\nu_{\rm H}=\mathcal D_{\rm H}\nu_n,
\]

\[
\boxed{
\mathcal R_{\rm H}
=\mathcal R_n+D_0\ln\mathcal D_{\rm H}
},
\]

\[
D_0\ln\mathcal D_{\rm H}
=\Gamma_{\rm H}^2\beta_{\rm H}\cdot D_0\beta_{\rm H}
-
\frac{
D_0\beta_{\rm H}\cdot e_n
+\beta_{\rm H}\cdot D_0e_n
}{1-\beta_{\rm H}\cdot e_n}.
\]

The aberration and its derivative are evaluated at finite tilt; no
small-beta expansion is used.

## Chart lifts

### Bianchi II / class A

\[
\Sigma_{ab}=\mathrm{diag}
(-2\Sigma_+,\Sigma_++\sqrt3\Sigma_-,
\Sigma_+-\sqrt3\Sigma_-),
\]

\[
N_{ab}=\mathrm{diag}(N_1,N_2,N_3),
\quad A_a=R_a=0.
\]

### Tilted class B / Hervik gauge

\[
N_{ab}=
\begin{pmatrix}
0&0&0\\
0&\sqrt3\lambda N&\sqrt3N\\
0&\sqrt3N&\sqrt3\lambda N
\end{pmatrix},
\quad
A_a=(A,0,0),
\]

\[
R_a=(\sqrt3\lambda\Sigma_-,
-\sqrt3\Sigma_{13},
\sqrt3\Sigma_{12}).
\]

The chart tilt is used as \(\beta_{\rm H}\), with
\(D_0\beta_{\rm H}=H\beta_{\rm H}'\).

### Exceptional VI_-1/9 / HHW gauge

\[
\Sigma_{13}=\Sigma_2,
\quad\Sigma_{23}=\Sigma_\times,
\quad\Sigma_{12}=0,
\]

\[
N_{22}=2\sqrt3N_-,
\quad N_{23}=3A,
\quad N_{33}=0,
\]

\[
R_a=(-\sqrt3\Sigma_\times,-\sqrt3\Sigma_2,0).
\]

This lift was independently closed against the primitive general-chart
RHS before release.

## Moving Doppler boundary

For \(x=(\nu_{\rm H}-\nu_{\rm abs})/\Delta\nu_D\),

\[
\mathcal A
=\frac{\nu_{\rm H}\mathcal R_{\rm H}-D_0\nu_{\rm abs}}
{\Delta\nu_D}
-xD_0\ln\Delta\nu_D-D_0x_{\rm boundary}.
\]

Every zero of \(\mathcal A_{R/B,q}\) splits the timestep and changes the
upwind trace. The piecewise-linear regression integrates each branch
exactly and closes the combined interior/red/blue number and
four-momentum ledger.

## Microphysics firewall

The v0.47 collision conductance, Bose action and same-event four-force
are consumed without any geometry argument. Bianchi dependence enters
only through the characteristic and boundary-speed adapter.
