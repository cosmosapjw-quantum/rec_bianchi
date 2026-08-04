# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The current durable endpoint is **PR-02 / v0.49**. **PR-01 and PR-02 are complete.**

## Closed in v0.49

- Connected the inherited v0.47 nonlinear stimulated Bose edge action to actual v0.48 `BackgroundSnapshot` states.
- Locked the adaptive positive-weight angular lanes: `L=12` for finite/mixed tilt, `L=20` for nonlinear even shear, and `L=24` for directional red/blue crossing.
- Used the 302-, 590-, and 974-point positive Lebedev rules for the three lanes.
- Added exact analytic collision JVPs and exact matrix-free backward-Euler residual JVPs.
- Added a log-occupation Newton–GMRES update, so every accepted nonlinear iterate is strictly positive without clipping or post-step number renormalization.
- Closed exact discrete Bose–Einstein null, photon-number, boundary-edge number, free-energy dissipation, implicit positivity, implicit number and same-event total four-force gates.
- Verified the PR-01 microphysics firewall: a common hydrogen-frame field gives a bitwise-identical local collision action for Bianchi II, tilted VI_h, and exceptional VI_-1/9 snapshots.
- Added deterministic full-network scientific evidence, compact CI tests, an independent 80-digit `mpmath` receipt, a manifest, and an immutable stage ZIP.

## Representative hard results

| Quantity | Result |
|---|---:|
| Maximum BE action relative residual | `8.8144e-16` |
| Maximum photon-number residual | `8.0183e-18` |
| Maximum boundary-number residual | `8.6653e-18` |
| Maximum collision JVP relative residual | `6.5349e-11` |
| Maximum implicit-residual JVP residual | `3.8515e-11` |
| Maximum implicit residual | `1.7038e-14` |
| Minimum implicit occupation | `2.1987e-01` |
| Largest explicit stress-step minimum | `-1.4962e-02` |
| Largest implicit free-energy change | `-4.0490e+15` |
| Minimum quadrature weight | `1.4383e-04` |
| Maximum harmonic Gram residual | `3.1260e-15` |
| Maximum frame round-trip residual | `3.9540e-16` |
| Hydrogen-frame total four-force residual | `0` |
| Normal-frame total four-force residual | `0` |
| Geometry-to-local-collision action difference | `0` |
| Maximum 80-digit reference residual | `2.1084e-81` |

The released stress timestep is 1.02 times the first explicit-Euler positivity limit. Explicit Euler becomes negative in all three lanes, while the converged implicit result stays strictly positive, preserves the discrete photon number, and decreases the released free-energy functional.

## Architecture locked through PR-02

Bianchi geometry enters local recombination only through the physical tetrad snapshot

\[
\mathcal B=
\{H,q,\sigma_{ab},N_{ab},A_a,R_a,
\beta_{\rm H}^a,D_0\beta_{\rm H}^a\}.
\]

It determines normal- and hydrogen-frame characteristics, aberration, direction flow, red/blue boundary speeds, and branch events. It is not an argument of the local scalar atomic amplitude or conductance table.

The nonlinear collision state uses the activity

\[
\phi_{iq}=\frac{f_{iq}}{z_i(1+f_{iq})},
\qquad z_i=\frac{\pi_i}{g_i},
\]

with a common activity-reference subtraction before the harmonic convolution. Pair symmetry provides the discrete photon-number left null. The runtime update solves

\[
\mathcal R(f^{n+1})=
 f^{n+1}-f^n-\Delta t\,C[f^{n+1}]=0
\]

in variables `u = log(f)` with the exact JVP. Photon and atom four-force contributions are formed as opposite parts of the same collision event and transformed independently between the hydrogen and normal tetrads.

## Explicit limitations

- The PR-02 stress occupations are deterministic collision-substep regression fields generated from actual background characteristics; they are not solutions of the coupled Liouville plus recombination system.
- The amplitude is still the provisional unresolved scalar `2p` pole+crossed model. Full bound, continuum, seagull, and interference physics is PR-03.
- Exterior–exterior collisions remain assigned to the boundary/Liouville module, as locked in v0.47.
- This release exercises the three adaptive runtime lanes, not the all-11 automated sweep reserved for PR-10.
- The 80-digit independent receipt uses `mpmath`; Wolfram and Precise Special Functions connectors were not exposed in this runtime.

## Immediate next release

**PR-03 full scalar COM–KHW amplitude** must:

1. replace the provisional unresolved scalar `2p` pole+crossed amplitude with the complete scalar bound-plus-continuum COM–KHW construction;
2. include seagull and interference terms with explicit gauge and reciprocity audits;
3. regenerate the frequency-pair conductance moments without changing the PR-01/PR-02 geometry and nonlinear-update interfaces;
4. rerun BE, number, entropy/free-energy, positivity, JVP, boundary-event and same-event four-force regressions;
5. publish the implementation, tests, formalism, ledger, numerical evidence, manifest, immutable ZIP, commit, remote-check receipt and binary-safe patch exports.

## Repository synchronization

The owner reports that v0.47 was expanded and merged into the private `main`. This runtime exposes neither a GitHub connector function nor a working SSH/HTTPS Git route, so the exact remote merge SHA remains independently unverified. The v0.49 delivery therefore includes a cumulative patch from the exact local v0.47 base, an incremental patch from the exact local v0.48 parent, and a standalone full bundle. Apply only on a feature branch after fetching remote `main`; never force-push shared history.
