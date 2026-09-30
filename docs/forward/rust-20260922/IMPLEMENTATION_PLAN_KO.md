# rec_bianchi selected-He source repair and forward-port Implementation Plan

> For agentic workers: 기존 계획의 native/inline 실행 방식을 따른다. Superpowers executing-plans를 사용하되, 이 문서의 웹/로컬 역할 분리가 전역 TDD 및 compile 위치의 일반 기본값보다 우선한다. 새 worktree를 만들지 않는다.

**Goal:** 최초 START가 지정한 selected-He source를 일반 material-frame fixed input에서 의미를 유지하는 callable Rust library로 완성하고, 미검증 코드 게시와 local 검증을 분리한다.

**Architecture:** 현재 PR #81의 `rec_microphysics`를 최소 보완한다. Pointwise source kernel, measure/각도 적분, signed event ledger를 분리하고 기존 solver는 연결하지 않는다. Source subset, 입력 fixture, 실패 분기와 exact candidate가 Git으로 전달되므로 local Codex는 대화나 파일 다운로드 없이 재검증할 수 있어야 한다.

**Tech Stack:** Rust rlib / f64 / 현행 Mat2, Mat3, Complex64 / external Rust dependencies 0개 / Python standard-library reference와 검증 runner. 기준 toolchain은 Rust 1.94.1이지만 실제 local binary/version은 실행 때 기록한다.

**Spec:** `START_CONTRACT_AND_DELTA_KO.md`. 최초 START와 최신 사용자 지시를 함께 보존한다.

## Global Constraints

- Repository `cosmosapjw-quantum/rec_bianchi`.
- Original base `5a09f3797210284f83a1a1adb0e0092d1ac48475`.
- Observed continuation head `49d64b2660f227f6e4d888d6c02ead266d97a138`.
- Existing branch `forward/rust-he-sources-20260922`, PR #81. 이 branch의 좁은 수정만 한다.
- Git/kernel 기준과 archive/delivery 기준을 구분한다. ZIP/TAR SHA는 commit/tree SHA가 아니다.
- 원 source subset을 repo에 추가하고 SHA/size로 잠근다. 기존 local exact bytes가 있으면 redownload하지 않는다.
- 원 T4 ID `T4L01` ... `T4L15`를 유지한다. 임의 L01 rename이나 일부 시험의 PASS 승계 금지.
- Compiler, cargo fmt/test/clippy와 전체 package parity는 이 스레드에서 실행하지 않는다. Toy는 작은 식/연산자/negative control에 한한다.
- TDD의 compiler-red/green은 local 소유다. 여기서 toy-red를 확인했더라도 Rust-red 또는 Rust-green이라고 쓰지 않는다.
- 기존 허용치 `4096 * f64::EPSILON = 9.094947017729282e-13`은 유지한다. 물리 오차/interval proof로 해석하지 않는다.
- Existing Python/C solver와 PROJECT_STATE science 판정 불변. Heavy eigensolve/grid/history/S4/S5/G10 실행 금지.
- 다음 두 commit을 기본 작업 단위로 한다: 후보 source/fixtures, local evidence/handoff. 필요한 최소 follow-up은 허용하되 새 연구단계로 만들지 않는다.

## Review Focus

1. 서로 수직인 photon 방향의 screen overlap은 rank deficient일 수 있다. Identity나 unitary rotation으로 대체하지 않는다.
2. `1+abs(a)+abs(b)`의 임의 차원 있는 바닥이 아주 작은 source의 삭제를 숨기지 않아야 한다. Nonfinite actual/expected/gross는 거절한다.
3. 공개 mutable state를 통해 constructor validation을 우회할 수 있다. 각 public source 경계에서 finite/domain/PSD/screen을 검증한다.
4. 에너지 lookup의 eV와 물리 적분측도 dE_J를 섞지 않는다. 이미 적분된 rate에 E², delta-width, pair 1/2, photon 2를 다시 곱하지 않는다.
5. Archive 내부 lock과 Git lock의 JSON 구조가 다를 수 있다. 실제 source member identity, raw bytes, code identity를 각각 검증하며 문서 내용이나 파일명만으로 대체하지 않는다.

## 0. 현재 확인된 gap와 근거

이 계획은 완료된 코드를 처음부터 다시 만드는 계획이 아니다. 아래를 고치는 계획이다.

| 항목 | 현재 근거 | 결론 |
|---|---|---|
| Pair geometry | `he_singlet.rs:861-891`에서 T12 identity 고정, V1/V2 입력 부재 | 일반 방향 source와 다름. 최우선 수정 |
| BB angular bath | `he_bb_source`가 전체 stencil에 F 하나를 broadcast | 일반 F(E,e)용 per-node 입력 보완 |
| Spectral/measure API | BB는 `shell_integrated: bool`; pair는 M와 일부 weight만 반환 | source 종류/measure의 명시적 분리 및 marginal 조립 추가 |
| Domain checks | Hermitian 검사와 일부 density/T 검사만 있음 | PSD, screen 정규성, positive finite energy, constants 검증 보완 |
| Comparison | 현 `close`에 차원 없는 1을 차원 있는 수치에 더하고 finite 검사 없음 | 기존 숫자 재현과 별도로 엄격한 reference-scale 검사 추가 |
| Oracle independence | Rust example의 자체 residual + 소수 상수 중심 | 독립 full matrix 성분, 재조립 장부, 실패 mutant 필요 |
| Source preservation | Git lock의 preservation.git = HASH_LOCK_ONLY... | 원문 subset 10개를 Git으로 보존 |
| CI evidence | verify.yml은 Python install/import/quick/pytest만 수행 | Rust 검증 근거와 분리. Python CI 녹색은 Rust gate가 아님 |

원문: WU29 §2, §4 Eqs.(7)-(13), §5 Eqs.(14)-(16), §6 Eqs.(19)-(22); WU30 §§3-5; WU31-A1 §3; T4 source interface §§2,6,9 및 T4 test matrix.

작은 실제 검산은 `evidence/toy_contract_checks.py`, `evidence/toy_results.json`에 있다. Rust를 컴파일/호출하지 않았다. Source archive A7/A6 manifest는 이번에 각각 26/26 일치했다.

## 1. 파일 소유권

수정:
- `rust/rec_microphysics/src/he_singlet.rs`: source kernel, 명시적 screen 입력, 검증, spectral outputs.
- `rust/rec_microphysics/src/coverage.rs`: 현재 D86/typed errors 유지, invalid/missing 구분 보완.
- `rust/rec_microphysics/src/ledger.rs`: 동일 사건 적분 결과와 material energy/four-force moments.
- `rust/rec_microphysics/src/lib.rs`: 기존 module 공개 유지, 확정 API re-export.
- `rust/rec_microphysics/tests/forward.rs`: 기존 시험 보존, 계약 반례·비선형/복소 입력 추가.
- `rust/rec_microphysics/examples/eval_fixture.rs`: full matrix raw output와 input fixture 실행 경로.
- `scripts/check_rust_forward_parity.py`: 독립 참조, finite/gross-scale 검사, raw command receipt.
- `tests/fixtures/rust_forward/fixed_source_oracle.json`: 역사적 fixture 보존 또는 명시적 version 분리.
- `docs/forward/rust-20260922/{SOURCE_IMPORT_LOCK.json,SOURCE_DOMAIN_MANIFEST.json,PORT_TEST_COVERAGE.json,FORWARD_STATUS.json,START_HANDOFF_KO.md,RETURN_HANDOFF_KO.md}`.
- `HANDOFF_PROMPT.md`: 새 scoped entry만 보완. Heavy continuation 지시는 실행하지 않는다.

신규:
- `tests/fixtures/rust_forward/frozen_inputs_v2.json`.
- `tests/fixtures/rust_forward/reference_values_v2.json`.
- `tests/fixtures/rust_forward/reference_v2.py`: production Rust와 독립된 성분 수축 reference, Python default dependency 0개.
- `tests/fixtures/rust_forward/acceptance_v2.json`: 실행 전 허용치/규모/실패시험/적용 gate 고정.
- `docs/forward/rust-20260922/source_subset/`: 아래 10개 원문.
- `docs/forward/rust-20260922/{IMPLEMENTATION_PLAN_KO.md,START_CONTRACT_AND_DELTA_KO.md,LOCAL_CODEX_VERIFY_HANDOFF_KO.md,KNOWN_GAPS_20260923.json,CANDIDATE_LOCK.json}`.
- `docs/forward/rust-20260922/local_returns/<actual_run_id>/`: local 결과, raw log, receipt.

보호:
- `src/full_bianchi_hyrec/**`와 기존 C sources.
- `state/PROJECT_STATE.json` 및 기존 scientific receipts.
- workflow, global dependency locks, unrelated user changes.

Cargo.toml/lock은 새 dependency가 필요하지 않으므로 기본 변경 없음. Compile fix 때문에 필요한 최소 metadata 변경만 local receipt에 기록한다. 전체 cargo update 금지.

## 2. API 변경 계약

다음은 계획에서 확정하는 인터페이스다. 구현되지 않은 signature를 현재 기능으로 소개하지 않는다. 0.1 API signature 변경은 APIDelta로 기록하고 이 repo의 tests/example/callers를 함께 바꾼다. 기존 interface가 처리할 수 없는 geometry를 legacy wrapper로 조용히 통과시키지 않는다.

```rust
pub struct WeightedBbMode {
    pub v: RealV,
    pub f: Mat2,
    pub weight_sr: f64,
}
pub struct PairInput {
    pub y: f64,
    pub f1: Mat2,
    pub f2: Mat2,
    pub v1: RealV,
    pub v2: RealV,
}
pub enum SpectralMeasure {
    SharpLineDeltaPerJoule { energy_ev: f64 },
    ContinuousPerJoulePerSteradian,
    PairDyDOmega1DOmega2,
}
```

- `he_bb_source(channel, n_lower, wp, modes: &[WeightedBbMode])`는 같은 wp에 per-node F를 적용한다. Pointwise `he_bb_kernel(channel,n_lower,wp,f,v)`와 angular assembly를 분리한다.
- `he_p_bf_source`와 `he_s_bf_source`는 현행 `energy_ev, &SourceState, table` 경계를 유지할 수 있다. Material E를 J로 한 번 변환하고 출력의 density measure를 명시한다.
- `he_two_photon_pair_source(input: &PairInput, state: &SourceState)`는 실제 V1,V2로 T12를 계산한다. M12와 differential/marginal coefficient 및 event weight를 이름으로 분리한다.
- `assemble_he_event_ledger`는 이미 적분된 signed event rates와 independently accumulated energy moments를 받는다. 원자 사건율에 pair 1/2를 재적용하지 않는다.
- 수치 단위 newtype의 전면 도입, matrix crate 교체, solver architecture refactor는 하지 않는다.

## Task 1. 원문 고정과 상태 정정

**Owner:** 이 스레드, 후속 구현 시작 시.

**Inputs:** current exact branch, A7 embedded A6 source subset, 원 START.

**Produces:** 실제 source bytes와 source lock, known-gap record, 미검증 candidate 상태.

- [ ] 실제 작업공간에서 origin/branch/AGENTS/dirty state를 읽는다. 기존 clone이 없으면 git clone은 허용하되 worktree는 만들지 않는다. Clone 불가 시 connector 기반 편집임을 기록하고 local checkout이 있다고 쓰지 않는다.
- [ ] GitHub actual main/head를 읽어 원 base와 continuation head 차이를 확인한다. Head가 다른 경우 기존 source 범위 diff만 읽는다. 다른 스레드의 user changes를 덮어쓰지 않는다.
- [ ] A7 안에서 아래 10개를 경로와 raw SHA/size로 복원해 docs/source_subset에 보존한다. WU29 standalone Dropbox의 동명 31652-byte 파일은 A6의 31983-byte member를 대신하지 못한다.
- [ ] WU29/30/A1/T4 exact byte를 고정한 뒤 변경할 식/코드 line map을 작성한다.
- [ ] 기존 PASS 문서/로그는 역사적 기록으로 보존하고 현재 pending-local 및 known gaps를 별도 명시한다. 기존 로그를 새 raw output으로 복제하지 않는다.

원문 member:
```
source_subset/sources/BASS_WU29_20260913_RESULT_v1.txt
source_subset/sources/BASS_WU30_20260914_RESULT_v1.txt
source_subset/sources/BASS_WU31_20260914_AMENDMENT_WU31_A1_v1.txt
source_subset/reports/01_T4_SOURCE_TO_TRANSPORT_INTERFACE_KO.md
source_subset/reports/02_T4_CONSERVATION_EQUILIBRIUM_FRAME_AUDIT_KO.md
source_subset/reports/03_T4_COVERAGE_AND_MISSING_PHYSICS_KO.md
source_subset/schemas/SELECTED_HE_SOURCE_LEDGER.json
source_subset/schemas/SOURCE_COVERAGE.json
source_subset/schemas/T4_SOURCE_INTERFACE_SCHEMA.json
source_subset/plans/LOCAL_CODEX_T4_TEST_MATRIX.json
```

Source byte identity 검산의 구체형:
```python
payload = source_path.read_bytes()
assert len(payload) == expected_size
assert hashlib.sha256(payload).hexdigest() == expected_sha256
```

**Stop:** 원문 누락은 해당 family만 `MissingAuthority`; 나머지 확정 family의 이식을 막지 않는다. 실제 회수된 WU29/T4 pair geometry는 MissingAuthority가 아니므로 구현해야 한다.

## Task 2. State/domain/units와 independent fixture 사전등록

**Owner:** 이 스레드 작성, local 실제 검사.

**Consumes:** Task 1 raw authority. **Produces:** fixed input/output/measurement contract와 error tests.

- [ ] 모든 public source에서 n_g,n_S,n_+,n_e 유한/비음수, T 유한/양수, photon energy 유한/양수를 검사한다. E=0은 invalid boundary로 명시한다.
- [ ] F와 WP의 모든 성분 유한, Hermitian, PSD를 검사한다. Density/occupation 검증과 collision source의 부호/PSD는 구별한다. Signed source matrix에 PSD 조건을 걸지 않는다.
- [ ] PSD 검사: 2x2 또는 3x3 Hermitian scaled matrix의 모든 principal minors를 사용한다. 음의 definite counterexample을 반드시 reject한다. Hermitian/screen 검사에는 기존 구현 수준의 1e-12를 기록하고, 정규화한 principal minor의 roundoff 경계는 4096eps로 사전등록한다. minor가 -4096eps보다 작으면 invalid, [-4096eps,0)에 있으면 numerical-domain-uncertain 오류를 반환한다. clipping/PSD projection으로 입력을 바꾸지 않는다. 이는 f64 domain guard이며 exact PSD 인증이 아니다.
- [ ] V는 real finite 3x2, V^TV=I2를 검사한다. Direction을 별도 받으면 V^T e=0, e.e=1도 검사한다. General complex basis는 원문 conjugation adapter가 없으면 지원한다고 하지 않는다.
- [ ] HeConstants의 finite/positive, DeltaP=DeltaS+epsilonIR, IHe=DeltaP+chiP=DeltaS+chiS를 검사한다. 가능한 한 canonical constants를 single owner로 유지한다.
- [ ] Lookup E는 eV, dE 적분은 J임을 모든 differential output에 기록한다. `dE_j = EV_J * dE_ev`는 caller adapter에서 한 번만 사용한다.
- [ ] BF subthreshold 0은 0<E<chi에서만 반환한다. chi<=E이나 q<1, q>1.4는 MissingAuthority다. q=1/1.4를 material-energy API로 왕복한 endpoint fixture도 고정한다. 광범위 clamp로 domain을 늘리지 않는다.

검증용 구체 입력:
```
invalid scalar: NaN, +/-Inf, negative n, T=0, E=-1, E=0
invalid matrices: diag(-1,1), diag(-1,1,1), non-Hermitian offdiagonal, NaN entry
invalid V: 2*[(1,0),(0,1),(0,0)]
valid complex F: [[0.2,0.03+0.04i],[0.03-0.04i,0.1]]
valid complex WP: diag(0.4,0.7,1.1), W01=0.05+0.02i, W10=conjugate
energy: chi/2, chi, chi+1*Ry, chi+1.2*Ry, chi+1.4*Ry, chi+1.6*Ry
```

Test names: `reject_nonfinite_public_inputs`, `reject_non_psd_input`, `reject_nonorthonormal_screen`, `bf_zero_vs_missing_vs_invalid`, `jacobs_energy_endpoint_roundtrip`.

## Task 3. BB angular kernel와 sharp-line 표기

**Owner:** 이 스레드 작성. **Consumes:** WP one owner, per-mode F,V. **Produces:** B, J-shell, C-shell, event trace와 measure tag.

- [ ] 먼저 비등방 두-mode fixture를 작성한다. 예: weights=(1,1) sr, F0=diag(0.1,0.4), F1=diag(0.7,0.2), 서로 다른 V. Isotropic-F broadcast와 같아야 한다는 가정을 제거한다.
- [ ] WU29 (8)-(10)의 pointwise 두 식을 그대로 구현한다. BB에 BF의 transpose를 삽입하지 않는다.
- [ ] b_shell=3A/(8pi)이고, 아래 B/J를 angular weight로 한 번 합산한다.

```text
H = I2 + F
B_shell = b_shell [nL V F V^T - {V H V^T, WP}/2]
J_shell = b_shell [{H,V^T WP V}/2 - nL F]
C_shell = J_shell/(a_gamma epsilon_J^2)
C_E(E) = C_shell delta_J(E-epsilon_J)
```

- [ ] SharpLineDeltaPerJoule를 반환한다. Delta의 pointwise 값을 계산하거나 bin width로 조용히 나누지 않는다.
- [ ] Stencil의 sum weight=4pi, sum(weight VV^T)=(8pi/3)I3 조건을 별도 기록한다. 임의 부분 angular domain에 vacuum B=-AW를 강제하지 않는다.
- [ ] 같은 WP로 584와 IR을 각각 평가한다. lower만 ng/ns로 달라진다.

Local tests: `bb_anisotropic_node_modes`, `bb_atom_photon_trace_complex`, `vacuum_bb_full_stencil_minus_aw`, `bb_lte_each_mode_584_ir`, `bb_sharp_shell_not_profile`, `bb_same_wp_two_channels`.

## Task 4. Two-photon screen tensor와 measure/assembly

**Owner:** 이 스레드 작성. **Consumes:** PairInput, common ng/ns, D86 w. **Produces:** unweighted M12, tagged marginal, unordered-event contribution.

- [ ] 기존 반례 V1=(x,y), V2=(y,z), F1=F2=0, nS=1을 fixture로 고정한다. T12=[[0,0],[1,0]], M12=diag(0,1), tr=1이다. Identity shortcut의 tr=2를 거절해야 한다.
- [ ] T12=V1^T V2를 실제 수축한다. T12는 일반적으로 unitary가 아니므로 F2만 회전시켜 대체할 수 없다.
- [ ] 다음 순서를 문자 그대로 구현한다.

```text
H1 = I2+F1; H2 = I2+F2
XH = T12 H2^T T12^dagger
XF = T12 F2^T T12^dagger
M12 = (ns/2){H1,XH} - (ng/2){F1,XF}
atomic_integrand_dy_dOmega1_dOmega2 = (1/2) w(y) g_ang tr(M12)
tagged_C_integrand_dOmega2 = w(y) g_ang M12/(a_gamma E1_J^2 DeltaS_J)
```

- [ ] y, E1=Delta*y, E2=Delta*(1-y)를 한 곳에서 고정하고 pair partner는 같은 material frame 값으로 읽는다.
- [ ] Pair kernel에 dy/dOmega weight를 넣지 않는다. Assembly에서 정의된 measure를 한 번 곱한다. 기존 caller의 integrated R2g를 ledger가 다시 1/2로 줄이지 않는다.
- [ ] Full ordered pair grid를 쓰고 atomic 1/2는 한 번만 적용한다. 이미 unordered half grid를 쓰는 caller는 별도 contract 없이는 받지 않는다.
- [ ] D86 20개 원수치는 그대로 유지한다. 선형 representative와 symmetry를 검증하되 full-spectrum rescale은 하지 않는다.
- [ ] 두 marginal을 동일 event에서 독립적으로 합산해 photon number=2R2g, energy=DeltaS*R2g를 확인한다. 단순 photon_tags=2 상수 출력만으로 완료하지 않는다.

Local tests: `pair_perpendicular_vacuum_screen_overlap`, `pair_complex_transpose_reference`, `pair_swapped_tags_match`, `pair_lte_all_represented_modes`, `pair_measure_factor_once`, `pair_photon_count_energy_from_marginals`, `d86_all_twenty_nodes_and_reflection`, `d86_outside_band_error`.

## Task 5. BF source/ledger를 실제 동일 사건으로 접속

**Owner:** 이 스레드 작성. **Consumes:** current P/S tables와 SourceState. **Produces:** B_P, C_P/S, j_P/S, energy/heat/four-force moments와 ledger.

- [ ] WU30의 q nodes, separate L/V family, partial s/d labels, Mb->m2=1e-22를 유지한다. S-low/other source family를 추가하지 않는다.
- [ ] 아래 transpose를 변경하지 않는다.

```text
J_F = V F^T V^T
J_H = V (I2+F)^T V^T
K_F = T_E[J_F]
K_W = V^T T_E[WP^T] V
C_P = c[3 etaP sigma_tot (I2+F) - {F,K_W}/2]
B_P_density = c a_gamma E_J^2 [etaP T_E[J_H] - {K_F,WP}/2]
j_P = -a_gamma E_J^2 tr C_P
```

- [ ] 각 mode C, B, j 출력의 적분측도를 명시한다.
- [ ] scalar isotropic WP=nP I3/3 극한은 별도 scalar reference와 비교한다. Full complex matrix parity는 모든 real/imag 성분을 비교한다.
- [ ] jP/jS, E와 independent quadrature weights로 BF photon-energy와 Hkin을 각각 누적한다. Hkin=-Pint-Pgamma로 정의한 다음 conservation을 시험하는 순환 검증은 하지 않는다.
- [ ] 5개 event-matrix column을 각각 rate=+1,-1로 검사한다. BF photon=-1, ion=+1, e=+1이 actual source sign과 일치해야 한다.
- [ ] material moment에서 Qm0=-Pgamma/c, Qgamma=-Qm와 spatial momentum 합계를 계산한다. 내부에너지+Hkin이 물질에너지다. Hkin 혼자 -Pgamma와 같다고 두지 않는다.
- [ ] 기존 Python `four_force`의 nonnegative event-rate API를 signed net rate API로 수정하지 않는다. 신규 ledger 내부에서 해당 net signs를 소유한다.

Local tests: `pbf_complex_component_reference`, `pbf_isotropic_scalar_non_lte`, `sbf_lte_and_non_lte`, `bf_photon_ion_electron_sign`, `bf_independent_heat_moment`, `ledger_each_signed_channel`, `material_four_force_matches_photon_energy`.

## Task 6. Independent parity harness와 실패시험

**Owner:** 이 스레드 작성, local 실행. **Produces:** 독립 reference/fixtures, observable JSON, actual local receipt.

- [ ] `reference_v2.py`는 Rust 결과를 읽어 정답을 생성하지 않는다. 독립 component-index contraction, exact rational algebra fixtures, scalar closed forms를 사용한다. Reference intermediate gain/loss 규모도 별도로 산출한다.
- [ ] eval_fixture는 원 입력을 받으며 raw full matrices, real/imag components, signed events와 separate moments를 출력한다. 자기 계산한 residual만 출력하지 않는다.
- [ ] 기존 frozen outputs와 허용치는 보존하고, v2는 별도 acceptance contract로 추가한다. 기존 역사적 통과 숫자를 새 검사 결과로 바꾸지 않는다.
- [ ] dimensionful comparison의 reference gross scale과 tolerance를 fixture 실행 전에 고정한다. numerical values의 단위에 무관한 +1 floor를 금지한다.

```python
def compare_component(actual, expected, reference_gross, tol):
    if not all(math.isfinite(x) for x in (actual, expected, reference_gross)):
        return False
    if reference_gross < 0.0:
        return False
    if reference_gross == 0.0:
        return actual == expected
    return abs(actual - expected) <= tol * reference_gross
```

- [ ] finite guard, schema 키 누락, subprocess nonzero, malformed JSON는 각각 exit!=0을 내야 한다. Nonfinite를 JSON 숫자로 허용하지 않는다.
- [ ] output mutant 검사를 추가한다: matrix transpose/conjugation 교체, pair half factor 중복, BF signs 반전, small-source 전부 zero, Infinity, missing table을 zero로 대체. 각 mutant를 comparator가 검출해야 한다. Production source를 mutation하지 말고 fixture output/reference 검사 경로에서 실행한다.
- [ ] 약형/JVP는 이 source의 fixed finite stencil에 대해 독립 analytic derivative와 비교한다. September study 전체를 실행하지 않는다. 기존 4096eps와 지정된 legacy precision gates를 완화하지 않는다.
- [ ] 필요 helper만 실제 사용할 때 `study.py@59dafbd34bc21b1b885c716b7b8cc899636bbd60`, blob `f1ad5926de6090e8317961c6cc58914cfd5c8ba3`를 exact bytes로 취득한다. 사용하지 않으면 `NOT_USED`로 명시하며 회수가 조건이 되지 않는다.

## Task 7. 원 T4 matrix 적용과 claim gates

**Gate P:** 이 pure material-frame library의 종료 gate.

| 원 ID | Gate P에서 요구 | 원 시험 전체의 상태 |
|---|---|---|
| T4L01 | exact event null vectors | local 실행 후 판정 |
| T4L02 | 각 channel 독립 energy/heat ledger | local 실행 후 판정 |
| T4L03 | represented 모든 material modes LTE | local 실행 후 판정 |
| T4L04 | normal boosted LTE는 consumer 영역 | DEFERRED_CONSUMER, PASS 금지 |
| T4L05 | normal/material source 및 boost screen | DEFERRED_CONSUMER |
| T4L06 | normal-time atomic continuity | DEFERRED_CONSUMER |
| T4L07 | tilted normal-frame line support | DEFERRED_CONSUMER |
| T4L08 | material threshold/table 부분은 Gate P | full normal lookup는 DEFERRED_CONSUMER |
| T4L09 | material pair energy 부분은 Gate P | full normal pair condition은 DEFERRED_CONSUMER |
| T4L10 | full P matrix -> scalar isotropic limit | local 실행 후 판정 |
| T4L11 | 584/IR complex per-mode atom/photon trace | local 실행 후 판정 |
| T4L12 | missing, invalid, below-threshold, LTE mask | local 실행 후 판정 |
| T4L13 | duplicate total loss/continuum double-count 금지 | source+assembly 검사 후 판정 |
| T4L14 | material four-force energy moment | Gate P에서 구현·검증, 전역 동역학 아님 |
| T4L15 | common Maxwell 외 inverse 거절 | local 실행 후 판정 |

**Gate I:** 다른 repo의 exact-rev consumer integration. T4L04-L09의 실제 normal/material adapter 검증은 여기에 남는다. Gate P 완료가 전체 T4 완료는 아니다. G10/E1C/S4/S5도 아니다.

## Task 8. 미검증 후보 commit/push와 local dispatch

**Owner:** 이 스레드, 실제 이식 완료 후.

- [ ] API/source map, raw subset/lock, static diff, Python fixture syntax, JSON schema, secret/large file mix-in을 검사한다. Compiler PASS는 기록하지 않는다.
- [ ] source/tests/script/fixtures executable-content manifest를 생성한다. Source lock와 acceptance fixture도 이 digest에 포함한다.
- [ ] `FORWARD_STATUS.json`은 `CODE_WRITTEN_UNCOMPILED__AWAITING_LOCAL_CODEX`; tested_commit=null, allow_consumer_integration=false로 쓴다. 과거 status는 별도 historical record로 보존한다.
- [ ] 후보 C1을 commit한다. Commit message 예: `fix(rust): complete source-matched He kernels; local validation pending`.
- [ ] 기존 feature branch에 fast-forward만 push한다. Local git 경로라면 다음으로 종료한다.

```bash
git push origin HEAD:refs/heads/forward/rust-he-sources-20260922
git ls-remote origin refs/heads/forward/rust-he-sources-20260922
```

- [ ] connector 경로라면 실제 parent/tree와 returned commit을 기록하고 remote ref의 SHA를 확인한다. literal git push/ls-remote 성공이라고 부르지 않는다.
- [ ] PR #81의 설명을 'Unverified candidate / local verification pending'로 갱신한다. Merge/ready 인증을 하지 않는다. Draft 전환 여부와 실제 state를 기록한다.
- [ ] 현재 verify.yml은 push/PR에서 Python suite를 자동 유발할 수 있다. workflow는 변경하지 않는다. 수동 dispatch나 polling 반복으로 검증 절차를 대체하지 않는다. 관측한 CI만 보고한다.
- [ ] Raw code+source+candidate lock+handoff를 기존 Drive/Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/`에 create-only 보존한다. Drive folder ID는 `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`이다. Provider 별 acknowledgement, size/object ID를 분리한다.
- [ ] C1의 actual full SHA를 인계문 외부 또는 작은 dispatch receipt에 넣는다. Git commit 안에 자신의 SHA를 self-reference하지 않는다. Header candidate SHA와 source content digest를 local이 대조한다.
- [ ] Remote R1 확인이 끝나면 동일 repo/파일의 중복 회수를 하지 않는다. Upload와 restore 검증은 구별한다.

## Task 9. Local Codex 실검증과 최소 수리

**Owner:** Local Codex. **Inputs:** actual candidate C1와 acceptance_v2, source subset.

- [ ] 기존 local repo의 origin/branch/AGENTS/dirty state를 먼저 읽는다. 다른 변경을 clean/stash/reset하지 않는다. 읽기로 해소 가능한 질문을 사용자에게 반복하지 않는다.
- [ ] Candidate의 정확한 full SHA를 fetch/resolve하고 executable/source-lock digest를 확인한다. 현 branch tip이 dispatch보다 앞서면 자동으로 새 tip을 테스트하지 말고 diff를 분리한다.
- [ ] 현재 실행에서 `rustc -Vv`, `cargo -V`, Python version을 기록한다. 과거 failure/pass를 승계하지 않는다.
- [ ] Candidate에서 세 필수 명령을 실제 실행한다. 각 command/cwd/start/end/exit/stdout/stderr를 파일로 저장한다.

```bash
cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked
python scripts/check_rust_forward_parity.py
```

- [ ] 기존 Cargo.lock을 그대로 사용한다. `rec_microphysics`는 dependency 0개이므로 vendor 전체 빌드/검증은 필요 없다. Cargo network-off를 적용할 수 있지만 로그에는 실제 flag/env를 기록한다.
- [ ] Optional hygiene: `cargo clippy --manifest-path rust/rec_microphysics/Cargo.toml --locked --all-targets -- -D warnings`. 기본 3 gates와 분리해 결과를 기록한다.
- [ ] 기존 regression은 import/quick 및 필요한 non-slow만 실행한다. Science full suite/trajectory/whole-grid는 금지. CI의 기존 자동 full pytest 결과를 local source parity로 대체하지 않는다.
- [ ] MissingAuthority 함수는 reason과 query domain을 테스트한다. 소스 없는 함수를 상수0으로 바꾸어 green으로 만들지 않는다.
- [ ] 실패하면 실제 원인을 compile/type, numeric, physics/formalism, dependency, runtime/service로 분류한다. Format/type/minimal implementation fix는 source 범위에서 수행할 수 있다. 새 물리가 필요하면 해당 함수만 보류한다.
- [ ] Code 또는 acceptance-sensitive artifact가 바뀌면 관련 gates를 다시 실행하고 tested SHA를 새로 기록한다. 기존 tolerance를 느슨하게 바꾸지 않는다.
- [ ] 실제 새 시험 개수를 보고한다. 이전 '15 tests'를 예상 개수로 고정하지 않는다.

## Task 10. 검증된 delivery와 반환

**Owner:** Local Codex, 이 스레드에서 원문/identity 확인.

- [ ] 세 required gates와 Gate P coverage가 모두 닫힐 때만 `LOCAL_VERIFIED_SELECTED_HE_MATERIAL_SOURCE`와 실제 tested_commit_sha를 기록한다.
- [ ] 원로그, executable/source-lock digest, units/frame/domain manifest, 실패 이력, review 결과, 후속 인계를 C2에 보존한다. Raw log의 EOF/색상/whitespace 때문에 trim이 필요하면 raw와 display copy를 분리하고 변환을 기록한다.
- [ ] C2는 문서/evidence-only child다. C1 tested SHA와 C2 delivery SHA를 구분한다. C2의 code-content equality를 확인하면 code 재실행은 불필요하지만 C2 자체를 '시험한 commit'이라고 부르지 않는다.
- [ ] 실제 수정이 있으면 최소 follow-up commit을 허용하고 다시 시험한 code SHA를 반환한다.
- [ ] 동일 feature branch에 push, remote R1, create-only dual backup 후 반환한다. 백업 실패로 성공한 test를 반복 실행하지 않는다.
- [ ] 최종 RETURN_HANDOFF는 repository/base/source/candidate/tested/delivery SHA, 명령별 exit와 log, 실제 diff paths, Gate P/I, 기존 HOLD, provider receipt를 포함한다.
- [ ] 다음 작업은 다른 repo의 exact-rev integration 또는 이 port 종료뿐이다.

## DAG와 중단 규칙

```text
Current49d64b26 + A7/A6
    -> source lock / explicit pending state
    -> state-domain + fixture contract
    -> [BB kernel | BF kernel | pair kernel]
    -> common event/energy/material-force assembly
    -> independent oracle + negative controls + T4 mapping
    -> source candidate C1 / UNVERIFIED push / local dispatch
    -> local toolchain + 3 mandatory gates
       -> failure: minimal bounded fix -> repeat affected gates
       -> missing authority: affected function HOLD, continue others
    -> tested code SHA / evidence C2 / remote R1 / dual backup
    -> exact-rev consumer Gate I OR END
```

이식 도중 '검증 계획을 더 정교화하는 작업'을 새 단계로 무한히 만들지 않는다. 원문과 입력/출력이 닫히면 코드부터 작성한다. 웹에서 컴파일하지 않는다는 결정은 검증 의무를 삭제하는 것이 아니라 local owner로 옮기는 것이다.
