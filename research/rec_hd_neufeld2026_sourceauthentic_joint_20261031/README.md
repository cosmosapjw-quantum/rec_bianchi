# REC-HD | Original Neufeld v2 H2+HD physical atlas (2026-10-31)

## SCIENTIFIC RESULT: source-authentic but posterior-CONDITIONAL; no observational refit
Immutable base: Draft PR #177, HEAD `c393932e2f833a21302524970fc8d8bdcd268ca0`. Source ZIP (original FITS + isobaric posterior, original Francis Appendix F table, unchanged HD v2 FITS, H2+HD physical code/test/data/figures/20 stage ledger): [Google Drive immutable archival object](https://drive.google.com/file/d/13LNKsrpDh33jCoPRjrIjb1sBFi2MbsTf/view). `REC_HD_NEUFELD2026_H2_HD_20261031_SOURCE.zip`, **3,900,934 bytes**, SHA256 **`75b8b290d8cf84a5fb26647950f1cbdadbb7e90bbfb0c16aa89074a494c8b74d`**. Local source included in ChatGPT conversation as downloadable ZIP. NOTE: GitHub's binary-upload connector returned an HTTP/2 transport error on this 3.9-MB payload, so full archive resides in Google Drive rather than falsely claiming a Git-binary upload. Git tree carries this source manifest, data summary and all R/C stage records.

### Source ownership and hashes
- D. A. Neufeld (2026), ApJ 1007:16, DOI 10.3847/1538-4357/ae851a. Original [Zenodo v2 21165907](https://zenodo.org/records/21165907) `h2_population_grids.fits`: MD5 `cc652422aeb54f27899ddfc435cd93ae`, SHA256 `a6fb8376297f2dbe07650f7939a58135fe384441b4a9b2ad5dfe54b784a9eec5`. Isobaric posterior `posterior_isobaric.csv.gz`: MD5 `f21c0527fcf00829ad95888887d20afd`, SHA256 `17b647f2b70af891686a5c39802e114d8e9babd9bfb3de5222a418066bf5ed72`. Both original bytes verified.
- Frozen original HD grid `hd_population_grids.fits` MD5 `3fffb1591b0f96b254210ed54599667a` and SHA256 `0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1` from PR176 source; unchanged. Original Francis et al. (2025) A&A 694 A174 DOI 10.1051/0004-6361/202451629, final Zenodo 14592550, 364 printed entries, derived CSV SHA256 `eb550e1790fa2f127ce074fdbf5cff9bb1412c29121a149cf6d9ba5ef4d7896a`. Original 29,640 HD profile scores **not recalculated**.
- Publisher FITS stores `log10(f_J/g_J)`, with para H2 and ortho H2 normalized separately. Source state-weights and OPR split preserved. Optically thin intrinsic brightness `I_ul = h*c*(E_u-E_l)_wavenumber*A_ul*sum_c N_u,c/(4*pi)`; isobaric `n_H2,c = (p/k_B)/T_c`; HD molecular `x_HD=N_HD/N_H2` is **not** elemental D/H. Flux requires actual solid angle and extinction/extraction calibration. The original FITS collider OPR=3 is retained separately from fitted emitter OPR.

### New source-real science
- 26 source-published aperture bestfits × 2 physical components = **52** physical states.
- **728** component-level target line upper-level contributions, **364** physically computed intrinsic transition surface brightness values: 208 H2 S(1..8) and 156 HD R(4..9), linked to 364 final printed Francis flux entries. These are **not simulated observational fluxes**.
- Original paper Table 1 and 2 (T=1000K,n=1e4 cm^-3): H2 Trot=**495.9395919702K** vs 495.9K; HD Trot=**347.3286517999K** vs 347.3K.
- **181** source-posterior-conditioned H2 relative flux/intensity ratios, 7 line-by-line descriptive effective differential attenuation slopes and 2 plots. H2 S3/S1 `Delta k_eff=0.4566750266964509`, `R²=0.993802462871176`. The posterior and its tau_9.7 were **already fitted using the same Francis observations**: this is a dependent internal physics diagnostic, NOT an independently recovered KP5 extinction curve or significance result.
- Source posterior xHD median across 26 best-fit molecular ratios = 1.1102365704e-5. Different author paper headline medians use a different position subset/statistic, not equated to this value. Original per-aperture 8 rounded-zero HD errors are not treated as exact. 

### Verification with actual commands
`python src/joint_atlas.py`; `python src/plot_science.py`; `python -m unittest discover -s tests`; `python -O -m unittest discover -s tests`; `python verification/independent_flux_oracle.py`; `python verification/package_and_replay.py`.
Actual current standalone tests **39/39 normal + 39/39 Python -O**, an independent-implementation but same-author **364/364** flux comparisons (max relative difference **3.865820850463677e-16**), source ZIP CRC + SHA manifest **31/31**, clean replay derived science artifacts **10/10 byte exact**. True distinct-author R6/C9 **NOT_RUN**.

### Explicit missing observational interface and immutable holds
Measured JWST MIRI per-aperture 1D extracted spectra, joint line-fit/pixel/calibration covariance and complete original KP5 transmission/extraction coupling **NOT_ACQUIRED**; published Neufeld best-fits are not independent likelihood reconstruction. No measured covariance, independent new H2/HD posterior, D/H chemistry inference, uncertainty intervals, original 35 Hz fix, or production acceptance. Native browser tab connector could not access originating Chrome context, source/Zenodo research used dedicated connectors.

`CANONICAL_DAG=28/88 (+0)`; `REC_PHYSICAL_DAG=0/313 (+0)`; `EXISTING_SCOPED_R_C=18/20`; `R6_C9_DISTINCT_AUTHOR=NOT_RUN`; `ORIGINAL_35HZ=FAIL7/8`; `PRODUCTION=HOLD`; `NO_MERGE=true`; `NO_OWNER_SOURCE_SWITCH=true`; `NO_35HZ_RELAXATION=true`; `AUTO_NEXT_NODE=false`.

**New scoped side-physics 1/1 completed**, not canonical/physical DAG admission. Per-stage R1–R10 and C1–C10 logs in full source archive and accompanying Git publication ledger. No 20 separate remote uploads claimed.
