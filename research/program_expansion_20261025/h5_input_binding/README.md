# H5 실제 history 연결과 조건부 오차 소비기

원 PB01/KS01 science archive에서 필요한 원자료만 복원해 **313개 실제 query,
626개 서로 다른 endpoint slot, 314×313의 기존 K_s entrywise interval**을 연결했다.
`inputs/SOURCE_CONTEXT.json`은 원 byte identity와 실제 cell/clock/source routing을
담는다. `inputs/ACTUAL_BOUND_INPUTS.json`에 요구되는 물리 bound는 아직 공급되지
않아 actual bound coverage는 **0/313**, physical epsilon은 `null`이다.

## 현재 산출물

- `code/prepare_actual_binding.py`: 고정 PB01 S2의 필요한 member만 복구하고 실제
  query와 원 history의 endpoint를 대조한다. 원 trajectory, RHS, KS certificate,
  PB01 primary를 다시 실행하지 않는다.
- `code/h5_bounds.py`: 원 조건부 유도의 defect/stability → tube → endpoint →
  interpolation bound를 실행 가능한 계약으로 옮긴다. 연속영역 proof를 받는
  경로와 실제 source의 입력 부재 경로를 구분한다.
- `code/consume_bounds.py`: 공급자 packet을 읽어 결과와 정확한 미충족 입력을
  저장한다. 구조·byte 확인은 외부 proof의 수학적 승인과 구분한다.
- `tests/test_h5_bounds.py`: 해석적 equality/limit, orientation, tube escape,
  sampled-bound 거부, clock/reference/source, actual 313-query 계약을 검증한다.
- `inputs/DERIVATION.md`, `inputs/INDEPENDENT_THEORY_REVIEW.md`: 중앙
  `641a725ada4be27473069c2c35005a94c2ab0248`의 유도와 독립 심사 원문이다.
  유도 SHA256은 `e4dc39a4d142a5baea3458b8a68ca2d68ce7aed0a1537c6160401c646258169b`이다.

전체 위치는 REC-HISTORY의 H5 잔여 의무다. PB01의 source-history pullback 완료,
KS01의 represented-matrix certificate와 이번 source binding은 재사용할 수 있다.
다음 실제 진척은 아래 공급자 입력에 있다.

## 다음 실제 공급자 입력

같은 원 cosmology (`z=1099.9986525171403`, `T0=2.728 K`,
`nH0=0.18745798773143102 m^-3`), `eta=ln(a)`, native Wien departure와
prefix5127에 대해 다음을 공급한다.

1. 연속 재구성 `x_h`, target source equation `F`, native history map `G`, 고정
   성분 scale과 norm, 초기 오차 `e0`. 원 source의 retarded history를 포함하는
   상태 정의 또는 정당화된 해당 구간의 closure를 명시한다.
2. 전체 선언 구간에서 defect `d`, source/model discrepancy `b`, stability `L`의
   상계와, 재구성 주위의 uniform open safe tube radius의 양의 인증 하계
   `tube_radius.lower`, existence/bootstrap 근거. 같은 재구성·고정 norm·eta
   domain의 전체 tube를 그 하계 반경 이상 덮어야 하며 `E_upper<rho_lower`를
   엄격히 만족해야 한다. Tube 반경의 upper-only 입력이나 경계 equality는 거절한다.
3. 각 313 query cell에서 `K_left/right`, reference mismatch와 endpoint
   representation radius, `ess sup |y''|`의 `M2` 및 cell regularity 근거.
4. 증거 파일의 실제 위치·해시, 원 목표의 observable error allocation과 필요한
   nonlinear outgoing remainder. 수학적 bound의 유효성과 science tolerance
   충족은 별도 판정이다.

원 KS01의 `rho=3.458800151575591e-12`는 행렬 inverse residual이다. 이 값의
의미는 실제 ODE defect 또는 위 tube radius와 다르다. REFINE01의 저장된
grid 차이와 sampled second differences도 whole-cell bound 입력을 공급하지 않는다.

다음 최소 공급자 단위는 아직 미실행인 `REC-H5-BOUND-PRODUCER01`의 첫 실제 cell
증명이다. 시작 owner는 `research/rec_history_thermo_20261024/provenance/source_intake/ORIGINAL_NATIVE_HISTORY_LEAD.json`과
`SOURCE_HISTORY_PROVENANCE.json`이 가리키는 원 `input.dat`·PR05B2 source이며,
복구 경로는 고정 PB01 S2 → `delivery/recovery001/KS01_S2_RECOVERED.zip` →
`inputs/pr05b2_source_history_v060.npz` 및 `inputs/THERMO01_S2.zip`이다.
`scripts/run_pr05b2_causal_history_stage.py::parse_raw_history`의
`eta=-log1p(z_start)+dlna*index` clock과 저장된 prefix5127을 유지한다.
`research/rec_history_thermo_20261024/vendor/hydrogen.c::rec_HMLA_2photon_dxHIIdlna`
및 `fplus_from_fminus`/`interp_Dfnu`에서 지연 history를 포함하는 실제 `F`를
정의하고, 같은 디렉터리 계열의 `code/source.py::parameters`, `rates`, `build`,
`outputs`의 primitive와 native `G`를 재사용한다. 이 파일들의 점별 미분은 전체
연속상태의 stability 증명이 아니므로, 원 `HyRec_Oct2012.zip`
(`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`)의
`history.c` thermal/helium branch와 함께 원 상태의 연속 재구성, retarded-history
상태공간 또는 method-of-steps closure, 고정 성분 scale/norm 및 native reference를
먼저 명시해야 한다. 첫 cell도 초기 오차 `e0`와 지연 입력의 인증 enclosure가
필요하며 0으로 가정할 수 없다. 원 interpolation stencil, history routing,
small-optical-depth branch 경계를 분할하거나 해당 regularity를 증명하여 실제
`d,L,rho_lower,K,bG,M2`를 생산한 뒤 313개 cell 전체로 확장한다. 현 소비기는
313개 완전한 packet을 요구한다. 현재 완료는 source binding과 조건부 계산
guard/직렬화 구현이며, 이 다음 producer 및 물리 bound 승인·연결 0/313은 남아
있다. 이 조사에서는 새 RHS·IVP·원 source 실행을 하지 않았다.

## 실제 표현 차이의 연결

고정 query의 binary64 값을 좌표로 택한다. 원 저장된 knots와 endpoint 값으로
정확한 유리수 geometric linear interpolant를 만들고 실제 nominal input과의
차이를 `b_repr`로 분리했다. 실제 313개 query 모두에서 그 값이 0보다 크며,
최댓값은 `2125323597749/7573333069425850157122243222373270552576`
(표시값 `2.806325270875912e-28`)이다. 이는 occupation departure의 표현 차이이며
physical history error의 보정값이나 상계 전체를 뜻하지 않는다.

실제 물리 endpoint/curvature bound가 공급되면

`epsilon_j = (1-a_j)e_Lj + a_j e_Rj + M2_j (q_j-L_j)(R_j-q_j)/2 + b_repr,j`

로 조합한다. Query/geometry retiming은 PB01의 별도 좌표 입력이며 이 식의
`b_repr`에 포함되지 않는다. 기존 `K_s` interval을 소비하는
`frozen_box_upper`는 독립적인 작은 exact control로 검증했다. 실제 source에서는
epsilon 입력이 없으므로 새 실제 matvec는 수행하지 않았다.

## 실행과 자원

공통 `../EXECUTION_FREEZE_HD_H5.json`의 H5 한도는 CPU90초, execution wall600초,
1thread, 1GiB다. 원 예산을 재설정하거나 빌리지 않는다. 실행별 명령, 코드/입력
identity, exit code, CPU/wall/RSS는 `evidence/execution/`에 보존한다.

복구된 현재 원자료는 `evidence/SELECTIVE_RECOVERY_AND_BINDING.json`의
`materialized_directory`에 있으며, 이 경로는 물리 identity가 아니다. 다음
세션에서도 고정 PB01 S2 archive로 직접 복구할 수 있다.

```bash
python3 code/prepare_actual_binding.py \
  --archive /absolute/path/REC_HISTORY_PB01_S2.zip \
  --unit /absolute/path/h5_input_binding \
  --materialized /absolute/path/recovered/H5_SELECTED
```

변경한 공급자 packet은 새 경로로 저장한 뒤 아래 소비기를 실행한다. 기존
packet과 결과를 덮어쓰지 않고, 필요한 후속 실행 예산을 먼저 고정한다.

```bash
python3 code/consume_bounds.py \
  --context inputs/SOURCE_CONTEXT.json \
  --packet /absolute/path/supplied_bounds.json \
  --proof-root /absolute/path/proof_artifacts \
  --output /absolute/path/new_bound_candidate.json
```

현재 실제 packet 소비 결과는 `results/ACTUAL_BOUND_CONSUMPTION_FINAL.json`이다.
외부 proof 파일을 읽고 숫자가 조합되어도 이 소비기는 `physical_epsilon=null`을
유지한다. 과학 검토가 실제 연속영역 bound와 model/observable 범위를 판단해야
physical admission이 가능하다.

내부 enclosure 산술은 exact rational이다. `exp(x)`는 `0<=x<=64`에서 양의
Taylor 합과 증명된 geometric tail로 상계화한다. 밖의 값은 지원 범위 오류로
반환한다. 매우 큰 정수 비율의 직렬화는 64유효자리 decimal grid의 exact
integer ceil/floor를 사용한다. 상계는 위로, tube margin 하계는 아래로 반올림한다.

`Physical HOLD`, `HOLD_9_FAIL/HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`,
`global_convergence=NOT_RUN`, `production=NOT_APPROVED`, `REI_activation=false`,
`global_physical_completion=null`을 유지한다.
