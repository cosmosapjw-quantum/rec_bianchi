# REC-HD-JOINT-INTERVAL01 이론 독립 검토

검토자 `/root/independent_hd_review`, 2026-10-29 KST. `research/rec_hd_joint_interval_20261029/THEORY.md` R3–R5만 대상 이론 원자료로 읽고 별도 유도와 반례 제어를 수행했다. 작업 문맥을 상속한 비저자 검토이며 blind 심사는 아니다. 판정은 **PASS_SCOPED**, all-zero edge case와 복잡도 문구에 작은 명료화가 있다. 코드 C9와 원본 취득 진본성은 이 이론 심사에 포함하지 않는다.

## 재구성한 논증

기준식 `delta_j+x_j-x_(j-1)=y_j`에서 `x_j=x_(j-1)-delta_j+y_j`다. 따라서 전 단계 reachable interval `[l,u]`에 허용 y 구간을 더한 집합은 정확히 `[l-delta-lambda*s,u-delta+lambda*s]`이며 현재 level box와 교차시키는 recurrence는 정확하다. 연속인 실수 interval의 Minkowski sum/projection을 사용하므로 과대근사가 발생하지 않는다. 선택한 x_j의 predecessor 집합은 `I_(j-1) intersect [x_j+delta-lambda*s,x_j+delta+lambda*s]`이고 recurrence 때문에 공집합이 아니다. 뒤로 재귀하면 모든 등식과 level/frequency box를 만족하는 witness를 구성한다.

연속 구간 p..q에서 등식을 합하면 `D_pq+x_q-x_p=sum y_j`다. 그러므로 segment 부등식은 필요하다. 충분성 증명의 difference-constraint graph는 bidirected path와 zero-node spokes로 이루어진다. 단순 cycle이 zero node를 포함하지 않으면 path의 양방향 한 edge two-cycle밖에 없고 weight는 `2lambda*s>=0`이다. zero node를 포함하면 정확히 두 spoke와 유일한 monotone path가 남는다. 양방향 weight는 `lambda*(r_p+r_q+S) +/-D`다. 모든 단순 cycle이 비음수이면 모든 closed walk도 비음수이며, super-source shortest potentials가 해를 준다. 모든 연속 구간 조건은 따라서 필요충분하다.

모든 양의 denominator에서 ratio 최대를 취하면 finite scale 필요조건과 충분조건을 동시에 포착한다. 유한 maximum에서 경계 부등식은 닫혀 있으므로 최소값은 달성되고 forward/backward recurrence가 witness를 준다. d=0,D≠0이면 finite scale은 불가능하다. d=0,D=0은 제약을 더하지 않는다. λmin=0일 때 그보다 작은 **허용된 nonnegative** scale은 없으므로 lower-scale obstruction 주장은 공허한 경우로 읽는다.

문서가 exact tie-to-even 정책을 추가 조건으로 분리한 것은 정확하다. closed enclosure에서의 충분성은 특정 tie-break printing에 대한 충분성과 다르다. alpha_print와 unknown underlying defect interval의 구분, ordinary frequency의 h와 hbar 관계, T>0도 올바르게 명시되어 있다.

## 반례 시도와 독립 제어

rowwise pass가 충분하다는 잘못된 명제를 겨냥한 δ=(1,1), r=(1/2,1/2,1/2), s=(0,0) 제어는 λ1에서 joint infeasible, λ2에서 feasible이다. δ=(1,-1)은 λ1에서 feasible이다. 원문이 제시한 판별과 일치한다. 별도 코드로 exact Fraction Bellman–Ford negative-cycle 검사를 작성하여 n2, δ∈{-1,0,1}, r,s∈{0,1}, λ∈{0,1/2,1,2}의 **1152개** 경우를 all-segment 조건과 대조했고 전부 일치했다. 이는 증명의 보조적인 유한 제어이며 일반 필요충분성은 위 그래프 논증에 의존한다. 기존 HD 과학 campaign·native·IVP·stationarity는 재실행하지 않았다.

## 작은 보강 두 가지

- **JT-A1.** n>0이고 모든 denominator와 defect가 0인 경우에도 λmin=0을 명시하면 좋다. `max({0} union {|D|/d:d>0})`, 단 d=0,D≠0이면 infinity로 쓰면 n0까지 한 식으로 포괄한다. 현재 zero/zero rule과 모순은 없고 해는 x=y=0이다.
- **JT-A2.** O(n)은 interval 산술 연산 수와 저장 interval 수에 대한 표현으로 한정하면 정확하다. exact rational bit complexity는 literal 및 scale bit length에 의존한다.

새로운 일반 graph theorem이나 strong no-go의 신규성을 채택하지 않는다. 표준 difference-constraint 결과의 이 source admission 문제에 대한 구성적 적용으로 적절하다. 중앙28/88 및 physical0/313의 완료 수를 바꿀 근거는 이 math review 자체에서 생기지 않는다.

검토 입력 SHA256와 check별 판정은 `JOINT_THEORY_REVIEW.json`, 새 exact 제어는 `JOINT_THEORY_CONTROLS.json`에 남겼다.

실제 제어 실행은 `python3 -` heredoc으로 수행했고 exit code 0이었다. 실행한 stdin source를 `JOINT_THEORY_CONTROLS.py`에 보존했으며 재현 명령은 `python3 /workspace/scratch/e0012d8fd22a/review/JOINT_THEORY_CONTROLS.py`다. `JOINT_THEORY_EXECUTION.json`에 source SHA256·실행/재현 명령·결과를 기록했다. child CPU/wall/RSS는 실행 시 별도 측정하지 않아 **unknown, not zero**이며 자원 정량값을 주장하지 않는다. 소스 보존만을 위한 제어 재실행은 수행하지 않았다.
