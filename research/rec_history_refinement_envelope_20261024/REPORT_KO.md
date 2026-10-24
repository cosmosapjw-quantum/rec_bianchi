# REC-HISTORY-REFINE01 결과 보고

## 결과와 판정

**실제 h/2·h/4 outgoing history의 공통 구간 비교를 완료했다.** 314개 채널과 759개 coarse cell에서 저장된 두 piecewise-affine 함수의 차이를 공통 시각의 값 차이와 fine 중간점 detail로 분해했다. 각 cell의 정확한 수학적 supremum과 이를 감싸는 binary64 구간을 계산했다.

판정은 `PASS_SCOPED_STORED_HISTORY_ENVELOPE`, 자식 상태는 `COMPLETE_SCOPED_STORED_HISTORY_ENVELOPE`다. 한 차례 fresh 독립 검토에서 material open finding은0이다. 부모 REC-HISTORY는 PARTIAL, H5는 INPUT_DEPENDENT_UNCALIBRATED를 유지한다. 현재 실제 physical-reference uncertainty, endpoint uncertainty, curvature M2, absolute physical bound와 convergence order는 null이다.

가장 큰 저장 함수 차이는 helium branch 전환을 포함한 마지막 cell의 `lyman_out[0]`에서 약1.65e-15였다. 같은 채널의 저장 history 크기로 나누면 약29.2%이므로 작은 절대 occupation departure를 높은 물리 정확도로 해석하지 않는다. 전환 이전 continuation 구간의 최대 절대차는 약4.60e-17이다.

## 실제 입력과 정의역

Source parent는 `ae189694c15e09c6f96c44ef6b74b48afc2632ac`이다. 두 원본 NPZ의 전체 bytes, SHA256과 Git blob을 확인했다.

| 항목 | h/2 direct continuation | h/4 R3Q event continuation |
|---|---|---|
| 전체 columns | 761 | 1519 |
| step | 4.245e-5 | 2.1225e-5 |
| 시작 photon index | 36446 | 72892 |
| bytes | 3,710,522 | 7,390,437 |
| Git blob | be6e267cbe9bcfa309eec9b2dd458b0ceecbed44 | d91967045a484c5d164edf6c051e01dab57f7dbc |
| SHA256 | 70274c9631b33e4ed1c4b8761608cd9ce22f82d96b0afbcb36c0e786e2c04c6d | 7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9 |

공통 clock은 eta=-log(8001)+gh이고,36446h2=72892h4다. Coarse nodes0...759와 fine nodes0...1518로759개 cell을 구성했다. 원 coarse column760은 보존하되 비교에는 사용하지 않았다. Photon columnj는 input state g0+j에 속하며 accepted output state g0+j+1과 구별했다.

사용한 채널은 virtual_out311개 다음 lyman_out3개, 총314개 signed dimensionless occupation departure다. 두 표가 같은 source Wien reference를 쓰므로 공통 eta에서 reference는 차이에서 소거된다. average_virtual은 별도 field이며 사용하지 않았다. 공통 source archive·FLRW frame·T0=2.7255 K·nH0=0.18971712352134673 m^-3를 producer와 receipt에 연결했다.

저장 함수 closure는 x=(eta-eta0)/H in[0,759], 운영 query는[0,759)다. Native iz>=2는 current step/committed prefix 길이 조건이며 emission coordinate의 하한2를 뜻하지 않는다. 실제 face의 가용 prefix를 별도로 검사한다. 직접 보간은 bracketing samples를, 분해 경로는 해당 fine cell의 세 점을 요구한다. 후자는 일부 partial-prefix query에서 더 보수적으로 거절할 수 있다.

원래 고정 target는 T0=2.728 K,nH0=0.18745798773143102 m^-3,face z=1099.9986525171403,source queries313개(z1100.092189396162...1133.87330719964)다. 이번 pair의 target coverage는0/313이며 물리 매개변수도 다르다. 이번 자체 domain의 비교가 원래 target를 대체하지 않는다.

## 유도한 식과 오차의 의미

한 coarse cell에서 coarse 양 끝값을 C0,C1, fine 세 점을 F0,Fh,F1로 둔다. 다음을 정의한다.

    E0=C0-F0,  E1=C1-F1,
    delta=(F0+F1)/2-Fh,  phi(u)=2min(u,1-u).

두 저장 함수의 차이는

    D(u)=(1-u)E0+uE1+phi(u)delta

이며 cell supremum은

    B=max(|E0|, |(E0+E1)/2+delta|, |E1|)

이다. 좌우 half-cell에서 두 interpolant를 직접 빼면 첫 식을 얻는다. 각 half-cell에서 D가 affine이므로 절댓값의 convexity에 의해 최대는 세 fine knot 중 하나에 놓인다. Half-open domain에서도 연속 closure의 endpoint 극한은 supremum을 정하는 유효한 witness다.

E에는 독립 초기 상태·predictor memory·time stepping·mode event·roundoff의 차이가 함께 들어간다. delta는 fine 표 자체에 대한 coarse chord의 중간점 residual이다. 이 분해는 두 저장 함수의 차이를 정확히 설명한다. Underlying physical solution과의 오차를 정하려면 별도 uncertainty가 필요하다.

Twice-differentiable physical function의 whole-cell bound |f''|<=M2가 정당하게 주어지면 linear interpolation remainder는 M2 H²/8 이하이다. 이는 NIST DLMF3.3.5의 n=1 경우다. 이차함수에서는 delta=f''H²/8이 정확히 성립하지만, 실제 표의 second difference만으로 continuous M2를 공급하지 않는다.

같은 domain에서 |I_fine-f_physical|<=eps_ref가 독립적으로 증명되면

    max(0,|D|-eps_ref) <= |I_coarse-f_physical| <= |D|+eps_ref

이고, cell 전체의 uncertainty를 eps_ref_cell이라 하면 B_upper+eps_ref_cell을 사용할 수 있다. 코드의 조건부 helper는 이 입력이 없으면 UNAVAILABLE/null을 반환한다. H01의 source-owned boundary transfer와 single-event number/energy ledger,02R의 조건부 characteristic map은 기존 identity로 재사용했다.

## 측정 결과

| 구간 | cell | 최대 B | 최대 절대차의 채널·위치 | 해당 채널 history scale로 나눈 값 |
|---|---|---:|---|---:|
| startup 출처 포함 | 0–7 | 1.8537853650065213e-16 | lyman_out[0],m0,u0.5 | 0.03280834663623202 |
| 전환 이전 continuation | 8–757 | 4.601037190915281e-17 | virtual_out[136],m8,u0.5 | 0.01120084288214378 |
| event-straddling | 758 | 1.6498272419025407e-15 | lyman_out[0],m758,u1 | 0.2919868991524095 |
| post-startup 전체 | 8–758 | 1.6498272419025407e-15 | 같은 마지막 cell | 0.2919868991524095 |

마지막 열은 최대 절대차를 가진 채널의 descriptive normalization이다. 모든 채널의 최대 상대차나 physical relative-error certificate가 아니다. 분모는 해당 채널의 선택된 전체 representation에서 max(|C|,|F|)이며 zero scale은 별도로 처리했다.

전체 최대의 outward enclosure는 다음과 같다.

    [1.6498272419025405e-15, 1.6498272419025410e-15]

위치는 x759,eta=-7.407969562850124,z=1648.0746029265927의 저장 endpoint다. 운영 query에서는 제외되며 one-sided supremum witness로 사용한다. 이 cell의 E0=1.7683147056424054e-21,E1=1.6498272419025407e-15,delta=-1.6599938418419126e-15,Dmid=-8.350793367332902e-16이다. 중간점에서는 nodal term과 fine detail의 부호가 반대이므로 크기를 단순히 더하는 triangle bound보다 세 knot의 실제 최대를 쓰는 식이 더 정확하다.

C758/F1516은 H_HE input,F1517은 첫 H_ONLY input,C759/F1518은 H_ONLY endpoint다. 두 trajectory는 z8000부터 자신의 state/predictor를 만들었고 j<2의 zero incoming도 각각2h2,2h4라는 서로 다른 physical duration을 가진다. m>=8 집계는 초기 출처의 cell을 제외하지만 전파된 startup 오차를 제거하지 않는다. 전체 차이를 순수한 interpolation error 하나로 환원하지 않는다.

## 구현·검증·독립 검토

envelope.py는 direct/decomposed query와 outward interval arithmetic, analyze_pair.py는 source binding·한 번의 실제 배열 분석·독립 Fraction reference, run_bounded.py는 누적 resource enforcement, render_results.py는 저장 결과의 그림을 구현한다. 원 binary64 값을 exact real로 해석하고 각 add/subtract/half operation 뒤 nextafter로 구간을 넓혔다. IEEE round-to-nearest와 gradual underflow, nonfinite/overflow refusal이 명시된 조건이다.

| 검사 | 실제 결과 |
|---|---|
| channel-cells / witnesses | 238326 /714978 |
| Fraction point comparisons | 350/350 PASS |
| exact-rational cell enclosures | 70/70 PASS |
| synthetic·boundary controls | 26/26 PASS |
| 전체 midpoint decomposition | PASS |
| worst midpoint residual/tolerance | 0.015607467292599894 |
| worst oracle residual/tolerance | 0.017121122007845685 |
| primary/figure exit code | 0/0,stderr empty |
| source snapshot 변경 | 없음 |
| fresh 독립 검토 | 1회 PASS_SCOPED,material open0 |
| 최초 PNG 검토 | 2개 직접 확인,layout repair0 |

첫 primary 전에 조건부 scalar bound의 plain floating addition/subtraction을 outward rounding으로 교정했다. 최소 normal/2와 최소 subnormal/2의 exact Fraction 사례를 명시적으로 추가했다. 원 코드와 원 receipt는 evidence/pre_repair_s1/에 남겼다. 이미 완료한 primary를 반복하지 않았으며 독립 검토도 추가 수치 probe가 불필요하다고 판단했다.

## 자원

| 실행 | CPU seconds | execution wall seconds | peak RSS KiB |
|---|---:|---:|---:|
| primary001 | 2.242494 | 2.271521004004171 | 97324 |
| figures001 | 2.589971 | 2.6235228270088555 | 97512 |
| 이번 unit 누적 | 4.832465 | 4.895043831013027 | 최대97512 |

새 allocation은30 CPU/90 execution wall seconds,1thread,1GiB이다. 이 unit의 남은 allocation은25.167535/85.10495616898697이며 새 campaign의 자동 승인이 아니다. 종료 후 inclusive getrusage와 실제 process-local CPU/AS·group wall enforcement를 구별했다. 전체 turn의 I/O·게시·대기 시간을 과학 execution wall로 표시하지 않는다. Wolfram은 timeConstraint5s의 한 요청에서 항등식3개 residual0을 반환했고 client elapsed7.664s,remote CPU는 미관측이다.

기존 H01,ADM01,02R의 지출과 원 HISTORY02 StageA 이후 owner 지출 UNKNOWN은 각각 별도 ledger로 유지했다. 새 IVP0,native runtime0,dense RHS0,old campaign replay0,완료 science 재실행0이다.

## 조사와 전체 목표

SURVEY_SYNTHESIS_KO.md와 보존된 intake는8개 저장소 branch metadata1618개,REC all-state PR132개,다른7개 repo 최근PR70개 및 selected sources를 다룬다. 모든 branch의 모든 본문을 재열람했다고 주장하지 않는다. Dropbox의104 direct/144 recursive 항목,첨부20개,이전 조사 뒤 갱신 파일90개도 확인했다. 다른 대화 검색은 unavailable이었다. SciSpace는 발견에, NIST와 arXiv 원전은 적용 조건·연도 확인에 사용했다.

Intake는566f242b에서 닫았고, 복구 뒤 fca9a31의 DAG가 같은 Git blob56c015ccf8322bdd6ab5979a5be8ec1beb797c6f임을 확인했다. 게시 직전 actual parent는c40d287874f72519103e68267e659fc022eba188로 전진해 변화분만 읽었다. HE-ANG의 TDCS54 sparse source 관측이 추가됐으나 full joint physical provider는false다. 이를 보존한 최신 DAG로 REC patch를 만들었다. Selected-HI consumer, pressure static preparation 및 sparse TDCS는 REC history의 reference uncertainty를 공급하지 않는다.

GLOBAL_PROGRESS.md/json은 원래40nodes·17조건부integrationedges·원저자 상태와 이번 관측을 분리한다. REC는 LINE02 이후 HISTORY/FIELD, 독립된 LI의 입력을 연결한 뒤 COUPLED로 진행한다. H01·ADM01·02R·REFINE01 child는 scoped complete이며 HISTORY parent는 PARTIAL이다. FIELD/LI/COUPLED의 기존 계획,COUPLED NOT_SCHEDULED를 유지한다. 유한 loop의20단계와 전체 물리 목표의 완료율을 혼동하지 않으며 후자는null이다.

## 게시·백업·복원

실제 Git branch는 `research/rec-history-refinement-envelope-delivery-20261024`, draft PR은133이다. S0 commit639e34b66e262c7cd5e910d2df96c57a1cf84ad1,S1 commit4841878fea42437d34465df389c3a8c52c89fbaf,S2 science commitc166b146e32fedb9e4b76e98f5f058a27d3b5e57를 게시했다. S2의 projection109개 blob은 실제 readback과109/109 일치했다. S1의 source code와 input은 원 checkpoint와 같으며 두 설명 metadata는 S2에 추가했다.

S0/S1/S2 full archives는 Dropbox 완료 ACK를 받았다. 작업 공간 초기화가 관측된 뒤 S1과 S2를 실제 복원했고, 각89/146payload의 size·SHA256·Git blob과 ZIP CRC가 일치했다. 코드·입력·raw·review·최초 PNG는 원 bytes다. 이 보고서와 최종 설명 문서는 S2 이후의 문서이므로 복원된 원 과학 근거로 재구성했다. 이 작업은 science replay가 아니다. Clock jump와 중단된 tool의 elapsed 표현은 실제 관측으로 남기며 원인이 확인되지 않은 환경 설명을 만들지 않는다.

Bulk survey·large literature dump·약21MiB RAW_COMPARISON.npz의 전체 bytes는 full-stage archive에 있다. Git에는 core source·CASE_PLAN·원 input blobs·CSV·SUMMARY·oracle·review·그림과 exact location pointer를 게시한다. 전체 ZIP과 Git projection의 범위를 구별한다. 원래 제안 branch의 생성 요청은 응답과 cancellation이 미확정이어서 독립된 delivery branch를 사용했다.

중앙 draft PR225(https://github.com/cosmosapjw-quantum/rei_bianchi/pull/225)는 actual parent c40d287874f72519103e68267e659fc022eba188에서 commit47abc82646d0f92b12d4843abb770be9b3593a37로 게시했다. 두 REC observations와 companion만 추가했으며40contracts/plan_status/dependencies/authority·다른38nodes·HE-X1·최신HE-ANG·17edges를 보존했다. 실제 두 파일의 Git blob readback은2/2 일치했다. 중앙의 immutable observation은S2 science를 고정하며 최종S3·provider상태·마지막HEAD는 delivery/PUBLICATION_STATE.json과 외부 final companion receipt가 기준이다. Merge와 activation은 하지 않는다.

## 다음 의무와 근거

NEXT_INPUT_CONTRACT.md는 원래313query에 맞는 same-source/frame/domain uncertainty 또는 justified endpoint/curvature/stability bound를 요구한다. h4 U4A1551/U4B1583columns와 h2 U516733columns가 실제로 존재한다는 사실을 보존한다. Same-h parity나 storage equivalence는 시간 interpolation error의 certificate가 아니다. Full angular supplier/frame/direction/measure와 full thermodynamic Jacobian도 열린 입력이다.

Physical HOLD;REC_U5 HOLD_9_FAIL/HOLD_8_FAIL;CLOSED_HOLD_NOT_RESET;global_convergence NOT_RUN;production NOT_APPROVED;REI_activation=false;first failed REI raw HISTORICAL_LOCAL_ONLY를 유지한다.

핵심 근거: THEORY.md,FROZEN_CONTRACT.md,CLAIM_GATES.json,BUDGET_LEDGER.json,results/primary001/,evidence/independent_review/FINAL_REVIEW.md,evidence/report_facts.json 및 delivery의 복원·게시 receipt.

원전: NIST DLMF3.3.5(https://dlmf.nist.gov/3.3),Peck/Criscuoli/Rast2017 ApJ850,9(https://arxiv.org/abs/1708.09362),HyRec-2(https://arxiv.org/abs/2007.14114). 마지막 두 자료는 관련 문맥이며 이 두 저장 history의 physical error provider로 사용하지 않았다.
