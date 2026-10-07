# Task7 원 T4 대응과 claim gate

상태: **정적 대응표와 시험 작성 완료, Rust/T4 실행 미수행**. 원 matrix의 ID, class, test 문구는 변경하지 않았다. 본문의 한국어 항목명은 요약이며 정본은 T4_COVERAGE_MAP.json의 original이다.

## 원 항목과 실제 대응

| 원 ID | 요구 요약 | material Gate P | 원 항목 전체 |
|---|---|---|---|
| T4L01 | 정수 사건 null vector·양/음 column | 작성됨 / NOT_RUN | NOT_RUN |
| T4L02 | 5채널 독립 열·에너지 | 작성됨 / NOT_RUN | NOT_RUN |
| T4L03 | material LTE, 양쪽 BF gauge | 작성됨 / NOT_RUN | NOT_RUN |
| T4L04 | boosted LTE | 대상 아님 | DEFERRED_CONSUMER |
| T4L05 | normal/material source·screen | 대상 아님 | DEFERRED_CONSUMER |
| T4L06 | normal-time 원자 연속식 | 대상 아님 | DEFERRED_CONSUMER |
| T4L07 | tilted line support | 대상 아님 | DEFERRED_CONSUMER |
| T4L08 | material threshold·lookup / normal E 변환 | 작성됨 / NOT_RUN | DEFERRED_CONSUMER |
| T4L09 | material pair / normal pair 조건 | 작성됨 / NOT_RUN | DEFERRED_CONSUMER |
| T4L10 | 등방 WP·일반 복소 F의 scalar reduction | 작성됨 / NOT_RUN | NOT_RUN |
| T4L11 | 584/IR complex atom–photon trace | 작성됨 / NOT_RUN | NOT_RUN |
| T4L12 | coverage·missing·LTE mask | 작성됨 / NOT_RUN | NOT_RUN |
| T4L13 | 2gamma/584 중복 계수 금지 | 작성됨 / NOT_RUN | NOT_RUN |
| T4L14 | material energy·four-force | 작성됨 / NOT_RUN | NOT_RUN |
| T4L15 | species-drift inverse 거절 | 작성됨 / NOT_RUN | NOT_RUN |

9개 원 항목은 material library 범위, 4개는 consumer-only, 2개는 material subcheck와 consumer 부분으로 분리된다. 따라서 Gate P 요구는 11개이고 Gate I의 normal-frame 의무는 6개이다. 이 숫자는 통과 수가 아니다.

## Mapping이 가리키는 것

36개의 실제 Rust 시험 symbol을 파일 SHA-256과 1-based line range로 고정했다. 251개 기존 parity input의 ID, 예상 error/status와 출력 field는 FIXTURE_REGISTRY.json에 있으며 원 input/reference/15-file lock은 변경하지 않았다. 모든 행렬 real/imag 및 raw energy/force 관측량은 Task6 example/비교기의 local 실행에서 얻어야 한다. 현재 map은 실행 결과나 Rust 문법·타입 유효성을 입증하지 않는다.

## 보완한 시험과 이유

기존 70개 시험의 65,773-byte prefix를 그대로 둔 채 5개 시험을 추가했다. T4L01은 직접 정수 null-vector 검사, T4L03은 P/S × L/V × 5개 q node/midpoint × 2개 screen의 40개 LTE 입력, T4L02/T4L14는 각 채널만 활성화한 source/heat/energy 비교, T4L13은 Pbf를 584 원자 붕괴율로 재분류하지 않는 결합 시험, T4L10은 WP만 isotropic이고 F는 복소인 matrix reduction을 검사하도록 작성했다. 전부 Rust NOT_RUN이다. 두 supplemental acceptance JSON은 해당 시험 작성 전에 고정했고 기존 허용치 4096eps는 바꾸지 않았다.

## 해석을 제한해야 하는 부분

T4L03의 유한 40개 BF 입력과 기존 BB/pair stencil은 연속된 전체 phase space에서의 정리가 아니다. Pointwise LTE 대수는 동봉된 T4 원문 §4–5에 근거하고 실행 시험은 그 유한 예제를 검증한다. T4L08/09의 material subcheck가 성공해도 D가 들어가는 원 normal-frame 식은 아직 검증되지 않는다. 회전된 material screen은 Lorentz boost의 시험이 아니다.

T4L13: no-double-count는 rate 이름뿐 아니라 실제 reachable source/assembly 경로를 검토해야 한다. assemble_selected_he_material_ledger는 r2g=pair.event_rate를 그대로 전달하고 full tag1만 photon moment에 사용한다. Pbf는 독립 채널이고 584 source의 A나 r584를 바꾸는 propagation-opacity 입력이 없다. 신규 Pbf 결합 시험은 H/He propagation absorber 구현/검증을 대신하지 않는다. 이 물리 source 밖에 소비자가 추가할 absorption은 별도 검토 대상이다.

T4L14: Q_m=-Q_gamma는 정의다. 독립적으로 누적한 P_gamma와 P_int+H_kin을 cQ 성분과 비교해야 하며 H_kin만 물질에너지라고 두지 않는다. Species별 force partition과 normal-frame/전역 중력 동역학은 범위 밖이다.

## local 승인 기준

기본 세 명령을 실제 candidate exact revision에서 실행하고 command/cwd/start/end/exit와 raw stdout/stderr를 보존한다. 모든 mapped test가 실행돼야 하며 0 tests, filter, ignore, skip은 이를 만족하지 않는다. 실제 Rust 251-record 출력과 frozen reference를 비교하고 audit 행은 같은 code identity에서 검토한다. 이후에만 material Gate P 판정을 별도 local receipt로 기록한다. Python CI/32개 과거 checker 시험/이번 18개 정적 검사기 시험은 이를 대체하지 않는다.

Gate P가 닫혀도 전체 원 T4 완료나 G10/E1C/S4/S5 승격이 아니다. 별도 승인된 exact-rev consumer integration test를 시작할 수 있을 뿐 Gate I는 그 시험으로 닫는다. 현재 candidate/tested/delivery SHA=null, consumer integration=false다.

## 다음 단계

Task8은 기존 feature branch fresh diff 위에 누적 overlay를 적용해 미검증 후보를 게시하고 local 검증으로 인계하는 단계다. 새로운 이론 단계나 검증 설계 반복을 추가하지 않는다. 원문과 source state를 더 넓게 재조사할 이유가 없다면 바로 게시 작업으로 간다.
