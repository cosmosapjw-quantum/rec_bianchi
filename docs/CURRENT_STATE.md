# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The current durable endpoint is **PR-01C / v0.48**, and **PR-01 is complete**.

## Closed in v0.48

- Added a chart-independent `BackgroundSnapshot` physical tetrad interface.
- Added adapters for primitive Bianchi II/class A, tilted class-B VI_h, and exceptional VI_-1/9 charts.
- Verified the exact finite-tilt normal-frame to hydrogen-frame frequency characteristic.
- Verified the exact aberrated direction derivative.
- Evolved three nonlinear homogeneous background trajectories from the supplied primitive solver.
- Located one or two red/blue boundary-speed roots in every representative model.
- Closed segment-local branch integration to `7.66e-16` relative residual.
- Preserved photon number and boundary four-momentum exactly.
- Demonstrated that the inherited v0.47 local collision action is unchanged across Bianchi types.
- Closed PR-01 and advanced the active roadmap to PR-02.

## Representative hard results

| Quantity | Maximum / minimum result |
|---|---:|
| Primitive constraint residual | `3.13e-13` |
| Finite-tilt frequency residual | `1.49e-11` |
| Finite-tilt direction residual | `1.12e-11` |
| Branch quadrature residual | `7.66e-16` |
| Minimum selected root count | `1` |
| Boundary number residual | `0` |
| Boundary four-momentum residual | `0` |
| Local collision-action difference across models | `0` |

Representative trajectories:

- Bianchi II, class A, large shear;
- Bianchi VI_h, tilted class B, nonlinear shear and finite tilt;
- exceptional VI_-1/9.

## Architecture locked by PR-01

Bianchi dependence enters local recombination only through physical tetrad characteristics:

\[
\mathcal B=
\{H,q,\sigma_{ab},N_{ab},A_a,R_a,
\beta_{\rm H}^a,D_0\beta_{\rm H}^a\}.
\]

The local scalar Ly-alpha collision kernel remains Bianchi-type independent. Geometry changes

- normal-frame frequency drift;
- direction flow;
- hydrogen-frame Doppler adapter;
- red/blue boundary speed and branch events.

It does not modify atomic amplitudes or conductance tables.

## Immediate next release

**PR-02 nonlinear anisotropic Bose collision production integration** must:

1. connect the v0.47 nonlinear Bose edge action to runtime `BackgroundSnapshot` states;
2. use the positive-weight harmonic-exact `L=12/20/24` grids;
3. add positivity-preserving implicit updates and analytic/JVP Jacobian tests;
4. run finite-tilt, nonlinear-shear and directional-crossing trajectories;
5. close BE, photon-number, entropy, positivity and total four-force gates.

## Repository synchronization

The owner reports that v0.47 was expanded and merged into the private `main`. This runtime still exposes neither a GitHub connector function nor a working SSH/HTTPS Git route, so the exact remote merge SHA was not independently verified. Incremental v0.48 artifacts are anchored to the fresh-clone-verified local v0.47 commit `ced7255…`; a raw patch and standalone full bundle are also exported for squash-merge or divergent-history cases. See `docs/GITHUB_PRIVATE_REPO_ACCESS.md`.
