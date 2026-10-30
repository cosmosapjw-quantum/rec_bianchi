# REC JWST source-conditional covariance | handoff

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rec_bianchi
PARENT_PR=174
IMMUTABLE_PARENT_HEAD=4a5916761c60bf68163ab1f3845db35cbb789d97
GRANDPARENT_PR=173
IMMUTABLE_GRANDPARENT_HEAD=90d883c77b3823322f2ecdb09888442b9a620a97
CURRENT_UNIT=JWST_LINE_FLUX_JOINT_COVARIANCE_20261031
SOURCE_FRANCIS=arXiv:2501.02085v1 Table_E1_E2_TRANSCRIPTION_NOT_FINAL_PDF
FRANCIS_FINAL_APPENDIX=Zenodo:14592550_SOURCE_BYTE_NOT_ACQUIRED
NEUFELD_SOURCE=Zenodo:21165907_v2_FOUR_FILES_SHA256_LOCKED
OBSERVED_PRINTED_ENTRIES=364
DETECTED_POSITIVE_ERROR=283
UPPER_LIMITS=73
ROUNDED_ZERO_ERROR=8
NONLTE_15_LEVEL_SINGLE=342
NONLTE_15_LEVEL_TWO_T_ISOBARIC=1368
SINGLE_T_DENSITY_CM3=1e2..1e8_19_LOG_POINTS
TWO_T_LOG10_P_OVER_KB=7..10_19_LOG_POINTS
SCOPED_HH211_AP7_CHI2_RHO0_ONE_T=28.793125019836225
SCOPED_HH211_AP7_CHI2_RHO0_TWO_T=0.4499042299958944
OLD_LIBRARY_FULL_SCIENCE_SHA256=56e54a8ce165560b3be3ad52bbb6b98b6d0c9534059c3802faa9d9f791d34079
ALIGNED_GRID_COMPARISON=364/364;10944/10944;43776/43776_PASS
CONDITIONAL_GLS_GRID_SCORES=54720
FIT_ELIGIBLE_APERTURES=16/26
JOINT_COVARIANCE=NOT_ACQUIRED
JOINT_LIKELIHOOD=NOT_RECONSTRUCTED
SUNG_FULL_COVARIANCE=SOURCE_ACQUISITION_PENDING
CDMS2011_FULL_PRECISION_COVARIANCE=NOT_RECONSTRUCTED
ORIGINAL_35HZ=FAIL7/8
CANONICAL_DAG=28/88
REC_PHYSICAL_DAG=0/313
R_C_SCOPED=18/20
DISTINCT_AUTHOR_R6_C9=NOT_RUN
GITHUB_CI=FAIL_VERIFY_REPO_QUICK_AT_PARENT
PRODUCTION=HOLD
NO_MERGE=true
NO_OWNER_SOURCE_SWITCH=true
NO_35HZ_RELAXATION=true
AUTO_NEXT_NODE=false
```

Continue only source-acquisition blocker work: acquire Francis 2025 final Appendix D–G original PDF and numerically reconcile its Appendix F entries against transcribed arXiv v1 Table E.1/E.2. For the real joint likelihood obtain MIRI extracted spectra, per-line fit uncertainties and off-diagonal covariance, correlated instrument calibration (MIRI/MRS subband-dependent), dust-extinction nuisance and H2 excitation. For unrelated Sung lab fit, obtain raw Labfit multispectra/normal matrix from Sung et al. JQSRT 295 108412 (2023), DOI 10.1016/j.jqsrt.2022.108412, or original experiment archive. Do not infer Sung lab line-center covariance from the astronomical flux covariance. Do not merge or reinterpret historical 35 Hz. 

R/C results are source-conditionally scoped, no genuine distinct-author review, no admission to the canonical or physical DAG.
