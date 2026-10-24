# 다음 입력: 고정 도메인 H5 calibration

## 완료 결과와 재사용

Source/clock/coverage 판정은 완료했다. h2U5 313/313, 다른 세 후보0/313의
결론은 exact-recovered SUMMARY와 이미 완료한 한차례 독립 review에 있다.
환경 reset 이후 원1,252rows/queries/PNG/controller 파일은 복구되지 않았다.
이를 숨기지 않고 delivery/RECOVERY_STATUS.json으로 인계한다. 같은 입력에서
완료한 primary/probe를 재실행해 이 보존 손실을 숨기지 않는다.

## 필요한 물리 입력

Target CSV SHA256는
3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7,
z_face=1099.9986525171403이다.313 native source queries의 도메인은
z=1100.092189396162..1133.87330719964다.

1. 동일 native source·normal frame·energy grid·signed departure reference와
   물리 parameter를 공유하는 실제 outgoing history. Target T0=2.728K,
   nH0=0.18745798773143102m^-3와 다른 history를 사용하려면 model-response
   uncertainty를 따로 정당화해야 한다. Actual h2U5의 T0=2.7255K,
   nH0=0.18971712352134673m^-3 차이를 임의의 rescaling으로 제거하지 않는다.
2. 모든 query의 두 endpoint가 retained prefix 및 target 이전 causal domain에
   존재할 것. Photon column은 input state g에 속하고 final accepted state g+1은
   저장되지 않은 outgoing을 제공하지 않는다. Latest endpoint는 strict exclusive다.
3. 같은 도메인의 independent reference 자체의 uncertainty와 endpoint error,
   또는 actual cell의 exact function에 대한 정당화된 M2 및 endpoint error.
   Same-h parity·storage equivalence·sampled second difference·단순 두-grid
   discrepancy를 인증된 bound로 사용하지 않는다.

## 다음 실행 전 동결

정확한 input/source/parameter/frame identity, covered cell 목록, independent
oracle 및 자체 uncertainty, 목표 input-error allocation과 norm/단위, 누적 budget과
새 finite cap을 먼저 고정한다. 조건부 식

e_u <= 0.5 M2 h^2 alpha(1-alpha) + (1-alpha)eL + alpha eR + e_arithmetic

의 미제공 항은 null로 둔다. h4 후보가 있는 더 이른 epoch로 target을 바꾸는 것은
별도 질문이며 기존 H5를 닫지 않는다. 다음 입력이 공급되면 변한 의존성만 확인한다.
이번 잔여 budget을 새 IVP 또는 과거 campaign 승인으로 해석하지 않는다.

H5 INPUT_DEPENDENT_UNCALIBRATED, REC-HISTORY PARTIAL을 유지한다.
REC-HISTORY-02의 Bianchi geodesic·direction·frame/Wien-reference 및 full
thermodynamic Jacobian은 별도 의무다. 기존 Physical/U5 HOLD,
CLOSED_HOLD_NOT_RESET,global_convergence NOT_RUN,production NOT_APPROVED,
REI_activation=false,first_failed_REI_raw HISTORICAL_LOCAL_ONLY를 보존한다.
