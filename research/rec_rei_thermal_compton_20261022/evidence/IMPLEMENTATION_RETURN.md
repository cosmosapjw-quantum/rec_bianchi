# THERM02 implementation return — C5/C6/C7 adapter scope

This return covers the new implementation and its finite pre-ODE checks. It is not a trajectory acceptance, independent physical cooling accuracy claim, or campaign approval. The parent owns exactly-eight IVP execution, plotting, acceptance, publication and handoff. No cosmological ODE was executed by this worker.

## Owned changes

- `code/coupled_thermal.py`
- `code/checks.py`
- `evidence/PRE_ODE_CHECKS.json`
- `evidence/CHECKS_20261022T150341_197986Z.log` — first attempt, actual process exit 1.
- `evidence/CHECKS_20261022T150445_725654Z.log` — repaired attempt, actual process exit 0.
- `evidence/CHECKS_previous_receipt_20261022T150445_725654Z.log` — complete first receipt preserved before replacement.
- `evidence/CHECKS_failed_sources_20261022T150341.log` — first-attempt source bytes recovered by reversing only the repair patch and verified exactly against both first-receipt SHA-256 values.
- This note.

All 70 retained files were verified by byte length, SHA-256 and Git blob identity. Their bytes were not changed. REC126, REI129, warm729, THERM01 eight, PR121 thermal eight and the retained 114-point source check were not executed.

## Implementation and equation ownership

`CoupledThermalAtomic` inherits THERM01 `ThermalAtomic`. Its number-rate method is the identical donor `AtomicNetwork.rates` function; the new closure changes only recombination kinetic energy moments. Six Mao factors, evaluated with natural logarithms at `t = k_B*T_K/eV_J`, map to the 13 isotope recombination channels through `[0,0,0,1,2,1,2,3,4,5,3,4,5]`. The hybrid is `beta_RR = k_B*T*alpha_donor*f_Mao`. The alternative `rate_derivative` calls the retained THERM01 energy-moment formula. Signed DR amplitudes remain summed before positivity checks. Recombination binding energy has its separate escape owner.

The existing 272 GL4 nodes across 68 threshold-split energy bins supply two contractions at construction:

- `U_uv_base = sum(Phi_j*E_j)/c = 1.1416599128906846e-16 J/m^3`.
- `M_uv_base = sum(Phi_j*E_j^2)/c = 3.1681648628575677e-34 J^2/m^3`.

Only the prescribed UV amplitude multiplies these values inside a point evaluation. The old GL4 spectrum and atomic coefficients remain unchanged. Here Phi is scalar angle-integrated photon flux `c*n_gamma`, not net vector flux.

`CoupledThermalSystem` inherits the unchanged compact lift/restriction and expansion interface. A point computes the current temperature, rates, electron density and geometry once. The actual photon energy density is current `rho_crit,J*Omega_gamma*y[4]/a^4`; no stored photon or ion history is replayed. Current electron density enters the inherited elastic photon opacity. Neutrinos receive no direct Thomson term.

For `actual_hot`, `Q_C = -4*K*n_e*k_B*T*U_gamma`. For `planck_reference`, `Q_C = 4*K*n_e*k_B*U_ref*(T_ref-T)` with `T_ref=2.7255/a` and the independent external Planck bath. The two owners are alternatives. Both active branches include `Q_UV = K*n_e*(M_uv-4*k_B*T*U_uv)`. The `off` branch disables both Compton sources.

The implementation uses the inherited `THOMSON=sigma_T*c`, not `sigma_T`. `K=THOMSON/(m_e*c^2)` uses the frozen electron mass. The inherited `k_B` and `c` remain the single sources of truth. The thermal RHS evaluates the exact current-state contraction `B-A*w`; it also retains the direct volume form for a residual diagnostic. The exact fixed-coefficient `frozen_subflow` is a verification fixture and is never called by the coupled RHS.

Gas/source transfers are stored with their signed owners:

- Gas: `Q_abs-Q_escape+Q_C+Q_UV`.
- CMB/reference bath: `-Q_C`.
- UV bath: `-Q_abs-Q_UV`.
- Escaped radiation: `Q_escape`.

No Compton source is added to the photon hierarchy or Einstein equations. `|Q_C|/(H*U_gamma)` is reported for all branches; the Planck branch separately reports `|Q_C|/(H*U_ref)` with the correct bath owner. The parent must retain and integrate these diagnostics when forming the campaign report. The ratios do not themselves bound omitted backreaction.

## Public API

Exports required by the parent: `ROOT`, `XEND`, `KB`, `lift34`, `restrict63`, `CoupledThermalSystem(config, full=False)`.

Configuration strings are exact:

- `rr_closure`: `mao2017` or `rate_derivative`.
- `cmb_branch`: `off`, `actual_hot`, or `planck_reference`.

The inherited `point(x,state)` shape remains `(full63,Y,eta,T,uv,nb,network,field)`. Its `network['compton']` dictionary contains signed `Q_C`, `Q_UV`, affine `A`, `B`, `w_source`, independent `direct_w_source`, the radiation moments and their algebraic residual. `full_rhs_from_point(p)` reuses the evaluated point. `diagnose_from_point(p,x)` and `ledger_from_point(p)` let the runner avoid another geometry evaluation. Public `diagnostics(x,state)` was explicitly checked to evaluate geometry once.

`ledger_integrand(x,state)` and `ledger_from_point(p)` return five signed columns in exactly this order: `[absorption, escape, adiabatic_work, CMB_or_reference, UV_Compton]`, in J per baryon per unit x. The parent owns dense GL8/GL16 integration, the absolute-throughput normalization and saved/accepted-state gates.

All baseline THERM01 diagnostic names remain. New scalar keys are:

`rr_cooling_W_baryon`, `dr_cooling_W_baryon`, `binding_escape_W_baryon`, `compton_W_baryon`, `uv_compton_W_baryon`, `gas_source_W_baryon`, `cmb_bath_W_baryon`, `uv_bath_W_baryon`, `escaped_owner_W_baryon`, `local_transfer_W_baryon`, `local_transfer_scaled`, `local_ledger_scaled`, `atomic_source_scaled`, `U_gamma_J_m3`, `U_ref_J_m3`, `T_ref_K`, `U_uv_J_m3`, `M_uv_J2_m3`, `compton_A`, `compton_B_K`, `compton_over_HUgamma`, `compton_over_HUref`, `affine_direct_scaled`.

`U_ref` and its ratio are zero when that external bath is not active. Actual UV density remains available in all branches because UV photoionization remains active even with Compton off.

`checks.run_checks(output_path)` returns and writes an identity-bound receipt. The parent should reuse the matching PASS receipt instead of repeating the same suite. It contains no ODE or old-suite dispatch.

## Actual checks, failures and repair

Command, from the unit directory, on both attempts:

```bash
MPLCONFIGDIR=/tmp/therm02-mpl OPENBLAS_NUM_THREADS=1 python code/checks.py
```

Attempt 1 exited 1. The preserved log identifies two concrete issues:

1. Adaptive UV quadrature was given 67 internal break points while the default QUADPACK subdivision limit was only 50. The repair sets `limit=200`; the spectrum, expected moment and acceptance tolerance were not changed.
2. A new bitwise exact initial lift guard rejected the inherited D+ fraction roundoff at full coordinate 44. A separate read-only constructor probe found only `2.710505431213761e-20` discrepancy. The retained compact admission already permits `8*machine_epsilon = 1.7763568394002505e-15`. The repair restores that existing isotope-roundoff rule while requiring exact excluded geometry and neutron/tritium zeros. The original full63 IC is preserved; it was not projected to hide the bit difference.

The frozen-subflow expected value was also made independent of implementation arithmetic by using an integrating-factor quadrature. This is an algebraic fixture, not an IVP.

Attempt 2 exited 0; 11 new finite check groups passed in 1.3774621420016047 s of measured check-body time. This is not an end-to-end speedup claim.

| New check | Observed evidence |
|---|---:|
| Reused payload identity | 70 files, byte/SHA-256/Git blob verified |
| Six-factor/scalar Mao and 13-channel mapping | Maximum relative difference 0 at 4 new adapter temperatures |
| Independent SI/cgs Compton and heat capacity | Maximum relative discrepancy 2.7012248691691586e-16 |
| Planck energy/induced-recoil integrals | `I4/I3 = 4.000000000000001`; a_R relative discrepancy 2.606690188263696e-16 |
| Continuous UV U/M integrals | Maximum relative discrepancy 2.159303572789725e-16 |
| UV occupation upper bound | 6.077255719410923e-20 at lower energy edge |
| Frozen affine semigroup | Maximum relative discrepancy 1.648567121689569e-16 |
| Full63/compact34 RHS, three synthetic physical states, all six branch/closure pairs | Maximum scaled discrepancy 4.4081336778725497e-16 |
| Local gas energy residual | Maximum scaled discrepancy 3.8342838735258373e-16 |
| Local source transfer residual | Maximum scaled discrepancy 1.9683235624186835e-17 |
| Atomic energy source residual | Maximum scaled discrepancy 2.9416633164199166e-16 |
| Affine/direct current-state Compton | Maximum scaled discrepancy 1.7966697470981423e-16 |
| Number RHS relative to retained owner at the same state | Exact equality |
| Current photon monopole perturbation | Actual-hot Q ratio 1.1000000000000003; external-reference Q difference 0 |
| Current ionic opacity feedback | Explicitly observed; no direct neutrino Thomson change |
| Complete thermal partial, finite difference vs retained analytic coefficient derivatives | Maximum scaled discrepancy 6.3973315273617e-9, below 2e-7 gate |
| Deliberate extra/missing c, opposite sign, Kelvin/eV, charge-shift mutations | Expected rejection distinguished from correct values |
| Thermal trial/domain and unknown-source guards | Expected rejection observed |

These states are explicitly synthetic physical points, not completed trajectory samples. The checks do not count as any new cosmological IVP.

## Receipt identities

- `code/coupled_thermal.py`: `599be84fabe9bdc904fdcda46e685f2fcaffa5985ba72dcabcd1fa5cb97a51db`.
- `code/checks.py`: `a1ebe75e2f883885095117ce7cb2891b6792cacca6193fab2306d192d2d8fa95`.
- `FROZEN_CONTRACT.md`: `076a97a621d2bdc55eb24859bd122792ac47c32d320458e7d97ff0836d2f4169`.
- `provenance/REUSED_FILES.json`: `9e327157bfab4c4fa2809699a4b0e7c4fbf2582b4bd6ac186ab73804a5e96c1d`.

## State and remaining obligations

Implementation and the new finite pre-ODE adapter gate are complete at these identities. Fresh independent review and all eight new trajectory admissions remain the parent's next stages. No global numerical convergence is established here. No finite trajectory domain guard is replaced by a continuum positivity claim.

The Mao product remains a source-backed hybrid with unchanged donor alpha, and the derivative alternative is a closure comparison. Neither establishes independent physical accuracy of the full thermal model. Actual-grey recoil/induced spectral ownership, radiation energy/Einstein backreaction, unresolved Li final yields and other omitted channels retain their distinct obligations. Matter and radiation stress remain separately signed in the unchanged donor output.

Preserved status: Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false. REI first-failure raw retention scope remains local-only. No new no-go theorem is claimed.

