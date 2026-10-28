# rec_bianchi 다음 스레드 / Codex 복사 인계

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rec_bianchi
LATEST_UNIT=REC_HD_FIELD_SEMANTICS01
PARENT_PR=154
PARENT_SHA=2b86465fe641977aa8a584ed4fb66888fd300929
BRANCH=research/rec-hd-field-semantics-20261029
LATEST_PR_AND_HEAD=READ_LIVE_GITHUB_AND_FINAL_DELIVERY_ACK
ROOT=research/rec_hd_field_semantics_20261029/
CANONICAL_DAG=28/88 (+0)
REC_PHYSICAL=0/313 (+0)
NEW_UNIT_SCOPED=18/20; R6_C9=PARTIAL_NONAUTHOR_NOT_RUN
ORIGINAL_HD_SOURCE_BYTES=2289
ORIGINAL_HD_SOURCE_SHA256=0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb
ORIGINAL_35HZ=FAIL_7_OF_8_PRESERVED
CDMS2011V2_RAW=NOT_ACQUIRED
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false

먼저 PR의 실제 HEAD, source/test Git blob, FINAL_DELIVERY_ACK, REPORT_KO,
THEORY, CODING, DAG_DELTA, NEXT_NODE_CONTRACT 및 저장소/백업의 최신 identity를 읽어라.
본 연구의 16 targeted tests, exact Fraction ratios와 Wolfram 결과를 재사용하라.
공식 LAMDA format의 FREQ optional/not-used 진술은 해당 문서의 프로그램 범위이고,
myRadex는 2021-11-25부터 printed FREQ를 기본 사용하는 반례임을 보존하라.
이 차이를 REC/BASS/REI 전체의 실제 코드 동작으로 추정하지 말라.

다음 독립 작업 A: REC_HD_CONSUMER_CALLSITE_AUDIT.
실제 최신 코드/branch/commit에서 ν_P vs ν_E 선택, Einstein A/B,
Gaussian velocity width vs frequency width, frame redshift/tilt 및 energy ledger를
정확한 함수/행/데이터 흐름으로 매핑한다. 가능한 실제 consumer마다 원본
FREQ metadata-only mutation의 source/core metamorphic test를 설계한다.
기본 production 동작은 수정하지 말고 읽기 전용 분류 결과를 Draft PR에 게시한다.

병렬 입력 의존성 B: CDMS_V2_SOURCE_RECOVERY.
CDMS Dec2011 v2 .cat/.egy/.par/.fit/.lin 원바이트와 SHA/크기/출처를 확보하고
2019mtime c003501.cat과 2011 c003501i.cat의 정체성을 구별한다.
QN/measurement TAG/uncertainty/LAMDA conversion recipe가 확인될 때에만
물리적 source-choice proposal을 검토한다. 2026 v3를 v2로 대체하지 말라.

이전 PR150 24-case, PR151 9x9, PR152 26-channel, PR154 joint interval,
기존 native/IVP/full suite를 무의미하게 재실행하지 않는다.
source-level opacity ratio 최대5.332463622370740788e-7(J2->1)는
고정 A/점유수/속도폭, 각 자체 line centre 비교의 조건부 결과다.
관측 오차·물리적 불확실성·H5 closure로 승격하지 않는다.
각 단계에서 Git commit 및 create-only backup ACK를 구분하여 보고하고
중앙28/88과 scoped progress를 함께 표시한다.
```

Reproduction (private original source file must be restored from owner-controlled SOURCE ZIP, never commit it to public Git):

```bash
python3 field_semantics.py --source source_private/hd.dat --output results/replay.json
python3 -m unittest discover -s tests -v
python3 plot_field_semantics.py
```

Expected: original source SHA/bytes match, 8 source rows, 16 targeted tests PASS, exact maximum J2→1 and max relative peak-opacity difference 5.332463622370740788…e-7. A metamorphic mutation must set `raw_verified_this_execution=false`; it is not a new source pin. Native subagent dispatch was unavailable in this run; distinct-author R6/C9 remain open.
