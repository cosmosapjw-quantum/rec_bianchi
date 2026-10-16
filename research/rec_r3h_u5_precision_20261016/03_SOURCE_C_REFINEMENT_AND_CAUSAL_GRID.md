# R3h phase 3: **actual source-native C h/h2/h4 full H+He** + causal 313-edge prototype

Date 2026-10-16. Baseline original-C immutable ZIP `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27` and archived C stdout `6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400`.

## Actual sandbox execution (scientific, not only algebra)

The raw archived original HyRec October 2012 H+He C sources were extracted into **three distinct temporary directories**. Each variant differs only by a single `hyrec_params.h` `#define DLNA` token at `8.49e-5`, `8.49e-5/2` and `8.49e-5/4`. Atomic source, energy bins, cosmology, constants, physical model, C code and compile flags `gcc -O3 -fno-fast-math` were fixed. The source ZIP itself was never edited. Each executable evolved the *entire physical original FULL H+He q=0* history and returned 8,001 rows from z8000 down to z0. The default h native C stdout was **BYTE IDENTICAL** to the preserved R3f/R3c baseline.

Source C stdout SHA-256:
- h: `6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400`
- h/2: `5b60e5a79b96e16d28b4c49a46f6a65b65b55859ae8ed6e8fbc2947673f52ea8`
- h/4: `790827f7ff0f361547edf111bee6864ae988698ffb3da37e300b6c937db7df7b`

Native C execution wall only: h 0.540 s, h/2 1.235 s, h/4 2.208 s (sequential on this sandbox); whole command including extraction, compilations and comparison ~6.46 s. No NCP or owner-PC mutation. These are not performance benchmarks for the Python FULL solver.

The full 8,001-row differences measured as **maximum per-output relative**:
- xe: h→h2 `1.4326313844213375e-6`; h2→h4 `8.701314624916069e-7`; both maxima around z1563, **signed differences opposite**.
- Tm/Tr: h→h2 `1.7833444211867596e-7`; h2→h4 `6.779469971046311e-8`; strong signed reversal near z836.

Local three-level empirical order from same physical z values:
- at z20: xe `2.016333526745808`, Tm/Tr `2.0120953445988365`;
- at z1100: xe `1.676900907996379`, Tm/Tr `1.4856098928737376` (the latter near printed C-output precision);
- at z0: xe `0.5615360146341639`, Tm/Tr `2.083763949043782`;
- at z1563, signed xe first-to-second and second-to-third differences have opposite signs, so `p=log2(D01/D12)` is **undefined** as a monotone convergence order there.

Across all 8001 printed rows, median locally same-sign and nontrivial finite-difference orders were ~1.99991 for xe (2745 rows) and ~2.01595 for Tm/Tr (1167 rows). This is **descriptive, not a global p=2 acceptance**. The source output precision, stage switching and clock-onset phase matter. Report both full-grid differences and signed controls, never silently discard transition regions.

## Actual 313-frequency-link transport prototype

Extracted original 311 energies from the immutable two-photon C table and rebuilt all 311 virtual incoming links + 2 Ly-line incoming links (139→LyA, 270→LyB, 310→LyG, and LyA from 140, LyB from 271). Smallest `ln(E_src/E_dst)=8.49527887747085e-5`, **strictly greater** than original `h=8.49e-5`; source C's causal energy spacing is satisfied and h/2,h/4 safe on the unchanged frequency grid.

`history.c` original RT start `izH0=floor[1+ln(k_B T0 (1+8000)/0.4 eV)/h]`: observed coarse, h/2, h/4 are `18223,36446,72892`, zRT all `1702.0722635483426` for *this* input. Do not assume exact multiples for arbitrary cosmological inputs, because `floor` can move a stage transition.

For all 313 links, an independent two-neighbor, accepted-past-only sampler reproduced affine histories to <5e-16 of amplitude and bounded the exponential relative interpolation error by `exp(|lambda|h) lambda^2 h^2/8`. Maximum measured analytic exponential errors: h `2.2524103427029148e-10`, h/2 `5.63121697005778e-11`, h/4 `1.407572747132196e-11`. At the second RT step, **12 source links are already active at h**, but none at h/2 or h/4: different valid history clocks require separate full accepted-history constructions. All j1 queries had zero thermal prehistory distortion. This is a **mathematical transport prototype**, not a true h/2 Python primordial run.

## Verification, limitations, and stage backup

Actual Python standard-library unittests: **12 PASS**, including six U5 adversarial tests, original-C default byte identity, altered C variant preservation, source-edge indexing, strict future-read rejection, interpolation/blackbody prehistory and signed nonmonotonic transition checks.

Portable source, actual 8,001-row C stdout gzip for each grid, manifest, JSON, plots and all tests are in `REC_R3H_P3_SOURCE_C_REFINEMENT_20261016.zip` (18 entries, 569,084 bytes). SHA-256 `63419c2583019df60817df3fc8837aa8102d88d0316594066dcac45a6a24b485`. **Verified exact-byte readbacks** from:
- Google Drive `/Google Drive/rec_bianchi_research_backups/20261016/R3H_SOURCE_C_P3/REC_R3H_P3_SOURCE_C_REFINEMENT_20261016.zip`.
- Library `/rec_bianchi_recovery/R3H_20261016/REC_R3H_P3_SOURCE_C_REFINEMENT_20261016.zip`.

This is original **C h/2,h/4 time-step sensitivity**, not independently integrated **Python** at h/2 and not a proof of 2nd-order global convergence. U5 historical FAIL stays HOLD. No REI or Bianchi prediction. The source archive's actual C physics is unchanged in each temp variant, but executable hashes differ as required because DLNA changed.

## DAG

| Task | Status |
|---|---|
| P1 source formula / conditioning / analytic clock | VERIFIED & BACKED_UP |
| P2 nine U5 IEEE shadow + six negative tests | NUMERIC_SCOPED_PASS, U5 original HOLD; Google Drive + Library readback |
| P3 actual original C 3-level + 313-link sandbox | **COMPLETED NUMERIC_CONTROL**, C-only; Google Drive + Library readback |
| P4 independent Python h/2, h/4 primordial integration | **NOT_RUN**, future Codex compute |
| P5 native REI donor, signed Bianchi and CMB | **NOT_AUTHORIZED/NOT_STARTED** |
