# REC scientific validation against RECFAST 1.7, original HyRec FULL 2012, and HyRec-2 SWIFT 2020

**Date:** 2026-10-15 KST
**Execution:** Direct authenticated Ubuntu Python/GCC/gfortran, no local Codex, independently pinned upstream source binaries
**REC parent:** `6fcf576c52dd198497b4fcd31268be4eb1e5131e`, REC PR #89
**Scientific-admission scope:** Primordial FLRW reference-source reconstruction + atomic primitive parity + source-matched background normalization only. **NOT** an independently computed full REC (x_e(z),T_m(z)) history, coupled helium/Thomson/Lyα solver, or a new reionization history.

## 1. Source and implementation inventory

The current REC codebase is not a single completed self-consistent recombination code. Three separate scientifically meaningful lanes are distinguished:

- **Byte-locked original HyRec primitive-rate adapter**: `OriginalHyRecPrimitiveRateTable`, effective hydrogen recombination rates (alpha_{2s},alpha_{2p}), temperature departure (Dalpha), photoionization (eta_{2s},eta_{2p}), (R_{2p,2s}), and fixed original HyRec two-photon virtual-bin weights. These may be compared **directly** with original October-2012 C functions when input units and source files match.
- **Prescribed normal-comoving LRS Bianchi I geometry and passive photon characteristics**: basic domain (a_mathrm{ref}=1/21, a_mathrm{end}=1/5) is **redshift 20 down to 4**. In this domain, neutral hydrogen recombination is *not* the entire ionization source; UVB/external photoionization and helium cooling chemistry are independently prescribed by REI owner lanes.
- **Coupled original-HyRec/recoil source research**: dynamic atomic macro-source ownership and its actual historical native state depend on physically consistent combined photon-number/energy/source ledgers and boundary conditions. REC canonical v0.75 has a source-ownership/split-domain blocker. Local component tests do **not** certify a completed full recombination history.

Current paired upstream source identities:
| Upstream | Exact authority | Native output | Scientific physics |
|---|---|---|---|
| Original HyRec FULL October 2012 | archive SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27` | z, (x_e=n_e/n_H), **(T_m/[T_0(1+z)])**; stdout 8001 | Hydrogen effective multilevel atom plus explicit radiative transfer; 2012 source |
| HYREC-2 SWIFT (2020) | commit `09e8243d0e08edd3603a94dfbc445ae06cafe139` | z, (x_e), **(T_m) Kelvin**; 8000 rows | fast SWIFT correction, not FULL native 2012 transfer |
| RECFAST 1.7 Modern Fortran | commit `b34efc0f409050a980be5deca7d016a01bd13631` | z,(x_e); 1000 data rows; **no (T_m)** output | corrected effective 3-level atom, approximations/fudge coefficients; NOT RECFAST 1.5.2 |

All three were independently compiled and run on this machine in isolated source directories. Portable deterministic rerun tool `scripts/run_matched_primordial_benchmarks.py` compiles the actual pinned sources in an empty user-provided output directory, consumes source-sha matched inputs, and refuses overwriting existing scientific outputs. Comparison logic never substitutes one native program for REC's own self-consistent primordial ODE.

## 2. Matching cosmology, units, redshift, source semantics

Chosen common reference was (h=0.6735837,Omega_b=0.0494142797907188,Omega_{cb}=0.31242079216478097,T_0=2.7255,K,Y_{m He}=0.245, N_mathrm{eff}=3.0) with **massless neutrinos**. This is intentional because the pinned RECFAST executable hardwires (N_
u=3). It is not the default HYREC-2 sample ((N_mathrm{eff}=3.046,sum m_
u=0.06mathrm{eV})). The flat density closure uses (omega_{cb}=0.14175,omega_b=0.02242,omega_r=4.1578740068818545\times10^{-5},omega_Lambda=0.3119234221656212).

The source-matched Hubble normalisation is
[
 H(z)=3.2407792896393\times 10^{-18}
 \sqrt{\omega_{cb}(1+z)^3+\omega_r(1+z)^4+\omega_\Lambda}\ \mathrm{s}^{-1},
]
where (omega_i=Omega_i h^2). REI/REC prescribed background `hyrec_source_equivalent_flrw_background(...)` explicitly uses (q_mathrm{ref}=0) and reconstructs this source H(z) for z3000→600. Changed density closure is rejected instead of silently changing the claimed source model.

The original HyRec 2012 hydrogen density is
[
 n_{m H}(z)=11.223846333047\,\omega_b (1-Y_{m He})(1+z)^3\ \mathrm{m}^{-3}.
]
HYREC-2 stores the corresponding (n_{H,0}) as (11.223846333047\times10^{-6}\omega_b(1-Y_{m He})\ \mathrm{cm}^{-3}). Both are explicitly and numerically identified, including endpoint tests, in `recombination_reference.py`.

The reference (x_e=n_e/n_H) is *not* (x_{HII}) and may exceed 1 due to helium. A source-correct mapping requires
[
 x_e=x_{HII}+\frac{n_{HeII}}{n_H}+2\frac{n_{HeIII}}{n_H}.
]
`electron_fraction_from_species` checks all three independent composition fractions and helium nucleus conservation. No unique inverse from total (x_e) to three ion stages exists without additional source and state information.

Reference temperature conventions: original HyRec 2012 third output = (T_m/[T_0(1+z)]); HYREC-2 third output = (T_m) in K; pinned RECFAST has no temperature column. The comparator converts them before comparison, not a phenomenological post-hoc fit. Interpolation is only within supplied ({z}), with no extrapolation and input cosmology SHA consistency.

## 3. Observed independently executed three-code comparison

Three **original executable** output SHA256 fingerprints match across two separate full runs:
- Original HyRec 2012 full z→0: `e772c8cdd19e20618a1f71c2104e542fbb7de287ecc8ee1c7ae06697af8bf906`.
- HYREC-2 2020 SWIFT: `33d2a5598a90ee11f8648933b669e1704c958f8646d0987fc8f7775431c0a9a8`.
- RECFAST 1.7: `cfb21568475b3105a9570179cb15d1a907c4cee0e328bad2b99a0e7a08d84163`.

Their **reference-to-reference** differences on 10-in-z common checkpoints, all with matched FLRW:
| Window | HyRec2 vs original HyRec FULL maximum | RECFAST1.7 vs original HyRec FULL maximum |
|---|---:|---:|
| Hydrogen (600\le z\le1600) | (7.17958447\times10^{-5}) at z750 | (2.59804038\times10^{-3}) at z600 |
| Helium (1600\le z\le3000) | (1.61631631\times10^{-6}) at z1730 | (2.65848811\times10^{-3}) at z1800 |
| Post recombination NO reionization (20\le z\le200) | (1.93347428\times10^{-5}) at z200 | (8.31830967\times10^{-3}) at z20 |

The HYREC-2/HyRec2012 matter-temperature relative difference peaks around (2.44598\times10^{-4}) at z770 for the hydrogen comparison. These differences calibrate a realistic upstream reference discrepancy and cannot be interpreted as error of REC's presently unexecuted full-history solver.

At z1100: original HyRec (x_e=0.144674115); HYREC-2 (0.144674760); RECFAST1.7 (0.144508902). Source spectra/whole thermal history plots in `research/rec_hyrec_reference_20261015/reference/`.

## 4. Direct REC atomic rate parity and a fixed actual edge failure

The previous REC original-HyRec Python `PrimitiveRateSnapshot` erroneously required strictly (eta>0). The original C at the source table's allowed edge (T_r=0.004,\mathrm{eV}) computes physically nonnegative (eta=0) after binary64 Boltzmann-factor underflow. The REC adapter raised `ValueError`; this was directly observed as RED.

Fixed: only (eta<0) is rejected; exact (eta=0) is explicitly flagged as a **floating representation phenomenon** by `photoionization_zero_in_binary64`, not treated as a finite source rate or replaced by an invented positive floor. A detail-balance residual test in which both forward and reverse rates underflow to zero now raises an explicit `FloatingPointError` rather than returning an uninformative exact-zero mathematical residual.

Standalone native C comparison `scripts/verify_original_hyrec_rate_grid.py` compiles unmodified archived original HyRec functions, then evaluates 10 (T_r\in[0.004,0.38]\) points × 6 (T_m/T_r\in[0.1,1]\) points, 60 evaluation points × 7 rate outputs. C native 12 cold points had zero photoionization, exactly reproduced in Python. Maximum relative error of finite nonzero source elements is (1.3642420526593924\times10^{-12}), within declared scoped (3\times10^{-12}) parity gate. The previous one-point test at z1100 and actual C at off-grid/stencil points were reused, not recast as novel original computations.

Source atomic temperature admissibility alone is (T_r=0.004\dots0.4)eV, hence at (T_0=2.7255\,K), (z\approx16.03\dots1702.1) for fsR=meR=1. This domain does **not** cover the whole HeII→HeI transition z1700..3000 or late z4–16 reionization, and should not be silently extrapolated. Other original HyRec helium and external UVB source branches must be separately integrated.

## 5. Actual REC additions and trust boundary

New `src/full_bianchi_hyrec/trajectory/recombination_reference.py` is a typed scientific reference container, NOT a substitute for evolved gas/radiation chemistry. It binds upstream executable identity, input/output source SHA, complete cosmology SHA, initial helium normalization, matter-temperature units, redshift interpolation domain, and distinguishes different physical codes. It compares upstream-reference datasets only and sets `scientific_admission=REFERENCE_CODES_ONLY`. It explicitly **prevents** accidentally interpreting reference agreement as REC solver output.

New `scripts/run_matched_primordial_benchmarks.py` and `scripts/compare_primordial_references.py` run and compare source-locked binaries, honoring overwrite refusal. A separate native-C rate grid parity script tests the ACTUAL code's scientific subcomponent. Existing `AxisymmetricBianchiIBackground` code is untouched, but new named source-bound `hyrec_source_equivalent_flrw_background` method supplies the common z3000→600 geometry and `hyrec_source_hydrogen_number_density_m3` closes the atomic normalization. The original Bianchi I z20→4 scenario remains unchanged.

New tests check helium mass/number normalization, (x_e>1) physical, abundance conservation, H/nH source parity, density closure, gamma underflow, source identity and against invalid extrapolation. C/GFortran binaries are reference data only; no user production solver process touched. The updated Python full suite and fresh scoped tests are attached in the actual run receipt.

## 6. Release/admission verdict

| Claim | Present verdict | Missing work for promotion |
|---|---|---|
| Original HyRec2012 effective hydrogen primitive-rate semantics | **SCOPED_NATIVE_C_PARITY_PASS**, 60 source points | Native gas chemistry/Lyα collision closure |
| Common FLRW input H(z), hydrogen density n_H(z) | **SOURCE_MATCHED_BACKGROUND_COMPONENT_PASS** | Full recombination clock evolution, baryon+radiation source |
| Matched HyRec2012/HYREC2/RECFAST reference historical curves | **SOURCE_LOCKED_REFERENCE_REPRODUCED** | Actual independent REC self-consistent (x_e(z),T_m(z)) trajectory |
| Current normal-frame LRS Bianchi I geodesic/passive scalar radiation | PREVIOUS_C5_TO_C10_SCOPED_COMPONENT_PASS | Full radiation-chemistry-collision system and observational mode |
| Full primordial REC (x_e(z),T_m(z)) vs HyRec FULL | **NOT_RUN, NOT_ADMITTED** | End-to-end original Lyα, He, two-photon, thermal transfer, staged stiffness checks |
| REI full signed family z20→4 plus photoionized H/He | **OWNER_IN_PROGRESS, NOT_ADMITTED** | External source/reionization histories, AX08/AX11/AX12, actual photon+energy ledger |

This audit closes **real mismatches of physics domain and numerical underflow** and delivers runnable external comparisons. It does **not** force global equation-level no-go from absent whole-history results. Next constructive task: run local first self-consistent **q=0 REC hydrogen+helium+matter temperature** in source-valid primordial FLRW, using actual original atomic and radiation exchange already mapped, then compare (max_z|x_e^mathrm{REC}/x_e^mathrm{HyRec}-1|) and (T_m) against the existing immutable references on equivalent inputs. Avoid duplicating full HyRec C as if that were an independently implemented REC solver. Couple upstream rates with actual emission/absorption conservation and prove accepted step and atomic source owner semantics before full HyRec release.

### Primary sources

Ali-Haïmoud and Hirata, *Phys. Rev. D* **83** (2011) 043513, DOI `10.1103/PhysRevD.83.043513`; Lee and Ali-Haïmoud, *Phys. Rev. D* **102** (2020) 083517, DOI `10.1103/PhysRevD.102.083517`; Seager, Sasselov and Scott (1999/2000) primordial recombination; pinned original C source code and table hashes. Paper-literature novelty of this local numeric reference adapter is NOT claimed.
