# PR-01B0 bridge-gate supersession

## Original gate

The original PR-01 plan required the exact microscopic recoil-event
Kramers–Moyal drift to approach the v0.33 line-centre drift within
\(10^{-6}\).

That gate is invalid.

## Root cause

The two compared objects have different definitions.

### Microscopic event recoil

In the initial atom rest frame,

\[
\Delta x(\mu)
=
-\frac{g(1-\mu)}
{1+g b_D(1-\mu)}.
\]

For the normalized Rayleigh phase

\[
p(\mu)=\frac38(1+\mu^2),
\]

\[
\langle1-\mu\rangle=1,
\qquad
\langle(1-\mu)^2\rangle=\frac75,
\qquad
\langle(1-\mu)^3\rangle=\frac{11}{5}.
\]

Hence

\[
\boxed{
\langle\Delta x\rangle
=
-g+\frac75 b_Dg^2-\frac{11}{5}b_D^2g^3+\cdots.
}
\]

At the locked \(T_m=3000\,{\rm K}\) parameters,

\[
\langle\Delta x\rangle_{\rm event}
=
-4.629199542864045\times10^{-4}.
\]

### v0.33 thermodynamic completion

v0.33 starts from a symmetric no-recoil finite-volume Hummer proposal
\(B_{ij}\) and constructs

\[
W_{ij}=B_{ij}\sqrt{\Pi_i/\Pi_j}.
\]

Its line-centre drift is

\[
\boxed{
M_1^{\rm v0.33}
=
(b_D-g)M_2
=
-1.4464018889\times10^{-4}.
}
\]

This is a detailed-balance/Fokker–Planck closure. It is not the direct
angular mean of one microscopic recoil event.

The relative difference is

\[
0.6875481656.
\]

## Shift-only Hummer diagnostic

A finite-volume Hummer kernel with the exact rest-frame recoil shift
reproduces the no-recoil v0.32 line column to

\[
4.15\times10^{-13},
\]

and gives the converged drift

\[
M_1^{\rm shift}
=
-4.5615156778\times10^{-4}.
\]

However, its pairwise thermal-balance residual is

\[
2.16\times10^{-5}.
\]

Thus simply shifting the Hummer Gaussian is not a production event
kernel. The full forward/reverse event weight must include the
Kramers–Heisenberg \(\nu_f/\nu_i\) factor, Maxwellian incident-state
measure, exact resonance arguments, aberration/Jacobian factors, and
the reverse-event construction in one phase-space measure.

## Superseded and replacement gates

### Superseded

\[
\text{exact-event drift}
=
\text{v0.33 drift}
\quad\text{within }10^{-6}.
\]

### Replacement

1. Exact Rayleigh recoil moments agree with the analytic angular
   integral to \(10^{-12}\).
2. Forward and independently reconstructed reverse event weights obey
   pairwise detailed balance to \(10^{-12}\).
3. The exact event kernel reduces to the microscopic Basko recoil
   moments when the thermal velocity is turned off.
4. v0.33 remains an independent Bose-equilibrium and Fokker–Planck
   closure comparator.
5. The exact event kernel and v0.33 are compared as distinct operators;
   neither is forced to equal the other outside their common controlled
   limit.

## Status

\[
\boxed{\text{PR-01B0 root-cause audit}=\mathrm{PASS}}
\]

\[
\boxed{\text{original v0.33 equality gate}=\mathrm{SUPERSEDED}}
\]

\[
\boxed{\text{shift-only Hummer kernel}=\mathrm{REJECTED\ FOR\ PRODUCTION}}
\]

\[
\boxed{\text{full Maxwellian microreversible event kernel}=\mathrm{OPEN}}.
\]
