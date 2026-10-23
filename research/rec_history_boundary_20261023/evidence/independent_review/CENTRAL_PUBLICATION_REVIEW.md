# 중앙 publication 일관성 확인 — 기존 독립 검토의 delivery 연속 단계

**판정: PASS_MECHANICAL_CONSISTENCY. 실제 REC publication SHA/branch/PR 결합은
명시적으로 남은 root의 마지막 작업이다. 과학 판정 변경이나 새 검토 pass는 없다.**

검토자 `/root/independent_review`는 중앙 `AGENTS.md`,
`central_sync/baseline_to_final.patch`, `STRUCTURAL_VALIDATION.json` 및 해당
validator의 조건을 읽고, 기존 `REVIEW.json`과 현재 unit의 `REPORT_KO.md`,
`CLAIM_GATES.json`에 대조했다. Validator나 과학 시험을 다시 실행하지 않았고,
외부 변경 및 다른 담당자 파일 수정도 하지 않았다.

## 확인한 보존 범위

- 제안된 중앙 경로는 **README.md, assembly/DAG.json,
  assembly/REC_HISTORY_STATUS_UPDATE.json의 세 개**다.
- DAG에서 바뀌는 wrapper는 **REC-LINE02와 REC-HISTORY 두 개**이며,
  변경 key는 `plan_status`와 추가 `observed_completion`이다.
- Patch와 보존 validator의 결과는 **40개 node의 원 contract object,
  17개 conditional integration edge, authority/integration object,
  나머지 node 및 기존 HE-X1 observed completion을 그대로 유지**한다.
  고정 handoff와 authority 문서는 수정 경로에 들어 있지 않다.
- REC-LINE02는 기존 **194 checks의 과학 완료 재사용**과 이후의
  **FINAL_RECEIPT_RESOLVED**를 구분한다. Dropbox는 기존 whole-byte 확인의
  재사용, Drive는 metadata/size와 whole-byte `NOT_RUN`으로 기록하여
  provider 검증 수준을 승격하지 않는다.

## 과학 상태의 일치

| 항목 | 중앙 관측과 unit 문서의 상태 | 기존 독립 판정과의 관계 |
|---|---|---|
| REC-HISTORY-01 | COMPLETE_SCOPED_BOUNDARY; primary608/608, independent3cases14/14 | 일치 |
| Parent REC-HISTORY | PARTIAL | 일치 |
| 실제 history interpolation | INPUT_DEPENDENT_UNCALIBRATED | 후보 파일의 존재와 same-domain reference/curvature admission을 구분하므로 일치 |
| Bianchi directional propagation | OPEN / OPEN_INPUT_CONTRACT | energy/direction/frame provider가 남으므로 일치 |
| Full thermodynamic/cosmological Jacobian | NOT_CLOSED | 고정 계수 방향의 결과로 승격하지 않음 |
| Global coupled history | NOT_RUN | 일치 |
| 새 allocation | CPU4.848191s / wall4.736567968s; reset 없음 | 기존 receipt 및 독립 보고서와 일치 |
| Primary live aggregate CPU/RSS | NOT_OBSERVED_PID_NAMESPACE_LIMITATION | 기존 F8 제한 보존 |

Unit의 REC-FIELD 재사용 문구는 finite boundary/event/source **interface**와
열린 H5–H7을 함께 전달하는 범위다. 중앙에서 REC-FIELD나 다른 node를 완료로
바꾸지 않으므로 전체 coupled history 또는 physical admission의 과장으로
읽히지 않는다. `608`을 assertion 수로 설명하고 actual native runtime/IVP
및 old LINE02 replay를 모두 0으로 유지한 점도 기존 판정과 일치한다.

Physical `HOLD`, REC_U5 `HOLD_9_FAIL/HOLD_8_FAIL`,
`CLOSED_HOLD_NOT_RESET`, global convergence `NOT_RUN`, production
`NOT_APPROVED`, `REI_activation=false`가 중앙 sidecar와 unit claim gates에서
보존된다. 이번 확인에서 수정이 필요한 상태 과장은 발견하지 않았다.

## Publication 결합의 남은 한 단계

`publication_source.commit`, `branch`, `pr`가 현재 `null`이고, sidecar status가
`DRAFT_OBSERVATION_ROOT_SOURCE_PIN_PENDING`인 것은 현재 준비 단계와 일치한다.
Root는 실제 REC publication 결과로 이 필드를 채우고 pending 상태를 갱신한
다음 중앙 expected-SHA 갱신을 진행하면 된다. 바로 전 실제 중앙 HEAD/대상
blob 확인 및 병렬 변경 보존 의무도 sidecar에 남아 있다.

여기서 기존 `a7c46fd...`는 재사용한 LINE02 과학/source pin이다. 새
`research/rec_history_boundary_20261023/...` evidence 파일의 publication
identity는 새로 결합할 REC commit이다. `LINE02_DELIVERY/source_pin`을
새 관측 파일 자체의 주소로 사용하지 않고 이 두 의미를 구분해야 한다.
현재 `kind=currently_read_local_observation_pending_new_delivery_commit`
표시는 그 구분을 이미 드러낸다.

실제 source 결합과 Git/provider delivery가 끝났다는 주장은 이 확인에
포함하지 않는다. 기존 **PASS_SCOPED** 과학 verdict는 유지되며, 새로운
과학 실행·추가 assertion·새 review cycle 없이 이 일관성 확인을 종료한다.
