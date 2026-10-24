# REC-HISTORY 다음 입력 admission 계약

## 다음 과학적 의무

원래 target의 313개 strict-past incoming query에 대해 독립적으로 정당화된
오차 상자 `epsilon_j >= 0`를 받아들인다. 이번 RESP01은 이 오차가 314개
outgoing 값과 같은 Lyalpha atomic/radiation event에 미치는 응답을 준비한다.
실제 epsilon, 절대 history 오차, production 허가는 여전히 null/open이다.
실행 시점의 최종 판정과 resource 잔액은 CLAIM_GATES.json 및 BUDGET_LEDGER.json을 읽는다.

## 1. 고정한 target과 바이트 identity

- Source parent: rec_bianchi@c5394eccf6ff45f134e396c549844af91988aeb7.
- T0=2.728 K; nH0=0.18745798773143102 m^-3.
- z_face=1099.9986525171403; eta_face=-7.003972912850124.
- Incoming 313 queries: z_emit 약1100.092189396162–1133.87330719964.
- Query별 source index, source/target energy, eta_emit는
  results/primary001/QUERY_RESPONSE_COEFFICIENTS.csv에 있다.
- Scalar FLRW, non-tilted local frame, signature(-,+,+,+), proper seconds,
  signed dimensionless Wien occupation departure를 유지한다.
- Original snapshot SHA256:
  3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7.
- PREPARED_BLOCKS SHA256:
  014ce6c467639b28086cfc1d6a70a09818544896b5d21e88508523bec111b9de.
- 공급자는 이 query마다 사용한 실제 endpoint prefix, source row/channel,
  eta convention, frame, parameter와 원본 Git/backup identity를 제공한다.

## 2. 실제 finer 데이터의 지위

기존 h/2 U4 history, h/4 continuation, R3Q finer 및 retained h/2 U5 데이터가
존재한다. 없다고 기술하지 않는다. 기존 REFINE01은 실제 h/2/h/4 저장값의
동일 구간 refinement discrepancy를 인증했으나 원래 T0=2.728 target의
313개 query를 그 후보로 덮지 못했다. 다른 T0/nH0 또는 다른 eta/prefix의
자료를 원래 target의 절대 오차로 옮기는 근거는 아직 없다.

Same-h parity, storage equivalence, 두 해상도 차이, 더 많은 유효숫자만으로
절대 시간보간 오차를 certify하지 않는다. 이미 완료한 저장값 비교는
입력/코드 identity가 유지되면 재실행하지 않는다.

## 3. 허용 가능한 오차 공급 방식

다음 중 하나를 정확한 source/query 도메인에 대해 제출한다.

1. 독립 reference와 그 reference의 오차 상한, 또는 validated trajectory
   endpoint enclosure 및 query 평가 오차.
2. 각 endpoint의 정당화된 uncertainty와 해당 구간 전체의 curvature bound.
   선형 보간의 경우 alpha=(eta-a)/(b-a)에 대해
   epsilon(eta) <= (1-alpha) epsilon_a + alpha epsilon_b
   + M2/2 * abs((eta-a)(eta-b)) + epsilon_eval.
   M2는 exact target function의 구간 전체 2차 미분 상한이어야 하며,
   유한 표본의 최대 second difference를 상한으로 선언하지 않는다.
3. 다른 validated defect/residual 방식이면 안정성 상수, event/startup 처리,
   범위 및 rounding 기여를 포함한 유도를 제출한다.

물리적 target을 바꾸는 parameter/frame transfer가 필요하면 그 transfer의
정의와 별도 불확실성을 제공한다. 기존 다른 우주론 자료의 endpoint를
동일 target으로 간주하지 않는다. 상대오차는 기준량과 영점 처리를 명시해
차원이 없는 absolute occupation epsilon으로 변환한다.

## 4. Admission 순서와 실제 응답 사용

먼저 바이트 provenance와 semantic identity를 확인하고, 모든 313 query의
strict-past prefix/구간 coverage를 확인한다. 이어 independent uncertainty의
증명 범위와 오차 예산을 심사한다. 통과한 epsilon에 대해서만

    abs(delta o_i) <= sum_j abs(K_ij) epsilon_j
    abs(delta R_gamma) <= sum_j abs(c_j) epsilon_j

를 이번 저장된 구간 계수로 outward 계산한다. 코드 진입점은
code/conditional_box.py이며, CLI의 epsilon 공급은 CALLER_RESPONSIBILITY다.
이 API 자체는 입력 공급자의 물리적 admission을 대신하지 않는다.
공급자가 없으면 API의 epsilon과 bound가 null인 현재 상태를 유지한다.

Outgoing row별 허용 오차 b_i 또는 event 허용 오차 b_R를 목표로 정한다면
sum_j upper_abs(K_ij) epsilon_j <= b_i와
sum_j upper_abs(c_j) epsilon_j <= b_R를 사전에 동결한다.
목표 tolerance 또는 epsilon을 계산 결과가 통과하도록 사후 선택하지 않는다.
동일한 오차 상자의 여러 row 최댓값이 하나의 공통 perturbation에서 모두
실현된다고 주장하지 않는다.

## 5. 아직 별도 owner가 필요한 연결

- Scalar local-q 경계와 실제 Bianchi transport의 연결: geodesic, direction,
  source/target frame, energy convention, angular measure, incident trace와 clock.
- Full thermodynamic Jacobian: M/B/T/P의 xHII, xe, TR/TM, geometry 계수 변화.
  primitive rate derivatives나 frozen incoming response K만으로 전체 Jacobian을
  완료로 바꾸지 않는다.
- BASS B3b2의 910 initial packets, HH event-measure 기록, HE/CR/REI의 다른
  유한 완료는 유용한 owner lead다. 이들은 현재 REC uncertainty 공급을
  직접 인증하지 않는다.

## 6. 다음 실행 전 고정할 것

R1/R2에서 변한 ref/입력/owner만 확인한다. 이번 627개 dense RHS, exact dots,
toy controls와 과거 캠페인은 재실행하지 않는다. 다음 비교의 입력SHA,
query 목록, error allocation, branch/precision, resource cap과 이전 누적 비용을
동결하고 그때 필요한 유한 실행만 승인한다. 이번 인계는 새 IVP 또는
native runtime을 승인하지 않는다.

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false;
최초 실패 REI raw HISTORICAL_LOCAL_ONLY를 유지한다.

중앙 고정 authority rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17,
original40nodes/17edges, 다른 owner의 완료 관측을 보존한다. 새 REC 관측과
실제 provider receipt만 추가하며 전체 assembler/renderer를 재실행하지 않는다.
