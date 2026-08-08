# PR-05C2C1B1 source-adapter and full-withheld formalism

## Scope and conventions

The metric signature is `(-,+,+,+)`.  Frequency is ordinary `nu` in Hz and
`c`, `h`, and `k_B` remain explicit.  The stage is scalar, unpolarized and
homogeneous, with finite tilt and nonlinear large shear entering only through
`BackgroundSnapshot` characteristics.

## Canonical original-HyRec virtual spike

The October-2012 source defines a distributional virtual-state update

\[
 f^- = f^+ + (f^{\rm eq}-f^+)\left(1-e^{-\tau}\right).
\]

On a fixed directional branch with local speed
\(r=-d\ln\nu/dt\ne0\), the optical depth is

\[
 \tau_{\rm dir}=\tau_{\rm FLRW}\frac{H}{|r|}.
\]

A zero or sign change of `r` is an event; it is never differentiated through.
The implementation uses `expm1` and an analytic JVP.  This adapter is
source-identical to `HyRec/hydrogen.c` at the locked source lines.

## Positive paired one-photon line model

The v0.65 scalar source-isotropy axiom permits a separate physical line adapter

\[
 C[f]=\eta(1+f)-\kappa f,
\]

with

\[
 \eta=\frac{c^3 n_H}{8\pi\nu^2}A_{ul}\phi(\nu)x_u,\qquad
 \kappa=\frac{c^3 n_H}{8\pi\nu^2}A_{ul}\phi(\nu)
 \frac{g_u}{g_l}x_l.
\]

Both rates are nonnegative.  In LTE,
\(x_u/x_l=(g_u/g_l)e^{-h\nu/(k_BT_H)}\), and the Planck occupation is an exact
null.  This paired-rate model is a theory-contract source adapter; it is not
relabelled as an explicit coefficient decomposition stored by original HyRec.

The phase-space prefactor gives `[eta]=[kappa]=s^-1`.  With positive normalized
angular weights summing to one, isotropic deposition requires no extra
`1/N_angle` factor.

## Characteristic face transfer

The directional radiation field is evolved along the exact finite-tilt Bianchi
characteristic.  Native face data are initial-boundary-value data, not an
instantaneous scalar-to-angular inversion.  A requested face that is not
forward-reachable fails closed; frequency-speed zeros require event
localization and restart.

## Full withheld thermodynamic audit

The z~1100 direct node is withheld from the z~900/z~1300 family.  Every 442
unordered pair block and all 17 same-cell blocks are compared.  Three error
classes are retained separately: event-mass weighted scalar error, maximum
active-edge relative error, and operator-moment/same-cell errors.  This audit is
a validation witness and does not replace direct production compilation.

## Claim boundary

This stage completes the canonical spike adapter, a positive physical
one-photon source contract, source-derived face characteristics, and a full
withheld-node audit.  It does not yet close the canonical two-photon/Raman
source decomposition, select a faster AP/Schur preconditioner, or run a
four-or-more-macro trajectory.
