# REC-HISTORY-ADM01 인계 — 입력 도메인 판정 완료, H5 calibration 열림

이 문서는 원 LINE02 handoff와 고정 중앙 handoff
`rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`에 추가하는 관측이다.
실제 Git/provider IDs와 현재 전달 상태는 `delivery/PUBLICATION_STATE.json` 및
최종 companion receipt를 읽는다. Merge·activation은 수행하지 않았다.

## 채택할 결과

- HISTORY01은 `93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`, draft PR130에 게시돼 있다.
  과거18:49중단 기록은 당시 기록으로 보존한다.
- 새 경로 `research/rec_history_input_admission_20261024/`.
  ADM01 `COMPLETE_SCOPED_INPUT_ADMISSION`; physical_reference_admitted=false;
  H5 `INPUT_DEPENDENT_UNCALIBRATED`; 부모 REC-HISTORY `PARTIAL`.
- 최초 primary386/386, 한차례 fresh independent review3probes 모두PASS.
  당시 material blocker0. 환경 reset 후 이 과학 검증을 반복하지 않았다.
- 새 coverage 표시까지 누적 CPU5.928528894s / wall6.092751947s,
  cap20/60s,1thread,최대관측RSS107564KiB. Primary1회,독립probe3개,
  그림render3회. New IVP/native runtime/dense solve/old replay는 모두0.
- HISTORY01 608+14와 LINE02 194checks·202rankqueries·과거6reviewprobes 재사용.
  기존 HISTORY01 CPU4.848191s/wall4.736567968s는 별도 닫힌 배정이다.

## 전달 보존 한계

환경 재연결 후 로컬 workspace가 비어 있었다. StageA45 source/contract는
Dropbox 원 archive SHA/CRC를 확인해 복원했다. Primary SUMMARY는 원SHA256
`6b21a45bb6c3ba2b2460c284e87ac224872226a0bb2aaa46ee4c948d05f8f84e`와 정확히 일치한다.
Review/probe 원문은 남은 도구 기록에서 복원했고 reviewer script는 원SHA와 일치한다.
다른 review 파일의 원 byte identity는 원hash가 없어 별도로 인증하지 않는다.

원1,252상세rows·313querytable·checks·이전controller파일·원PNG/PDF는 미복구다.
원자료가 완전히 보존됐다고 하지 않는다. 현재 그림은 exact SUMMARY로 만든 새 표시다.
`delivery/RECOVERY_STATUS.json`과 review `RECOVERY_RECORD`를 반드시 읽는다.
과학 결과 validity, provenance 보존 상태, publication 성공을 구별한다.

## 실제 입력 판정

고정face z=1099.9986525171403의313 source queries는
z=1100.092189396162..1133.87330719964를 요구한다.
h2U4(2006열),h4R3Qevent(1519열),h4smoke(24열)는 각각0/313.
실제h2U5(16733열)는313/313이며 target 이전10277열 prefix만 사용했다.
Actual/finer 데이터가 없다고 말하지 않는다.

Native source와 energy grid는 일치한다. Photon column j=g-g0는 input state g에,
accepted state는g+1에 속한다. Native 최신 interpolation endpoint는 exclusive다.
Target T0=2.728K,nH0=0.18745798773143102m^-3와 실제 producer
T0=2.7255K,nH0=0.18971712352134673m^-3는 다르다.
U5 actual caller·source capsule·NPZ binding과 actual thermal event의 독립T0복원으로
이 차이를 확인했다. Endpoint/reference uncertainty와 정당화된 curvature bound는
null이다. Same-h parity/storage equivalence를 시간보간 오차 인증으로 쓰지 않는다.

## 다음 행동

AGENTS,실제HEAD,병렬변경,backup을 먼저 확인하고 REPORT_KO.md,
CLAIM_GATES.json,BUDGET_LEDGER.json,독립 FINAL_REVIEW와POST_RESET_DELIVERY_NOTE,
NEXT_INPUT_CONTRACT.md를 읽는다. 완료 검증을 반복하지 않는다.
동일 query 도메인의 matching-parameter history와 independent reference/endpoint오차
또는 정당화된 M2를 공급받은 뒤, 바뀐 의존성과 최소 유한 비교를 동결한다.
새 IVP나 과거 campaign은 이 인계로 승인하지 않는다.

REC-HISTORY-02 characteristic/Wien-reference owner와 full thermodynamic Jacobian은
별도 의무다. Physical HOLD;U5 HOLD_9_FAIL/HOLD_8_FAIL;CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN;production NOT_APPROVED;REI_activation=false;
first_failed_REI_raw HISTORICAL_LOCAL_ONLY를 유지한다.
중앙은 원40nodes/17edges,authority,고정handoff,HE-X1 및 병렬완료를 보존하며
REC-LINE02/REC-HISTORY observations만 추가한다. 전체 assembler/renderer 재실행0.
