# C6 — PID 관측 경계의 한정된 수정

Root/Astra와 독립 검토자가 진단 원문을 읽고 승인한 수정이다. 과학식, 허용오차, original input, source adapter와 solver는 변경하지 않았다. 수정한 코드 파일은 code/run_stage.py 하나다. 역사 C5 manifest와 C6_attempt001 실패 원문은 보존했다. 수정 전후 bytes/SHA는 coding/C6_IMPLEMENTATION_DELTA.json에 기록했다.

## 실제 원인

진단 worker의 os.getpid는6, os.getppid는5였으나 /proc/self/stat의 실제 proc PID/PPID는390949/390948이었다. /proc/6/stat는 worker가 아닌 caas-prefix-tra와 PPID1을 가리켰다. Short child의 namespace PID7과 /proc/self PID390951도 달랐고 /proc/7/stat는 sites-preview였다. 따라서 Popen namespace PID를 그대로 /proc 숫자 경로의 family seed로 쓴 것이 잘못된 기존 프로세스를 선택한 원인이다.

잘못 선택한 proc6의 즉시 before/after utime/stime/cutime/cstime delta는 모두0이며 그 절대 누계는46.28s였다. 실제 진단 worker wait4 CPU는0.065527s다. 그 안의 short child0.034305s는 재합산하지 않았다. Child wall0.099317s, actualCPU0.25s 이하, AS512MiB, single-thread 조건을 지켰다. HyRec/generator/binder/native imports와 field 호출은0이다.

## 수정 범위

Preexec에서 setsid와 RLIMIT 설정 후 exclusive PROC_IDENTITY.json에 /proc/self의 실제 proc PID/starttime 및 namespace PID를 보존한다. Parent는 Popen namespace PID와 identity를 대조하고 proc PID/starttime이 일치할 때만 해당 proc family를 관측한다. wait4와 killpg는 기존 Popen namespace PID를 사용한다. Poll에서는 wait4를 먼저 실행해 빠른 정상 종료를 처리한다. Receipt는 두 PID, 실제 identity와 선택된 family CPU sample을 기록한다. 무관한 기존 카운터를 baseline subtraction으로 감추지 않는다.

Stage allocation에서도 같은 charge_stage가 이미 지불한 실제 child CPU를 먼저 차감한다. 기존 실패0.003394s와 diagnostic0.065527s를 보존하므로 C6는0.068921s를 이미 사용했고 새 C6 cap은9.931079s 이하다. Remote0.06227s까지 포함한 total known은0.131191s이고 총 남은 budget은59.868809s다. Cap을 늘리거나 예산을 초기화하지 않았다.

추가 probe는 하지 않는다. 승인된 영향 확인은 C6 명령 재시도 딱1회다. 그 결과와 실패 비용을 보존하고 실패하면 즉시 root에 반환한다. C7/C8은 아직 승인되지 않았다.
