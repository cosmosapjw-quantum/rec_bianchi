# REC_HD_RECOIL_ONLY_BOUND01 | 수학·물리·코드 연구 통합 판정

**2026-10-29 KST.** Original parent REC Draft PR157 `e209cd0180c8bf199fc476c37e3cbf8d50394b6c`. New research: distinguish a concrete recoil-only mechanism from source-field line-frequency discrepancy, using the exact 8×3 signed rational frequency transcript in REC PR156 (Git blob `5a99c9e31604347cf756abb4ab3ea1a134238e0d`). **No actual 2011 CDMS v2 raw bytes. No new physical source choice, no heat-rate interpretation.**

## Source survey and cross-repository boundary

Checked PR157 is latest REC PR; BASS PR253, REI PR267, CR PR124, BASS_HE PR110, WU088_HH PR162 are independently maintained and were checked at the time of the run. WU's ionic reaction H+ + HD -> D+ + H2 is not the same as neutral HD free rotational photon. BASS/REI source-only code does not authorize REC production binding. The previous two frozen REC ZIPs were restored, CRC checked and SHA-256 matched their saved digests. The earlier current-runtime checks were PYTHON_PASS and independent C++ compiler availability; this run built actual code, not relying on historical runtime state. Overall repo-wide CI inherited historical whitespace problems; a new overall CI success is not claimed.

## Derived primary result

For initial stationary HD mass M_u, lower mass M_l=M_u-ΔE/c² with ΔE=hν_E, emitted photon and recoil 4-momenta obey

`M_u c² = Eγ + sqrt(M_l² c⁴ + Eγ²)`.

Exact algebra gives `Eγ=ΔE(1−ΔE/(2M_u c²))`, emission shift `(ν_E−ν_γ)=hν_E²/(2M_u c²)`, and final kinetic recoil `K=ΔE−Eγ`. Absorption with initial stationary lower mass gives photon shift of the opposite sign. Therefore for arbitrary such initial rest masses `M>=M_min` the recoil-only shift magnitude is bounded by `hν_E²/(2M_min c²)`. With conservative declared `M_min=2u` and fixed `1u=1.66053906660×10^-27 kg` physical reference, **J2–J8 seven lines exceed the maximum recoil-only magnitude** with factors from 15.529 to 30036.331. Four source deltas have opposite sign to free emission recoil. J1 difference `-8.2410162 Hz` is small and passes the frozen print-only 35Hz gate; it still does not match free emission recoil sign. The most robust bound is J8: observed source-field difference ≈6864.99 Hz vs conservative free recoil ≤442.07 Hz. These are *algebraic source-field differences* rather than measured spectral residuals.

The two-sector source-energy mismatch Q=h(νP−νE)R becomes three-sector balanced if a **source-confirmed** recoil reservoir of kinetic energy K is included in a physically consistent event. Our data are NOT authenticated as recoil-corrected frequencies; no third reservoir is inserted into solver or interpreted as heat.

## Execution/reproducibility

- Exact-rational Python model with hard source-tuple/provenance checks: **21/21 unit tests PASS**; Python -O 21/21 PASS, compileall PASS.
- C++20 long-double independent implementation compile/pass: 8 rows and 24 numerical value comparisons. Against Python exact Fraction/Decimal high-precision values, max recorded relative discrepancy <3.3×10^-19 (C++ outputs 19 digits). This tests arithmetic for declared constants, not an experimental model.
- Wolfram exact symbolic kinematics returned identical emission, absorption and recoil formulas. No external physical ensemble, new IVP, old stationary rerun or solver full suite.
- Plot generated (`evidence/RECOIL_BOUND.png`), directly visually read. Figure is conditional model diagnostic, not observational uncertainty.
- Source fixture is public PR156 selected-field transcription, not full Git-result-byte identity or private LAMDA raw. The old 35Hz gate remains FAIL7/8; no scientific promotion.

## Stages and storage status

New scoped stage record 18/20: R1–R5,R7–R10,C1–C8,C10 complete within the narrow source-only investigation; **R6/C9 PARTIAL_DISTINCT_AUTHOR_NOT_RUN**. Each stage has a standalone ZIP+SHA/CRC and status JSON created as *post-execution stage snapshots*; cloud/Git receipts are recorded separately, not presumed. A serial model cannot replace a distinct-author agent. Backend/production benchmark and raw source validation remain unexecuted and no production speedup is asserted.

Central `28/88 (+0)`; REC physical `0/313 (+0)`; inherited H5 ε null; H6/H7 OPEN; L4 false; REI activation false; production HOLD. CDMS 2011 v2 `NOT_ACQUIRED`; 2026 v3 not substituted. No production paths, previous parent PRs, or original bytes changed.

## Stop and next action

Current bounded node closes at **SCOPED_CONDITIONAL_RECOIL_ONLY_DISCRIMINATION** with source-assignment unresolved. The actual science priority is to acquire immutable December 2011 CDMS v2 `.cat/.egy/.par/.fit/.lin` and both 2011 `c003501i.cat` / 2019 `c003501.cat`; record QN, TAG, uncertainty, fit provenance and map to LAMDA 2021 original bytes. Independently complete local REC/BASS/REI native/generated call graph for HD inputs. Only new confirmed consumers get source-preserving mutation. Distinct-author R6/C9 remains required for claim closure. Full physics source choice and production stay HOLD.
