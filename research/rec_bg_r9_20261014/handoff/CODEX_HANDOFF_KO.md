# R9 REC → REI Codex: finite interval geometry를 같은 사건에 결속

이번 파일은 **새 solver 실행 명령이 아니다.** `rei_bianchi`의 최신 STATE·live owner authority·source SHA를 먼저 확인한다. R9 분석에서 확인한 공개 HEAD는 `750b78705beff198b4db4d69b8f07428ac06a64e`였고, 이 HEAD의 `HALF_MINUS_TERMINAL_PLUS_PRELAUNCH_HOLD_001.json`에는 half-minus 200000 accepted step의 scoped 부분 종료, PLUS 선행 `LIVE_WORKERS_OR_CHILDREN_HOLD`, PLUS solver start 0, 별도 recovery owner가 기록되어 있다. 그 이후 변경되었다면 현재 HEAD가 우선한다. **이 계약으로 재시작하거나 기존 launcher를 우회하지 않는다.**

### 1. 권장 선택

- 현재 `BACKGROUND_TABLE_001`에서 이미 component 검산을 통과한 **stable polynomial interval**을 첫 native finite contract 대상으로 삼는다. 이때 실제 `a1,a2`, 해당 source/family, `log1p((a2-a1)/a1)`을 결속한다. `point_at_scale(a2).time_s-point_at_scale(a1).time_s`가 들어간 모든 실제 source/ray/adaptive call site를 한정 목록으로 작성한다.
- 이번 R9 독립 대안은 양의 F=1/H를 cubic Hermite로 보간한 `code/interval_reference.py`다. `dt=∫P dL`, `db=∫sP dL`을 같은 간격·같은 P로 만든다. 새 음영 영역은 node/exp/log/series roundoff이므로 ideal theorem과 actual native error는 분리한다.
- `BACKGROUND_EXACT_CACHE_001`의 bit-preserving cache에 dt 오차 수정을 끼워 넣지 않는다. 새로운 source/method identity는 기존 checkpoint와 다르다.

### 2. 최소 input/output 계약

정의/상태/예외/검산 정보는 `contracts/REI_NATIVE_INTERVAL_INTERFACE.json`에 machine-readable로 묶었다. 핵심은

```text
finite_interval_geometry(a1:f64,a2:f64,immutable_background_identity)
  -> (delta_l_dimensionless, delta_t_s>0, delta_b_dimensionless,
      method_identity, error_scope)
```

보존 성질: $q\to-q$일 때 *background* dt는 even, db는 odd, q=0이면 db=0. 모든 trial/accepted step은 같은 interval 값을 기체 원자 source·광자 진화·event ledger·ray 및 선택한 observer clock에 일관되게 사용해야 한다. 방향 cosine 및 에너지 사상 오차는 동일 fixed ΔL에서 

```text
|δln(E2/E1)| <= 2 |δb|
|δmu_final| <= 2/sqrt(3) |δb|
|δln(dOmega2/dOmega1)| <= 6 |δb|
```

로 제한할 수 있다. 이들은 photon kinematics이지 Thomson collision/ionization source error certificate는 아니다.

### 3. 다음 actual native pass의 acceptance를 설계할 때

- 기존 R8 서명된 원본 102 selected accepted steps의 local oracle 입력·해시를 사용하되, 원 source가 바뀌지 않았으면 old history producer와 previous oracle을 다시 돌리지 않는다. 가장 큰 old 오류는 PLUS #100: 6,446,090.361918509s vs local 6,446,090.4791734519898s, 상대 -1.81900864e-8. 
- Candidate의 native short interval과 같은 supplied binary64 a1,a2의 독립 60자리 local quadrature를 직접 비교한다. 기존 R7B component target 1e-9는 owner가 명시적으로 채택할 때만 native gate로 사용한다. 출력을 예쁘게 만들기 위해 tolerance를 넓히지 않는다.
- source/config/bin identity, actual launch budget, cold source He normalization, q sign, exact allocation/checkpoint의 새 output namespace를 분리한다. 같은-a vs 같은-proper-time 비교는 별도다.
- 한정된 실제 첫/후기 step의 gas fractions, electron abundance, thermal energy, all photons, ledgers, rejecting/accepted trials, total energy/charge and adaptive control을 비교한다. 변경 방법은 old historical bit parity가 아니라 source-equivalent numerical/refinement test를 요구한다.
- 실제 R9에서는 **production code 0건, solver starts 0건**이다. 이번 공개 packet이 owner의 AX11/AX12를 READY 또는 PASS로 변경하지 않는다.

### 4. 파일과 실행

```bash
python3 -m unittest discover -s research/rec_bg_r9_20261014/code -p 'test_interval_reference.py' -v
```

이 명령은 standalone 수학적 reference의 synthetic test만 실행한다. Rust driver 호출, Grackle 계산, NCP 작업은 하지 않는다. 실제 코드와 dossier 증보는 `research/rec_bg_r9_20261014/`에 추가 게시되면 공개 경로를 통해 가져온다. 수신자가 계약을 실제 적용·검토했다는 ACK는 현시점 확인되지 않았다.
