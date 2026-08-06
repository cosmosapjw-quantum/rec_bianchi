# PR-04C0/C1A hypothesis audit

## H1 — single ownership

Accepted. Ten declared process groups have one owner each; duplicate, missing
and undeclared ownership fail closed.

## H2 — source-identical fixed-interface sample

Accepted for post-solve diagnostics. Four of six packets require the current
trajectory endpoint as the right interpolation value. This is legitimate only
because `Dfminus_hist[:,iz]` has already been solved and stored at the guarded
diagnostic location. A future endpoint remains forbidden.

## H3 — positive unresolved packet

Accepted. The Planck reference is nonnegative, the distortion is retained as a
signed audit component, and the total occupation/number/energy packet is
strictly positive at all six interfaces.

## H4 — atom-energy companion at a computational interface

The preliminary plan's `Phi_Egamma+Phi_EH=0` interface rule is rejected. It
confused transported absolute photon energy with a collision energy increment.
A representation crossing is not a new atom-photon event; the interface atomic
source is zero. Recoil remains owned by native or COM collision physics.

## H5 — coupled production closure

Open. No packet is deposited into the far-boundary/Liouville state in v0.55.
