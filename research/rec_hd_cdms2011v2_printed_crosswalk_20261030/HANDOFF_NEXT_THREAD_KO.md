# REC HD | next-thread handoff, 2026-10-30

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/rec_bianchi
SOURCE_PR=161
SOURCE_HEAD=5bf22a4258ba571e8aebb1cfedab9cafe7ac6481
SOURCE_PARENT_PR=160
SOURCE_PARENT_HEAD=0a8a0bcf740da6e4a2acda9d4fd071f7ed8e2691
NEW_UNIT=REC_HD_CDMS2011V2_PRINTED_CROSSWALK_20261030
NEW_AUX_CROSSWALK=1/2_SCOPED
PARENT_PR161_AUX=1/2_UNCHANGED
CANONICAL_DAG=28/88_UNCHANGED
REC_PHYSICAL_DAG=0/313_UNCHANGED
ORIGINAL_35HZ=FAIL7/8_UNCHANGED
CDMS2011V2_EGY_RENDERED_TEXT=9_V0_LEVELS_IMPORTED
CDMS2011V2_RAW=NOT_ACQUIRED
CDMS2011V2_FULL_FIT_COVARIANCE=null
FULL_EIGHT_LINE_PRODUCTION=HOLD
R6_DIFFERENT_AUTHOR=NOT_RUN
C9_DIFFERENT_AUTHOR=NOT_RUN
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
AUTO_NEXT_NODE=false

NEW_SCIENCE:
- CDMS 2011 v2 J0..8 printed six-decimal `.egy` energies and 2021 inherited 8 printed photon frequencies admit one consistent 9-level rounded realization, exact 8/8.
- Max joint offset 14604.021 Hz; minimum print-cell slack 385.6019 Hz (J4).
- Max individual printed-CDMS-gap minus 2021 photon frequency 24917.6546 Hz (J2).
- 2022 experimental-minus-2011 `.egy` printed gap J2-J0 -14864136.031 Hz; J3-J1 -45021603.217 Hz.
- Earlier 2022 experiment-minus-2021 photons -14877400 Hz and -45034200 Hz, unchanged.
- A print-cell tolerance is NOT the original 35Hz physics/source consistency gate and is NOT Gaussian model uncertainty.

TESTS: 8/8 Python normal PASS; 8/8 Python -O PASS; compileall PASS; Wolfram exact rational independent method PASS. Initial `assert` stripped under -O is a real failed negative test; repaired with explicit ValueError. Different-author independent R6/C9 NOT_RUN.

NEXT:
1. Recover original CDMS Dec2011 v2 `.fit`, `.par`, `c003501i.cat`, `.egy`, `.lin` bytes and genuine line metadata. Never auto-substitute 2019 `.cat` or 2026 v3.
2. Find full parameter fit covariance or prove it absent from recovered 2011 SPFIT artifacts. Treat marginal level errors and print-cell widths separately.
3. Perform covariance-aware two-measured-combination assimilation into source-consistent eight-line model only if justified; owner-native source gate stays untouched until separate approval.
4. Preserve unrelated WU reactive HD, REI photo, BASS radiation, and BASS_HE/DD datasets as distinct physics processes.

Do not merge, change parent PRs or main, loosen 35Hz, rewrite production defaults, infer source heat or promote L4/REI.
