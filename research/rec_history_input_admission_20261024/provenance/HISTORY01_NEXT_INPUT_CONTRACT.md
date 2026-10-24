# REC-HISTORY 다음 입력 계약

현재 REC-HISTORY-01 경계 adapter는 COMPLETE_SCOPED_BOUNDARY이고 부모는 PARTIAL이다.
완료된 primary608와 독립 tiny14, LINE02의194 및 historical six probes를
다음 intake에서 다시 실행하지 않는다. AGENTS·실제 HEAD·병렬 변경·provider
backup을 확인한 뒤 바뀐 의존성이 처음 필요한 단계부터 시작한다.

## A. 실제 scalar history 보간 정확도

필요한 최소 payload는 다음과 같다.

| 필드 | 요구 내용 |
|---|---|
| Identity | repository/commit 또는 immutable provider ID, SHA256, source build/options |
| Source domain | atomic model, selected channels, native constants, coefficient/opacity scope |
| Frame and coordinates | local normal frame, departure 기준, η=ln a, time/energy units |
| Grid | η0, 각 η 또는 uniform h, 실제 valid prefix iz, append/ownership rule |
| Outgoing | `[virtual311, Lya, Lyb, Lyg]` 순서의 retained array; signed departure 보존 |
| Query domain | 평가할 face times와313 retarded source/target energy pairs |
| Uncertainty witness | 독립 finer/reference history와 자체 불확실성, 또는 cell별 정당화된 M2=upper|d''| |
| Acceptance | input·population·outgoing·number/energy observable별 물리오차 allocation |

실제 retained history가 있다는 사실과 그 history의 uncertainty가 admit되었다는
사실을 구별한다. 조사한 후보는 provenance/HISTORY_INPUT_INVENTORY.json에
남긴다. 현재 LINE02 z≈1100 snapshot으로 시간 이웃이나 곡률을 추정하지 않는다.
다른 redshift/state/domain의 짧은 continuation이나 same-h parity만으로 이
동일 도메인 오차 gate를 닫지 않는다.

입력이 admit되면 먼저 header/shape/좌표/valid-prefix/energy/frame identity와
reference uncertainty를 확인한다. 그 후 아직 실행하지 않은 유한 cell·query
집합과 별도 budget을 동결하고, 아래 오차 전파를 비교한다.

`e_u = M2*h²*α(1-α)/2 + (1-α)e_left + α e_right + arithmetic`

`e_X ≤ |M*^-1 B| e_u`, `e_out ≤ (|O||M*^-1 B|+|P|)e_u`.

Native M의 현재 positive-comparison witness는 그 exact matrix에서 재사용한다.
다른 thermodynamic state 또는 M*에서 certificate를 주장하려면 그 변경된
matrix에 대한 근거가 필요하다. Actual data를 확보하지 못하면 이를
INPUT_DEPENDENT_UNCALIBRATED로 유지한다. 새로운 IVP를 실행하거나 과거
실패/누적 예산을 초기화하는 것이 이 intake의 대체 동작은 아니다.

## B. 선택한 Bianchi directional history owner

Local q(n)>0 경계와 scalar FLRW history는 각각 admit된 범위가 다르다.
연결에는 다음 물리 payload가 필요하다.

- metric/tetrad와 normal-frame convention, H(t), σ_ab(t), 선택 Bianchi model;
- `d ln E/dt = -H-σ_ab n^a n^b`와 direction evolution의 실제 characteristic owner;
- source event와 target face 사이의 retarded-time/energy map, direction rotation 및 frame transform;
- angular basis/grid와 interpolation, positive-q/domain guards, uncertainty allocation;
- 동일 사건의 atomic·radiation·reservoir ownership 및 redshift-work 회계.

그 입력에서 `δquery`뿐 아니라 `δM,δB,δO,δP`가 필요한 방향을 분리하고
현재 fixed-coefficient tangent와 합성한다. Scalar 배열에 directional outgoing을
단순히 저장하는 것으로 propagation contract가 충족되지는 않는다.

## C. 인계할 downstream 상태

REC-FIELD는 현재 finite boundary/event ledger와 source-to-history interface를
scoped dependency로 소비할 수 있다. 실제 spectrum/thermal-reservoir와
정량적 interpolation uncertainty는 REC-FIELD 자신의 admission에 연결한다.
REC-COUPLED는 선택한 REC-LI/REC-FIELD/REC-HISTORY source gate가 닫힌 뒤
별도 승인된 새 control 계약이 필요하다. Global convergence·production·REI
activation은 각각 독립된 후속 gate다.

현재 protected 상태: Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL;
CLOSED_HOLD_NOT_RESET; global_convergence NOT_RUN; production NOT_APPROVED;
REI_activation=false. C3 등 다른 노드의 기존 잔여 budget도 이 단위에서 사용하지 않는다.
