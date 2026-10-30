# REC HD SOURCE-COVARIANCE | next thread handoff

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rec_bianchi
PARENT_PR=164
IMMUTABLE_PARENT_HEAD=e050b97b7d5c6c0929062fafd7333e0164112399
IMMUTABLE_GRANDPARENT_PR=163
IMMUTABLE_GRANDPARENT_HEAD=65c5c4c9105c9957418ff014d34e007e53a63b3b
UNIT=REC_HD_SOURCE_COVARIANCE_RECONSTRUCTION
SOURCE_ZIP_PR164=REC_HD_SUNG2022_CYCLES_20261030_SOURCE.zip
SOURCE_SHA_PR164=2d781a67a312a7f124955d3ad9c83fe739fa8fb0925390b5139df7d954e92dd8
SOURCE_INPUT_SHA=e568752432b1dc45e2b5ca37f8b767dad0ced0cea2c289fa29dc77ccdbf8da32
CDMS_V2_OFFICIAL_INDEX=https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/
CDMS_V2_RAW_BYTES=DISCOVERED_NOT_ACQUIRED
CDMS_FIT_COVARIANCE=null
SUNG_CENTER_JOINT_COVARIANCE=null
SUNG_2023_HAL=https://hal.science/hal-03870721
MEASURED_ROWS=9
INCIDENCE_RANK=6
CYCLE_DIM=3
CALIBRATION_COUNTERFACTUAL_RANK=2
CALIBRATION_NOMINAL_INVARIANT_MHZ=-41.0505797921160089478
COVARIANCE_ALGEBRA_IMPLEMENTED=true
STATISTICAL_INFERENCE=NOT_PERFORMED
NEW_SCOPE=PARTIAL_NOT_COMPLETED
PR164_SCOPED_R_C=18/20_UNCHANGED
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
CANONICAL_DAG=28/88_UNCHANGED
REC_PHYSICAL_DAG=0/313_UNCHANGED
REC_EXP_SPECTRAL=PARTIAL
ORIGINAL_35HZ=FAIL7/8
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false
DO_NOT=MERGE_OR_USE_CDMS_2019_OR_2026_AS_2011_OR_ASSUME_FULL_COVARIANCE

RESTORE:
1. Verify this derived package MANIFEST/SHA and the original immutable PR164 ZIP.
2. Read RESEARCH_REPORT_KO.md, source/SOURCE_DISCOVERY.json,
   input/LAB_INPUT_PR164_IMMUTABLE.json and evidence/RESULTS.json.
3. Run src/correlated_cycles.py; src/emit_tables.py; 14/14 tests normal/-O.
4. Acquire original Dec 2011 CDMS v2 raw HD.fit/.par/.lin/c003501i.cat/.egy,
   preserving SHA and historical file identity; then identify original SPFIT covariance.
5. Seek complete Sung line-center/line-shape fit covariance and systematic budgets.
6. Test nine-row experimental covariance only after source-grounded acquisition;
   do not invent diagonal errors, sigma, p-value or promote DAG prematurely.
7. Stop; do not auto-start the next research unit or change owner/main/production.
```
