# rec_bianchi 다음 스레드 / local Codex 복사 가능한 handoff

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rec_bianchi
LAST_UNIT=REC_HD_CONSUMER_CALLSITE_AUDIT
BRANCH=research/rec-hd-consumer-callsite-20261029
LATEST_PR_AND_HEAD=VERIFY_LIVE_GITHUB_AND_FINAL_DELIVERY_ACK
PARENT_PR=155
PARENT_IMMUTABLE_HEAD=861b7f8b3e52d580437a1b4ad448d9669b0d2706
PREFIX=research/rec_hd_consumer_callsite_20261029/
CENTRAL_CANONICAL=28/88 (+0)
REC_PHYSICAL=0/313 (+0)
SCOPED_STAGE=18/20, R6_C9_PARTIAL_NONAUTHOR_NOT_RUN
LAMDA_HD_ORIGINAL_BYTES=2289
LAMDA_HD_ORIGINAL_SHA256=0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb
PR151_MULTICHANNEL_GIT_BLOB=029255494bf0a63b93bf8b2715327a8585afb5f3
PR155_FIELD_SEMANTICS_GIT_BLOB=21517960f912efbd2dc9df8b94fd577e03ca2e27
ORIGINAL_35HZ=FAIL_7_OF_8_PRESERVED
CDMS_2011_V2_RAW=NOT_ACQUIRED
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD
AUTO_NEXT_NODE=false

먼저 실제 PR HEAD, FINAL_DELIVERY_ACK.json, THEORY.md, CODING.md,
CALLSITE_MATRIX.json, SOURCE_MAP.json, results/RESULT.json,
DAG_DELTA.json, NEXT_NODE_CONTRACT.json을 읽고 현재 repo/branch identity를
새로 확인한다. 이전 스레드의 실행환경 실패/성공을 새 런타임으로 추정하지 않는다.

이번 연구에서 실제 PR151 multichannel.generate(...source_consistent=False)는
인쇄된 photon nu_P로 radiation Bose occupation과 photon_E를 계산하고,
충돌 상세균형에는 level E_u-E_l을 사용한다. PR155 frequency_comparison은
두 정책의 진단 비교다. REC hyrec_source_adapter의 one_photon_planck_null_residual은
같은 frequency로 Boltzmann population과 Planck occupation을 만들므로
독립된 source energy mismatch를 검출할 수 없는 항등적 null이다.

국소 프레임, ordinary frequency, h=2*pi*hbar:
  nu_E=100*c*(w_u-w_l), nu_P=1e9*nu_print_GHz,
  R_ul=n_u W_down-n_l W_up,
  Q_m+gamma = sum_ul h*(nu_P-nu_E)*R_ul.
최대 |h(nu_P-nu_E)|=1.210962399179234431758e-27 J/event (J6->5).
이것은 실제 heat rate, entropy, observational uncertainty가 아니다.
원본 source를 수정하지 않고 PR151의 메모리상 J2 nu_P만 +0.001GHz 바꾸면
복사 edge 1개만 변하고 7개 복사/18개 충돌 edge는 불변이다.

실제 검증: Python unittest 23/23 PASS, 6 source-node generate+ledger
preflight PASS, compileall PASS, Decimal90/Fraction exact8 coefficients 일치,
Wolfram exact symbolic local ledger/null check, figure 직접 확인·수정.
초기 RED: analytic bath oracle의 불필요 exp(-x_E) 인자 및 matrix test의
표시 이름 규칙 오류. 둘 다 수정 후 재검증했고 CODING.md에 기록했다.
Native distinct-author R6/C9 NOT_RUN; 이 단계는 완료라고 표시하지 말 것.

NEXT A (local full checkout): REC/BASS/REI 실제 전체 repo의 native C/Rust,
generated code, runtime source adapter, LAMDA/HD ingestion, frequency frame,
Einstein B, line width와 energy ledger의 call graph를 정확한 commit/tree로 추적.
CALLSITE_MATRIX의 9개 파일 검토는 전체 부재 증명이 아니다. 실제 추가 HD
consumer를 찾으면 metadata-only metamorphic mutation과 source identity를
보존한 독립 테스트를 추가한다. default production 코드는 수정하지 않는다.

NEXT B (independent input): CDMS December 2011 v2 original .cat/.egy/.par/.fit/.lin
원바이트와 SHA/크기/버전, c003501.cat 2019mtime 문제, QN/TAG/uncertainty,
LAMDA conversion recipe를 확보한 후에만 source-choice proposal을 작성한다.
CDMS 2026 v3로 대체하거나 원35Hz gate를 완화하지 않는다.

기존 PR150 24case, PR151 9x9 stationary, PR152 cycle, PR154 joint interval,
PR155 16 tests 및 native/IVP/full suite는 무의미하게 재실행하지 않는다.
REC PR155 verify-durable-backup CI는 역사적 CSV trailing whitespace를
포함한 repo-wide verify_repo.py --quick failure였으며 새 연구 PASS와 구분한다.

Reproduction (owner private source restored separately; never publish raw HD on public Git):
  python3 research/rec_hd_consumer_callsite_20261029/audit_consumer.py \
    --source /private/hd.dat \
    --multichannel research/rec_hd_multichannel_affinity_20261029/code/multichannel.py \
    --field-semantics research/rec_hd_field_semantics_20261029/field_semantics.py \
    --output /tmp/hd_callsite_result.json
  REC_HD_SOURCE_PATH=/private/hd.dat \
    python3 -m unittest discover \
    -s research/rec_hd_consumer_callsite_20261029/tests -v

실제 단계별 Git commit과 Drive/Dropbox ACK가 있는 경우만 BACKUP_COMPLETED를
표기한다. 중앙28/88 및 REC0/313은 새로운 실제 물리 승인 없이는 유지한다.
```
