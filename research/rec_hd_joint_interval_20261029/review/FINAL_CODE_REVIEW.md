# REC-HD-JOINT-INTERVAL01 C9 독립 구현 검토

검토자 `/root/independent_hd_review`, 2026-10-29 KST. 판정 **PASS_SCOPED**. 새 `joint_interval.py`와 해당 tests/CODING_CONTRACT, immutable PR153 이후 `precision_audit.py`의 실제 diff 및 새 regression tests를 읽었다. 작업 문맥을 상속받은 별도 비저자 검토이며 blind 심사는 아니다. 코드·실제 실행의 SHA256를 `FINAL_CODE_REVIEW.json`과 `FINAL_CODE_CONTROLS.json`에 고정했다. 심사 대상 파일은 수정하지 않았다.

## 알고리즘 및 입력 계약

`Fraction` recurrence의 전진 부호와 후진 witness 선택은 R3–R5의 식과 일치한다. finite exact scale≥0, radii≥0, n+1/n/n shape를 명시적으로 검증한다. 최소 scale 계산은 positive-denominator ratio와0의 최대이며 zero-denominator/nonzero-defect이면 null+INFINITE로 구분한다. all-zero n3와 n0도 λmin0의 witness를 반환한다. JSON은 Fraction을 유리수 문자열로 보존하고 Decimal60은 display에만 사용한다. 원 physical/source gate 대신 최소 scale을 사용하는 코드 경로는 없다.

독립 difference-constraint Bellman–Ford를 새로 작성해 empty/all-zero/infinite interior/3-edge mixed/4-edge accumulated/photon-only 모델의 **29개 exact scale**에서 실제 public API와 대조했다. 이전1152개 이론 제어를 반복하지 않았다. 모든 feasible witness는 독립적으로 길이·level/frequency bounds·등식 잔차0을 확인했다. 모두 일치했다.

## 실제 source 입력과 경계

현재 취득된 `acquisition/hd.dat` 원 바이트를 다시 읽어2289bytes와 SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`를 확인했다. 원문에서 독립적으로17개 level/frequency token을 추출했고 fixture와 전부 일치했다. 상수 half-quanta와 직접 segment 합으로 `lambda_min=9137862803786/174896229`, maximizer `(5,6)`를 재구성했다. 독립 Bellman–Ford에서 정확한 λmin은 feasible, λmin−1e−12는 infeasible이었다. 원 λ1은 infeasible다. 이 계산은 source printing enclosure의 거리이며 실제 분광 측정불확도나 허용오차 변경이 아니다.

실제 `--lamda <원바이트>` CLI와 raw API의 `raw_verified_this_execution=true`, fixture-only CLI/API의 `false`가 구분됨을 실행 확인했다. 원 donor 변조와 raw mode의 fixture literal 변조는 모두 거부했다. fixture-only mode의 원본 SHA는 선언된 참조 identity이고 현재 실행의 raw 검증 주장이 아니며, 그 구분이 결과에 유지된다. CDMS2011v2 진본성과 conversion lineage는 여전히 해결되지 않았다.

## 기존 두 finding의 종료

**REV-F1 CLOSED.** legacy `main`의 parent mkdir 추가를 확인했고 깨끗한 중첩 output 경로에서 actual CLI exit0을 확인했다. 새 checker CLI도 동일하게 통과했다. legacy의8개 부호 있는 delta를 immutable ancestor RESULT_SUMMARY와 유리수로 비교해 전부 일치했고 FAIL7/8도 유지됐다.

**REV-F2 CLOSED.** frequency·uncertainty·elo의 `.is_finite()`를 positivity 검사 전에 수행한다. 세 필드×Infinity/−Infinity/NaN/sNaN **12개** negative control이 모두 ValueError로 거부되며 finite 양/음 TAG 의미는 유지됐다. 새 API의 Decimal nonfinite, negative scale, rational zero denominator도 거부됨을 확인했다.

현재 범위에서 blocking code finding은 없다. O(n) time/memory 문구는 THEORY R6처럼 exact rational 산술 연산 수/저장 interval 수에 한정해 읽어야 하며 bit complexity와 production 성능을 검증한 것은 아니다.

## 실행·자원과 범위

실행 명령은 `python3 /workspace/scratch/e0012d8fd22a/review/FINAL_CODE_CONTROLS.py > /workspace/scratch/e0012d8fd22a/review/FINAL_CODE_CONTROLS.stdout.log 2> /workspace/scratch/e0012d8fd22a/review/FINAL_CODE_CONTROLS.stderr.log`이고 exit code0, stderr0bytes다. 원 실행 소스·stdout·stderr·result JSON을 모두 보존했다. Python `resource`와 `monotonic`으로 controls의 own CPU **0.013527s**, child CPU **0.117877s**, wall **0.132278s**, self/child peak RSS **12800KiB**를 측정했다. 측정은 receipt 직렬화 직전까지의 실행 범위이며 model/provider 비용은 unknown, not zero다.

기존 과학 suite·1152 theory control·native·IVP·stationary campaign은 재실행하지 않았다. 새 figure의 육안 검토와 root의 최종 통합 검증은 이 C9와 별도다. 중앙28/88(+0), physical0/313, H5 epsilon=null, H6/H7 OPEN, L4/REI=false, production HOLD를 유지한다. 실제 게시본 identity가 이 receipt와 일치함을 root가 확인한 뒤 채택할 수 있다.
