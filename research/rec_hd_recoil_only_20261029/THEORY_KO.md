# REC-HD-RECOIL-ONLY-BOUND01 | 자유 분자 2체 운동학과 소스 주파수 불일치

2026-10-29 KST. Parent: `cosmosapjw-quantum/rec_bianchi` Draft PR157 `e209cd0180c8bf199fc476c37e3cbf8d50394b6c`. Scope = **source-only disambiguation of a specific physical mechanism**; no production, thermal source, spectroscopy correction, new IVP or ownership transfer. Source-only source transcript traces to PR156 `results/RESULT.json` blob `5a99c9e31604347cf756abb4ab3ea1a134238e0d`. **This is an 8×3 field transcription, not the original LAMDA/CDMS data.**

## R1–R3: problem, provenance, assumptions

Old result: `nu_E=100c (w_u-w_l)` and `nu_P=10^9 nu_print_GHz` in ordinary Hz, `delta_nu=nu_E-nu_P` with old, unmodified 35-Hz print-only criterion `FAIL_7_OF_8`. A prior two-sector internal-level/photon ledger `Q=h (nu_P-nu_E)R` is a conditional source mismatch and **not an observed energy injection**. Recoil of a molecule is one possible third sector in the energy ledger. Determine how much of frozen delta_nu a *free single-photon recoil-only* kinematic model can explain. CDMS v2 primary bytes are still not acquired, and no physical source choice is made.

Metric signature (-,+,+,+). At one event use the molecule's **initial rest frame**, not an observer endpoint boost, cosmological normal frame, or thermally averaged fluid. Retain `h=6.62607015×10^-34 J s = 2πħ`, `c=299792458 m/s`; compare energies `ΔE=hν_E` and `M c²`. Fix conservative explicit **assumption** `M_u,M_l >= 2 u` (u input `1.66053906660×10^-27 kg`), noting actual HD mass is around 3 u, but **no precise mass source or uncertainty is inferred from the LAMDA file**. Require ΔE>0, M>0; no medium, collisions, pressure shift, stimulated transfer, thermal velocity or gravity-induced frequency shift is included. These missing processes must be assessed with independent data, not absorbed in a fake heat term.

## R4–R5: exact constructive emission/absorption derivation

For photon energy Eγ>0 and final lower-molecule recoil momentum of magnitude `Eγ/c`, conserve four-momentum. In the initial upper-state molecule rest frame:

`M_u c² = Eγ + sqrt(M_l² c⁴ + Eγ²)`, with `M_u-M_l = ΔE/c²`.

Squaring and rearranging (no weak-recoil approximation) yields

`Eγ,em = (M_u²−M_l²)c²/(2M_u) = ΔE (1−ΔE/(2M_u c²))`.

Thus `nu_E−nu_em = h nu_E²/(2 M_u c²) > 0` and final molecule kinetic energy `K=ΔE−Eγ=h(nu_E−nu_em)` is **positive**. The three-sector local balance is `(-ΔE)+Eγ+K=0`; comparing just internal and photon sectors gives a nonzero recoil term and is not proof of physical heat. In the lower initial rest frame for absorption:

`M_l c²+Eγ = sqrt(M_u² c⁴+Eγ²)`, yielding

`Eγ,abs=ΔE(1+ΔE/(2 M_l c²))`, so `nu_E−nu_abs=−h nu_E²/(2 M_l c²) < 0`.

For either **single free kinematic event** where the appropriate initial rest mass is at least `M_min=2 u`, the **absolute recoil-only shift** obeys

`|delta_nu|_recoil <= h nu_E²/(2 M_min c²)`.

It is a conditional structural upper bound, not an observational error, not a print-tolerance replacement, and not a universal exclusion of medium or relativistic-frame effects. Its sign distinguishes free emission from free absorption. Using `M_ref=3 u` yields a *reference* scale, not a measured precise HD recoil prediction. The source object contains rates and fitted frequencies; neither is adjusted.

## R6–R8: verification and conditional scientific inference

- Wolfram exact symbolic mass-shell algebra returned emission `h ν (1−hν/(2M_uc²))`, recoil `hν²/(2M_uc²)` and absorption `hν (1+hν/(2M_lc²))`.
- Fresh Python exact-rational model with frozen selected-field transcript: `21/21` tests PASS normal and `-O`; separate C++20 long-double check on eight lines, 24 numerical value comparisons against exact Fraction/Decimal, worst observed relative discrepancy `< 3.3×10^-19` when retaining printed 19-digit C++ outputs. This checks the kinematic formulas and arithmetic, **not CDMS source authenticity**.
- For the explicitly assumed `M_min=2u`, **all seven lines J=2..8** exceed recoil-only magnitudes by factors from 15.529 to 30036.331. J=1 has `δν=-8.2410162 Hz`, opposite the free-emission recoil sign and near the 2u bound `7.942342 Hz`, but independently satisfies the prior 35Hz print criterion. Four lines have `ν_E−ν_P<0`, excluding *free emission recoil* on sign alone within its assumptions. The fit/medium alternative remains OPEN.
- Generated `evidence/RECOIL_BOUND.png` directly inspected. The left axis is logarithmic magnitude; the right axis is signed detuning. The plot cannot compare absolute spectroscopic uncertainty because none was supplied; plotting the `2u` envelope is not a confidence interval.
- Same-context review tests signs, dimensions, mass shell and nonzero kinetic ledger. Native distinct-author R6 NOT_RUN; do not claim independent author.

## R9–R10: computational form, preserved gates

The bounded operator consumes **only selected-field exact rational literals** (frequencies, signed difference) with PR156 source-blob identifier and frozen tests, and computes a recoil-only upper envelope and residual. Negative controls reject any altered literals, invalid/missing lines or nonphysical mass. No silent physical correction, prior 35Hz gate loosening, legacy full-solver rerun or production mutation. Source origin: public recorded result, not new private-source re-download.

**Result classification**: `DERIVED + WOLFRAM_SYMBOLIC_CHECKED + PYTHON_NUMERIC_CHECKED + CPP_PASS`. The conditional **recoil-only explanation is insufficient for J=2..8** at the assumed `M>=2u`, but neither CDMS 2011 v2 authentication nor an alternative mechanism is established. Source-choice, H5 epsilon and REI physical gates unchanged. `canonical 28/88`, `REC physical 0/313`, `original35Hz FAIL7/8`, `CDMS2011v2 RAW NOT_ACQUIRED`, `H5 epsilon null`, `H6/H7 OPEN`, `L4 false`, `REI activation false`, `production HOLD`.

### Relevant sources

- Pinned REC PR156 `research/rec_hd_consumer_callsite_20261029/results/RESULT.json`, Git blob `5a99c9e31604347cf756abb4ab3ea1a134238e0d`.
- Official CDMS December 2011 v2 archive index: <https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/>; byte retrieval unresolved.
- Official CDMS program/field manual: <https://cdms.astro.uni-koeln.de/classic/general>.
- LAMDA HD page: <https://home.strw.leidenuniv.nl/~moldata/HD.html>.
- CDMS current Aug2026 v3 primary description (not substituted): <https://cdms.astro.uni-koeln.de/cgi-bin/cdmsinfo?file=e003501.cat>.
