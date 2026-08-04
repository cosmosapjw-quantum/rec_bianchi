# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The current durable endpoint is **PR-01B1-B3B3B0 (v0.46)**.

## Completed foundations

- Tetrad and 1+3 Bianchi characteristic structure and all-11 registry.
- Exact finite-tilt normal/hydrogen frame adapter and direction-dependent red/blue branch contract.
- Dynamic red/interior/blue boundary state and four-momentum ledger.
- HYREC-2 source/data contract and native 2s/2p+311 sparse block audit.
- Continuous-mu harmonic/Nystrom Hummer-II reference.
- Two-sided finite-volume frequency kernel and adaptive ell-max policy.
- Rybicki thermodynamic completion, Bose stimulation and entropy identity.
- Exact elastic recoil kinematics and PT reverse reconstruction.
- Lorentz-invariant Maxwell–Jüttner photon-pair measure.
- Analytic Faddeeva pole and pole+crossed conditional averages.
- All 136 distinct interior-cell unordered pairs through ell=6.
- All 17 same-cell regularized angular remainders through ell=24.
- All 204 interior/near-exterior unordered pairs through ell=24 over `|x|<=10.25`.
- Near-exterior scalar number/equilibrium, dilute entropy and same-event transfer ledgers.

## Open blocker for PR-01

The near red/blue interface is closed, but direct interior scattering jumps beyond `|x|=10.25` are not yet in the far-boundary ledger. The nonlinear anisotropic Bose action has also not yet been regenerated on the adaptive `L=12/20/24` harmonic-exact grids with exterior states.

## Immediate next release

PR-01B1-B3B3B1 must:

1. integrate direct far jumps beyond `|x|=10.25`;
2. combine interior, near-exterior and far-boundary ledgers;
3. apply nonlinear Bose edge flux on `L=12/20/24` grids;
4. require BE null, photon number, entropy, positivity, ell-tail and total four-force gates;
5. then run PR-01C against the primitive `BackgroundSnapshot` finite-tilt/large-shear adapter.

## Repository synchronization

The current sandbox cannot resolve `github.com`, so remote `main` is unverified. Patch exports are anchored to the fresh-clone-verified local base declared in `state/PATCH_BASE.json`. Run `scripts/check_remote_state.py` at the start and end of every bounded stage.
