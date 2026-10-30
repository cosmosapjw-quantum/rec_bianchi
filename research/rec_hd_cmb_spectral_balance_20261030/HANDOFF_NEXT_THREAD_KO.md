# REC HD CMB spectral balance | 다음 연구 인계 (2026-10-30)

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/rec_bianchi
UNIT=REC_HD_CMB_SPECTRAL_BALANCE_20261030
PARENT_PR=166
IMMUTABLE_PARENT_HEAD=152663436e9a3ee9f88414e91d00d4e0771e7670
SIBLING_PR=165
SIBLING_HEAD=ee18ea757ab1da163ee63184b341fa46a5ebdf97
NEW_BRANCH=research/rec-hd-cmb-spectral-balance-20261030
NEW_PR=SEE_FINAL_DELIVERY_RECEIPT
AUTO_NEXT_NODE=false

CANONICAL_DAG=28/88
REC_PHYSICAL_DAG=0/313
REC_EXP_SPECTRAL=PARTIAL_9_LAB_ROWS_RANK6_THREE_CYCLES
INHERITED_AUXILIARY_DAG=1/2_UNCHANGED
NEW_CMB_J1_SCOPED=1/1_NOT_OWNER
SOURCE_35HZ=FAIL7/8
PRODUCTION=HOLD

SOURCE_PR161_ZIP_SHA256=27fee6fc9cd815100b60e57bf730f9855ea49b41c280b15d4ceed3d3913695ac
LAMDA_TRANSCRIPTION_SHA256=d44406daf59616c982ca7a33bb3ee962138130588dfb74c7b801972c933da796
SUNG_PR164_JSON_SHA256=e568752432b1dc45e2b5ca37f8b767dad0ced0cea2c289fa29dc77ccdbf8da32
SOURCE_PR166_ZIP_SHA256=b81028ec60f592570a1ba45bebf5ca95362c34f5818ab4fb0dab7ed19c670780

ACTUAL_PHYSICS:
 - CMB_T0_K=2.72548 (Fixsen 2009)
 - SOURCE_T_K=50,100,200
 - Z_GRID=0,10,30,50
 - N_H2_CM3=1,100,10000,1000000
 - ORTHO_F=0,0.5,1
 - J1_SOURCE_GATED_CMB_CASES=144
 - FULL9_DIAGNOSTIC_CMB_CASES=144
 - FULL9_PERLINE_PHOTON_RECORDS=1152
 - SUNG_FOUR_LINE_FRW_REDSHIFT_ROWS=16
 - J1_THERMODYNAMIC_ZERO_Z=Tgas/2.72548-1
 - NUMERICAL_STATUS=Python19/19 normal and -O; Wolfram exact identity; NumPy 12 case cross-solve

BACKUP_AND_RESTORE:
1. Read RESEARCH_REPORT_KO.md, SOURCE_CENSUS.json, DAG_EVIDENCE_DELTA.json and evidence/RESULTS.json.
2. Check archive ZIP CRC, MANIFEST_SHA256.json, backup/PR161_SOURCE_IMMUTABLE.zip and backup/PR166_SOURCE_IMMUTABLE.zip checksums.
3. python src/hd_cmb_balance.py
4. python -m unittest discover -s tests -v
5. python -O -m unittest discover -s tests -v
6. python tests/independent_numpy_compare.py
7. Compare Tgas=50 K, z=30, nH2=1e4, ortho=0.5 signed net rates and 9-level energy ledger.

NEXT_PHYSICAL_SOURCE:
A. Acquire byte-authentic Neufeld 2026 HD collision `.dat` and population `.fits` from https://zenodo.org/records/21165907 and verify official MD5 (hd_lamda.dat c45c4740011df579a973a7c336c5bc22, hd_population_grids.fits 3fffb1591b0f96b254210ed54599667a). Compare current source-locked 2021 collision grid at overlapped physical T,n, with metadata/hypotheses preserved; NO silent source replacement.
B. Acquire original 2011 CDMS v2 HD.fit/HD.par/HD.lin/c003501i.cat/c003501.egy bytes, and original covariance. Only then recalculate true statistical lab cycle compatibility.
C. Obtain Sung original Labfit joint frequency calibration, systematics and experiment covariance; do not use its Table 7 width/shift correlations as frequency covariance.
D. After real original source acquisition, new independent R6/C9, owner ACK and physical-gate admission can be revisited.

PROTECT:
- ORIGINAL_35HZ=FAIL7/8 unchanged. CDMS 2019/2026 v3 NEVER silently replaces 2011 v2.
- No invented sigma/chi-square, no measured eight-line spectrum, no cosmological thermal IVP.
- No main/owner/production switch or parent PR mutation, no merge, no automatic next node.
- Native different-author R6/C9 NOT_RUN. New scoped J1 only; full9 DIAGNOSTIC.
