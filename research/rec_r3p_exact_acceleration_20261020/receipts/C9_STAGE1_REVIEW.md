# REC R3P 독립 C9 읽기 전용 검토

초기 검토 기준: 2026-10-20 05:43:56 UTC Stage1/runner 스냅샷. Stage1 HEAD: `dc61dea363f7a9366557a1994f996861111a57ff`. **후속 검토: 05:48:23 UTC까지 resource repair와 15개 실제 결과 영수증을 추가 확인했다.** 아래에서 수정 전/후 benchmark 소스를 구분한다.

## 1. 판정과 범위

**판정: 검토 범위를 한정한 C9 보고서이며 전체 후보 PASS 또는 smoke 실행 승인서가 아니다.** 고정된 정상 REC 입력에 대한 감사 경로에서 P0/P1 수치·메모리 결함은 이번 검토로 확인하지 못했다. **실제 발생한 P1 resource 초기화 결함 C9-04는 수정 및 해당 inherited-limit 경로의 복구 실행을 확인했다.** 아래 P2 세 항목과 runner의 최종 소스 결속/실행 증거가 남는다. “발견하지 못함”은 모든 입력·플랫폼에 대한 증명이 아니다.

리뷰어는 후보 코드를 작성하지 않은 독립 child agent이다. 부모의 native subagent 존재를 전제로 했으며 재귀 agent를 생성하지 않았다. 후보 저장소는 수정하지 않았다. 물리 적분·빌드·성능 반복을 실행하지 않았다. 부모가 5분간 CPU 검사를 중지하도록 요청한 뒤에는 추가 실행 검사를 하지 않고 작은 소스·영수증의 읽기와 보고서 작성만 했다.

- **Stage1 검토:** `r3p_stream_audit.py`, `r3p_rust_audit.py`, `build_r3p_rust.py`, `benchmark_r3p_audit.py`, Rust crate/header/tests. 비용·소스 귀속을 판단하기 위해 `run_r3p_audit_series.py`와 기존 R3J/R3L/frozen verifier의 연결 지점도 읽었다.
- **새 runner 검토:** 파일이 실제로 생긴 후 `run_r3p_u6_audited.py` SHA `53040282…`의 418행을 정적으로 검토했다. 기준 시점에 runner와 해당 테스트는 **untracked**였고 Stage1 커밋의 일부가 아니다. 최종 커밋 및 그 이후 변경분까지 검토했다고 주장하지 않는다.
- **고정 물리 조건:** 원본 HyRec2012 atomic/thermal 연산, `h=4.245e-5`, 원래 stage/causal guards, `REI=false`를 유지한다. U5 h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, 비용 `CLOSED_HOLD_NOT_RESET`를 승격하지 않는다.
- 부모의 전체 saved-stream 대조와 timing은 **부모가 실행하고 게시한 영수증을 읽은 증거**다. 이 리뷰어가 전체 스트림을 다시 실행한 결과가 아니다.

최종 읽기 스냅샷: [/tmp/rec_r3p_c9_stage1_snapshot/MANIFEST.json](sandbox:/tmp/rec_r3p_c9_stage1_snapshot/MANIFEST.json). 최초 읽기 스냅샷은 `/tmp/rec_r3p_c9_t0qk0fc2/MANIFEST.json`이다.

## 2. Findings — 열린 P2 세 항목과 수정된 P1 한 항목

### C9-01 — P2: 새 runner의 전체 실행 비용과 wall 제한 범위가 영수증에서 구분되지 않는다

**위치:** 새 runner `scripts/run_r3p_u6_audited.py:323`, `:343`, `:367`, `:406`; frozen verifier `scripts/verify_r3i_h2_u6_rt_boundary.py:352`, `:445`; `scripts/r3l_u6_cost.py:137`.

**소스 증명:** runner는 source/input/build 검증을 `profiled.execute()` 전에 수행한다. 반환 뒤에는 다시 source/input/V6 closure/build 검증 및 profile hash를 계산하고 자신의 receipt를 fsync한다. frozen verifier의 wall alarm은 main 내부에서 설정되고 `:445`에서 해제된다. R3L ledger는 자신의 summary clock 전에 끝나며 이미 profile closeout을 제외한다고 명시한다. 새 runner에는 그 바깥 구간의 process-tree CPU/wall 계측, 종료 시 총비용 판정, 별도 wall deadline가 없다. 그런데 runner receipt의 `limits`에는 범위 설명 없이 60 CPU / 180 wall / 2 GiB가 기재된다.

**영향:** verifier 내부 제한을 바꿨다는 뜻은 아니다. 부모 프로세스의 hard CPU/AS 제한도 main 이후 남는다. 다만 신규 preflight·closeout·git 자식 프로세스 비용까지 포함한 **전체 launcher**의 60 CPU/180 wall 보장을 이 receipt로 주장할 수 없다. 실제 초과가 관측된 것은 아니며, 정적 제어 흐름으로 확인한 계측·제한 공백이다. 느린 closeout 파일 읽기/fsync는 verifier wall alarm 밖에서 실행된다.

**부모 권고:** smoke 전에 바깥 실행 구간을 계측하고 같은 승인 예산 안에서 preflight/closeout 및 최종 receipt 쓰기 reserve를 관리하거나, 별도의 이미 승인된 enclosing budget 영수증과 연결하라. 최소한 `limits_scope`, 전체 비용, 제외 구간을 명시해야 한다. 기존 verifier cap을 늘리거나 새 allocation을 이 리뷰로 생성하는 권고는 아니다. 최종 runner 커밋에서 확인할 항목이다.

### C9-02 — P2: Rust backend의 더 좁은 입력 계약이 공통 comparator 설명에 드러나지 않는다

**위치:** [`r3p_stream_audit.py:25`][cached25], `:105`; [`lib.rs:322`][parse322]; [`r3p_rust_audit.py:128`][adapter128]. 새 runner의 `audit` 설정 `:293–298`에도 Python-prefix nonfinite correction만 기록된다.

**실제 짧은 재현:**

| 입력 변화 | frozen legacy | 현재 adapter + 아래 명시한 시험 바이너리 |
|---|---|---|
| 첫 정상 prefix 행에 `,ignored` 추가 | 성공, `PASS_PENDING_REVIEW` | `ArithmeticError: C_PREFIX_ORDER:0` |
| 두 번째 prefix tag를 `UNKNOWN`으로 변경 | `UNKNOWN_C_RECORD:UNKNOWN` | `C_PREFIX_ORDER:1` |

Rust parser는 정확히 네 field를 요구한다. ASCII 정수 문법, 양의 유한 Tr/energy, 유한 tolerance도 요구한다. Python이 허용하던 일부 수 표기·trailing field 및 incidental exception 종류까지 보존하는 drop-in 계약은 아니다. Rust README에는 이 좁은 문법이 이미 기술되어 있으므로 Rust 구현 자체의 숨은 설계라고 보지는 않는다. 문제는 공통 comparator의 “Python-prefix nonfinite 외 다른 parser behavior 보존” 문구가 hook 사용 시에도 읽힐 수 있다는 점이다.

**영향:** canonical 원본 C 생성 스트림의 정상 수치 결과가 달라졌다는 증거가 아니다. 하지만 전체 legacy 입력 언어/오류 메시지까지 exact라고 선언하면 실제 재현과 충돌한다. 첫 오류 위치와 첫 오류의 종류도 구분해야 한다.

**부모 권고:** 공통 설명을 `prefix_auditor=None`인 cached scalar 경로로 한정하고 Rust backend의 canonical grammar, 추가 거부 조건, 오류 매핑을 runner receipt에도 기록하라. legacy의 모든 입력을 받는다는 요구가 별도로 있다면 그때 parser를 일치시켜야 한다. 보안·자원 경계를 무조건 느슨하게 하라는 권고는 아니다.

### C9-03 — P2: EOF 수정 후에도 “항상 가장 이른 bad record”라는 adapter 문구는 크기 제한 실패에서 성립하지 않는다

**위치:** [`r3p_rust_audit.py:173`][adapter173]–`:199`, 특히 `:188–190`.

**정적 반례:** 필요한 정상 preamble 뒤 첫 prefix 행을 `PV,0,0,1.0\n`으로 두고 해당 Python 값은 0으로 둔다. 다음 행을 4 MiB 한계를 넘는 행으로 두면 scalar legacy는 첫 행에서 `C_PREFIX_PARITY:0:0:PV`를 낸다. 현재 adapter는 전체 block을 읽는 중 다음 행에서 `R3P_TEXT_BYTES_LIMIT`를 내며 앞선 행에 대해 FFI를 호출하지 않는다. 이 반례는 **추가 실행하지 않았다**. 크기 검사 `:190`이 유일한 audit call `:199`보다 앞선다는 소스 증명이다.

**영향:** 정상·크기 제한 안의 원본 스트림에 대한 수치 보존 문제는 아니다. resource/transport 실패가 앞선 아직 검증되지 않은 logical failure를 덮는 우선순위 문제다. 추가 chunk guard도 scalar와 다른 시점에 실행되지만 그 차이는 이미 명시된 accelerated-path 계약이다. 예산이 끝난 뒤 parity를 찾기 위해 계속 계산하라고 요구하지 않는다.

**부모 권고:** (a) 크기/guard/transport abort가 논리적 row 오류보다 우선할 수 있음을 정확히 명시하고 earliest-row 보장을 Rust에 전달된 bounded block 안으로 한정하거나, (b) 예산이 남는 크기 실패에 한해 이미 보관한 bounded prefix를 먼저 검사하고 더 이른 logical error가 없을 때 pending size error를 반환하라. 실패한 block은 commit하지 않아야 한다. 후자의 경우 missing-row 결과와 pending input error를 구별할 구조화된 결과가 필요하다.

### C9-04 — P1, 수정·해당 경로 검증 완료: inherited hard CPU 한도를 올리려다 series 마지막 worker가 영수증 없이 종료

**위치:** 수정 전 `scripts/benchmark_r3p_audit.py:95–103`, 특히 `:100`; 수정 후 `:104–123,143`. 수정 전 SHA `7527a1cd388a41952ab8bf3780c5d9f9452e1abc8797fad0142c66375514a4ae`, 수정 후 SHA **`56dc2b2afdf7d29419e33042bae2e5c086eab53bdbdcdb3051c8dad5e58d8e04`**.

**실제 실패 증거:** 기존 15번째 `round2_rust2` stderr는 `resource.setrlimit(resource.RLIMIT_CPU,(60,61))`에서 `ValueError: not allowed to raise maximum limit`로 끝난다. 부모 Budget은 series 잔여 allowance에 따라 더 작은 hard CPU 제한을 자식에 상속시킨다. worker가 이를 61로 올리려 한 것이 원인이다. 해당 코드는 `report` 생성 및 `try`보다 앞에 있어 worker `result.json` 실패 영수증도 만들지 못했다. 초기화 단계 실패이며 input load/감사 이전이다. 첫 14개 성공을 취소하는 수치 오류도, 실패한 15번째의 숫자 PASS도 아니다.

**보존:** `SERIES_001_INTERRUPTED.json`은 `status=FAILED`, `exit_code=2`, 14개 성공 sample, 실패 command/log SHA와 `process_tree_cpu_s=249.937286`을 보존한다. 당시 마지막 command 자체의 CPU는 1.3191579999999874초다. 부모의 실제 trace를 읽었으며 이 실패를 재현하려고 별도 worker를 실행하지 않았다.

**수정 정적 검토:** affinity/limit 설정이 `try` 안으로 이동했다. `tighten()`은 requested/inherited finite soft 및 hard의 최솟값으로 soft를 정하고 hard도 inherited hard 이하로 정한다. 따라서 한도를 올리지 않는다. effective CPU/AS를 receipt에 남기고 absolute `time.process_time()` 기준 3 CPU초 reserve, SIGXCPU handler를 추가했다. source/adapter/Rust 수치 body는 변경되지 않았다. 이 수정은 source-bound 16-step runner의 별도 C9-01을 자동으로 해결하지는 않는다.

**실제 수정 후 증거:** 남은 단 하나의 Rust2 sample은 effective CPU `[49,50]`, AS `[2147483648,2147483648]`에서 성공했다. 전체 verdict/native array/diagnostic equality가 원래 baseline과 같고 library SHA도 같다. audit CPU 10.661630328000001초 / wall 10.672073230998649초, worker total CPU 12.034741202초다. 이 inherited-limit 실패 경로의 수정은 정적 검토와 부모가 게시한 실제 복구 결과로 닫는다. 모든 signal/OOM/hard-kill 상황에 durable receipt가 생긴다는 일반 보장은 하지 않는다.

수정/실행 사본 및 정확한 SHA: [/tmp/rec_r3p_c9_resource_snapshot/MANIFEST.json](sandbox:/tmp/rec_r3p_c9_resource_snapshot/MANIFEST.json). 부모만 후보를 수정했고 이 리뷰어는 수정하지 않았다.

## 3. 부모 수정 확인 — 열린 결함으로 중복 기재하지 않음

| 항목 | 검토 결과 |
|---|---|
| source closure 누락 report 허용 | **수정 확인.** `library_from_build:34–42`가 정확한 schema/status, `source_hashes()` dictionary 전체 동등성, vendor metadata/실제 archive SHA를 검사한다. 과거 빈 `source_sha256` 순회 문제를 현재 열린 결함으로 취급하지 않는다. |
| prefix buffer 누적 제한 | **수정 확인.** 누적 문자 수를 append 전에 4,194,304로 제한한다. 다만 문자 제한과 UTF-8 bytes 제한은 서로 다르다. 후자는 `audit_block:106`에서 검사된다. |
| EOF가 앞선 parity를 덮음 | **현재 adapter 수정 확인.** StopIteration에서 즉시 실패하지 않고 이미 읽은 partial block을 Rust에 보내어 앞선 record 오류를 고른다. 실제 짧은 확인에서 양쪽 모두 `C_PREFIX_PARITY:0:0:PV`였다. |
| 단일 거대 행 | TextIO/generator가 한 행을 반환하기 전에 그 행을 이미 할당할 수 있다. append 전 누적 제한이 이 최초 할당을 막지는 않는다. legacy reader도 같은 readline 문제를 가진다. 검증된 canonical raw/source-generated 입력이라는 현재 경계를 그대로 명시한다. 이를 새로 발생한 무제한 누적 buffer 결함으로 주장하지 않는다. |

CPU 검사 중지 요청 **이전** 합성 확인은 `timeout 9s python -B`, n=0, prefix=2, 36,447 HE preamble, Rust 1 thread / block_columns=2에서 수행했다. 검사 loop 경과 시간은 **0.386363767초**, tool 전체 약 1.03초였다. 물리 적분이나 성능 반복은 없었다.

실행 영수증: [/tmp/rec_r3p_c9_checks_kmd04ply/checks.json](sandbox:/tmp/rec_r3p_c9_checks_kmd04ply/checks.json). 각 사례의 stream.csv도 같은 디렉터리 아래 보존되어 있다.

- adapter SHA: `397a30a8677b520fb85565a4210fe74cdf9268e05bf7c5c8a61d9ca92d74e004`
- 사용한 기존 바이너리: `/tmp/rec_r3p_rust_impl_target/release/librec_stream_audit.so`
- 그 바이너리 SHA: `567ec4b4a2ff1009f38a51970632804e04867094579b0c967ddfa31f5195103a`
- **이 짧은 확인에는 source-bound build receipt를 사용하지 않았다.** 부모의 BUILD_001/PILOT_RUST 바이너리 `7e6f4bde…`와 동일 바이너리라고 주장하지 않는다. wrapper 제어 흐름의 정적 확인과 구분한다.
- pytest helper import를 이용하려던 최초 시도는 `ModuleNotFoundError: pytest`로 실행 전에 종료되었다. 위 결과는 이후 자체 구성한 합성 사례에서 얻었다. 전체 pytest suite를 이 리뷰어가 실행했다고 기록하지 않는다.

## 4. FFI·정확 산술·순서 검토 결과

| 검토 축 | 소스에서 확인한 점 / 한계 |
|---|---|
| ABI metadata | C header, `#[repr(C)] RecStatus`, ctypes field/arg/restype가 대응한다. Rust `:127–140,200–244`에서 null/alignment, checked byte extent/end, 1..64 columns, 314 slots, text/array lengths, overlap를 검사한 뒤 slice를 만든다. 포인터가 실제 live allocation인지 여부는 여전히 unsafe caller 의무다. |
| 출력 초기화 | `MaybeUninit<f64>` output으로 NumPy의 미초기화 `empty` buffer를 받는다. 성공 시 전 슬롯을 쓰고, 실패 block은 Python에서 cv/cl에 commit하지 않는다. partial output은 실패 후 버린다. |
| 수명·동시성 | Python 배열/text/status를 동기 호출 동안 보유한다. `audit_block`/handle free는 같은 lock으로 직렬화한다. pool은 로컬이며 전역 pool/물리 C operator를 worker에 보내지 않는다. 실제 adapter는 **ctypes**, CFFI 구현은 없다. 입력의 동시 mutation을 막는 소유권 계약은 필요하다. 여러 Python caller에서 stats까지 원자적으로 갱신된다는 계약은 없다. |
| parallel decomposition | `lib.rs:460–492`는 열별 disjoint output에 계산한 뒤 모든 job을 join하고 열 순서로 첫 오류를 선택한다. column 내부 row 순서는 유지한다. later-column speculative work는 attempted_rows에 포함된다. 물리 시간 단계의 독립성을 가정하지 않는다. |
| scalar math | `lib.rs:352–390`은 원래 tolerance의 곱/합 결합 순서를 유지하고 system `expm1`을 부른다. 원래 gate는 `abs(py-native)>tol` 그대로이며 ratio gate로 바꾸지 않는다. finite/zero tolerance, overflow 예외 경계는 별도로 다룬다. 플랫폼 libm/기본 FP 환경 조건을 일반적인 실수 항등식으로 대체하지 않는다. |
| NaN·signed zero·reduction | prefix nonfinite Python 값 거부는 알려진 계약 강화다. `abs` 뒤 상대항 max에 들어가므로 ±0 동률은 +0이다. spectrum maxima는 기존 순서의 Python `max(old,ratio)`로 남으며 Rust horizontal floating reduction이 없다. 유한 실수 max의 결합법칙만으로 NaN/signed-zero/exception 순서를 증명했다고 하지 않는다. |
| ratio SIMD 후보 | `rec_ratio_batch`는 별도의 independent-lane 비율 API다. 현재 prefix 승인 gate로 대체되지 않는다. 0/0·비유한 ratio를 거부하고 finite ratio>1은 반환하므로 “성공 코드 = parity PASS”로 사용할 수 없다. |
| 캐시·causality | cached scalar는 guard/forensic 경계 뒤 cache를 무효화한다. causal geometry의 key는 정규화된 shape+실제 energy bytes, LRU=4, buffer는 immutable bytes-backed이다. 매 호출 `j-delay`, 활성 구간, `floor(emit)+1<=j-1`를 검사한다. `d>1`만으로 floating index guard를 없애지 않았다. |
| bound와 panic | Rust max text=4 MiB, max columns=64, max records=20,096, worker count≤4 및 지정 stack이다. unwind containment와 caller 의무가 문서화되어 있다. OOM abort, invalid live pointer, stack overflow를 catch_unwind가 보장한다는 주장은 없다. Python direct ratio/audit caller가 제공하는 원본 배열의 크기·불변성까지 이 ABI가 소유하지는 않는다. |

Rust/기존 Python 테스트 **소스**에는 finite boundary, FMA와 구별되는 vector, NaN/zero tolerance, metadata/overlap, 1/2/4-thread first-error, scalar guard mutation 및 forensic negative controls가 있다. 이 표는 그 테스트들을 새로 실행했다는 뜻이 아니다. 독립 review는 현재 정상 경로와 정적 조건에 한정된다.

## 5. 게시된 실행 증거와 비용 귀속

[부모의 differential receipt][pilot-diff]와 세 pilot 영수증을 읽었다. 게시된 결과는 다음과 같다.

| backend | audit CPU s | audit wall s | 기록된 total CPU s |
|---|---:|---:|---:|
| legacy | 21.437194202 | 21.441452274000767 | 22.804312024 |
| cached | 19.968856622 | 19.996596913002577 | 21.310198568 |
| rust1 | 9.786856076000001 | 9.787473668999155 | 11.102774529000001 |

모두 entire verdict hash `99ce067477d566d910beca63cf87473097a531c50cd8341ef2033ba5eb2ed561`와 두 native array hash를 동일하게 기록한다.

- cv: `e1cde4fd84512e60a8fa5f3c5468eac632af2cf0b34f181dc03d327bb7105f8c`
- cl: `961a10b46e0839f07bded61f0e409ff6ffa31f8344fa86fc1a61fc83b3bee646`
- 두 diagnostic 파일은 모두 **빈 파일 hash** `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`다. 이 full-stream 사례에서 실제 비어 있지 않은 forensic branch까지 실행·동등 확인됐다는 뜻은 아니다.
- pilot들의 adapter SHA는 **이전 `4526d270…`**다. 수정 후 Stage1 `397a30a8…`와 혼동하지 않는다. 후속 15개 series 결과는 수정된 adapter의 실행 증거이며 바로 아래에서 별도 귀속한다.
- 부모 BUILD_001/PILOT_RUST library SHA: `7e6f4bde4497d7771d0f45167d4c7a33a000949d248cab33bbffa126564aaec8`.

**benchmark 범위:** `benchmark_r3p_audit.py:55–88`은 3개 raw 입력을 고정 SHA로 검사하고 frozen source/checkpoint, 복원 C source/binary를 검증한다. setup/pool creation을 별도 기재하며 audit interval은 배열 할당, CSV 읽기, predicate/maxima/forensic 작업을 포함한다. `:160`에서 raw identity를 재확인한다. 이것은 감사 비용의 관측이지 물리 적분 전반의 speedup·수렴 증거가 아니다.

**standalone attribution 한계:** benchmark 단독 receipt는 `:116–117`의 Python 3파일 SHA를 import 후 기록하고 자체 source closeout을 하지 않는다. 이를 독립적인 전체 launch seal로 취급하지 않는다. 부모의 실제 `run_r3p_audit_series.py:71–74,108`는 source/build receipt 변화를 sample 전과 series 종료 시 검사하므로, 이번 선언된 series의 지속적인 source drift 방지는 상위 경로에서 제공된다. series는 입력/affinity/source 및 entire verdict/native bytes/diagnostics 동등성도 비교한다. 3회 관측 범위를 population confidence interval이라고 하지 않는다.

benchmark의 `total_*:169`는 final result.json serialization/fsync 직전 값이다. build/series의 공용 finalizer는 이 마지막 write를 별도로 reserve하고 scope를 명시한다. 따라서 숫자를 전체 사용자 명령의 모든 시작·종료 I/O를 포함한 무조건적인 total로 재명명하지 않는다. 이 귀속 한계와 새 runner의 C9-01은 구분한다.

Stage1 일반 CI failure receipt는 문서 EOF 공백 검사에서 tests 이전에 실패한 기록을 보존하며 부모가 그 공백 수정을 staging했다. 부모는 별도의 기존 R3O CI run `39376038857` PASS와 Stage1 원격 3개 whole-SHA readback PASS를 보고했다. 이 리뷰어가 원격 CI/backup을 다시 실행하거나 조회한 것은 아니다. 이 서로 다른 증거를 하나의 test PASS로 합치지 않는다.

### 후속 15개 실제 saved-audit 결과 — 독립적인 영수증 일관성 확인

`receipts/AUDIT_COMPARISON.json` SHA **`8693d21669c78786129143b6deaff3af37b44070d1877660788c4a4599949083`**를 읽었다. status는 `PASS_ALL_15_DIFFERENTIAL_WITH_DISCLOSED_RESOURCE_REPAIR`다. 15개 실제 `result.json` 파일의 SHA를 comparison receipt와 비교하고, 각 result의 entire verdict/그 hash/native array hash/diagnostic hash가 baseline 및 comparison 안의 값과 일치하는지 **파일 읽기·JSON 대조만** 수행했다. 모두 일치했다. 현재 실제 BUILD_001 shared library의 SHA도 `7e6f4bde…`이며 모든 Rust receipt와 일치했다. 전체 native 배열/물리 스트림을 다시 계산하지 않았다.

독립 확인 기록: [/tmp/rec_r3p_c9_receipt_crosscheck.json](sandbox:/tmp/rec_r3p_c9_receipt_crosscheck.json), SHA `69ab1ba1900214ce656638d9a2b918212fa8294a143162e350b4821973dd5efe`.

**주 분석은 처음 두 uninterrupted round, 총 10개 sample**로 제한한다. 아래는 해당 receipt의 descriptive 값이다.

| backend | audit CPU 중앙값(s), n=2 | audit wall 중앙값(s), n=2 | round별 legacy/candidate CPU 비의 관측 범위 |
|---|---:|---:|---:|
| legacy | 22.368621475 | 22.380442220 | 1 |
| cached | 20.258669566 | 20.297470728 | 1.102084–1.106080 |
| rust1 | 10.027651230 | 10.028265443 | 2.117069–2.347957 |
| rust2 | 9.926132620 | 9.610650850 | 2.122275–2.391093 |
| rust4 | 9.888654041 | 9.409341361 | 2.195481–2.327724 |

세 번째 round의 기존 4개 결과는 보존하고, 누락된 Rust2만 수정 후 한 번 실행했다. 이 재개된 round/세 round 통합 요약은 **부수적인 descriptive 자료**로 별도 표시한다. worker resource-control SHA 변경을 지우고 같은 소스·중단 없는 3회 측정이라고 부르면 안 된다. 원래 15번째 실패와 복구 sample은 별개이며, 성공한 14개를 반복하지 않았다. 두 번의 관측 범위는 confidence interval도, Rayon/SIMD만의 인과적 기여도 추정도 아니다. 물리 production speedup은 여전히 `NOT_MEASURED`다.

비용 기록은 기존 실패 포함 **249.937286 + 복구 구간 13.585642 = 263.522928 CPU초**, 원래 300초 한도 안이다. 원래 allowance를 reset하지 않았다. filesystem timestamp로 기록한 plan-write→continuation-receipt span은 **335.59711503982544 wall초 <480초**이며 debugging pause를 포함한다. 이는 연속 monotonic watchdog 측정과 구분된 filesystem 관측 범위다. 최종 receipt 쓰기는 공용 finalizer가 별도 reserve하는 범위라는 기존 한계도 유지한다.

보존 영수증 SHA:

- `SERIES_001_INTERRUPTED.json`: `77155e1f4568a24d14f8d75db99971434b2e823a44e952e8ca1675027427305e`
- `SERIES_001_CONTINUATION.json`: `bbb361537f66202d805e6a7487caab7d9cc1120fc60f2173e2c52abad5a6913d`
- `RESOURCE_REPAIR.json`: `3e4b048bc0b666f89f79beeffd8f24e176d3471612dfecf515540c79d3b3f742`
- `RESOURCE_REPAIR.diff`: `09e8f39408a44c1ab8a069cf2de83ba0172436dab21ea4cd61c1d18bcf20370d`

각 사본은 위 resource snapshot 아래 원래 상대경로에 있다. 아직 게시하지 않은 후속 파일에 Stage1 URL을 허위로 붙이지 않는다.

## 6. 새 runner의 이미 검토한 범위와 남는 경계

코드가 생긴 뒤 확인한 사항:

- `step_count/validate_options`는 smoke=16, pilot≤128이며 full 모드·grid 변경·Rust 빌드를 제공하지 않는다. frozen verifier가 accepted steps와 source evaluations에 같은 상한을 전달한다.
- h/RT/PREFIX/U5 checkpoint 및 V6 109-file manifest identity를 검사한다. 외부 ZIP 경로 선택은 같은 pinned ZIP bytes에 한정된다.
- source binding은 기존 HEAD 일치+tracked diff 검사에 추가 파일의 tracked 여부 및 실제 SHA를 결합한다. 기준 시점 untracked runner/test와 dirty ACK/DAG가 있는 공유 작업트리에서는 launch gate가 거부하는 것이 예상 동작이다. 현 상태를 실행 가능하게 하려고 gate를 완화하면 안 된다.
- Rust build receipt의 schema/status/exit/resource/new-physical-run, **전체** build source dictionary, vendor, library/receipt SHA를 검증하고 audit 직전과 closeout에서 다시 확인한다.
- pool은 frozen main이 1 CPU affinity를 설정한 **뒤** threads=1로 만든다. helper module·class의 전역 메서드를 덮지 않고 module-local binding을 contextmanager로 복구한다.
- close 실패와 후속 closeout 실패는 기존 primary exception에 note/secondary로 붙인다. 실패한 verifier를 새 runner가 scientific PASS로 승격하는 경로는 보이지 않는다.

현재 tests 파일의 존재와 위 failure/identity/restore 테스트 소스까지 읽었지만, 최종 커밋·그 커밋의 CI·source-bound 16-step 실행·그 후 receipt를 이 리뷰가 확인한 것은 아니다. **C9-01 해결/범위 명시 및 최종 runner hash로 추가 검토가 필요하다.** 새 benchmark나 물리 적분을 이 리뷰를 위해 실행하도록 요구하지 않는다.

## 7. 정확한 소스 식별

모든 상대경로의 root: `/workspace/scratch/afe554957b2e/rec_work`.

| 파일 | SHA-256 |
|---|---|
| scripts/r3p_stream_audit.py | d7a60e225d72626200be5ace2fbd1bf7828c386846b102dbdd5cf30f6ea9da4b |
| scripts/r3p_rust_audit.py | 397a30a8677b520fb85565a4210fe74cdf9268e05bf7c5c8a61d9ca92d74e004 |
| scripts/build_r3p_rust.py | d7bfaaab5c3e32842e01b45201c4713e4b144d0c95a4ff3991e90ae4a5482adb |
| scripts/benchmark_r3p_audit.py — Stage1/최초 14개 | 7527a1cd388a41952ab8bf3780c5d9f9452e1abc8797fad0142c66375514a4ae |
| scripts/benchmark_r3p_audit.py — resource 수정/복구 1개 | 56dc2b2afdf7d29419e33042bae2e5c086eab53bdbdcdb3051c8dad5e58d8e04 |
| scripts/run_r3p_audit_series.py | 86383910b9516c7a52e1aab232144be70241c2ca7ee49b78b45cf643066887a3 |
| rust/rec-stream-audit/src/lib.rs | fddcdc1bb1282f26c1cf03be889966844c9827893d9b2be6adc9ba6e959d7743 |
| rust/rec-stream-audit/src/tests.rs | 0623b373145b12db40b084b0867ca6c72702760feda2d113996475c06ccf7b7f |
| rust/rec-stream-audit/include/rec_stream_audit.h | ed968004b79ef8a1793bc46b0dfe360bb7f3a3b96051688180a6aa54d9fbe6e5 |
| rust/rec-stream-audit/Cargo.toml | 823425e22da7436bc835f07dcf3cf298e7994a9b800bf041368405488d00ee16 |
| rust/rec-stream-audit/Cargo.lock | 7af2db0a742c71381057459b36e1ba711d907003012ab122ba5eb05a2c7fb052 |
| rust/rec-stream-audit/README.md | bd36a855ad736e92c843c4afee9107ecb18846dcd322b55170dacc907011193a |
| rust/REC_STREAM_AUDIT_VENDOR.json | ef6bd3aacbaa333f0f148683027626454b006f75ae5840cae6dfb796cda35368 |
| scripts/run_r3p_u6_audited.py — 미커밋 초안 | 53040282c11813c2a47e87564600e0829e8a6ddcb0e3326952fb652f90a6cb8b |
| tests/trajectory/test_r3p_u6_audited.py — 미커밋 초안 | 20138ca3f23503b27f01fc475e92133668217cd06fb0ad49d2d96964ba738cf0 |

Stage1 고정 URL root: https://github.com/cosmosapjw-quantum/rec_bianchi/tree/dc61dea363f7a9366557a1994f996861111a57ff

미커밋 runner는 위 SHA와 스냅샷으로만 식별한다. 존재하지 않는 commit URL을 만들지 않는다.

## 소스 링크

- [Stage1 cached comparator][cached25]
- [Stage1 Rust adapter][adapter128]
- [Stage1 Rust kernel][parse322]
- [Stage1 source-bound builder][builder]
- [Stage1 saved audit benchmark][benchmark]
- [Stage1 audit series][series]
- [PILOT_LEGACY][pilot-legacy], [PILOT_CACHED][pilot-cached], [PILOT_RUST][pilot-rust], [PILOT_DIFFERENTIAL][pilot-diff]
- 새 runner의 검토한 사본: [/tmp/rec_r3p_c9_stage1_snapshot/scripts/run_r3p_u6_audited.py](sandbox:/tmp/rec_r3p_c9_stage1_snapshot/scripts/run_r3p_u6_audited.py)

[cached25]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/scripts/r3p_stream_audit.py#L25
[adapter128]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/scripts/r3p_rust_audit.py#L128
[adapter173]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/scripts/r3p_rust_audit.py#L173
[parse322]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/rust/rec-stream-audit/src/lib.rs#L322
[builder]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/scripts/build_r3p_rust.py
[benchmark]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/scripts/benchmark_r3p_audit.py
[series]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/scripts/run_r3p_audit_series.py
[pilot-legacy]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/research/rec_r3p_exact_acceleration_20261020/receipts/PILOT_LEGACY.json
[pilot-cached]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/research/rec_r3p_exact_acceleration_20261020/receipts/PILOT_CACHED.json
[pilot-rust]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/research/rec_r3p_exact_acceleration_20261020/receipts/PILOT_RUST.json
[pilot-diff]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/dc61dea363f7a9366557a1994f996861111a57ff/research/rec_r3p_exact_acceleration_20261020/receipts/PILOT_DIFFERENTIAL.json
