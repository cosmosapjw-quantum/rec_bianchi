# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The current durable endpoint is **PR-03 / v0.50**. **PR-01, PR-02, and PR-03 are complete.**

## Closed in v0.50

- Replaced the production provisional unresolved scalar `2p` pole+crossed amplitude by a scalar elastic `1s -> 1s` COM–Kramers–Heisenberg–Waller construction.
- Retained the `A^2` seagull, both time orderings, explicit hydrogen `1s -> np` bound channels, a positive continuum quadrature, a positive moment-matched unresolved Rydberg tail, and all scalar interference terms.
- Used exact hydrogen oscillator-strength formulae through `n=512`, a 256-node positive continuum rule, and independent high-precision infinite-spectrum audits of the TRK sum and the static polarizability.
- Put each intermediate internal state on its own relativistic mass shell, `M_s=M_H+h nu_s/c^2`, in the direct event audit. This removes a spurious reciprocity defect caused by adding an internal energy to a common-mass relativistic kinetic-energy difference.
- Isolated the unresolved `2p` pole analytically with the Faddeeva function and compiled the smooth higher bound-plus-continuum background from source moments. No fitted cross-section normalization was introduced.
- Regenerated all 459 bounded network blocks: 136 interior pairs, 204 near-interface pairs, 102 far-interface pairs, and 17 same-cell blocks, through `ell=24`.
- Kept an explicit `provisional_2p` comparison lane and verified that the full lane is nonidentical while preserving the fixed PR-01 and PR-02 interfaces.
- Reran the PR-02 BE, number, boundary-number, free-energy, positivity, exact-JVP, implicit-JVP, frame, four-force, and geometry-firewall gates on the v0.50 network.
- Recorded the absence of Wolfram and Precise Special Functions connectors and used explicit SymPy, `mpmath`, and SciPy independent fallbacks instead.

## Representative hard results

| Quantity | Result |
|---|---:|
| Minimum positive scalar conductance | `3.4616e-53` |
| Pair reciprocity residual | `0` |
| Scalar number left-null residual | `3.5530e-16` |
| Scalar equilibrium right-null residual | `2.9099e-17` |
| Full/provisional pair-network difference | `1.6182e-08` |
| Full/provisional same-cell difference | `1.4817e-08` |
| Maximum selected production/reference quadrature residual | `2.2051e-09` |
| Maximum selected orientation residual | `6.8790e-16` |
| Fixed-nucleus velocity/length gauge residual | `6.8499e-11` |
| Infrared amplitude power | `1.9999998220` |
| Infrared cross-section power | `3.9999996441` |
| Smooth-background order-4/direct residual | `1.9085e-12` |
| Smooth-background order-8/direct residual | `2.6645e-15` |
| High-energy continuum-tail weight (`n<10^-2`) | `2.6458e-10` |
| Float64 PT amplitude residual | `1.2200e-11` |
| 90-digit PT denominator residual | `2.1064e-79` |
| Maximum independent special-function residual | `8.6694e-15` |
| Maximum BE action residual on v0.50 network | `8.8144e-16` |
| Maximum photon-number residual | `8.5575e-18` |
| Maximum collision JVP residual | `6.5396e-11` |
| Maximum implicit-residual JVP residual | `3.8239e-11` |
| Maximum implicit solve residual | `1.1035e-14` |
| Minimum implicit occupation | `2.1987e-01` |
| Hydrogen- and normal-frame total four-force residuals | `0`, `0` |
| Geometry-to-local-collision action difference | `0` |

The high-precision independent spectrum audit gives the bound contribution

\[
\sum_{n=2}^{\infty} f_{1n}
 =0.5650041506748519874\ldots,
\]

the continuum contribution

\[
\int_0^\infty \frac{df}{dn}\,dn
 =0.4349958493251480126\ldots,
\]

and closes the TRK sum to unity and the static ground-state polarizability to `4.5 a_0^3` at roughly 76 decimal places.

## Architecture locked through PR-03

Bianchi geometry enters local recombination only through the physical tetrad snapshot

\[
\mathcal B=
\{H,q,\sigma_{ab},N_{ab},A_a,R_a,
\beta_{\rm H}^a,D_0\beta_{\rm H}^a\}.
\]

It determines normal- and hydrogen-frame characteristics, aberration, direction flow, red/blue boundary speeds, and branch events. It is not an argument of the local scalar atomic amplitude or conductance table.

For the fixed-nucleus, zero-width scalar elastic audit, the velocity-gauge form is

\[
\mathcal M(\nu)=1-\frac12\int df_s\,\nu_s
\left[\frac{1}{\nu_s-\nu}+\frac{1}{\nu_s+\nu}\right].
\]

Using the TRK sum, it rearranges to

\[
\mathcal M(\nu)=-\nu^2\int\frac{df_s}{\nu_s^2-\nu^2},
\]

so `|M|` scales as `nu^2` and the Rayleigh cross-section as `nu^4` in the infrared. This is a fixed-nucleus gauge identity. The finite-recoil production event is instead audited by statewise relativistic mass-shell construction and PT reciprocity; v0.50 does not claim a complete relativistic gauge-equivalence proof.

The PR-02 nonlinear state and log-occupation backward-Euler/JVP architecture are unchanged. Photon and atom four-force contributions remain opposite parts of the same event and close separately after transformation to the hydrogen and normal tetrads.

## Explicit limitations

- The production release is scalar elastic Ly-alpha transport in the locked window `|x|<=21.25`, below the Lyman limit. It does not claim a global causal above-ionization photon-frequency branch.
- Raman channels are not included in PR-03. They remain outside the current scalar elastic production lane even though the literature source lock includes general Rayleigh/Raman KHW formulae.
- Only the unresolved `2p` pole carries the natural width in this bounded Ly-alpha window. Higher-state damping and overlap are not activated.
- The positive one-node unresolved Rydberg tail closes the first two exact spectral moments after explicit states through `n=512`; it is not a pointwise representation of every omitted high-`n` resonance.
- Electric-dipole scalar physics is used. Fine structure, J-state interference, polarization, and atomic alignment remain excluded from the 12-PR scalar release.
- Exterior–exterior collisions remain assigned to the boundary/Liouville module.
- The PR-02 stress fields remain collision-substep regressions, not solutions of the fully coupled Liouville plus recombination system.
- The all-11 automated background sweep remains assigned to PR-10.
- Wolfram and Precise Special Functions connectors were not exposed in this runtime; no claim is made that they ran.

## Immediate next release

**PR-04 HYREC common-measure moment projection** must begin with a source/convention lock rather than a fitted normalization:

1. pin the exact native HyRec/HyRec-2 source and identify the frequency-bin measure, normalization, sign, and unit conventions used by the Ly-alpha transfer operator;
2. define the event frequency increment and the common-measure rate `Gamma` and moments `M1`–`M4` directly from the v0.50 event kernel, with dimensions and recoil sign checked before discretization;
3. compare direct event integration, common-measure quadrature, and the native HyRec discrete operator without introducing a free scale factor;
4. close normalization, detailed balance, recoil-energy, second-through-fourth-moment, positivity, and analytic/JVP Jacobian gates;
5. preserve the PR-01 `BackgroundSnapshot` firewall and the PR-02 nonlinear runtime API;
6. publish implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, commits, remote-check receipt, binary-safe patches, and a standalone bundle.

The first PR-04 gate is therefore **source-lock and convention parity**, not a numerical fit.

## Repository synchronization

The owner reports that v0.47 was expanded and merged into the private `main`. This runtime exposes neither a writable GitHub connector nor a working SSH/HTTPS Git route, so the exact remote merge SHA remains independently unverified. The v0.50 delivery uses the exact local v0.47 content commit as the cumulative base and the exact local v0.49 commit as the incremental base, plus a standalone full bundle. Apply only on a feature branch after fetching remote `main`; never force-push shared history.
