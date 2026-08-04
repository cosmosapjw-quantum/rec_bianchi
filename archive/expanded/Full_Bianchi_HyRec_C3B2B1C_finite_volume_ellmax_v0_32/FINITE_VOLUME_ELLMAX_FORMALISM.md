# C3B2B1-C two-sided finite-volume and ellmax lock

## Two-cell formula

For \(x=u+v\), \(x'=u-v\),

\[
dx\,dx'=2\,du\,dv.
\]

For \(I_i=[a_i,b_i]\), \(I_j=[a_j,b_j]\),

\[
u\in[(a_i+a_j)/2,(b_i+b_j)/2],
\]

\[
v_{\min}(u)=\max(a_i-u,u-b_j),
\qquad
v_{\max}(u)=\min(b_i-u,u-a_j).
\]

With \(\mu=1-2s^2\), \(c_\theta=\sqrt{1-s^2}\),

\[
\boxed{
\overline{\mathcal R}_{ij}(s)
=
\frac{1}{\Delta x_j}
\frac{1}{2\sqrt{\pi}c_\theta}
\int du\,
H\left(\frac{a}{c_\theta},\frac{u}{c_\theta}\right)
\left[
{\rm erf}\frac{v_{\max}}s-
{\rm erf}\frac{v_{\min}}s
\right].
}
\]

The unknown is the source-cell average occupation.

## Coherent limit

\[
\overline{\mathcal R}_{ij}
\to
\frac{\delta_{ij}}{\Delta x_j}
\int_{I_j}\phi_x(x')\,dx'.
\]

No incoming-frequency centre sample remains.

## Harmonic kernel

\[
K_\ell(i,j)
=
\frac12\int_{-1}^{1}d\mu\,
\Phi_R(\mu)P_\ell(\mu)
\overline{\mathcal R}_{ij}(\mu).
\]

\[
C_{\ell m}
=
n_{1s}c\frac{\pi r_ecf_{12}}{\Delta\nu_D}
K_\ell F_{\ell m}
-\Gamma_{\rm cap}F_{\ell m}.
\]

## Adaptive ellmax

The bounded nonlinear audit gives:

- finite tilt \(\beta=0.3\): \(L=12\);
- mixed tilt/shear: \(L=12\);
- strongly nonlinear even shear: \(L=20\);
- direction-dependent red/blue crossing: \(L=24\).

The solver monitors the omitted collision-action norm rather than using
one global bandlimit.

## Harmonic-exact grids

- \(L=12\): Lebedev order 25, 230 points;
- \(L=20\): order 41, 590 points;
- \(L=24\): order 53, 974 points.
