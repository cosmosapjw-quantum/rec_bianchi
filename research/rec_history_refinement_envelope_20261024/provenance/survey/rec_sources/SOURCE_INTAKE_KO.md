# REC 다음 history 비교를 위한 R1/R2 source intake

## 채택 가능한 다음 유한 연구 단위

실제 h/2 continuation 761 columns와 독립 h/4 R3Q event continuation 1519 columns는 같은 FLRW source frame, 같은 우주론, 같은 시작 eta를 가진다. 두 원본 NPZ를 현재 REC commit `ae189694c15e09c6f96c44ef6b74b48afc2632ac`에서 내려받아 전체 바이트의 Git blob SHA1과 SHA256을 확인했다. 다음 단위는 이 두 저장 history의 공통 초기 구간에서 piecewise-affine 차이의 정확한 구간별 envelope와 nodal/중간점 분해를 계산하는 것이다. 실행 계약은 root가 동결한다. 이 intake에서는 과학적 수치 비교를 실행하지 않았다.

실제 더 긴 h/4 U4A 1551 columns와 U4B 1583 columns도 현재 tree에 있다. 선택한 R3Q 1519 pair는 소스 closure가 직접 연결된 유한 비교 범위이며 최대 coverage 주장으로 사용하지 않는다. target z1100–1133의 물리적 history error reference는 아래 별도 입력 의무로 유지한다.

## 조사 coverage와 현재 identity

- 150개 branch를 100+50 항목의 실제 pagination으로 열거했다. 이전 149개와 이름/SHA를 비교한 결과 기존 branch 변경 0, 삭제 0, 새 branch는 완료된 02R branch 하나다.
- all-state PR 132개를 30+30+30+30+12로 열거했다. PR 제목/본문의 h/8, h8, eighth 정확 토큰 검색 결과 신규 후보 0이다.
- 현재 recursive tree 6183 entries, `truncated=false`를 전부 path/blob/size/type 기준으로 조사했다. NPZ뿐 아니라 BIN, JSONL, CSV, archive 등 refined raw 경로 171개를 별도 보존했다.
- source 내용 읽기는 해당 후보의 producer, startup, receipt, 독립 review에 집중했다. 150개 모든 branch의 모든 파일을 읽었다고 표현하지 않는다. 이전 149 branch head identity가 유지되어 기존 조사 근거를 재사용한다.
- 기록: `REC_METADATA_INVENTORY.json`, `REC_CURRENT_TREE_INVENTORY.json`, `REFINED_HISTORY_RAW_PATH_INVENTORY.json`. 원본 텍스트와 byte identity는 `fetched/`, `FETCHED_TEXT_IDENTITIES.json`에 있다.

## 실행 준비가 된 정확한 두 입력

| 항목 | h/2 | h/4 |
|---|---|---|
| 실제 local NPZ | `raw/h2_continuation_python_continuation.npz` | `raw/h4_event_python_continuation.npz` |
| 원 Git 경로 | `research/rec_r3i_time_refinement_20261016/h2_continuation_001/ncp_run_001/python_continuation.npz` | `research/rec_r3q_h4_continuation_20261020/ncp_event_001/python_continuation.npz` |
| 크기 | 3,710,522 B | 7,390,437 B |
| Git blob | `be6e267cbe9bcfa309eec9b2dd458b0ceecbed44` | `d91967045a484c5d164edf6c051e01dab57f7dbc` |
| SHA256 | `70274c9631b33e4ed1c4b8761608cd9ce22f82d96b0afbcb36c0e786e2c04c6d` | `7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9` |
| step | 4.245e-5 | 2.1225e-5 |
| photon 시작 global index | 36446 | 72892 |
| columns | 761 = 8+753 | 1519 = 8+1511 |
| virtual_out / average_virtual | [311,761] 각각 | [311,1519] 각각 |
| lyman_out | [3,761] | [3,1519] |
| states_json / steps_json | 754 / 753 | 1512 / 1511 |
| 마지막 photon input index | 37206 | 74410 |
| 마지막 accepted state index | 37207 | 74411 |

Spectral arrays는 binary64이며 states/steps는 Unicode JSON이다. h/4에는 scalar dlna, source_zip_sha256, parent_checkpoint_sha256, rei_activation=false와 final_predictor[2,2]가 함께 저장되어 있다. h/2에는 이 scalar들이 내장되어 있지 않아 정확한 producer receipt와 archived startup producer로 identity를 묶는다. NPZ header와 state/step index만 읽었고 array value 비교는 하지 않았다.

h/2 U4 2006-column NPZ의 parent SHA256이 위 h/2 continuation SHA256이다. 이번 공통 구간은 그 상속된 첫 761 columns 안에 전부 있으므로 직접 parent를 선택하면 9.65 MB U4 파일의 새로운 구간을 불필요하게 섞지 않는다.

## 공통 source·우주론·frame 및 startup

공통 original archive SHA256은 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`이다. h/2와 h/4의 original C 비교에서는 활성 DLNA 토큰만 각 grid로 바뀌었다. h/2 원본 startup producer와 h/4 producer/receipt를 함께 확인했다.

| 우주론 항목 | 두 후보의 값 |
|---|---:|
| T0 | 2.7255 K |
| nH0 | 0.18971712352134673 m^-3 |
| omega_b h² | 0.0224 |
| omega_m h² | 0.14309694000000003 |
| omega_DE h² | 0.31113726660800006 |
| YHe | 0.2454 |
| N_eff | 3.03821934419124 |
| curvature / w0 / wa | 0 / -1 / 0 |
| fsR / meR | 1 / 1 |

h/4는 h/2 모듈의 시간 step과 무관한 scalar 식과 우주론만 재사용하고 z8000부터 자신의 He trajectory와 derivative memory를 독립적으로 만든다. h/2 checkpoint interpolation, C state import는 입력되지 않는다. 초기 물리 prescription은 같지만 FULL 시작점의 numerical He/H state와 predictor는 각 grid에서 따로 생성되므로 같다거나 정확한 reference라고 가정하지 않는다.

두 producer 모두 local photon j<2에서 incoming을 0으로 둔다. 따라서 zero-feedback startup의 물리적 시간 길이는 2h2와 2h4로 다르다. 이 grid-dependent startup 영향은 뒤의 nodal discrepancy에 전파될 수 있다. archived h/2 seed 연산 순서는 /(2*h2), h/4는 original-source /2./h4다. 이 차이도 total discretization/roundoff 차이에 포함된다.

`virtual_out` 311개와 `lyman_out` 3개는 source Wien reference에 대한 signed dimensionless occupation departure다. `average_virtual`은 별도 물리 field다. 이전 scalar 함수의 shear_q=0은 현재 local directional expansion의 FLRW q=1과 구별한다. 모든 계수와 frame은 이번 두 후보의 own-domain으로 고정한다.

## clock, causal prefix, event의 정확한 대응

eta(g)=-log(8001)+g h이고 36446 h2=72892 h4다. 따라서 coarse photon m과 fine photon 2m이 같은 eta에 놓인다. photon column j는 input state g0+j의 outgoing이며 update 뒤 accepted state는 g0+j+1이다. h/2 continuation은 state36454에서 재개하며 첫 새 photon col8, h/4는 state72900에서 재개하며 첫 새 photon col8이다.

두 파일에서 완전히 덮인 coarse segment는 m=0,...,758의 759개다. coarse nodes0...759와 fine nodes0...1518만 필요하다. 수학적 piecewise-affine 함수의 closure는 [eta0,eta0+759h2]다. 이 두 충분한 retained prefix에 대한 공통 emission-query 데이터 정의역은 eta0≤query<eta0+759h2다. 별도의 physical incoming query는 face가 소유한 실제 prefix length와 retarded source mapping을 함께 만족해야 한다. 오른쪽 endpoint는 저장된 outgoing 값이고 half-open domain의 supremum은 해당 연속 closure의 one-sided limit로 계산할 수 있다. 임의의 이후 column이나 extrapolation은 입력하지 않는다.

여기서 native guard iz>=2는 current step/committed prefix length 조건이며 emission coordinate x=(query-eta0)/h의 lower bound가 아니다. native interp_Dfnu는 iz>=2일 때 x=0과 첫 cell을 정상 사용한다. 따라서 [2,759)는 native source가 요구하는 emission-domain이 아니다. 실제 근거의 path·line·function은 SOURCE_GUARD_CLARIFICATION.md에 모았다.

event.iz는 outgoing을 만든 input index가 아니라 update가 끝난 output state index다. h/2 HELIUM_CUTOFF는 state37205, local759이고 h/4는 state74409, local1517이다. 그 결과 마지막 공통 segment m758에서는 C758/F1516이 H_HE input, midpoint F1517이 처음 H_ONLY input, C759/F1518이 H_ONLY endpoint다. event 전후의 다른 branch가 섞인 이 segment를 별도로 표시한다.

startup 출처는 각 node의 j<8 mask로 보존한다. coarse m>=8의 continuation-only 집계도 제안하지만, 이 집계가 이전 startup의 전파 오차를 제거했다고 해석하지 않는다.

## 다음 계산식과 acceptance scope

C_m과 F_j를 같은 outgoing channel의 coarse/fine 값으로 두고

```text
E_m     = C_m - F_(2m)
delta_m = (F_(2m) + F_(2m+2))/2 - F_(2m+1)
D_m(u)  = (1-u)E_m + u E_(m+1) + 2 min(u,1-u) delta_m, 0≤u≤1
sup|D|  = max(|E_m|, |(E_m+E_(m+1))/2+delta_m|, |E_(m+1)|)
```

를 계산한다. 두 stored interpolant의 차이가 각 fine half-cell에서 affine이므로 절댓값 최대는 위 세 node에서 얻어진다. 이 값은 저장된 함수 사이의 유한 discrepancy를 정확히 대상으로 한다. 구현은 roundoff allowance와 source identity, shape, finiteness, strictly covered domain을 계약에 연결한다.

E는 초기 상태·time stepping·branch event·roundoff가 섞인 nodal difference이고 delta는 fine 데이터에 대한 coarse chord의 midpoint residual이다. delta만으로 연속 physical solution의 M2나 시간 적분 정확도를 선언하지 않는다. 외부에서 같은 domain의 epsilon_fine_reference가 제공되면

```text
|I_coarse - f_physical| ≤ discrepancy_envelope + epsilon_fine_reference
```

를 적용할 수 있다. 현재 그 uncertainty와 justified curvature bound는 null이다. 새 strong no-go 주장은 없다.

root가 실제 313 retarded queries를 포함할 경우, 이전 source-owned routing을 재사용하고 각 upstream query가 공통 half-open domain 안인지 먼저 guard한다. query mapping과 all314 outgoing channel discrepancy는 다른 대상이므로 lowest virtual/line routing을 기존 source mapping 그대로 적용한다.

## 다른 실제 후보 및 최신성

| 후보 | 실제 보존 자료와 scope |
|---|---|
| h/2 U4 | 2006 columns, 9,645,700 B NPZ. 현재 선택 pair의 coarse parent를 포함한다. |
| h/2 U5 | checkpoint SHA256 7aeec545..., 16733 columns와 provider raw archive 기록 존재. 이전 admission에서 target313queries를 덮지만 candidate cosmology가 target과 다르다. 현재 provider readback은 backup 담당자가 관리한다. |
| h/4 R3S smoke | 24 columns, 119349 B NPZ, 02R 검증 근거를 재사용한다. |
| R3R actual32 | retained NPZ 197179 B, 실제 후보로 보존한다. 이번 pair의 입력으로 택하지 않았다. |
| h/4 R3T U4A | parent R3Q 뒤32steps, state74443,1519+32=1551columns. final_checkpoint.npz 7343882 B와 prefix/accepted binaries 존재. receipt PASS_SCOPED_U4A_RESTART. |
| h/4 R3T U4B | U4A 뒤32steps, state74475,1583columns. final_checkpoint.npz 7494526 B, SHA2561a8a224ff473c2c2cd054bc6ec78bcb06ee900b9e2694a9f30509591a56b5446. receipt PASS_SCOPED_U4B_RESTART. |
| original C h/h2/h4 | 기존 R3H canonical cosmology state trajectories가 있다. outgoing photon history field의 직접 reference와 구별한다. |
| v060 source history | data/pr05b2_source_history_v060.npz 35239470 B가 있다. 독립적인 same-target finer history로 새롭게 식별된 자료는 아니다. |

U4A/U4B의 완전 NPZ를 발견하기 전 split raw만 있다는 중간 메모는 현재 tree 조사로 교정했다. 원래 bytes/receipts는 보존했다. no-h8 관찰은 현재 tree 경로와132PR의 exact-token 검색 범위에만 적용한다.

## target 의무·실행·전달 상태

고정 target는 T0=2.728 K, nH0=0.18745798773143102 m^-3,313retarded queries z1100.092189396162...1133.87330719964다. 이번 pair의 source frame/우주론은 서로 일치하지만 이 target과는 다르며, 이전 mapping에서 이 초기 prefix의 target coverage는0/313이었다. 이 사실은 pair의 own-domain 비교를 막지 않고, target H5를 채우려면 target에 맞는 reference uncertainty 또는 정당한 bound가 필요하다는 의무를 고정한다. Bianchi geodesic/direction/frame owner와 full thermodynamic Jacobian은 별도 열린 연결이다.

이 intake: new IVP0, native runtime0, RHS0, old campaign replay0, scientific array comparison0, 외부 mutation0. 읽기·다운로드·NPZ header/index metadata 확인만 했다. 기본 네트워크 read의 EPERM 첫 실패를 raw/h2_direct_download_attempt.json에 남겼고 승인된 read-only network 실행으로 두 파일을 복원했다. CPU/wall을 과학 allocation의0초 실행으로 위장하지 않는다.

Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED, REI_activation=false를 유지한다. source intake 파일과 raw inputs의 새 백업/게시/단계 ledger는 root 소유다. 다음 행동은 root가 위 pair와 오류 allocation·resource budget을 동결한 뒤 유한 envelope 계산을 구현·실행하는 것이다.
