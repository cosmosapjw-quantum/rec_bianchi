# C3B2A substitution firewall

## C runtime parity

The standalone C solver agrees with the C3B1 Python Schur solution at
\(2.77\times10^{-15}\) relative error.

## The native \(T_{vv}\) diagonal is not additive

HYREC stores

\[
(T_{vv})_{bb}
=
\frac{\Gamma_b}{1-P(\Delta\tau_b)},
\qquad
\Delta\tau_b\propto\Gamma_b.
\]

Therefore

\[
F(\Gamma_{\rm true}+\Gamma_{\rm diff})
\ne
F(\Gamma_{\rm true})+F(\Gamma_{\rm diff}).
\]

Its small-optical-depth nonadditivity starts as

\[
F(g_1+g_2)-F(g_1)-F(g_2)
=
c g_1g_2
+\frac{c^2}{4}g_1g_2(g_1+g_2)+\cdots.
\]

The completed escape-compressed matrix cannot be lifted and patched.

## Entire native Ly-alpha transport sector to retire

The Bianchi production lane must jointly replace:

1. Sobolev \(R_{\rm Ly\alpha}\) in the \(2p\) diagonal;
2. the \(Df^+_{\rm Ly\alpha}\) feedback source;
3. virtual \(A^\uparrow,A^\downarrow\) diffusion;
4. the two line-centre \(2p\)-neighbor couplings;
5. the escape-compressed virtual diagonal and source;
6. the FLRW `fplus_from_fminus` Ly-alpha closure.

It is replaced by explicit Liouville transport, dynamic exterior states,
full-angle COM–KHW redistribution, and the same-edge matter four-force.

The native \(A_{2s}\), \(A_{3s3d}\), and \(A_{4s4d}\) true
two-photon/Raman couplings remain.

## Angular lift

With normalized angular weights,

\[
J=I_\nu\otimes\mathbf1,
\qquad
A=I_\nu\otimes w^T,
\qquad
AJ=I_\nu.
\]

The lifted real–radiation blocks satisfy

\[
\widetilde T_{rv}J=T_{rv},
\qquad
A\widetilde T_{vr}=T_{vr}.
\]

The positive native-to-fine remap in this bundle preserves both forward
and reverse integrated true rates to roundoff.

## Two remaining release blockers

### Angular order

Lebedev-26 preserves number and equilibrium and has an exact restricted
frequency operator, but an isotropic non-equilibrium spectrum develops
discrete angular leakage:

- smooth \(L=8\): \(2.19\times10^{-3}\);
- narrow core: \(7.43\times10^{-3}\).

Posterior angular balancing changes anisotropic actions by up to
\(1.48\%\), so it is rejected.

### Absolute normalization

The inherited COM–KHW conductance is not yet an \(s^{-1}\) operator.
Matching its coarse second moment to the native HYREC diffusion block
requires scale factors spanning more than \(3.1\times10^3\); one global
fit leaves a \(0.251\) relative residual.

A first-principles differential-cross-section prefactor and a common
discrete Fokker–Planck-limit regression are required before substitution.
