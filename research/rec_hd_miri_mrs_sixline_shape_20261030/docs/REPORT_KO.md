# REC-HD MIRI MRS source-profile results | REPORT (2026-10-30)

## Primary numerical output

- 4 source temperatures × 5 physical source H2 densities × 7 low-redshift grid points = **140 new source-model conditions**, each with two direct original-source 15-level stationary solutions; **120 with 2+ accessible lines** and 20 at z=1.25 with zero MRS six-line coverage.
- MIRI MRS selected source frequencies from Zenodo v2, STScI effective 4.9–27.9 um (not 28.8 um nominal). Accessible R4..R9 line count by sampled redshift: `z=0:6`, `.1:6`, `.25:5`, `.5:4`, `.75:3`, `1:2`, `1.25:0`.
- Required simultaneous MRS grating settings A/B/C by sampled redshift: `ABC, ABC, ABC, ABC, BC, C, none`. This is geometric bandpass feasibility, *not* adequate integration time or confirmed ability to detect the lines.
- New alternate vs standard model density/temperature nuisance-profiled log-ratio shape residual (z=0):
  - 4000 K, n=1e4 cm^-3: **0.166897522140**, original direct **0.188318478765**, 1% model floor YES.
  - 3000 K, n=1e4 cm^-3: **0.151971478665**, original direct **0.166506077936**, 1% floor YES.
  - 2000 K, n=1e4 cm^-3: **0.132023835164**, but 1% model floor NO; do not treat as strong source diagnostic.
  - 1000 K, n=1e6 cm^-3: **0.070496875536** after temperature allowed to move from 1000 to 4000 K, direct **0.698037794021**, 1% model floor YES. Earlier fixed-T density-only profile is **0.211418625380**. Therefore freely changing the assumed gas temperature can dramatically reduce apparent source discrimination.
- Across z=0 20 model points, 3 exceed `ln(1.1)` logshape after profiling, but ONLY 2 of those 3 pass the reference 1% model-relative line-power floor; this count is not a statistical significance or telescope sensitivity result.
- At z=1 with two lines, best profiled residual median `~2.88e-9`, effectively source-degenerate at the numerical search precision for these cases. It is not a global theorem that all 2-line models are degenerate.

## Verification boundaries

- Four original Neufeld `.dat/.fits` objects individually SHA256 verified against unchanged parent source hash locks.
- 10 new source-locked unittest normal PASS; 10 under `python -O` PASS; `compileall` PASS.
- Independent SciPy differential evolution optimizer compared to the deterministic grid/bracket optimizer for T=4000 K,n_alt=1e4,z=0; within 2e-5 absolute logshape.
- Same-context blind-referee audit: `docs/BLIND_REFEREE_SAME_CONTEXT_KO.md`. Native distinct-author R6 and C9 NOT_RUN, GitHub CI NOT_VERIFIED unless specifically checked, original CDMS2011 35Hz FAIL7/8 preserved.

## Workflow / DAG

- Additive unit only, **1/1 SCOPED** within its own auxiliary; no source ownership migration.
- Canonical REC DAG **28/88** (+0); REC physical gate DAG **0/313** (+0). This physical atlas is not a replacement for experimental joint covariance or qualified observational output.
- `PRODUCTION=HOLD`; `NO_MERGE=true`; `NO_35HZ_RELAXATION=true`; original PR #171 and sibling #170 unchanged; parent #172 kept immutable.

## Data and figures

`evidence/MIRI_ORIGINAL_HD_LINE_WINDOW.csv`, `evidence/MIRI_MRS_REDSHIFT_COVERAGE.csv`, `evidence/MIRI_SOURCE_NUISANCE_PROFILE_140.csv`, `evidence/MIRI_SHAPE_SUMMARY.json`, `figures/MIRI_SIXLINE_BANDPASS_GRID.png`, `figures/MIRI_SIXLINE_SOURCE_PROFILE.png`.
