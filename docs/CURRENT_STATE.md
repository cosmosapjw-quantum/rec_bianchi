# Current scientific state

## Summary

The project targets a verified scalar Full Bianchi–HyRec solver on spatially homogeneous backgrounds, for all 11 Bianchi types, including finite tilt and nonlinear large shear. The durable endpoint is **PR-04A / v0.51**. PR-01, PR-02, and PR-03 are complete; PR-04 is deliberately still in progress because exact original-HyRec archive/native-stencil parity remains open.

## Closed in PR-04A / v0.51

- Pinned the inherited byte-level HYREC-2 FULL source registry at commit `09e8243d0e08edd3603a94dfbc445ae06cafe139`, including the exact blobs for `hydrogen.c`, `hydrogen.h`, `Alpha_inf.dat`, `R_inf.dat`, and `two_photon_tables.dat`.
- Locked the FULL representation `(2s,2p) + 311 virtual photon states`, including the 80-state Ly-alpha diffusion block at zero-based virtual indices `100..179`.
- Kept ordinary frequency `nu` in Hz and fixed
  `Delta nu = nu_target - nu_source`,
  `Delta E_gamma = h Delta nu`, and
  `Delta E_H = -h Delta nu`.
- Projected all 136 off-diagonal pairs and 17 active same-cell jump measures of the interior core `-4.25 <= x <= 4.25` through fourth frequency order.
- Preserved the accepted v0.50 zeroth pair mass exactly and obtained `M1`–`M4` from independently integrated conditional moment ratios. No HYREC output or free multiplicative normalization was used.
- Enforced exact exchange parity
  `S^(r)_ji = (-1)^r S^(r)_ij`, nonnegative zeroth/even moments, and exact conversion between dimensionless Doppler-coordinate moments and Hz moments.
- Added source-conditioned `Gamma,M1,...,M4`, a conservative scalar Bose edge operator, exact analytic JVP, and a log-occupation backward-Euler update.
- Closed BE, photon-number, free-energy, positivity, same-event photon-plus-atom energy, and common-local-state geometry-firewall gates.
- Retained HYREC-2 primitive `Aup/Adn` diffusion rates as diagnostics only. Direct substitution is forbidden because those rates live inside an escape-compressed real/virtual Schur system.
- Recorded unavailable Wolfram and Precise Special Functions plugins explicitly and used SymPy exact algebra, `mpmath` 80-decimal references, and SciPy positive numerical quadrature as fallbacks.

## Common-measure definition and dimensions

For target cell `i`, source cell `j`, and ordinary-frequency jump

\[
\Delta\nu=\nu_i-\nu_j,
\]

the oriented positive event moments are

\[
S^{(r)}_{ij}=\int_{I_j\to I_i}(\Delta\nu)^r\,d\mathcal S,
\qquad r=0,\ldots,4.
\]

The event tensor has dimensions

\[
[S^{(r)}]={\rm m}^{-3}{\rm s}^{-1}{\rm Hz}^{r}.
\]

With source equilibrium measure `Pi_j`,

\[
\Gamma_j={1\over\Pi_j}\sum_i S^{(0)}_{ij},
\qquad
M_r(j)={1\over\Pi_j}\sum_i S^{(r)}_{ij},
\]

so `[Gamma]=s^-1` and `[M_r]=Hz^r s^-1`. The atomic recoil power per source photon is `-h M1`; the photon contribution is its exact opposite on the same event.

The lower-cost production quadrature is used only for conditional ratios:

\[
S^{(r)}_{ij}\leftarrow S^{(0),v0.50}_{ij}
{S^{(r),raw}_{ij}\over S^{(0),raw}_{ij}}.
\]

This is a conservation projection to the already accepted first-principles v0.50 event mass, not a fit to HyRec.

## Representative hard results

| Quantity | Result |
|---|---:|
| Interior states | `17` |
| Off-diagonal pairs | `136` |
| Active same-cell jump cells | `17` |
| Maximum raw-to-durable `C0` projection | `4.0106e-06` |
| Durable off-diagonal `C0` reproduction | `0` |
| Exchange-parity residual | `0` |
| Maximum pair conditional-moment refinement residual | `1.1178e-06` |
| Maximum same-cell conditional-moment refinement residual | `1.6042e-06` |
| Minimum source `M2` | `9.1512e+16 Hz^2 s^-1` |
| Minimum source `M4` | `3.0742e+39 Hz^4 s^-1` |
| BE relative null | `0` |
| Stress photon-number relative residual | `7.4728e-17` |
| Stress free-energy production | `-4.4656e+15 m^-3 s^-1` |
| Photon-plus-atom energy residual | `0 W m^-3` |
| Analytic-JVP relative residual | `5.2050e-08` |
| Implicit residual | `2.8370e-13` |
| Explicit stress-trial minimum | `-1.5901e-02` |
| Implicit minimum occupation | `6.7513e-02` |
| Implicit number relative change | `3.9475e-14` |
| Implicit free-energy change | `-2.2815e+16 m^-3` |
| Native source-snapshot detailed-balance residual | `2.7105e-20` |
| Geometry-to-local-microphysics difference | `0` |
| TRK and static-polarizability residuals | `0`, `0` |

## Native HYREC source interpretation

The official HyRec description distinguishes two roles: original HyRec performs numerical time-dependent radiative transfer, while default HYREC-2 uses correction functions derived from that calculation. Consequently, HYREC-2 SWIFT is a production/parity target but is not by itself the native anisotropic frequency-space operator.

The pinned HYREC-2 FULL arrays provide exact source and convention evidence, but the primitive adjacent `Aup/Adn` coefficients are not equal to the v0.51 source-conditioned COM–KHW moments. They enter the virtual-state matrix and its escape-compressed Schur reduction. The superseded route “copy the completed `Tvv` matrix or fit a scale” remains forbidden.

## Architecture preserved

- Metric signature: `(-,+,+,+)`.
- `c`, `h`, and `k_B` remain explicit.
- Bianchi geometry enters through `BackgroundSnapshot` tetrad characteristics, not through the local atomic amplitude or common-measure table.
- Every red/blue boundary-speed zero remains localized within the timestep.
- Adaptive angular policies remain `L=12` for finite/mixed tilt, `L=20` for nonlinear even shear, and `L=24` for directional crossing.
- Photon and atom four-force contributions remain opposite parts of the same event.

## Explicit limitations

- The official October-2012 original-HyRec archive bytes and SHA-256 were not acquired in this network-isolated runtime. PR-04 native original-archive parity is therefore open, not inferred from documentation or output matching.
- The release covers the 17 interior cells `|x|<=4.25`. Exterior transport remains assigned to the PR-01 Liouville/boundary module.
- Same-cell `Gamma` counts active frequency-changing events only; the coherent zero-transfer identity is excluded.
- Native `Aup/Adn` moments are diagnostic until the virtual-state/escape map is derived on one common measure.
- The production lane remains scalar elastic. Raman channels, fine structure, J-state interference, polarization, and atomic alignment are not added here.
- The geometry firewall tests a common local hydrogen-frame state; it is not the all-11 trajectory sweep assigned to PR-10.
- Wolfram and Precise Special Functions plugins were unavailable in this runtime; no claim is made that they ran.

## Immediate next release

**PR-04B original-HyRec archive and native primitive common-measure parity** must:

1. acquire and SHA-256 lock the official October-2012 original-HyRec archive;
2. compile and identify its native radiation variable, bin centres/edges, integration measure, time derivative, diffusion sign, recoil term, and coefficient units;
3. derive the virtual-state/escape map rather than fitting a normalization;
4. compare direct v0.51 event moments, original native primitive moments, and the Schur-reduced operator on one measure;
5. close native normalization, detailed balance, recoil energy, analytic/JVP Jacobian, and one FLRW snapshot parity gate;
6. keep PR-04 marked incomplete until these native-source gates pass.
