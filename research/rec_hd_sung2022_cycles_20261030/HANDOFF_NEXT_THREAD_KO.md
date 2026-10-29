# REC-HD-SUNG2022 | 다음 연구 스레드 인계

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/rec_bianchi
UNIT=REC_HD_SUNG2022_CYCLES_20261030
PARENT_PR=163
IMMUTABLE_PARENT_HEAD=65c5c4c9105c9957418ff014d34e007e53a63b3b
CANONICAL_DAG=28/88
REC_PHYSICAL_DAG=0/313
REC_EXP_SPECTRAL=PARTIAL_9_LAB_ROWS_RANK6_THREE_CYCLES
NEW_PHYSICS=FOUR_SUNG_2022_LAB_LINES_AND_H2_COEFFICIENTS
AUXILIARY_DAG=1/2_SCOPED
SCOPED_R_C=18/20
R6=PARTIAL_DIFFERENT_AUTHOR_NOT_RUN
C9=PARTIAL_DIFFERENT_AUTHOR_NOT_RUN
35HZ=FAIL7/8
CDMS_2011_V2_RAW=NOT_ACQUIRED
CDMS_FIT_COVARIANCE=null
SUNG_MULTISPECTRAL_JOINT_COVARIANCE=null
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false

SOURCE_DOI=10.1016/j.jqsrt.2022.108412
NEW_SUNG_R0_R3_cm_inverse=89.22792,177.84141,265.24055,350.85401
LAB_CYCLES_MHz=-3.921711314,-17.890385768,-60.258284058
MEASURED_MATRIX_RANK=6
CYCLE_DIM=3
NOMINAL_MINIMAX_MHz=8.945192884

RESTORE_AND_REPRODUCE:
1. Verify SOURCE ZIP SHA256, manifest and ZIP CRC. Parent ZIP SHA must remain 90ca686b37a15f69605b8f4aad1a259adfb94430474fd6fe8694a38d0365820d.
2. Read THEORY_KO.md, REPORT_KO.md, SOURCE_CENSUS.json, DAG_EVIDENCE_DELTA.json and data/LAB_INPUT.json.
3. python src/lab_cycles.py
4. python -m unittest discover -s tests -v (19/19); repeat with -O.
5. Read evidence/EXPERIMENTAL_CYCLES.csv and H2_PRESSURE_296K_CONDITIONAL.csv.

NEXT_SCIENCE: recover byte-authentic CDMS Dec2011 v2 source .fit/.par/.lin/.cat, determine original SPFIT covariance, ask for Sung multispectral joint calibration/systematic covariance; then source-consistent inference with 9 lab rows and three cycle constraints. Full eight-line experiment remains unidentified.
PROTECT: no 35Hz gate relaxation, no 2019/2026 CDMS catalog substitution, no owner/main/production changes, no merge, no fake sigma/no new IVPs/no cosmic heating claim.
