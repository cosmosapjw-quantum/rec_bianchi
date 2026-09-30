# Task6 독립 parity harness 계약

## 현재 근거 상태

고정 입력에서 계산한 참조값과 Rust 실행 관측을 구별한다. reference_values_v2.json의 251 records는 **REFERENCE_CALCULATION_NOT_RUST_OUTPUT**이다. 3027 scalar component와 111개 오류 기대값이 있다. 32개 Python 검사기/소규모 참조 교차검사만 현재 실행했다. Rust example/compiler/cargo/parity/T4는 NOT_RUN이다.

근거는 source_subset의 WU29 BB Eqs.(8)-(10), pair Eq.(16), WU30 BF 식과 WU31-A1 D86이다. 기존 Task2 domain fixture125, Task3/4 rational matrices와 Task5 SI scalar/component reference를 보존하고 교차검사한다. 신규 단면적, 표 splice, rate rescale, 물리 모델 변경은 없다.

## 파일과 역할

- `source_inputs_task6.json`: 251개의 원 입력. 기록은 숫자 상태와 행렬/모드/측도/방향을 포함한다. Expected-domain은 원 Task2 값을 그대로 포함하지만 Rust에는 전달하지 않는다.
- `reference_v2.py`: 표와 확정식을 explicit component-index sums로 평가한다. Rust output/source를 import하거나 읽지 않는다. P의 T_E를 네 index coefficient로 전개한다. BB/pair는 성분별 직접 수축이며 prior rational matrices와 별도 scalar closed form으로 교차검사했다.
- `reference_values_v2.json`: 계산된 독립 expected values와 차원 있는 reference gross. 실행 관측이 아니다.
- `acceptance_task6.json`: 기존 4096epsilon=9.094947017729282e-13, finite/shape/error/measure 정책과 작은 입력 한계.
- `task6_reference_lock.json`: 위 파일 및 과거 fixture15개의 SHA-256. 임의 actual output으로 reference를 재생성하지 않는다.
- `input_wire_v2.py`: JSON 입력을 Rust stdin token protocol로 변환한다. 물리 source나 기대오류를 계산하지 않는다. 태그형 nonfinite 입력만 NaN/inf token으로 전송한다.
- `eval_fixture.rs`: public Rust API를 호출하고 실제 전체 성분을 JSON으로 출력한다. Reference values나 scale/tolerance를 읽지 않는다. 아직 컴파일하지 않았다.
- `check_rust_forward_parity.py`: 명령의 raw stdin/stdout/stderr/exit를 보존하고 strict JSON/schema/domain/성분 비교를 한다.
- `test_harness_task6.py`: 작은 Python checker/negative control/reference unit tests. 이를 Rust parity라고 부르지 않는다.

## 비교와 단위

`finite(actual,expected,reference_gross)`이고 reference_gross>=0이어야 한다. 0이면 exact equality, 양수이면 `abs(actual-expected)<=4096epsilon*reference_gross`를 요구한다. 차원 없는 +1 floor나 actual이 제공한 scale은 없다. Reference scale은 독립 gain/loss 성분 항의 절댓값 합으로 계산하며 block별 dimensional scale을 사용한다. 이는 interval bound나 exact roundoff proof가 아니다.

행렬은 row-major `[Re00,Im00,Re01,Im01,...]`. Real diagonal과 imaginary zero도 비교 대상이다. BB는 atomic_b/node_b, mode별 J_shell/C_shell, event, epsilon_J와 stencil moments를 출력한다. J_shell은 m^-3 s^-1 sr^-1, C_shell은 delta_J를 곱하기 전 계수다. BF C는 occupation/s, B/j는 m^-3 s^-1 J^-1 sr^-1이며 실제 적분 weight는 J*sr다. Pair M12/M21, 두 C marginal, energy_J, event와 weight를 모두 비교한다. 각 full tag marginal을 서로 더하지 않는다. Combined ledger의 power는 J m^-3 s^-1, Q는 contravariant material tetrad (P/c, momentum_rate)이다.

Branch/measure 태그도 정확히 비교한다. InvalidInput, NumericalDomainUncertain, MissingAuthority, OutOfBand는 0이 아니다. Error record에는 부분 source values가 없어야 한다. Duplicate JSON key, NaN/Infinity, 1e999, 누락/추가 키, 잘못된 모양과 record 순서를 거절한다.

## stdin/stdout 계약

첫 줄은 `REC_HE_WIRE_V2 251`. 이후 한 줄당 `id opcode arguments`. Encoder가 모든 숫자를 roundtrip 가능한 binary64 decimal로 전달한다. State 순서는 ng/ns/nHePlus/ne/T, WP(18), F(8), V(6), 7 energy constants, electron-frame flag다. 출력을 생성하는 동안 fixture ID는 transport label일 뿐 expected physical data가 아니다.

Opcodes: BB, BF, PAIR, BFGRID, PAIRGRID, SELECTED, LEDGER, D86, GUARD, MAT2, MAT3, SCREEN, CONSTANTS, WIDTH, ENERGY. BB h=0은 일반 평가이고 h>0은 raw plus/minus와 finite difference도 출력한다. 새로운 analytic-BB derivative fixture는 선형 n_lower 의존성에 대해 h=1을 사전고정했고 기존 legacy h=2^-16 fixture도 별도로 보존했다. h를 실행 결과에 맞춰 조정하지 않는다. September study/helper는 사용하지 않았다.

Stdout는 `{"schema":"REC_HE_OBSERVABLES_V2","records":[{"id":...,"status":...,"values":{...},"tags":{...}}]}`이다. Scale/expected 값은 stdout에 없다. Adapter는 stdin2MB, 최대512 records 및 개별1024 modes 범위로 제한한다. 일반 purpose solver/parser 서비스가 아니라 이 고정 fixture에 대한 개발용 진입점이다. 전체 grid/history/trajectory를 실행하지 않는다.

## Local 명령과 판정

기본 명령 `python scripts/check_rust_forward_parity.py`는 Cargo run을 **한 번** 실행해 모든 고정 입력을 전달한다. 해시 불일치, 실행 실패, timeout, malformed output, 성분 불일치는 exit!=0이다. 해당 호출은 실제로 local에서 수행되어야 한다.

```bash
cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked
python scripts/check_rust_forward_parity.py
```

`--self-test`는 컴파일하지 않으며 성공 상태도 `SELF_TEST_PASS_NOT_RUST_PARITY`다. 추가한 private child-process tests는 의도된 Python stub/validator failure이며 runtime 불능을 뜻하지 않는다. 각 child command, 실제 exit와 원 bytes는 저장한다. Logs는 변환/trim하지 않는다. Default parity의 stdout 파일은 실제 Cargo subprocess에서만 생성하고 현재는 존재하지 않는다.

기본 성공은 fixed input parity뿐이다. 원 T4 Gate P의 완결은 Task7 매핑에 따른 별도 local 실행 근거가 필요하며, Gate I/normal-frame/G10/E1C/HOLD를 승격하지 않는다.

## 검토 한계

Rust adapter의 type/format/runtime correctness는 확인하지 않았다. JSON->token->Rust decoder의 실제 end-to-end도 미실행이다. Python self-tests의 정상 문서는 reference를 복사한 **synthetic comparator fixture**이고 Rust result가 아니다. 참조 계산의 독립성은 구현 경로 분리와 이전 유리수/단순 scalar 식 교차검사를 뜻하며 exact/outward proof가 아니다. Production kernels, Cargo files, 기존 Rust tests와 historical fixture는 변경하지 않았다.
