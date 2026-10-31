# REC-HD: H2+HD source-conditional correlated-censoring bridge (DRAFT/HOLD)

**Immutable base:** PR #176 HEAD `338f86a5a4ced83b6bcebb82e008bf7ca63bb1ec`. No owner-source changes, no merge, no production; original CDMS 35 Hz FAIL 7/8 is retained.

## Actual independent new science

- Reuses complete Francis final source ZIP (SHA256 `7deb535d22458cb74ae702595131902a750e8d0c9cb585bc309e1fbaba3a94f3`): manifest 50/50 pass, 29,640 old censored profiles counted **not recalculated**.
- 26 observed apertures, 364 printed lines; H2 207 detections/1 upper, HD 76 detections/72 upper, 8 zero-rounded errors excluded; 356 effective lines.
- Derived and tested physically dimensional optically-thin H2+HD forward operator with separately-normalized H2 para/ortho levels and explicit molecular-deuterium partition `ξ_HD`.
- Derived and tested correlated detected+censored multivariate Gaussian conditional likelihood, including model-dependent calibration covariance. The multivariate upper-limit CDF is **not** generally factorizable; faint-flux covariance numeric unit guard was fixed.
- **18 newly computed** original HD source-rate nonLTE ortho-collider scenarios; max fractional individual HD R(4..9) line change **4.1017%**, max normalized logarithmic shape spread **0.0312764**. No H2 source-population grid was fabricated.
- New code standalone tests **24/24 PASS normal, 24/24 PASS Python -O**, with analytic verification samples. Same-context only, distinct-author R6/C9 NOT_RUN.

## Full scoped code/data/report archive

`REC_HD_JOINT_SOURCE_CONDITIONAL_20261031_SCOPED_SOURCE.zip`: **210,610 bytes**, SHA256 `52d0d0951139931b5e932a452382e70e5156f1becfd892073be6fdc3e2bbcce7`. ZIP has 17 members, 16/16 manifest entries; includes four Python source files, two test modules, the 18-case generated CSV/summary, per-aperture observation census, PNG/SVG figure, full Korean derivation report, exact handoff and reproducibility commands. The original 4.33 MB source ZIP is **referenced by SHA** and must be preserved separately, not recompiled here.

**Independent dual storage restored byte-identical**: ChatGPT Library `/BASS/rec_bianchi/REC_HD_JOINT_SOURCE_CONDITIONAL_20261031/`; Google Drive https://drive.google.com/file/d/1X1OO9TerVBW6WVpn7eGGfUNNGeQDWTMA/view . Both readbacks matched archive SHA256.

## Scientific blocker, not masked

Authentic Neufeld v2 `h2_population_grids.fits` was located on Zenodo 21165907 with published MD5 `cc652422aeb54f27899ddfc435cd93ae`, **raw bytes NOT_ACQUIRED**. The Francis MIRI MRS per-aperture cross-line noise + calibration covariance and exact upper-limit reporting model are also **NOT_ACQUIRED**. Accordingly: NO new observational joint likelihood, no inferred D/H/pressure posteriors, no confidence or significance statement. The supplied flux kernel is a *preparatory physical interface* requiring these real inputs.

`CANONICAL_DAG=28/88 (+0)`; `REC_PHYSICAL_DAG=0/313 (+0)`; `EXISTING_SCOPED_R_C=18/20`; real distinct-author R6/C9 NOT_RUN. `ORIGINAL_35HZ=FAIL7/8`, `NO_MERGE=true`, `NO_OWNER_SOURCE_SWITCH=true`, `NO_35HZ_RELAXATION=true`, `PRODUCTION=HOLD`, `AUTO_NEXT_NODE=false`.
