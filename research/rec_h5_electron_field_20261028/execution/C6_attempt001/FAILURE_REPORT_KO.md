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
