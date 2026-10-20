# REC R3R — 실제 spectral 감사 연결과 제한 수치 연구

## 2026-10-21 재개: CI 수정과 복구 결과

자동 작업공간 정리 후 GitHub checkout과 세 고정 보존 archive를 직접 복구했다. Stage1/2/3 전체 SHA는 각각 기존 identity와 일치했다. 이번 복구는 기존 수치 결과의 재실행이 아니며, 원본 실패와 raw도 유지했다.

새 test-only source는 `70a53396e910869ea069e184a44f1fb21cb47a0a`, tree는 `565550bec51506b2a85c48442b9ab0d69be18be7`이다. **기존 성공 benchmark·pilot의 실행 source는 여전히 `1313b1f1b2c081d57bcce9c60e757ef79110df91`**이다.

일반 CI에서 전체 pytest 누적 CPU가 imported trace CLI의 55초 작업 guard에 들어가 두 기존 검사가 실패했다. 실제 실패값은 CPU92.440560/92.626558초, wall80.063518/80.249547초였다. 수치 ratio 불일치가 아닌 test process 범위 오류다. 두 trace를 새 bounded child에 배치하고, 부모의 소진된 guard는 child 실행 전후 모두 계속 거절하는 반례를 검사했다. NumPy comparator·benchmark·solver·resource cap은 변경하지 않았다.

현재 실제 CI는 일반 **1038 PASS /103 SKIP /72 subtest PASS**(138.69s), 전용 **60 PASS /1 SKIP**(9.47s)다. PR의 synthetic merge `2fe1008f31a4ccb36b1b03fe14e31a65a7c75b2f`의 tree도 source와 정확히 같다. `receipts/ci/CI_ISOLATION_CI.json` 및 별도 `CI_ISOLATION_AUDIT`를 읽는다. 반복 CI를 새 고유 테스트 수로 합산하지 않는다.

이 새 CI 반환이 실제 수정 검증을 완료했으므로 준비 중이던 `formal_validation_003` 로컬 재검사는 `NOT_RUN_SUPERSEDED_BY_ACTUAL_SOURCE70A_CI_RETURN`으로 종료했다. 원래 validation allocation 누적 CPU21.365609000000003초 /wall21.497515038005076초를 초기화하지 않았고, 새 적분은 0회다.

사용자는 64코어·128GB NCP를 이용한 미실행 작업의 일괄 준비를 추가로 요청했다. 이는 별도 R3S 노드 `research/rec_r3s_ncp_campaign_20261021/`에서 수행한다. 현재 연결 도구는 실제 월간 사용량 한도로 실행 호출을 중지했으며, online 장치의 CPU·RAM·NCP identity는 검증하지 못했다. 기존 h4 event+2/h2 low-z와 R3M full5210은 재사용하고, 원래 시간 recurrence와 아직 열리지 않은 global convergence/full-run 조건을 보존한다.

Stage1/2/3 Dropbox·Library의 전체 원격 SHA는 복구됐다. Drive는 기존 write 요청의 ACK가 없고, 현재 exact-name read에서도 완료 객체를 찾지 못했다. 과거 UNKNOWN은 취소나 성공으로 바꾸지 않는다. R3R의 과학·코드·CI 완료와 Drive 보존 미완료를 분리한다.

## 결론과 범위

R3P 이후 이미 반환된 R3Q NCP 결과를 먼저 복구한 뒤, 별도 R3R 노드에서 **후보 B: bounded NumPy ratio 계산을 실제 spectral stream 감사에 연결**했다. 원래 HyRec2012 atomic/thermal operator, predictor recurrence, causal/stage boundary, scalar Planck 계산과 same-h tolerance는 그대로 유지했다. 기존 R3Q comparator와 worker는 수정하지 않았다. 새 실행 경로는 opt-in이며 기본 backend는 legacy다.

실제 32-step raw stream을 다섯 쌍으로 비교했다. 전체 저장 CSV 감사의 paired CPU 가속비 중앙값은 **1.3641298366**, wall은 **1.3638913471**이다. CSV open·parsing·배열 할당·callback·최종 판정을 포함한 warm-cache 감사 비용이다. **전체 solver/production 가속률은 NOT_MEASURED**다. 같은 25,000개 lane의 ratio native binary64 bytes, verdict, maxima hex, guard 순서가 모두 일치했다.

새 NumPy 경로의 source-bound 32 accepted / 128 FULL pilot은 exit 0, same-h PASS, common-input 9개 sampled evaluations PASS였다. profile baseline과 비교한 6개 raw 파일 및 NPZ 10개 payload가 동일했다. 원래 verification의 **SMOKE_ONLY / CAP_BEFORE_EVENT_PLUS_TWO** 상태는 유지한다.

과학·구현 결과를 아래의 정확한 실행 source에 귀속한다. 최종 문서·백업 메타데이터 게시 commit은 별도 역할이며, 이를 실행 source로 대체하지 않는다. 최종 배송 현황은 `DELIVERY.json`, `BACKUP_ACKS.json`, `DAG.json` 및 최신 publication receipt가 권위 있는 후속 기록이다.

## 1. 먼저 확인한 최신 반환과 source identity

| 역할 | Commit SHA | Tree SHA / 관련 PR |
|---|---|---|
| 완료 R3P 실제 U5 실행 source | e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d | 기존 증거 complete_reused |
| 완료 R3P 전체 code/evidence snapshot | 0b80913bf1c665cc4cfab6dfaa3ea35f815a482f | 복구 delta의 고정 기준 |
| 완료 R3P 최종 보존 HEAD | 888d56d72579d1e1fd30f66abe02d9f91809a767 | 640eabc07aa590dba60f68579906e2fb5589fe9a / PR110 draft |
| 새로 찾은 R3Q NCP 실행 source | 1ad0380110621446c42df9d995fd85db3a6c7e7a | efd65193713f19d0e60a0617182b3449c7091510 |
| R3R base: R3Q 보존 HEAD | 5b44bb21ce0599e55e0848e5e3ff320c9e8ca172 | 9403d3778d0a81e9632cea58e42e59ed9581e980 / PR111 draft |
| R3R 단계 1 게시 | 46ebb765d2c5c8af6d53c5b59ade1a405d4551be | eac9172f63a3b4a07181e4c9a97258e680d066b0 |
| R3R formal 첫 시도 | 65ec195ec32cfcc4e918d1dd86b711fdeb5709ad | cf4071391ed3664eac8d9ecfed2d27815eb541ec |
| **R3R 실제 성공한 테스트·benchmark·pilot source** | **1313b1f1b2c081d57bcce9c60e757ef79110df91** | **97423cad509a9604269740132a6ad850faf8f19a** / PR112 draft |

[PR110](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/110), [PR111](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/111), [PR112](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/112)는 merge하지 않았다. R3R branch는 `research/rec-r3r-followup-costs-20261020`, base branch는 `research/orchestration-20261020-next-loop`다. production v3/rux, BASS/rec/RUN19 및 별도 reionization lane을 변경하지 않았다.

### 새 NCP 반환의 실제 내용

Drive와 Dropbox에서 각각 전체 readback한 `REC_R3Q_NCP_REVIEWED_RESULTS_20261020.tar.gz`는 14,318,848 bytes, SHA256 `5219995db41dfebf8d0ceafa445402f9125e01321241a34a54fd9f4592c513e2`로 일치했다. 그 안의 실제 NPZ와 command·supervision·verification·independent-review를 읽었다.

| 반환 | 기존 실제 실행과 검토 | 이번 처리 |
|---|---|---|
| h4 event+2 | 새 accepted 1,511; FULL 6,044; He cutoff iz74409, H_ONLY 두 단계 후 iz74411; 감독 CPU31.315760764 s / wall31.46869331 s; exit0; PASS_SCOPED_H4_FIRST_EVENT_PLUS_TWO | complete_reused, 추가 재적분 없음 |
| h2 low-z | 새 accepted153,327; 저장 상태153,328; reviewed same-h PASS; STOP_AT_SOURCE_Z0_CUBIC_STENCIL; CPU60.755865 s / wall62.63294565 s | 과거600/900 allocation 결과로 재사용. 이번60/180 allocation에 포함하거나 재개하지 않음 |

h4 NPZ SHA256은 `7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9`, h2 NPZ는 `b25e2cbdafe4037d222116c4985eac95a380552f6799a2b3e950fb499965dbe6`다. compact archive에 없는 native CSV, worker stdout/stderr와 일부 partial 파일은 기존 검토·해시 연결을 재사용했다. 이를 새 전체 raw 재감사로 표시하지 않는다. h2 compact receipt에는 top-level process exit code가 없으며, 관측되지 않은 exit code를 만들지 않았다.

R3Q 상단 EVIDENCE/DELIVERY 일부는 초기 smoke 시점의 기록이다. 이후 event/low-z receipt와 후기 REPORT/DAG를 함께 읽어 최신 상태를 재구성했다. 원문을 덮어쓰지 않았다. 과거 대화 조회는 현재 서비스에서 SERVICE_ERROR였다. 조사한 Library 최신 목록/R3P 폴더에서는 더 새로운 REC 반환을 찾지 못했으며, 조사 범위 밖의 부재는 주장하지 않는다. `receipts/intake/`에 조회 범위와 실제 응답을 보존했다.

### h2 z=0 종단 해석의 교정

기존 후속 문서의 “네 상태가 필요하지만 세 개만 남았다”는 해석은 원문 C와 일치하지 않았다. 원래 `rec_interp1d`는 마지막 stencil에서 index를 `Nx-3` 이하로 clamp한다. Nx=211717, raw index=211715.47262308892에 대해 ix=211714, s=1.4726230889209546이다. 사용하는 네 실제 상태는 **211713, 211714, 211715, 211716**이며 모두 존재한다. s를 [0,1]로 잘라서는 안 된다.

원문과 같은 scalar cubic 계산으로 저장된 z=0 endpoint의 float.hex를 재현했다. Python/native 차이는 xe 약3.876e-18, Tm 약2.533e-16이다. source-compatible 보간 완료와 추가 RHS 진화는 다른 조건이다. 이 자료에 추가 음의 z RHS step은 필요하지 않다. 원래 stop 상태와 raw를 보존하고 `receipts/intake/endpoint_correction.md`에 유도·계산을 추가했다. 전역 h/h2/h4 수렴성은 여전히 NOT_RUN이다.

## 2. 계약, 후보 세 개와 선택 근거

원래 R3P reference h=4.245e-5를 보존한다. 이번 짧은 실행은 이미 정의된 R3Q quarter-grid `dlna=8.49e-5/4=2.1225e-5` checkpoint를 그대로 쓴다. native와 Python은 동일한 grid와 입력을 사용하며, 이를 원래 h의 새 정의나 cross-grid 수렴 비교로 해석하지 않는다.

| 후보 | 실제 근거 | 판정 |
|---|---|---|
| A: selected common-input event에만 owned snapshot 생성 | 복사량을 줄이는 조건부 수학 모델은 성립. 실제32-step profile observer 누적0.006125704 s | 이번에는 보류. 현재 병목으로 입증되지 않음 |
| **B: bounded exact NumPy spectral 감사** | comparator 누적0.252768103 s / exclusive0.146397774 s; 기존 ratio 식 재사용 가능 | **선정·구현·측정** |
| C: NCP 플랫폼 또는 다음 h4 pilot | 이미 NCP event+2 반환 존재; 현재 Python/C++가 실제 실행 가능 | 이번 연구에서는 선택하지 않음 |

프로파일의 integrator 누적 경과시간은0.290664267 s다. cProfile 기본 elapsed timer이므로 위 수치를 exclusive process CPU나 비프로파일 속도 측정으로 사용하지 않았다. 새로운 실제 병목 자료가 생기면 A/C를 별도 DAG 노드로 재평가할 수 있다.

SciSpace로 HyRec 원 논문을 찾고 실제 primary PDF를 읽었다. Exa로 NumPy/Python primary 문서를 비교했으며, WolframLanguageEvaluator로 선택적 복사량과 Amdahl 식을 확인했다. 별도 WolframContext 호출의 service error도 보존했다. 검색 요약 자체를 물리 검증으로 쓰지 않았다. 이번 구현은 기존 NumPy ufunc와 R3P ratio/cache 원칙을 사용하며 새 외부 solver를 이식하지 않았다. VigilODE solver를 HyRec 시간 적분기로 채택했다는 주장도 없다.

## 3. 구성적 유도와 구현

lane i에 대해 Python/native occupation을 p_i,c_i, 원래 scalar Planck 값을 f_i라고 두면 기존 식은

```text
d_i = abs(p_i - c_i)
a_i = 1e-7 * max(abs(p_i), abs(c_i))
b_i = 1e-10 * f_i
t_i = a_i + b_i
r_i = d_i / t_i
PASS iff isfinite(r_i) and r_i <= 1
```

이다. 원래 `math.expm1` 계산의 괄호와 binary64 중간 연산 순서를 유지한다. NumPy에서도 subtract, abs, maximum, multiply, add, divide를 별도로 수행한다. algebraic 재결합, FMA, fast-math, reciprocal 근사, vector expm1, tolerance 변경은 추가하지 않았다.

각 lane의 입력은 다른 lane의 ratio에 의존하지 않는다. 동기 guard 사이에서 동일 j/energy 및 안정된 binary64 입력에 대해 같은 scalar Planck bits를 재사용한다. finite maxima의 묶음 계산은 기존 값을 선택하므로 합산 반올림 문제가 없고, 바깥 scalar max가 초기 +0을 유지한다. 이것은 조건부 프로그램 동등성 논증이며, 실제 플랫폼 binary64 검증을 대체하지 않는다.

| 변경 파일 | 기능과 검증 대상 |
|---|---|
| `scripts/r3r_stream_audit.py` | 실제 CSV 순차 parsing, HE 무시 동작의 exact fast path, 기본512/max625행 batch, bounded Planck cache, 별도 NumPy 연산, scalar 예외 replay |
| `scripts/benchmark_r3r_stream_audit.py` | 고정 source/input 검증, 전체 감사 paired timing, fresh-process RSS, untimed 전체 lane trace |
| `scripts/run_r3r_h4_supervised.py` | default legacy / opt-in numpy, 고정 source 검증, inherited limits 보존, 1..32 smoke 전용 감독 |
| `scripts/plot_r3r_audit.py` | raw/receipt identity 확인 후 비용·잔차·bitwise 차이·RSS 그림 |
| `tests/test_r3r_stream_audit.py`, `tests/test_r3r_supervised.py` | 새61개 고유 계약·반례 검사 |
| `.github/workflows/verify-r3r-stream-audit.yml` | 새 계약 검사 전용 CI |

per-tag V/A/L index 순서와 임의 interleaving을 유지한다. control row, 다음 parsing/index 오류, 8192-line guard 및 EOF 전에 pending batch를 처리한다. 예외적인 batch는 원래 scalar 순서로 replay하여 최초 실패의 class와 .17g message를 복원한다. guard 뒤에는 cache와 array 참조를 무효화한다. non-default NumPy floating error 정책에서는 scalar 경로를 사용한다.

계약 밖인 동시 array mutation, call-count 부작용이 있는 redshift 함수, warning stack/timing 및 실제 CPU cap에 도달하는 동일 시각까지 보장하지 않는다. 원래 ratio predicate가 검사하지 않는 photon positivity를 새로 입증하지도 않는다. 상세 식–코드 연결은 `EQUATION_TO_CODE.md`다.

### 실행 identity와 자원 경계

고정 source closure100개에 신규 runtime4개를 추가로 Git blob과 비교하고 실행 뒤 다시 확인한다. `-B`만으로는 오래된 .pyc 읽기를 차단할 수 없다는 실제 반례를 발견하여 supervisor/worker 모두 새 private cache prefix를 생성하고 startup부터 적용했다. manifest나 frozen source를 완화하지 않았다.

공개 launcher는 기존 worker가 허용하는 **1..32 accepted steps**만 받는다. 사용자의128 상한보다 엄격하다. event/full adapter가 없다. 60 CPU s / 180 wall s / process당2 GiB와 closeout reserve를 유지하며, inherited hard limit이 더 낮으면 그대로 존중한다. 기존 전체 process tree Budget을 재사용했다.

## 4. 실제 새 검증 명령과 실패 기록

실제 명령의 절대 경로, stdout/stderr SHA, exit code 및 environment identity는 `receipts/formal_validation_00*/`와 `FORMAL_RAW_LOGS.tar.gz`에 있다. 다음은 해당 실행의 핵심 명령이다.

```bash
python3 -B -X pycache_prefix=<new-empty-path> -m pytest -q -p no:cacheprovider \
  tests/test_r3r_stream_audit.py tests/test_r3r_supervised.py \
  --junitxml=<evidence-dir>/tests.xml

python3 -B scripts/benchmark_r3r_stream_audit.py \
  --source-sha 1313b1f1b2c081d57bcce9c60e757ef79110df91 \
  --native-stream <preserved-profile32>/worker/native_oracle_stdout.csv \
  --python-result <preserved-profile32>/worker/python_continuation.npz \
  --verification <preserved-profile32>/worker/verification.json \
  --rounds 5 --warmups 1 --output-dir <new-benchmark-dir>

python3 -B scripts/run_r3r_h4_supervised.py \
  --expected-commit 1313b1f1b2c081d57bcce9c60e757ef79110df91 \
  --new-allocation-id REC_R3R_VALIDATION_20261020_001_PILOT32 \
  --evidence-dir <new-pilot-dir> --backend numpy --steps 32
```

이 명령들은 이 스레드에서 이미 실행했다. 사용자의 수동 실행을 요구하는 절차가 아니다.

| 실행 / 검사 | 실제 결과 | 범위 |
|---|---|---|
| 최초 profile32 | worker FAIL, accepted0; wrapper outer exit0은 cProfile의 SystemExit 처리 때문 | inherited RLIMIT_CPU 요청 오류를 보존 |
| 복구 profile32 |32accepted/128FULL, same-h PASS,9 common-input PASS | 고정 solver source 유지, supervisor shim만 교정 |
| formal001 source65ec |60 PASS /1 FAIL, exit2 | stale-cache 반례 fixture의 prefix 컨텍스트 오류; benchmark/pilot 미실행 |
| formal002 source1313 |**61 PASS /0 SKIP**, tests exit0 | 실패 fixture 교정 후 같은61개 고유 검사 |
| paired audit |**PASS**,5쌍 | 모든 verdict/maxima hex/guard labels 동일 |
| lane trace |**PASS**,0/25,000 bytes 차이 | scalar/NumPy 각각200,000bytes |
| NumPy pilot32 |**PASS_SCOPED**,exit0 | SMOKE_ONLY,32accepted/128FULL |
| same-output 비교 |**PASS** |6개 raw byte동일,10개 NPZ shape/dtype/bytes동일 |
| C9 readback |**PASS_INDEPENDENT_EVIDENCE_READBACK** | 재적분·benchmark 재실행0회 |

adversarial 검사는 NaN/Inf, ±0, subnormal/extreme arithmetic, gate 근접값, 첫 실패 우선순위, malformed rows, 순서 오류, tag interleaving, guard에서의 입력 변경, NumPy error handler, 실제 full raw, stale bytecode 및 낮은 inherited limit을 다룬다. 33/129/8192 steps와 잘못된 source commit은 worker 실행 전에 거부된다.

원래 R3P 214/18 테스트나 일반 회귀 수치를 새 고유 테스트 수로 더하지 않았다. 반복된 로컬/CI 실행도 추가 고유 검사가 아니다.

## 5. 같은 입력과 같은 허용오차의 성능

실행 환경: AMD EPYC9V74, x86_64 Linux6.18.55/glibc2.39, Python3.12.14, NumPy2.3.5. benchmark affinity0..8, BLAS/OMP 계열 thread 환경1; pilot worker affinity0. 실제 Python executable SHA와 compiler/build/binary identity를 receipt에 보존했다. 현재 Python 실제 실행과 C++ compile/run은 PASS, rustc 실제 호출은 COMPILER_MISSING이다. 이 후보에는 Rust가 필요하지 않았다.

### 전체 저장 스트림 감사: warm-cache, 각 backend5회

| Backend | CPU 중앙값 (s) | Wall 중앙값 (s) | Fresh-process peak RSS (bytes) |
|---|---:|---:|---:|
| Frozen legacy |0.109308013|0.109321077|88,875,008|
| R3R NumPy |0.080130212|0.080153802|88,887,296|

paired CPU 가속비는1.274104,1.312704,1.364130,1.408808,1.409547이며 중앙값1.3641298366이다. paired wall 중앙값은1.3638913471이다. warmup 각1회는 제외했다. 시간에는 파일 open/parsing/배열 할당/callback/verdict가 포함되며 NPZ 준비·입력 hash·untimed lane 검증·fresh RSS child 준비는 각 trial 밖이다.

5쌍의 짧은 local warm-cache 측정이므로 cold-cache, 긴 event/full stream, 다른 CPU나 production solver에 일반화하지 않는다. 효과에는 scalar cache와 HE parsing fast path도 포함된다. SIMD 단독 효과나 thread 증가 효과로 귀속하지 않는다.

stream에는 총97,935개 record, STEP40개, 새 accepted32개가 있다. STEP에는 기존 checkpoint history가 포함되므로 STEP40을 새 적분40단계로 세지 않는다. spectral은 V12,440+A12,440+L120=25,000개다.

두200,000byte ratio trace의 SHA256은 동일한 `c174927905389fa933dc4bf5d3e89cfc32535e0721bbd58196101a1164c2bf3c`다. native CSV는15,434,249bytes/SHA256 `3f1ab809f7fec021aeccba45c5ab887a82872e66e108e15c4bcb6df14ebb803d`, NPZ는197,179bytes/SHA256 `a83f0831c1fb82e2e7d28c85551587671f7aaa0fe3816ff7c4d01953f24c1216`다.

### 새 pilot 및 전체 감독 비용

NumPy pilot supervisor의 CPU는3.857951 s, wall3.914853461 s다. preflight·compile·worker·audit·source closeout을 포함하며 마지막 receipt 쓰기 전 측정이다. worker 내부의 부분 범위 CPU1.920838 s / wall2.020213796 s와 혼동하지 않는다. 별도의 matched whole-solver speedup benchmark는 하지 않았다.

formal allocation은 실패한 첫 시도의CPU5.334566 s도 포함하여 총CPU21.365609 s / wall21.497515038 s로 끝났다. wall은 감독된 실제 실행 구간의 합이며 중간 코드 편집 대기시간은 제외했다. profile allocation의 두 시도 CPU합은4.739403 s다. 각각60/180 안에서 종료했고 새 full5210/event/full h4 allocation은 없다.

전체 formal supervisor가 관찰한 pilot subtree 최대 sampled RSS는324,034,560bytes, 내부 launcher가 관찰한 worker tree는305,954,816bytes다. 50ms sampling이므로 exact whole-tree peak가 아니다. worker가 회수한 child 최대 RSS222,298,112bytes와 parent peak85,303,296bytes도 별도 범위다. per-process AS2GiB 한도와 이를 구분한다.

NumPy의 명시적으로 관리하는 추가 payload 상한은60B bytes(B는 batch행수)다. 기본512행에서30,720bytes, 최대625행에서37,500bytes이며 Python 객체/NumPy 내부/입력 history/RSS 전체를 포함하지 않는다. 두 fresh RSS 차이12,288bytes만으로 메모리 개선·악화의 일반 결론을 내리지 않는다.

## 6. 물리·수치 잔차와 그림

pilot same-h ratio 최대값은 V6.131840645486276e-6, A1.5314944635351782e-5, L4.192518230086996e-6로 기존 gate1보다 작다. common-input9개 sample은 원래 oracle에서 PASS였다. 종 보존 장부 잔차 최대는 전자5.204170427930421e-17, 수소핵/헬륨핵0이다. 이는 이 짧은 same-input 실행의 기록이며 다른 trajectory/mesh의 물리 정확도 판정은 아니다.

`figures/`에 비용, 모든 normalized photon ratio, binary64 차이, fresh RSS의4개 그림을 남겼다. PNG/PDF는 직접 보존하고 SVG 원본4개는 `ORIGINAL_SVG.tar.gz`에 bytes 변경 없이 보존했다. 전체12개 원본은 Stage2 archive에도 있다. generator가 raw trace/중앙값/identity를 검증했고 root 및 독립 C9 reviewer가 PNG를 직접 확인했다. residual의 실제0 네 개는 그대로 유지하며 symlog 축과 gate1을 명시한다. 차이 그림의 y축 표시 여백은 허용오차가 아니다.

원래 `PLOT_GENERATION.json`의 PASS_GENERATED_PENDING_VISUAL_REVIEW/NOT_RUN은 보존한다. 후속 직접 검토 PASS는 별도 `receipts/VISUAL_REVIEW.json` 및 C9에 있다.

## 7. 독립 감사와 claim gate

PHYS-MATH AUDIT는 lane 독립성, 중간 반올림/Planck cache identity, max 선택, guard invalidation, 예외 replay와 payload 상한을 검토했다. PHYS-MATH-CODE AUDIT는 고정 source/manifest 연결과 resource/pycache/실패 폐쇄 경로를 검토했다. 독립 reviewer는 후보 source 작성자가 아니며, 작성자 실행을 자신의 새 실행으로 계산하지 않았다.

코드 감사에서 공개128과 frozen32 상한의 불일치, -B stale bytecode, benchmark resource 한도 설치 시점을 P2로 발견하고 formal 성공 실행 전에 교정했다. 각각 실제 반례 또는 code-bound probe와 최종 source inspection으로 닫았다. C9는 실행 source1313의104개 Git source hash, 두 formal receipt의 raw69개,17개 archived log,25,000 lane bytes,5쌍 중앙값,6 raw/10NPZ payload 및12 plot hash를 독립 재계산했다. solver/benchmark를 재실행하지 않았다.

| 판정 축 | 최종 과학/구현 판정 | 의미 |
|---|---|---|
| Mathematical correctness | **PASS_SCOPED** | 명시된 안정된 binary64 입력·순수 redshift·guard 계약 아래 구성적 동등성 |
| Numerical equivalence | **PASS_SCOPED** | 실제25,000 lane와32-step 출력,61개 계약/반례 검사 |
| Implementation correctness | **PASS_SCOPED** | source-bound opt-in 구현, 독립 PHYS-MATH-CODE/C9, 잔여P1/P2 없음 |
| Measured acceleration | **PASS_SCOPED_AUDIT_ONLY** |5쌍 warm-cache 감사 CPU중앙값1.36413배; whole solver NOT_MEASURED |
| Memory and resource behavior | **PASS_SCOPED** | 실제한도 내 종료, bounded payload와 구분된 RSS; exact aggregate peak 아님 |
| Physical validity | **NOT_ESTABLISHED / HOLD** | 원래 U5 실패와 미완료 전역 수렴 유지 |
| Production readiness | **NOT_APPROVED** | draft 연구, production speedup/전체 물리 검증 미완료 |

세부 독립 최종 판정과 미완료 배송 gate는 `receipts/C9_CODE_AUDIT.json` 및 `C9_CODE_AUDIT.md`에 있다. 원래 PHYS-MATH/PHYS-MATH-CODE의 당시 PENDING 실행 항목은 원문 보존하고 후속 actual C9로 닫는다.

## 8. CI, 보존과 다음 연구 인계

source1313의 전용 GitHub Actions는 실제60 PASS/1 SKIP였다. 외부 full raw를 요구하는 선택적 case1개는 CI에서 skip되고 로컬formal에서는 PASS였다. Python3.12.15/NumPy2.5.4의 계약 검사 결과이며 새 플랫폼 성능 측정은 아니다. 당시 일반 CI는 새 파일12개의 extra blank line at EOF 때문에 실패했고 전체 pytest 단계는 실행되지 않았다.

수치 source의 의미를 바꾸지 않고 EOF만 정규화했다. 실제 benchmark/comparator bytes는 동일하고 launcher 및 test의 AST는 location까지 동일하다. 원래 실행1313과 원문raw는 보존했다. `receipts/TEXT_NORMALIZATION.json`은 그 시점의 변환 기록이며 이후 REPORT/최종 metadata 내용의 확장을 제한하는 manifest가 아니다. 후속 CI의 실제 실행 결과는 `receipts/ci/`와 DELIVERY에 추가한다.

보존은 create-only다. Stage1은 intake와 failed/repaired profile raw; Stage2는 실제 source1313의 code delta와 formal raw/그림; 최종 preservation은 후기 보고·DAG·감사·CI·backup metadata를 담는다. Stage2 code delta는 완전한 R3P0b snapshot과 함께 target 전체 tracked tree를 재구성하도록 inventory/삭제 목록/entry hash를 제공한다. delta만으로 독립 full snapshot이라고 부르지 않는다.

각 provider ACK와 별도 전체 원격 readback SHA는 `BACKUP_ACKS.json`에 분리한다. 과거 R3P 단계0/단계2 ZIP의 whole readback NOT_RUN 기록은 그대로 유지한다. 현재 backup 호출의 실패·UNKNOWN도 성공 ACK로 덮어쓰지 않는다.

현재 과학 결과를 위해 추가 NCP 실행은 필요 없다. 다음 목표가 새 플랫폼 호환성 검증이면 새 환경identity를 먼저 읽고, 새 allocation을 명시해 같은 launcher의16 또는32-step numpy/legacy pilot 범위만 실행한다. 이 launcher의32 상한을128/event/full로 늘리지 않는다. 새 full5210, global h/h2/h4 convergence 및 h4 후속 물리 확장은 별도 선행 검증·명시적 allocation을 요구하는 다음 DAG다.

`HANDOFF_KO.md`에는 정확한 복구 순서, 선행 complete_reused 노드, 신규 결과와 유지되는 HOLD, 최소 다음 실행 범위를 정리했다.
