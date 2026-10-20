# R3S: 고정된 계산 DAG의 병렬 실행과 자원 한계

## 연구 질문과 선택

R3R에서 실제 spectral stream의 exact NumPy 경로를 연결하고 국소 동등성을 검증했다. R3S는 그 코드를 새로운 NCP 플랫폼에서 검증할 수 있도록 독립 작업을 묶고, 자원·결과·재개 계약을 코드로 만든다. 기존 적분기의 시간 병렬화나 새로운 물리 근사 도입은 연구 범위에 포함하지 않는다.

후속 후보는 세 개만 비교했다. Python 적분·oracle 내부의 추가 최적화는 새 exclusive CPU 프로파일과 원본 재귀의 별도 증명이 필요하다. Rust/SIMD backend를 더 연결하는 후보는 컴파일러 identity와 실제 전체 비용 비교가 필요하며, R3R의 NumPy 연결로 현재 확인된 작은 병목은 이미 다뤘다. 제한된 NCP 플랫폼 검증은 사용자 요청과 현재 구현된 작업 DAG에 직접 대응하므로 **후보 C**를 선택했다. 선택은 새 NCP 측정에서 이득이 확인됐다는 뜻이 아니다.

## 1. 시간 적분 안의 의존성

물리 상태, predictor 기억, accepted spectral history 및 stage 정보를 묶은 확장 상태를 \(X_n\)이라 쓰면, 현재 구현은

\[
X_{n+1}=F_n(X_n)
\]

형태의 고정 재귀를 따른다. 실제 predictor는 `1.25 * current_rhs - 0.25 * prev2_rhs`의 원본 연산 순서를 유지한다. accepted history column은 현재 FULL 평가 이후 한 번만 commit하고, post-Saha probe는 trial column을 commit하지 않는다. 다음 stage 결정도 accepted 입력에 의존한다. 이 관계는 `primordial_2012_quarter_continuation.py` 및 독립 `PENDING_GLOBAL_DAG_REVIEW`에서 확인했다.

같은 trajectory의 인접 accepted index를 별도 CPU에서 동시에 계산하려면 이 의존성을 만족시키는 별도 알고리즘과 오차·동등성 증명이 필요하다. R3S는 trajectory 하나의 내부 실행 순서를 유지하고, 서로 다른 입력 검증 또는 서로 다른 bounded run을 작업 단위로 다룬다.

## 2. 독립 작업의 순서 교환 조건

작업 \(J_i\)가 고정된 source·입력 \(I_i\)를 읽고 전용 출력 디렉터리 \(O_i\)에만 쓰며, 두 작업 사이에 계산 의존성이 없다고 하자. 이때 두 작업의 입력을 바꾸는 공유 상태가 없고 각 작업 안의 연산 순서가 고정돼 있으면, 완료된 과학 payload는 실행 순서와 무관하다. 이 주장은 CPU 시간, wall 시간, RSS, 로그의 시각, 자원 cap에 도달하는 시점까지 같다는 뜻은 아니다.

따라서 coordinator는 고정 Git blob 및 입력 SHA 검사를 수행하고, 결과 디렉터리는 create-only로 분리한다. source·입력·작업 ID·allocation·환경 identity가 다른 receipt를 재개 근거로 받아들이지 않는다. 오류 또는 종료되지 않은 이전 실행은 성공으로 바꾸지 않고 보존한다. 각 파일의 존재가 아니라 command, exit, source, raw output과 검증 결과를 연결한다.

## 3. 고정 DAG의 작업량과 critical path 하한

고정 DAG의 작업 비용 합을 \(W=\sum_i w_i\), 가장 긴 의존 경로의 비용 합을 \(L\), 사용할 수 있는 동질 CPU 수를 \(P\)라 하자. 작업을 중복·추측 실행하지 않고 각 작업 비용이 고정된 모형에서,

\[
T_P\ge\max\left(\frac{W}{P},L\right)
\]

이다. 첫 항은 시간 \(T_P\) 동안 처리할 수 있는 총 작업량이 최대 \(PT_P\)라는 사실에서 나온다. 둘째 항은 같은 경로의 후속 작업이 선행 작업 완료 전에는 시작할 수 없다는 사실에서 나온다. 이 모형의 하한은 실제 wall 예측값이나 모든 병렬 ODE 알고리즘에 대한 불가능성 정리가 아니다. startup, 파일 I/O, 메모리 대기, 외부 host 부하가 추가되면 실제 시간은 더 길어질 수 있다.

현재 허용된 첫 frontier는 두 개의 독립 trace 검사다. 그러므로 그 단계의 유효 병렬 폭은 최대 2이며, 명목 64 CPU가 있다는 이유로 같은 검사를 64개 복제하지 않는다. 저장 스트림 benchmark와 두 pilot은 해당 campaign 안에서 단독 실행하여 동시 작업에 의한 측정 오염을 피한다. 호스트의 다른 작업까지 단독으로 점유했다는 주장은 별도의 실제 reservation 증거가 있어야 한다.

## 4. 자원으로 제한된 실행 폭

실행 폭은 ready 작업 수, 명시적으로 배정된 CPU, 현재 affinity, cgroup CPU quota, 그리고 메모리 예약 중 가장 작은 값으로 제한한다. 개념적으로는

\[
p_{\rm run}\le\min\left(p_{\rm ready},p_{\rm assigned},p_{\rm affinity},p_{\rm quota},p_{\rm memory}\right).
\]

실행 중인 작업에 아직 사용하지 않은 2 GiB allowance도 예약된 것으로 계속 계산해야 한다. 이번 폭 2인 묶음에서는 `MemAvailable` 또는 cgroup headroom에 process-tree RSS를 다시 더하는 credit을 주지 않고, 실행 중인 작업과 새 작업의 full allowance를 보수적으로 예약한다. 합산 RSS에는 공유 페이지가 중복될 수 있으므로 이를 headroom에 더하면 실제 여유를 과대평가할 수 있다. 각 child의 address-space limit과 측정한 process-tree RSS는 서로 다른 양으로 기록한다.

새 플랫폼 묶음의 개별 작업 한도는 기존 **60 CPU seconds / 180 wall seconds / 2 GiB per process**를 유지한다. 캠페인 전체 한도는 선택한 서로 다른 작업 수와 supervisor reserve에서 명시적으로 계산한다. 5개 전부를 선택하면 작업 allowance 합은 300 CPU seconds / 900 wall seconds이고, supervisor 예산 5 CPU seconds / 12 wall seconds를 더한 명시적 campaign allocation은 **305 CPU seconds / 912 wall seconds**다. 이는 하나의 trajectory cap을 305 CPU seconds로 올리는 허가가 아니다. 기존 `CLOSED_HOLD_NOT_RESET` 장부를 재사용하거나 초기화하지 않는다.

Linux cgroup 제한은 상위 hierarchy까지 읽는다. 확인하지 못한 제한은 무제한으로 바꾸지 않는다. 64 CPU/128 GB 목표는 실제 hostname, CPU topology·affinity·quota 및 RAM 관측과 대조해야 한다. affinity만으로 CPU 소유권을 추정하지 않으며, 실제로 배정된 CPU 집합을 따로 요구한다.

## 5. 자식 프로세스와 비용 집계

메인 scheduler는 단일 스레드이고, 각 작업을 별도 bounded guardian 아래에서 실행한다. Linux subreaper는 부모가 종료된 descendant를 가까운 살아 있는 조상으로 다시 연결하여 종료·회수를 관리할 수 있게 한다. PID namespace가 있는 환경에서는 확인한 `/proc` identity와 signal 대상의 namespace PID가 일치해야 한다. start-time 검증 없는 숫자 PID 재사용이나 가장 안쪽 `NSpid`를 무조건 사용하는 방식은 허용하지 않는다.

whole cost는 preflight, supervisor, reaped children, 살아 있는 descendant의 누적 CPU와 최종 source/input/output hashing을 포함한다. 마지막 작은 receipt 직렬화·fsync 비용만 reserve 안에 남긴다. wall deadline은 실행 루프 외의 preflight와 최종화에도 적용한다. `RLIMIT_CPU`는 프로세스별 한도이므로 이것만으로 전체 process tree CPU cap을 검증했다고 주장하지 않는다.

이 설계는 악의적 권한 경계나 kernel resource container를 제공하는 것이 아니다. 고정 allowlist의 일반 Python/C 작업을 감독하고, 관측할 수 없는 환경 또는 불완전한 cleanup은 fail-closed로 남기는 연구 실행 도구다.

## 6. R3R exact ratio 계약의 재사용

저장 스트림의 한 lane에서 기존 spectral 판정은

\[
r_i=\frac{|p_i-c_i|}{10^{-7}\max(|p_i|,|c_i|)+10^{-10}f_{{\rm BB},i}}
\]

이고, 원본 scalar Planck 함수와 그 입력 연산 순서를 유지한다. R3R은 binary64 subtraction, absolute value, 두 개의 독립 product, sum, division을 각각 수행한다. NumPy ufunc를 나눠 호출하고 FMA나 vector transcendental로 식을 바꾸지 않는다. 정상 finite lane의 max는 이미 계산한 값 중 하나를 선택하므로 같은 lane 값이 주어지면 최대값도 보존된다. 예외 block은 scalar 순서로 재평가하여 원본 첫 오류를 유지한다.

이는 수학적 실수식이 같다는 사실만으로 bitwise 일치를 추론한 것이 아니다. R3R source `1313b1f1b2c081d57bcce9c60e757ef79110df91`에서 실제 25,000 lane bytes와 ordered diagnostic/guard trace를 비교한 증거를 `complete_reused`로 연결한다. R3S의 새 플랫폼 결과가 오기 전에는 같은 라이브러리/컴파일러/하드웨어에서의 재검증을 완료했다고 말하지 않는다.

## 7. 국소 측정을 전체 solver 가속률로 바꾸지 않기

R3R에서 측정한 저장 스트림 감사의 paired CPU 가속비는 \(a=1.3641298365714964\)다. 전체 원래 비용 중 그 감사 경로의 비중을 \(q\)라고 가정하고 나머지 비용이 그대로라면, 조건부 모형은

\[
S(q,a)=\frac{1}{1-q+q/a},\qquad 0\le q\le1,\quad a\ge1.
\]

이때 \(1\le S\le a\)이며

\[
\frac{\partial S}{\partial q}=\frac{a(a-1)}{[a+q-aq]^2}\ge0.
\]

실제 전체 solver의 \(q\)는 이번 연구에서 측정하지 않았다. 예시로 q=0.1, 0.25, 0.5를 넣으면 약 1.0274, 1.0715, 1.1540이지만, 이 값은 관측 또는 NCP 예측이 아니다. 정확한 새 Wolfram input/output은 `WOLFRAM_EXACT_INPUT_CHECK.json`에 있다. 같은 호출에서 미정 기호 W/L/P를 단순히 표시한 부분의 `Symbol::undefined2` 경고도 그대로 보존했으며, 그것을 DAG 정리 증명의 대용으로 쓰지 않는다.

## 8. 물리와 전역 수렴성의 남은 gate

h4의 first-event-plus-two 결과와 h2 endpoint stencil은 기존 성공 범위에서 재사용한다. h4의 이후 U4/U5/U6·low-z 단계 구현·검증, h2 연속 이력 조립, 원래 h의 nodewise C parity 및 early boundary provenance는 별도 의존성이다. `time_convergence.py::signed_triplet`는 필요한 오차 bound가 없으면 `UNCERTAINTY_MISSING`을 유지한다. h4 coverage가 완성됐다는 사실만으로 이 gate를 해제할 수 없다.

격자 이름에도 주의한다. 사용자 R3P 기준의 h는 4.245e-5이다. 기존 `time_convergence.py`의 H0는 8.49e-5이고, 그 모듈의 level1은 4.245e-5, level2는 2.1225e-5이다. 문서상 h/h2/h4 이름 대신 실제 `dlna`와 namespace를 receipt에 같이 써야 한다.

최종 claim은 Mathematical correctness, Numerical equivalence, Implementation correctness, Measured acceleration, Memory/resource behavior, Physical validity, Production readiness로 분리한다. U5 원래 h `HOLD_9_FAIL`, h/2 `HOLD_8_FAIL`, global convergence `NOT_RUN`, `REI_activation=false`, physical `HOLD`, production `NOT_APPROVED`는 유지한다.

## 출처와 재사용 범위

- Python 3.12 `subprocess` 문서: https://docs.python.org/3.12/library/subprocess.html — 스레드 parent에서 `preexec_fn` 사용 위험을 확인하고 별도 stdlib child/guardian 초기화를 사용한다.
- Linux cgroup v2 문서: https://docs.kernel.org/admin-guide/cgroup-v2.html — 상위 CPU/memory 제한 및 controller 관측 계약.
- Linux man-pages `PR_SET_CHILD_SUBREAPER`: https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html — orphan descendant reparent와 wait 계약. 설정은 fork/clone child에게 상속되지 않고 execve는 보존한다.
- S. Taghipour Anvar, D. Kaeli, *A Granularity Characterization of Task Scheduling Effectiveness*, arXiv:2602.20561: https://arxiv.org/abs/2602.20561 — SciSpace에서 발견하고 Exa로 원 abstract를 확인했다. task granularity 검토의 참고이며, 논문의 전체 정리·코드를 도입했다고 주장하지 않는다.
- 원본 HyRec 논문: https://arxiv.org/abs/1011.3758 — R3R에서 읽은 물리 배경을 재사용한다. VigilODE 고정 pin의 새 solver를 HyRec 적분기에 이식한 것은 아니다.
- 직접 확인한 저장소와 결과의 고정 SHA는 `EVIDENCE.json`, `PENDING_GLOBAL_DAG_REVIEW.json`, R3R 선행 receipts를 따른다. 외부 전체 abstract는 배포하지 않는다.
