# REC → REI 40-state tangent 연구 계약

2026-10-21, Asia/Seoul. Stage A: 새 결과 조사·단위 선택·입력 고정.

## 선택한 한 단위

고정 PR147 collisionless LRS Einstein–Boltzmann 40-state RHS의 analytic
Jacobian-vector product(JVP), transpose product(VJP), 초기 세 signed seed
`(S_F_i, P_m_F_i, P_r_F_i)`의 forward tangent 실행 인터페이스를 완성한다.
기존 175-case 그림과 729 warm pilot은 complete_reused로 연결한다.

후보 비교:

| 후보 | 최신 근거 | 결정 |
|---|---|---|
| massive moment 미분·native kernel | BASS_CR93 C21N의 pressure derivative, REI215의 NCP native 반환이 존재 | 식·격자 구조 재사용 |
| 전체 time-cell source enclosure | HH132 PHYS77이 8-state owner S0 계약으로 진행 중 | 이 단위에서 중복 구현하지 않음 |
| full40-state JVP/VJP 및 세 seed tangent | 읽은 source에는 H feedback과 amplitude 직접항을 결합한 이 API가 없음 | 선택 |

## 입력·물리 범위

- 물리 source: REI PR147 `3b85dedce84d37b3e165da00685a8a984950aafe`.
- 원 vendor 파일·MIT LICENSE를 byte-identical 복사하고 SOURCE_MANIFEST로 고정.
- L=8, 상태40개, mass fraction .1, m/Tref=30, 24×12 cells, Gauss3.
- 독립 massive-matter 및 gamma+massless-nu radiation, ne_source=None.
- x=ln(a/a_ref), a_ref=1/21, z20→2. Source의 positive fm branch에서
  thermal u는 H와 RHS에 기여하지 않는 원래 계산을 그대로 미분한다.
- sigma=diag(-s,-s,2s), pi_A=diag(-p_A,-p_A,2p_A), kappa_t=8piG/c².
  S_F=√6 s/H, P_A,F=√6 kappa_t p_A/H². Norm은 abs, half norm은 /√2.
  total signed=P_m+P_r를 먼저 만들고 마지막에 abs한다.
- 초기 S=0에서의 미분은 signed-shear smooth extension의 미분이다.
  기존 양의 초기 shear grid를 음의 shear 계산으로 재분류하지 않는다.

## 계산식과 납품 범위

`Z'=F_y Z+F_A A_p`, `Z(0)=dy0/dp`를 구현한다. Radiation seed는 초기
hierarchy 값으로, matter seed는 immutable canonical packet weight로 들어가므로
F_A 직접항을 반드시 포함한다. N(A)/Nref(A)의 normalization 미분도 유지한다.
같은 상태에서 mass-shell sqrt grid를 한 번 준비하고 여러 tangent 열에 재사용한다.
40×40 dense Jacobian은 실행 경로에서 만들지 않는다. VJP는 별도 transpose 식이다.
NCP 실행기는 독립 미완료 tangent case만 예약하고 새 output namespace를 사용한다.

## 가벼운 검증 계약 — 결과를 보기 전에 고정

- 기존 저장40case에서 epoch indices [0,40,80,120,152]를 그대로 추출한
  200state fixture. 7개의 S 값과 stress corners/cancellation/4 D8 cases를 포함.
- 원 RHS와 analytic adapter의 scaled max difference ≤2e-13.
- 5-point finite difference와 state JVP, amplitude 직접항 및 signed-observable
  JVP의 scaled difference ≤2e-8. Fixed deterministic directions, du=0.
- 별도 analytic VJP의 duality residual ≤512 eps64 × (1+절댓값 내적 규모).
- 초기 seed map/세 observables derivative의 scaled difference ≤2e-9.
- rho_b=-6pi, pi_b≤0의 독립 CAS·finite difference·packet 식 검산.
- 잘못된 shape, complex/nonfinite, collision source, changed closure를 거절.
- 새 synthetic interior seed `(0.002, 0.00007, -0.0002)`의 x∈[0,1e-4]
  parent IVP 한 번과 augmented IVP 한 번, output nodes3으로 wiring을 확인.
  전체 z20→2 tangent IVP와 성능 benchmark는 이 로컬 단위에서 실행하지 않는다.
- 물리·수학 독립 검토와 코드·원자료 독립 검토, 실제 plot 직접 확인.

## 최신 실행의 반영

REI215 `926bae816ef8339137e2813cc40f1d514b763e1f`는 NCP compile1,
작은2-step case5, 40/40 gates를 보고했다. 그 실행의 scientific adjudication은
PENDING이고 receipt integrity만 별도 PASS다. 이번 tangent의 NCP 검증으로
전용하지 않는다. NCP64CPU/128GiB는 target ceiling이며 최신 receipt의
관측값을 현재 live allocation으로 사용하지 않는다.

REI199 D8 case `1c39be4e…`의 FAILED_WORKER_EXIT/124와 data-only recovery
이력은 보존한다. 저장 state를 미분 fixture로 재사용하는 것은 solver_success
재판정이 아니다. 다른 대화 검색은 Personal Context unavailable로 공백이 있다.

## 단계·보존

A 조사/계약/입력 → B 유도/CAS/구현 → C 경량검증/독립검토/그림 → D push/backup/handoff.
각 단계마다 DAG evidence와 create-only checkpoint를 남긴다. 실제 provider ACK,
commit/ref를 확인한 단계만 게시·백업 완료로 기록한다. 기존 실패·예약·CPU debit은
수정하지 않는다. Physical HOLD, global convergence NOT_RUN, production
NOT_APPROVED, REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET,
REI_activation=false를 유지한다.
