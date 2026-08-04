# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The current durable endpoint is **PR-01B1-B3B3B1 (v0.47)**.

## Newly closed in v0.47

- Regenerated all 136 interior off-diagonal unordered conductance pairs through `ell=24`.
- Added 102 direct interior/far-interface pairs over `10.25<|x|<=21.25`.
- Combined 17 interior, 12 near-exterior and 6 far-exterior states into one 35-state core-to-boundary network.
- Closed scalar positivity, reciprocity, photon-number and thermal-equilibrium gates.
- Closed the far-tail gate: the outer adaptive bin contributes `9.04e-25` of the full generator norm and the continuation bound is `7.70e-29`.
- Recast nonlinear Bose scattering in an activity-reference-subtracted harmonic form, avoiding catastrophic near-equilibrium subtraction.
- Closed discrete BE, nonlinear number, entropy and total four-force gates.
- Locked adaptive nonlinear policies: `L=12` for finite tilt and mixed tilt/shear, `L=20` for nonlinear even shear, and `L=24` for directional red/blue crossing.
- Replaced the negative-weight 230-point `L=12` nonlinear grid by the positive-weight 302-point rule.

## Explicit scope boundary

Near/far exterior states carry resonant-scattering conductance to the interior core. Exterior–exterior collisions remain assigned to the boundary/Liouville transport module and are not silently included. The amplitude remains the provisional unresolved scalar `2p` pole+crossed model; full bound+continuum KHW physics is PR-03.

## Immediate next release

**PR-01C BackgroundSnapshot frame-adapter closure** must:

1. load finite-tilt, nonlinear-shear and turning/crossing snapshots from the supplied primitive Bianchi solver;
2. convert normal-frame characteristics to hydrogen-frame `R_H`, direction flow and red/blue boundary speeds;
3. run Bianchi II, one class-B model and exceptional `VI_-1/9` smoke regressions;
4. close branch localization, photon number and total four-force without changing local collision microphysics;
5. publish the PR-01 closure ledger and patch series.

## Repository synchronization

The owner configured private-repository access in the ChatGPT GitHub app. This standard chat runtime still did not expose a GitHub connector function, so the live remote ref/tree was not available for verification. The local v0.46 full bundle was fresh-cloned and used as the verified parent of v0.47. Run `scripts/check_remote_state.py` again when the connector or normal Git network path is available.
