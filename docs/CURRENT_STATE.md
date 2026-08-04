# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The current durable endpoint is PR-01B1-B3B3A (v0.45).

## Completed foundations

- Tetrad and 1+3 Bianchi characteristic structure and all-11 registry.
- Exact finite-tilt normal/hydrogen frame adapter and direction-dependent red/blue branch contract.
- Dynamic red/interior/blue boundary state and four-momentum ledger.
- HYREC-2 source/data contract and native 2s/2p+311 sparse block audit.
- Continuous-mu harmonic/Nystrom Hummer-II reference.
- Two-sided finite-volume frequency kernel and adaptive ell-max policy.
- Rybicki thermodynamic completion, Bose stimulation, entropy identity.
- Exact elastic recoil kinematics and PT reverse reconstruction.
- Lorentz-invariant Maxwell-Juttner photon-pair measure.
- Analytic Faddeeva pole and pole+crossed conditional averages.
- All 136 distinct-cell unordered pairs through ell=6.
- All 17 same-cell regularized angular remainders through ell=24.

## Open blocker for PR-01

The red/blue exterior scattering block and its same-event photon/hydrogen four-force have not yet been integrated into the full scalar collision operator. The current interior block is not a production release without that exterior closure.

## Immediate next release

PR-01B1-B3B3B must combine:

1. v0.44 off-diagonal pair conductance;
2. v0.45 same-cell regularized angular block;
3. red/blue exterior conductance and four-force;
4. adaptive L=12/20/24 collision actions;
5. BE, number, equilibrium, entropy, positivity, quadrature, ell-tail, and four-force gates.

After this, PR-01C applies the primitive `BackgroundSnapshot` finite-tilt/large-shear frame adapter and closes PR-01.
