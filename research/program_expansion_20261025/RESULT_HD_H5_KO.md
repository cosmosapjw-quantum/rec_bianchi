# REC HD 파서와 H5 실제 source 연결 — 2026-10-25

## 결론

고정 LAMDA HD 자료를 읽는 준위·방사 전이·collider 파서를 구현하고, WU의 고정 Species 생성기를 실제로 재사용했다. 원문 decimal, 동위원소 조성, J 표기, p/o-H₂와 정확한 온도 격자를 보존한다. 고정 source의 준위–주파수 일치 gate는 8선 중 7선에서 실패했으므로 원 계약 전체는 HOLD다. 실제 원 공급자의 파일도 고정 snapshot과 같은 2,289 bytes/SHA256이다.

H5는 실제 PB01 source의 313 query, 626 endpoint, 기존 314×313 K_s interval 자료를 결속했다. 조건부 defect–stability–tube–curvature 소비기를 구현하고 실제 nominal 표현 차이를 별도 항으로 유도했다. 실제 연속영역 bound는 공급되지 않아 coverage 0/313, physical epsilon/outgoing bound는 null이다. 이 물리 입력 연결 의무는 미완료다.

원 PB01/KS01 및 기존 캠페인 계산은 재실행하지 않았다. 새 RHS/IVP/native 실행은 0이다. 새로운 강한 no-go 주장은 없다.

## 기준과 실행 범위

고정 인계: rec_bianchi commit `5dd414982c5c9ada97dfdfcc0b77cf83af86d66e`, branch `research/program-expansion-20261025`, draft PR138. 기존 owner PR137의 `ea89c97abeb7a663a813f00e9aadddaf0b32a6a9`는 그대로 둔다. 중앙 고정 계약은 `rei_bianchi@641a725ada4be27473069c2c35005a94c2ab0248`; 통합 직전 관측 중앙 HEAD는 `78f7ac5864d5817ceb79b48cb5e298cc30006510`이다.

각 작업은 현재 HEAD, 적용 AGENTS 부재, 관련 PR/병렬 작업을 확인했다. 중앙의 실제 AGENTS도 읽었다. 현재 사용자 지정 physmath-research-loop built-in 1.0.0과 원 project evidence를 적용했다. 이전 범용 CMB 프로토콜의 물리→수학→구현→저장 및 실제 그림 검토를 이번 유한 작업에 적용했다.

새 독립 예산은 HD 90 CPU s, H5 90 CPU s, 독립 검토·통합 60 CPU s다. 각 단위 wall 600 s, process memory 1 GiB, 1 thread다. 실제 자원은 실행 receipt로 기록하며 network/tool/model/포장 등 미측정 비용은 UNKNOWN_NOT_ZERO다. PB01 잔액이나 C3의 과거 600 s cap을 전용하지 않는다. 원 실패 및 CLOSED_HOLD_NOT_RESET을 보존한다. 정확한 허용량은 `EXECUTION_FREEZE_HD_H5.json`에 있다.

## HD: literal parser와 source 일치 판정

### 지원 범위

| 항목 | 실제 구현·입력 |
|---|---|
| 분자 | 중성 ¹H²H, WU 고정 isotope composition |
| 준위 | 원 source의 J=0…8, 9개 |
| 방사 전이 | 8개 |
| collider | ID2=para-H₂, ID3=ortho-H₂, 별도 |
| 아래방향 collision pair | collider당 9개, 총 18개 |
| 온도 | 정확한 50, 100, 200 K |
| 제공 rate 값 | 54개 |
| 진동상태 | 원 file에 명시되지 않음; webpage v=1 설명과의 불일치 unresolved |
| missing pair | MISSING_NOT_ZERO |
| off-grid/외삽/p-o 혼합 | 지원하지 않음; 명시적 예외 |

소스는 [원 LAMDA HD](https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat), [HD 설명](https://home.strw.leidenuniv.nl/~moldata/HD.html), [LAMDA 형식](https://home.strw.leidenuniv.nl/~moldata/molformat.html)이다. 버전 7 June 2021, spectroscopy CDMS v2 December 2011, collision Flower (1999) Tables 1/2라는 원문 표기를 유지한다. 이 세 페이지와 [LAMDA 이용·인용 안내](https://home.strw.leidenuniv.nl/~moldata/)를 2026-10-25에 다시 확인했다. 공개 변경에는 원 table을 새로 mirror하지 않았으며, exact URL/hash를 통한 local ingestion을 쓴다. 공개 접근과 데이터 재배포 licence는 별도다.

파서는 원 bytes, 각 row 위치와 decimal spelling을 보존한다. 정확한 SI 변환은 E=h c 100 E_cm^-1, ν_Hz=10^9 ν_GHz, q_SI=10^-6 q_cm3/s다. c=299792458 m/s, h=6.62607015×10^-34 J s, k_B=1.380649×10^-23 J/K를 유지한다. Decimal의 명시적 정밀도와 별도 Fraction 계산으로 확인했다.

WU `Species.from_record`는 `34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad`의 unchanged code를 읽어 9개 실제 HD 상태를 생성한다. 기존 249-check 승인은 isotope/finite event 구조 범위로 재사용하며 실제 collision rate의 정확도나 핵 Q 승인으로 확대하지 않는다.

### 보존한 실패

고정 gate는 |100c(E_u−E_l)−ν_catalog|≤35 Hz다. 이는 printed decimal의 표현 일치 조건으로, 실제 spectroscopic uncertainty를 나타내지 않는다.

| line ID | 전이 | exact absolute gap / Hz | 원 gate |
|---:|---|---:|---|
| 1 | J1→0 | 8.241016200 | PASS |
| 2 | J2→1 | 947678.840324000 | FAIL |
| 3 | J3→2 | 1084318.742916400 | FAIL |
| 4 | J4→3 | 47627.409091400 | FAIL |
| 5 | J5→4 | 1245461.910729000 | FAIL |
| 6 | J6→5 | 1827572.560757200 | FAIL |
| 7 | J7→6 | 1411205.450255200 | FAIL |
| 8 | J8→7 | 6864.989622800 | FAIL |

모든 literal 값을 읽을 수 있고 별도 qualification을 조회할 수 있다. `require_energy_frequency_bridge`는 line1만 통과시키고 line2–8은 거절한다. 35 Hz를 늘리거나 두 source 열 중 하나를 덮어쓰지 않았다. 이 차이의 원인은 원 catalog/provenance 대조로 더 확인해야 하므로 현재 원자료 측정오류라고 단정하지 않는다.

### 상세평형과 방사식

한 Maxwellian collider와 같은 T에서 q_lu=q_ul(g_u/g_l) exp[−(E_u−E_l)/(k_B T)]를 사용한다. collision 상세평형은 준위 에너지 차를 사용한다. 방사 helper는 catalog의 photon energy hν를 사용한다.

B가 profile-averaged mean specific intensity J_ν를 곱하는 convention에서 g_l B_lu=g_u B_ul, A_ul/B_ul=2hν³/c²다. 빈도에 대해 정규화한 φ_ν에 대해

`j_ν=(hν/4π)n_u A_ul φ_ν`,
`α_ν=(hν/4π)(n_l B_lu−n_u B_ul)φ_ν`.

n은 m^-3, φ는 Hz^-1, j는 J s^-1 m^-3 sr^-1 Hz^-1, α는 m^-1이다. LTE algebra 검사는 같은 photon energy로 Boltzmann ratio와 Planck factor를 구성한다. expm1을 사용하고 inversion의 음수 α를 보존한다. 양의 비영 값이 binary64 underflow로 0이 되면 analytic-zero로 승인하지 않고 numerical-domain error를 반환한다.

실제 saved DB 54개 최대 reverse normalized residual은 1.2839532962581574e-16, LTE 24개 최대 residual은 2.085550193891887e-16이다. 원 허용치 128 ε64=2.842170943040401e-14를 유지한다. 이 대수 관계의 통과는 위 에너지–주파수 discrepancy를 해소하지 않는다.

처음 24개 unittest 중 23 PASS와 source gate 1 FAIL을 보존했다. changed-path 회귀를 포함한 서로 다른 26개 method는 25 PASS, 같은 source criterion 1 FAIL이다. 전체 primary를 다시 실행하지 않았다.

## H5: 실제 source 좌표와 조건부 오차 연결

### 복구한 실제 근거

원 PB01 S2 ZIP은 69,336,495 bytes, SHA256 `b43ec958374bb8ba97073c46355dc26131a64261cd5004fa64e65c6565da00d1`이다. 이번에 직접 내려받아 이 identity를 확인했다. 필요한 member만 선택 복구했다.

원 history는 35,239,470 bytes, SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`이다. 원 z=1099.9986525171403, T0=2.728 K, nH0=0.18745798773143102 m^-3, prefix5127과 313 query를 유지한다. 같은-source K_s interval314×313과 626 distinct endpoint slot을 결속했다. 원 KS inverse-defect rho는 ODE tube radius로 사용하지 않는다.

### 실제로 추가한 항

각 저장된 binary64 값을 정확한 유리수로 읽고
a_j=(q_j−L_j)/(R_j−L_j),
b_repr,j=|u_j^stored−[(1−a_j)Y_Lj+a_jY_Rj]|
를 계산했다. 이 항은 native weight의 연산 순서와 geometric interpolation의 차이를 포함해 한 번만 들어간다.

313개 모두 비영이며 최대값은 정확히
`2125323597749/7573333069425850157122243222373270552576`,
표시값 약 2.806325270875912×10^-28이다. 단위는 dimensionless occupation departure다. 이것은 source 표현 차이이며 연속 물리해의 defect 또는 uncertainty가 아니다.

### 조건부 계산식

η=ln(a), 고정 양의 scale S에서 ||v||_S=||S^-1v||∞를 사용한다. 같은 source/model/clock에서 연속 재구성, 초기 오차 e0, 전체영역 defect d, model discrepancy b, stability L≥0가 공급되면, 양의 진행거리 s≥0에서

`E(s)=exp(Ls)e0+(d+b)(exp(Ls)−1)/L`, L>0,
`E(s)=e0+(d+b)s`, L=0.

Tube 조건에 사용하는 반경은 proof가 보장하는 **안전 반경의 하계** ρ_lower여야 한다. E_max<ρ_lower의 엄격한 조건을 사용한다. 상계 rho만으로 이 검사를 통과시키던 첫 계약의 방향 오류는 root 검토에서 발견하여 별도 보존·수정·독립 확인했다.

각 endpoint에서 native-channel radius e_side=K_side E_side+bG_side+representation_side를 만들고, whole-cell curvature bound M2가 공급되면

`epsilon_j=b_repr,j+(1−a_j)e_Lj+a_j e_Rj+(M2_j/2)(q_j−L_j)(R_j−q_j)`.

이 식의 마지막 curvature 항은 a(1−a)M2 h²/2이며 최대 M2 h²/8이다. 원 K_s entrywise intervals는 |δo|≤W epsilon, W_ij=max(|Klo_ij|,|Khi_ij|)에 사용할 수 있다. 이는 frozen response 범위이며 nonlinear/source-model remainder 배분은 별도 의무다.

소비기는 0≤Ls≤64에서 양의 Taylor series와 geometric tail, repeated squaring으로 exponential의 정확 유리수 상계를 계산한다. 출력에만 exact integer ceil/floor의 방향을 보존하는 64유효자리 decimal token을 사용한다. 이 유한 구현 범위 밖에서는 unsupported를 반환한다.

### 현재 정확한 종료 지점

실제 same-source continuous reconstruction/state closure, initial/reference error, defect, stability, 안전 tube radius와 whole-cell curvature의 provider 증거는 현재 확인한 source/계약에 없다. 실제 bound coverage는 0/313이다. 따라서 actual packet 실행은 `BLOCKED_ACTUAL_BOUND_INPUTS`이고 physical epsilon/outgoing bound는 null이다.

합성 조건부 입력과 quadratic/L=0/backward/tube control은 소비기 구현만 검증한다. 실제 proof packet이 채워져도 자동으로 물리 승인하지 않고 `CONDITIONAL_BOUND_CANDIDATE_REVIEW_REQUIRED`를 반환한다. proof의 수학·물리 내용, source 대응과 observable error allocation의 독립 판정이 필요하다. 최종 실제 test 수와 자원·코드 identity는 `h5_input_binding/IMPLEMENTATION_RESULT.json` 및 독립 판정이 정본이다.

## 전체 목표에서의 위치와 다음 실행

중앙 DAG는 87 nodes, 17 integration edges와 15 authorities를 가진다. 이번 delta는 REC 소유 HD/H5 두 노드의 현재 관측만 바꾸며 다른 85개 node, 기존 source contracts, conditional dependency와 부모 containment를 보존한다.

| 전체 목표의 구간 | 현재 결과 | 다음 실제 입력/행동 |
|---|---|---|
| WU isotope/event identity → REC molecular source | HD parser 구현 완료, WU schema 재사용 | 기존 supplier code/249-check 재사용 |
| REC-HD-ADAPTER → 선택한 분자 준위·방사 결속 | 원 35 Hz gate 7/8 FAIL | CDMS/LAMDA의 일곱 line provenance를 대조해 정확한 source 해석·새 source identity 결정 |
| PB01/KS01 → H5 → REC-HISTORY | 실제 좌표·행렬 연결, bound 소비기 구현 | 같은 source의 continuous defect/stability/tube/curvature producer packet |
| H6/H7 → REC-FIELD/COUPLED | 이번 입력의무 대상 밖, 기존 OPEN 유지 | 선택 trace/geometry/clock와 실제 미분 owner 연결 |
| 선택한 모델 → REI-L4 | 기존 WAITING 유지 | 해당 모델의 필요한 물리 입력을 충족 |

REC-HISTORY와 REC-EXP-SPECTRAL 부모를 완료로 승격하지 않는다. 전체 물리 완료율은 null, L4_ready=false, REI_activation=false, production NOT_APPROVED다. 두 구현 단위의 결과와 전체 연구의 완성을 구분한다.

## 검토·보존·재현

독립 검토는 원 source를 직접 읽고 Fraction/Decimal 기준식, 실제 source-context와 변경된 경로를 확인했다. 동일 pass에서 발견한 HD underflow·ambient Decimal context, H5 giant-rational serialization·metadata key·tube bound 방향을 최소 수정 및 해당 회귀로 닫는다. 원 code/failure/metadata와 초기 HD source FAIL을 보존한다. 과거 PB01 최초 primary exit2/FAILED, saved vector repair PASS, patched primary NOT_RUN도 유지한다.

실행·기계 판정은 `hd_adapter/RESULT.json`, `h5_input_binding/IMPLEMENTATION_RESULT.json`, `review/INDEPENDENT_DECISION.json`에 있다. 그림은 saved diagnostics에서만 생성하며 실제로 읽는다. 부모의 `CLAIM_GATES_HD_H5.json`, `DAG_HD_H5.json`, `delivery/`는 source·review·publication·backup의 서로 다른 상태를 연결한다. 각 module README의 exact local-input 명령을 사용하면 재현할 수 있다. 원 HD 전체 test는 보존된 source criterion 때문에 실패한다.

게시와 이중 백업의 실제 commit/object ID는 마지막 delivery receipt에서 확인한다. 원 고정 인계서와 source 계약은 덮어쓰지 않는다.
