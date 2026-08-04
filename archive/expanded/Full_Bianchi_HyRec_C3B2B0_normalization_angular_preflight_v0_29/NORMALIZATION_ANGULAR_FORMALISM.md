# C3B2B0 absolute normalization and angular preflight

## 1. Cross-section convention

The dimensionless scalar hydrogen amplitude is normalized by

\[
\sigma_{\rm tot}(\nu)
=
\sigma_T|\mathcal M_{\rm KH}(\nu)|^2.
\]

For the Rayleigh phase,

\[
\frac{d\sigma}{d\Omega}
=
\frac{3\sigma_T}{16\pi}
(1+\mu^2)
|\mathcal M_{\rm KH}|^2.
\]

With the normalized sphere measure \(d\Omega/(4\pi)\), the angular
factor is

\[
\Phi_R(\mu)=\frac34(1+\mu^2),
\qquad
\int\frac{d\Omega}{4\pi}\Phi_R=1.
\]

The oscillator-strength opacity is

\[
\sigma_\nu
=
\pi r_ec f_{12}\phi_\nu,
\qquad
\int d\nu\,\phi_\nu=1.
\]

Hence

\[
\int d\nu\,\sigma_\nu
=
\pi r_ec f_{12}.
\]

Near the Ly-alpha pole, if

\[
A_{21}
=
\frac{8\pi^2r_ef_{12}\nu_\alpha^2}{3c},
\]

the Kramers-Heisenberg Lorentzian integrates to the same result exactly.

## 2. Gas rate

The physical event rate is

\[
d\Gamma
=
n_{1s}c_{\rm rel}\,d\sigma.
\]

For a moving atom, \(c_{\rm rel}\) is represented by the incident
Lorentz/invariant flux factor already present in the event-pair
construction. No free global normalization is allowed.

## 3. Why a previous relative conductance cannot simply be rescaled

A physical regeneration must apply the cross-section prefactor before
frequency-angle cell integration. A posterior global scaling cannot
repair missing endpoint measures, incident flux factors, or
frequency-dependent normalization.

## 4. Angular preflight

The preflight kernel is the normalized zonal function

\[
K_\kappa(\mu)
\propto
\frac34(1+\mu^2)e^{\kappa\mu}.
\]

It is not the production COM-KHW kernel. It tests how a Lebedev rule
handles a non-polynomial increasingly forward-peaked angular
dependence.

The result shows that 38 and 50 points are intermediate diagnostics,
not universal release grids. The actual physical kernel must be
recomputed at several angular orders until isotropic and anisotropic
actions converge.
