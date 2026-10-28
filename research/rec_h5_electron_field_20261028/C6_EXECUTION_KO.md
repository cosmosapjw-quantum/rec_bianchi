# C6 — 한정된 PID 관측 수정 후 실제 결과

현재 판정: **PASS_SCOPED_C6_BUILD_BIND_CONTRACT**. Root가 승인한 관측 경계 수정과 C6 재시도 딱1회를 수행했다. C7/C8은 아직 승인되지 않아 실행하지 않았다. 첫 실패와 진단 원문 및 실제 비용은 보존했다.

## 실제 수용 결과

| 항목 | 관측 결과 |
|---|---:|
| Original source/header/table/capture/native_path identity |16개 일치|
| Final writer binding |132개|
| 원 query mapping |313개|
| Endpoint references |626개|
| Invalid contract cases |24개 모두 native call 전 거부|
| Valid native point calls |2개|
| Tables context initialization |1회|
| 실제 divisor events |각 point472개|
| Zero/nonfinite/overflow divisor |각각0개|
| Caller input/table nonmutation |두 valid point 모두 PASS|

24개 invalid case는22개 C API 입력 거부와2개 call_id/slot binding 거부로 구성된다. Units label, coefficient-origin, phase/model/species/source, scalar domain, nonfinite, scalar/incoming/Lyman shape, wrong writer binding을 구별했다. 거부된 case의 새 kernel call은0이다.

Valid 첫 point는 saved native baseline(call7792,slot4770)이며 두 번째는 동일 P에서 incoming을 부호 반전한 signed-departure control이다. 두 번째 입력의 허용은 물리 spectrum positivity나 saved native parity를 뜻하지 않는다.

첫 saved baseline의 실제 FH bitwise equality는1/1, xr는2/2, xv는311/311이다. 실제 FH 차이는0이다. Gross scale S_F는 약298.1253706056이며 필수512eps64*S_F parity를 통과했다. 별도 Decimal80 sparse block reconstruction의 최대 normalized residual은 **1.0472340240534142807839862727286991576049820273253369910345580857977993838480879E-15**로,4096eps64=9.094947017729282e-13 이하이다. 이 결과는 baseline1점의 C6 확인이며 아직 실행하지 않은132-point primary 전체의 PASS로 일반화하지 않는다. Signed control에는 이 단계에서 saved-original parity를 주장하지 않는다.

## Compile와 관측 경계

Actual compiler는 /usr/bin/gcc의 gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0다. Frozen C11/O3/no-fast-math/ffp-contract=off/PIC/shared flags를 사용했고 command/version/stdout/stderr를 보존했다. Shared library SHA256은 `9a1b1586faa55af1899746b51005e2c7309175e904a1f7bc15fa57801442b40b`다.

Original hydrogen source의 warning9개를 보존했다: signedness 비교1개, unused TR parameter1개, fscanf 반환값 무시7개다. 무관한 native warning 정리를 하지 않았으며 compiler warning-free나 repository-wide CI PASS를 주장하지 않는다.

Generated source는 header1개+value-only hook3개이며 제거 시 원본 bytes가 복원되는 receipt와 diff가 생성되었다. 추가 native solve0이다. Outside231+Thomas240+Schur1의 실제472 events와 finite/nonzero를 두 valid point에서 확인했다. 원 source/inputs와 C5 역사 manifest는 수정하지 않았다.

자원 관측은 Popen namespace PID5와 /proc-visible PID393289, starttime4130603을 구별했다. PID/starttime을 확인한 family의 최대 관측은0.88s다. 이는 tick-resolution guard 값이며 실제 CPU charge는 wait4 user+system을 사용한다.

## 실패를 포함한 실제 비용

| 항목 | CPU seconds |
|---|---:|
| 기존 C6_attempt001 실패 |0.003394|
| 승인된 resource diagnostic |0.065527|
| C6_attempt002 실제 child |0.9076759999999999|
| C6 allocation에서 지불한 합계 |0.9765969999999999 /10|
| C6 allocation 잔액 |9.023403|
| 이전 R7 reported remote CPU |0.06227|
| 전체 known scientific-child 합계 |1.038867 /60|
| 전체 known 잔액 |58.961133|

재시도 cap은 이미 지불한0.068921s를 차감한9.931079s였고 실제 child 비용0.9076759999999999s는 이를 지켰다. 재시도 wall은0.9236254830029793s, maximum RSS는67788KiB다. Compiler 하위 프로세스의 비용도 wait4 child 합계에 포함된다. 진단 내부 short child 비용을 다시 더하지 않았다. Parent/network/model/metadata/packaging의 미관측 비용은 UNKNOWN_NOT_ZERO다.

## 결과 파일과 다음 경계

핵심 요약은 `coding/C6_RESULT_SUMMARY.json`, 수정 identity는 `coding/C6_IMPLEMENTATION_DELTA.json`이다. 실제 실행 자료는 `execution/C6_attempt002/`의 RESULT, RESOURCE_RECEIPT, PROC_IDENTITY, INVALID_CONTROLS, BASELINE_NUMERICAL_CHECK, VALID_CONTROLS, CALL_JOURNAL, api_raw, binding 및 build에 있다. 누적 비용은 `execution/RESOURCE_LEDGER.json`에 있다.

C6만 완료했으며 C7/C8과 자동 재실행은 하지 않는다. 실제 C6 게시·두 provider ACK와 size readback 후 root가 다음 단계를 승인한다. 원 producer/reference/native full-history/oldtests/BGJET audit/QSS03 certificate 실행0, remote mutation0이다. Canonical28/88+0, separate REI33/88, reference313/313, physical0/313, physical bounds null, H6/H7 OPEN, L4false, REIactivationfalse를 유지한다.

---

# 보존된 첫 시도 보고

# C6 — 첫 실행의 자원 관측 중단 보고

판정: **FAIL_EXECUTION_WATCHDOG_OBSERVATION_INCONSISTENCY / STOP_FOR_ASTRA**.
C6는 완료되지 않았다. 자동 수정이나 재실행은 하지 않았으며 C7/C8도 실행하지 않았다.

## 실제 실행과 결과

Root가 C5의 실제 게시 및 이중 백업 완료 후 승인한 명령을 unit root에서 정확히 한 번 실행했다.

    python3 code/run_stage.py C6

Worker는 `execution/C6_attempt001/`에 고유한 시도 기록을 만들었고,
process-family CPU watchdog이 SIGKILL로 종료했다. 실제 반환 코드는 -9다.
실행 stdout와 stderr는 모두 빈 파일로 보존되어 있다. RESULT.json과 build 하위 디렉터리,
compiler log, CALL_JOURNAL.jsonl은 생성되지 않았다.

원 코드의 순서가 build 다음 binding, 그 다음 context 초기화와 kernel call이므로,
build 산출물이 없는 이번 시도에서는 compiler, input binder, table initialization,
valid kernel, invalid contract cases 및 numerical acceptance까지 도달하지 않았다.
따라서 24 reject, valid2, binding132/626/313, FH parity 및 block residual은 **NOT_RUN**이다.
이 값을 실패한 과학적 parity나 residual로 분류하지 않는다.

## 실제 비용과 관측 불일치

| 항목 | 실제 기록 |
|---|---:|
| Worker user CPU | 0.003394 s |
| Worker system CPU | 0.0 s |
| wait4 실제 child CPU | 0.003394 s |
| Worker wall | 0.00469083699863404 s |
| Maximum RSS | 6808 KiB |
| Watchdog의 최대 process-family CPU 관측 | 1105.53 s |
| 이번 family CPU cap | 10.0 s |
| 알려진 native kernel calls | 0 |
| 미완료 API 진입 기록 | 0 |

실제 child CPU0.003394s와 wall 약0.004691s에 비해 watchdog의1105.53s 관측은
이번 worker의 실행 비용으로 해석할 수 없을 만큼 불일치한다. 이번 실패는 이 관측이
10CPU guard를 발동시킨 실행 경로의 문제다. `/proc` 관측이 어떤 다른 누적값 또는
PID 해석을 포함했는지는 아직 입증하지 않았고 원인을 단정하지 않는다. 이 보고서는
그1105.53s를 실제 사용량으로 ledger에 더하거나 과학 예산 초과라고 주장하지 않는다.

실패 시도의 wait4 비용은 그대로 차감되어 있다. 누적 ledger는 다음과 같다.

- 이전 R7 Wolfram reported CPU: 0.06227 s.
- 이번을 포함한 실제 local child CPU: 0.003394 s.
- 알려진 scientific-child 합계: 0.065664 s /60s.
- 알려진 남은 예산: 59.934336 s.
- Parent, network, model 및 미관측 비용: UNKNOWN_NOT_ZERO.

RLIMIT_CPU per-process10s, RLIMIT_AS512MiB, wall30s, 다섯 single-thread 환경 설정은
COMMAND/RESOURCE receipt에 보존했다. 이번 중단은 해당 메모리나 wall cap을 초과했다고
관측된 사건이 아니다. Compiler가 실행되지 않아 compiler warning 결과도 **NOT_RUN**이며,
빈 worker stderr를 warning-free compile로 해석하지 않는다.

## 보존한 근거와 다음 경계

- `execution/C6_attempt001/COMMAND.json`
- `execution/C6_attempt001/RESOURCE_RECEIPT.json`
- `execution/C6_attempt001/stdout.txt`
- `execution/C6_attempt001/stderr.txt`
- `execution/RESOURCE_LEDGER.json`
- `execution/STAGE_STATUS.json` — C6 pass=false.

과학식, 허용오차, input, source adapter, watchdog 코드를 수정하지 않았다. Root/Astra가
관측 불일치를 분류하고 한정된 수정 및 새 C6 시도를 명시적으로 승인하기 전에는
추가 실행하지 않는다. 이전 실패 기록과 실제 비용을 지우거나 초기화하지 않는다.

원 producer/reference/native full history/old tests/BGJET audit/QSS03 certificate 실행은0,
새 field kernel call도0, 원격 mutation도0이다. Canonical28/88+0, separate REI33/88,
reference313/313, physical0/313 및 모든 physical null ceiling을 유지한다.
