# PR-04C0/C1A split-domain boundary formalism

## Scope

This bounded v0.55 release closes the operator-ownership theorem and extracts
source-identical red/blue packets at `x=+-21.25` for the predeclared original-
HyRec snapshots near z=1300,1100,900. It does **not** deposit those packets into
the 35-state COM--KHW far-boundary/Liouville state; PR-04C1B/C2 remains open.

## Conventions and dimensions

`g=(-,+,+,+)`, hydrogen tetrad, ordinary frequency `nu` in Hz,
`x=(nu-nu_Lya)/Delta_nu_D`, and all `c,h,k_B` factors remain explicit. The
physical logarithmic-frequency mode factor is

`N_y = 8*pi*nu^3 f/(c^3 n_H)`.

Each packet carries positive total photon-number flux `Phi_N` in H^-1 s^-1
and transported photon-energy flux `Phi_E=h*nu*Phi_N` in W H^-1. The Planck
reference is nonnegative; the nonthermal distortion may be signed as long as
the total packet remains positive.

A computational representation crossing is not a new atom-photon event.
Consequently its atomic source is exactly zero. Atomic recoil remains owned by
the local COM--KHW collision or original-HyRec real/virtual operator. This
corrects the preliminary plan's conflation of transported absolute photon
energy with a collision energy increment. Global interface conservation is

`Phi_N_native + Phi_N_COM = 0`,
`Phi_E_native + Phi_E_COM = 0`,
`Phi_E_atom(interface) = 0`.

## Source-identical interface reconstruction

For an interface energy `E_I`, the least canonical native energy `E_s>E_I`
is selected. Free streaming gives the query time

`ln a_q = -ln[(1+z) E_s/E_I]`.

The October-2012 source's positive two-point linear history interpolation is
used without a fitted scale. At some interfaces `ln a_q` lies between the
previous and current trajectory endpoints. Diagnostics are emitted only after
`Dfminus_hist[:,iz]` has been solved, so `history_index_right==iz` is valid and
source-identical. Rejecting that endpoint would create a false range failure;
using any future endpoint remains forbidden.

## Ownership

Exactly one owner is assigned to native free streaming/escape/real-virtual
algebra, COM collision/Bose/recoil, COM internal Liouville transport, analytic
Planck reference, and the red/blue cross-interface terms. Each packet is
evaluated once and applied twice with opposite signs. Replacement switch OFF
returns exact state copies and a zero ledger.

## Results

- packets: 6;
- maximum independent reconstruction residual: 1.6537648327370854e-16;
- current-endpoint interpolation cases: 4;
- number and photon-energy global residuals: exactly zero;
- atom source at computational interfaces: exactly zero;
- Bianchi-label local-state firewall: exactly zero.

The Wolfram symbolic audit gives backward-Euler positivity, exact opposite-sign
number/energy cancellation and `Integral x^2/(exp(x)-1) dx = 2 Zeta(3)`. The
100-digit Precise Special Functions values agree with independent 120-digit
mpmath references at the residuals recorded in the ledger.
