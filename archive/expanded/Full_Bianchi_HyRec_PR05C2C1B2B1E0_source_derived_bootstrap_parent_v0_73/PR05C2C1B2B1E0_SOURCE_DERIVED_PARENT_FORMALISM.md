# PR-05C2C1B2B1E0 source-derived bootstrap-parent formalism

## Scope

This stage constructs a positive angle-frequency parent at the accepted scalar
original-HyRec slice `iz=5127`.  It is an initial
state for the next coupled macro, not a coupled macro endpoint.

## Point-characteristic reconstruction

For target ordinary frequency `nu_t`, convert to the source-rescaled energy

\[
 E_t = h
u_t/(f_{sR}^2m_{eR}).
\]

Choose the least canonical native centre `E_s>E_t` and query the accepted
history at

\[
 \eta_q=-\ln[(1+z_t)E_s/E_t].
\]

The distortion is linearly interpolated on the canonical accepted `ln(a)` grid
and added to the Planck occupation at `E_t`.  No native cell edges and no
native-to-COM conservative remap are inferred.

## Angular initial-data axiom

The accepted scalar field is lifted isotropically in the hydrogen frame.  This
is the explicit scalar/unpolarized initial-data axiom of v0.65, not recovered
original-HyRec angular information.

## Provenance and claim boundary

The parent is bound to exact history, atomic state, dynamic Bianchi-II provider
sequence, direct network and interface hashes.  It passes the v0.72 production
firewall.  Its metadata is permanently marked
`BOOTSTRAP_PARENT_NOT_COUPLED_MACRO_ENDPOINT`; no history append occurs here.

Minimum occupation: `7.27920591328606731e-15`.
Median activity: `9.95763960069027576e+02`.
Initial canonical-macro physical acceptance metric: `1.00000000311328652e+00`.
