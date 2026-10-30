# REC-HD J1 CMB single-pass slab | 다음 대화 handoff

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/rec_bianchi
CURRENT_UNIT=REC_HD_CMB_RT_J1_20261030
PARENT_PR=167
IMMUTABLE_PARENT_HEAD=434c7b66b382eda230e9c2f728c937da28c47a1b
SIBLING_PR=165
CURRENT_PR=SEE_FINAL_DELIVERY_RECEIPT

SOURCE_ZIP=REC_HD_CMB_RT_J1_20261030_SOURCE.zip
SOURCE_SHA256=SEE_FINAL_DELIVERY_RECEIPT

PHYSICAL_OUTPUT_CASES=432
SPECTRAL_SAMPLES=138672
PARAMETER_COLUMNS_CM2=1e14,1e16,1e18
SOURCE_GATED_J1=PASS
FULL9_ORIGINAL_35HZ=FAIL7/8
NEW_AUXILIARY=1/1_SCOPED_ONLY
R_C_SCOPED=18/20
R6=PARTIAL_DISTINCT_AUTHOR_NOT_RUN
C9=PARTIAL_DISTINCT_AUTHOR_NOT_RUN
CANONICAL_DAG=28/88
REC_PHYSICAL_DAG=0/313
REC_EXP_SPECTRAL=PARTIAL_9_LAB_RELATIONS_RANK6_THREE_CYCLES
PRODUCTION=HOLD
AUTO_NEXT_NODE=false

THEORY=THEORY_KO.md
REPORT=REPORT_KO.md
SOURCE_CENSUS=provenance/SOURCE_CENSUS.json
TABLES=results/J1_CMB_RT_432_PHYSICAL_CASES.csv;results/J1_CMB_RT_138672_SPECTRAL_SAMPLES.csv

REPRODUCE:
1. Restore ZIP and verify manifest SHA and CRC.
2. python src/j1_cmb_rt.py (432 physical cases; 138672 spectral samples)
3. python -m unittest discover -s tests -v and python -O -m unittest discover -s tests -v (20/20 each)
4. python tests/independent_quad.py (12/12)
5. python src/render_science.py

NEXT_SOURCE_FIRST:
1. Obtain byte-authentic Neufeld 2026 Zenodo v2 hd_lamda.dat + hd_population_grids.fits, validate MD5, compare matched source model only (do not silently replace Flower1999 original input).
2. Obtain byte-authentic CDMS December 2011 v2 original HD.fit/par/lin/c003501i.cat/egy and full fit covariance; obtain Sung line position calibration systematic and joint covariance.
3. Only after owner-source qualification and independent validation, consider full9/source gate. No 35Hz relaxation, no main/owner/production changes, no merge.

DO_NOT_AUTO_BEGIN_NEXT_NODE=true
