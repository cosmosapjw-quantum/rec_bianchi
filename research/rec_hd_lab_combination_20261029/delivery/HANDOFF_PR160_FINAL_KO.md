# rec_bianchi PR160 연구 인계 | 2026-10-29

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/rec_bianchi
LATEST_PR=https://github.com/cosmosapjw-quantum/rec_bianchi/pull/160
BRANCH=research/rec-hd-real-lab-combinations-20261029
PARENT_PR=159
IMMUTABLE_PARENT_HEAD=46ecb52d059e2dea156b9bca144356344db8a51a
SCIENCE_COMMIT=34f91a698b04aa45fe958bea93cae4d7df87d8dc
STAGE_20_HEAD=87890b184c3e8379feb8c4f4cb9c52842b9df5a4
FINAL_DELIVERY_ACK_COMMIT=af66b99f72ec464696c29cfad5eee3f57899e8a0
FINAL_HEAD=READ_CURRENT_PR160_HEAD_AFTER_HANDOFF_COMMIT

NEW_UNIT=REC_HD_LAB_COMBINATION_20261029
NEW_SCOPED=18/20
R6=PARTIAL_DIFFERENT_AUTHOR_NOT_RUN
C9=PARTIAL_DIFFERENT_AUTHOR_NOT_RUN
CANONICAL_DAG=28/88 (+0)
REC_PHYSICAL_DAG=0/313 (+0)
REC_EXP_SPECTRAL=PARTIAL_TWO_LAB_COMBINATIONS_IMPORTED
ORIGINAL_35HZ=FAIL7/8
CDMS_DEC2011_V2_RAW=NOT_ACQUIRED
ORIGINAL_LAMDA_HD_RAW_REACQUIRED=false
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false

실제 신규 물리 데이터: HD v=0 J2-J0 8,006,533,168(26) kHz, DOI 10.1140/epjd/s10053-022-00552-x; HD v=0 J3-J1 13,283,245,098(30) kHz, DOI 10.1103/PhysRevA.105.062823. 이전 REC PR156 photon printed-frequency 합과 실험값의 차이는 각각 -14.8774 MHz, -45.0342 MHz. 주파수 오차 sigma 또는 실측 heating 판정이 아니다. Rank2의 제약으로 3개 개별 전이 주파수를 모두 식별할 수 없다. 8개 source photon A/frequency에서 hnu, wavelength, spontaneous power, 3온도 photon occupation 생성. 실험 두 조합에 고정된 두 조건부 LTE 인구비 T=50,100,200 K 생성.

Python 19/19 일반·-O, compileall PASS; Wolfram rank/nullspace/합 잔차·LTE 검산; 3 figures 물리 source 데이터 사용. 원본 CDMS v2 및 private LAMDA raw input이 없으므로 physical native provenance full validation은 NOT_RUN. 독립 저자 R6/C9 NOT_RUN.

먼저 Git의 research/rec_hd_lab_combination_20261029/ 아래 THEORY_KO.md, CODING_KO.md, REPORT_KO.md, DAG_EVIDENCE_DELTA.json, STAGE_LEDGER.json, data/LAB_ANCHORS.json, evidence/MEASUREMENT_RECONCILIATION.json, evidence/PHOTON_PHYSICAL_TABLE.json, delivery/FINAL_DELIVERY_ACK.json, delivery/STAGE_GIT_RECEIPTS.json을 확인하라. Parent와 Git commit/tree/blob를 검증하고 원래 35Hz gate를 보존하라.

백업 원본 ZIP: REC_HD_LAB_COMBINATION_20261029_SOURCE.zip, 839151 bytes, SHA256 d9a920979e73c81e378670874952b06e76811fa81f3b669d153d43febf60ce51, 51 members, manifest50/50, CRC PASS. PR159 604100-byte 원본 ZIP SHA256 cdcbfbd1f5249ccdaf5d8a108d490431701febffbb3e6433e9c711e3ad8d035e 중첩 보존.
Google Drive: https://drive.google.com/file/d/13FB4dEwq9Yc1O2P07GV90E1kGedjRQUJ/view?usp=drivesdk; 실제 원격 전체 바이트 SHA256 MATCH. Library: /BASS/rec_bianchi/REC_HD_LAB_COMBINATION_20261029/REC_HD_LAB_COMBINATION_20261029_SOURCE.zip. R/C 20 stage JSON 각각 Git 커밋, Drive 20/20 upload+size ACK, Library 20/20 upload ACK. Git stage source 20/20 blob 일치. Stage records are retrospective publications, not independent 20 scientific calculations.
Dropbox Paper: https://www.dropbox.com/scl/fi/wbop8omlb04za6owrss9m/REC-HD-2022-primary-measured-rotational-combination-data-_-PR160-source-bound-report-and-handoff.paper?rlkey=7pdooisv5ed281xjqln3wud6d&dl=0 rev1 readback. Dropbox 바이너리 ZIP 백업 NOT_ACK. 이중 바이너리 백업 완료 주장은 금지.

후속 연구의 최우선 과학 작업: CDMS 2011 original v2 .cat/.egy/.par/.fit/.lin (c003501i.cat 2011 vs c003501.cat 2019) 원본 바이트, QN/TAG/fit covariance 및 2021 LAMDA hd.dat 원본 확보; 추가 제약을 출처 모델에 재적합/확산하고 물리 owner/native binding을 정확히 검증할 것. 2026 v3 대체 금지. Production default, original35Hz, main, 외부 owner 변경 금지, force push 금지, prior expensive IVP 반복 금지.
