# REC HD 실측 고회전 제약 연구 handoff (2026-10-30)

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/rec_bianchi
PARENT_PR=162
IMMUTABLE_PARENT_HEAD=4d60f74db02d7435add062eaefb15739e68c4b55
NEW_UNIT=REC_HD_1984_LAB_GRAPH_20261030
NEW_PR=PENDING_DELIVERY
SOURCE_ZIP_SHA256=PENDING_DELIVERY
NEW_SCOPE=18/20; R6/C9=DIFFERENT_AUTHOR_NOT_RUN
CANONICAL_DAG=28/88 (+0)
REC_PHYSICAL_DAG=0/313 (+0)
REC_EXP_SPECTRAL=TWO_2022_LAB_COMBINATIONS_PLUS_THREE_1984_DIRECT_LINES_PARTIAL
ORIGINAL_35HZ=FAIL7/8
CDMS2011_V2_ORIGINAL_RAW=NOT_ACQUIRED
CDMS2011_V2_FIT_COVARIANCE=null
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false

새 원 실험: Essenwanger/Gush, *Canadian J Phys* 62,1680(1984) DOI 10.1139/p84-213, HD R(3) 350.852±0.002, R(5) 514.656±0.001, R(6) 591.9327±0.0003 cm^-1. 2022 두 조합 차이는 parent PR160에서 재사용. 직접 실측 그래프 rank 5/9 (4 component), 2011 nominal 1-0 conditional anchor로 rank 6/9 (3 component), full 8-line measured spectrum은 미식별.

1984−2021 photon residual: J4−J3 = −28.7337784 MHz, J6−J5 = +433.1123448 MHz, J7−J6 = +0.00685766 MHz. 공동 공분산과 2011 fitting 원본이 없어 σ/χ²는 미산출. 신규 3 measured photon E/λ/P(단 P에 기존 Einstein A 혼합), 9 LTE conditional ratios 저장.

실행: `python src/produce_atlas.py; python -m unittest discover -s tests -v; python -O -m unittest discover -s tests -v; python src/plot_science.py`. 실패 이력 `evidence/FIRST_FAILED_RUN.json` 보존. 원본 zip nested: `backup/PR162_SOURCE_IMMUTABLE.zip`.

최우선 다음 물리: CDMS Dec2011 v2 `.fit` `.par` `.lin` `c003501i.cat` `.egy` 실제 원바이트+fit covariance, 2011 Drouin J1−0 lab uncertainty, 1991 Ulivi direct J4−3 등 실험 정확 입력 인증. 그 다음 joint covariance와 2022/1984 측정 조합을 원본 owner contract와 대조. 2019/2026 CDMS 자동 대체, 35Hz relaxation, production switch, main merge, parent PR mutation 금지. `AUTO_NEXT_NODE=false`.
