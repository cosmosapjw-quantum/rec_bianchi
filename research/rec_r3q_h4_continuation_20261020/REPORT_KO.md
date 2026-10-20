# R3Q 독립 h4 continuation 및 NCP 제한 실행 결과

## 2026-10-20 NCP 실행 후속

PR #111의 게시된 소스 `1ad0380110621446c42df9d995fd85db3a6c7e7a`에서 입력과 완료된 R3M U6 결과를 SHA 검증 후 재사용했다. NCP `s1a0e5abed09`는 64 CPU / 약 125 GiB RAM 호스트였다. 재귀 순서가 직렬인 두 서로 독립적인 경로를 CPU 63과 62에 각각 고정하고 BLAS/OMP 스레드를 1로 제한해 병렬 수행했다. 각 allocation의 주소공간 한도는 계약대로 프로세스당 2 GiB였다. 두 경로 실행 중 기존 HE29 작업도 관찰되어 계속 실행되도록 두었다.

| 경로 | 실제 결과 | 자원 및 범위 |
|---|---|---|
| h4 first event+2 | helium cutoff `iz=74409` 후 H_ONLY 2 step, endpoint `iz=74411`, `EVENT_PLUS_TWO`; native same-h parity PASS, source closure 100/100. Astra 독립 판정 `PASS_SCOPED_H4_FIRST_EVENT_PLUS_TWO`. | 30.196 CPU s / 30.345 s runner wall; allocation 600/900 CPU/wall, 2 GiB/process. NCP affinity `[63]`. |
| h2 low-z | 153,327 accepted steps, 43 checkpoints, same-h PASS. Source-defined z=0 cubic stencil에서 정지; 마지막 입력 z=`-2.238689928646398e-5`, 네 번째 경계 상태 부족. Astra 독립 판정 scoped PASS. | 60.756 CPU s / 62.633 s runner wall; allocation 600/900 CPU/wall, 2 GiB/process. launch CPU 62 확인. |

원본 실행물과 검토서는 각각 `ncp_event_001/` 및 `../rec_r3o_grid_frontiers_20261019/lowz_ncp_full_001/` 아래 있으며, 하위 `INDEPENDENT_REVIEW.json`은 최종 검토판정 및 해시를 기록한다. h4 continuation NPZ SHA는 `7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9`, h2 low-z NPZ SHA는 `b25e2cbdafe4037d222116c4985eac95a380552f6799a2b3e950fb499965dbe6`이다. h2 z=0 interpolation 수치는 native 대 Python `xe=0.0001756130661263253 / 0.00017561306612632919`, `Tm=0.021729482901094277 / 0.02172948290109453`로 계산됐고, 그 값은 독립 검토서에서 4-state cubic 재계산으로 검사했다. 기존 source 경계에서 필요한 stencil coverage가 없으므로 이를 완전 z=0 종료로 해석하지 않는다.

사용자의 64코어 자원 요청을 반영해 두 독립 경로를 동시 배정했으나, 두 시간축 재귀는 각각 직렬이며 기존 호스트 작업도 있어 나머지 코어를 임의로 과할당하지 않았다. allocation의 2 GiB/process 제약을 유지했으며 128 GiB 전체를 작업에 노출하거나 사용했다고 주장하지 않는다. h2 실행 중 PSR 62 스냅샷과 launcher taskset은 남았지만 전체 연속 affinity mask 및 동시 process-tree RSS 합계는 측정하지 않았다.

**상태 경계:** 원래 budget `CLOSED_HOLD_NOT_RESET`, 원본 h U5 `HOLD_9_FAIL`, h2 U5 `HOLD_8_FAIL`을 그대로 보존한다. h4 event+2만 완료되었고, 후속 h4 U4/U5/U6/low-z 모듈 연결은 구현 미완료다. h2 노드는 source cubic-stencil 경계에서 종료됐다. 세 격자 수렴 `HOLD/NOT_RUN`, 전체 물리 admission 미승인, `REI_activation=false`, Bianchi/REI/CMB admission=false다. 이 scoped PASS들은 역사적 U5나 전역 과학 주장을 변경하지 않는다.

두 경로는 이번 새 allocation에서 합계 약 90.952 CPU초와 93초 solver wall을 사용했다. 서로의 비용을 역사적 U5 비용에 합산하거나 U5를 재개하지 않았다. 실행시각·호스트·launcher 및 관찰의 한계는 allocation/runtime observer receipts에 보존되어 있다. reviewed 결과 묶음은 `NCP_EXECUTION_DELIVERY.json`에 기록한 SHA `5219995db41dfebf8d0ceafa445402f9125e01321241a34a54fd9f4592c513e2`로 Dropbox와 Google Drive에 각각 업로드한 뒤 전체 재다운로드 hash까지 일치했다. PR #111 브랜치에는 commit `2236c19ff71b2706696e1985d968b2b841fd55bc`로 게시했고 원격 ref SHA를 확인했다.

---

실제 start8 checkpoint에서 다음2개 accepted steps를 진행하는 새 Python/C 실행 경로를 완성했다. h4=2.1225e-5, iz72900→72902에서 original-C 같은-h 검증 PASS이며, 동일 소스의 독립 검토는 `PASS_SCOPED_TWO_STEP_CONTINUATION_AND_EXECUTION_HARNESS`다. 첫 stage event 실행은 NCP에 넘길 준비가 됐다.

## 구성과 이론

증강 상태는 accepted atomic state, He/H 각각 두 이전 RHS, post-Saha flag, 수용된 virtual/Lyman photon prefix로 정의한다. 고정된 원본 source와 h4에서 이 증강 상태 및 동일 연산 순서를 주면, 다음 원자입력·causal interpolation·predictor·accepted photon column이 차례로 정해진다. 따라서 체크포인트에서 저장된9상태/8열/최종 predictor를 그대로 가져오는 재개는 동일 step map의 연결이다. 초기 h4 helium72,893행을 Python에서 반복하거나 h2상태를 보간할 필요가 없다.

첫 continuation의 photon index는8, global index는72900이다. current accepted input에서 계산한 열만 commit하고, 다음 post-Saha trial은 그 열까지의 prefix를 읽는다. trial spectrum은 저장하지 않는다. He cutoff와 post-Saha switch는 매 accepted input의 stage 조건에서 결정하고 event 뒤2단계까지 비교한다. source의 H+He 비postSaha 분기는 neutral xH1s를 직접 갱신하며 H-only분기는 원본 total xe를 넘긴다. 부동소수점의 `/2./delta`, `/2./DLNA` 순서도 보존했다.

시간축은 이 인과 prefix 때문에 순차 실행한다. h2 low-z, 다른 원자repo와의 독립 계산, 완료 photon-column 감사는 별도 작업으로 병렬 배정할 수 있다. 원자·열 연산자, 고정cosmology, 원래 tolerance를 바꾸지 않았다. 이 단위에는 새 tensor/curvature 유도가 없어 xAct 계산을 추가하지 않았다. 외부식은 Git에 고정된 원본 HyRec2012 `history.c`, `hydrogen.c`, `helium.c`를 실제 읽고 컴파일한 것을 사용했다.

## 실제 결과와 교정

최종 smoke003은2accepted/8FULL evaluations이다. 독립 C는 자신의72,893He rows와8prefix+2새열을 생산했다.10STEP,3,110virtual+3,110average+30Lyman fields 비교에서 xHII/xe/Tm 차이는0, 최대He 절대차5.421010862427522e-20, H RHS scale-max1 차1.2790463133072194e-13이었다. 최대photon tolerance ratio는7.883083461150054e-6이다. common-input8회도 PASS, electron ledger 최대2.6861108823328372e-17, H/He nuclei ledger0이다.

전체 supervisor CPU2.418778164초/wall2.522254687초, 최대 waited-child RSS222,298,112bytes다. RSS는 동시 process-tree 합계가 아니다. 실행 시 source closure100개가 전후 일치했다.10개 고유 stdlib unittest methods는 checkpoint mutation, h2cosmology 거부, detached callback, 잘못된Schur residual4종, 비postSaha neutral변수, closure변경, nonzero child, wallkill, 잘린receipt, false-success 방지를 검증했다. pytest는 이 sandbox에 없어 동일 경량검증을 표준 unittest로 작성했다.

독립 reviewer가 (1) source 연산순서, (2) 비postSaha neutral H 갱신, (3) failure 후 success label 유지, (4) supervisor의 잘린verification 처리 공백을 지적했고 모두 교정했다. 마지막 실제 실행은 교정 후 소스와 결속한다. smoke001/002는 개발 중 상태로 보존하고 최종 채택 결과로 합산하지 않는다. event 실행/전역수렴은 HOLD다.

## 연구 루프와 다음 노드

| 단계 | 이론 R | 코딩 C |
|---|---|---|
|1|최근72h 과학결과/범위 읽음|baseSHA와 frozenstart8 고정|
|2|HyRec 원전·R3M/O/P 재사용|state/predictor/photonprefix 연결|
|3|h4 q=0 source와 closure 명시|ordered arithmetic/causal쓰기 설계|
|4|증강상태 연결 선택|host1core, 새allocation DAG|
|5|결정적 step map 연결과 original재귀|전용module/C oracle/worker/supervisor 완성|
|6|독립 원본 C 및 reviewer|10focused methods PASS|
|7|최종 실제2step 대조|ledger/상태/RHS/spectrum PASS|
|8|2step scoped채택, event/수렴open|source100개·자원·native독립성 기록|
|9|단위사상과 NCP계약 작성|독립review 네 지적 교정|
|10|DAG와 handoff 보존|게시·백업은 parent receipt와 연결|

새 strong no-go 주장은 없다. 기존 U5 HOLD는 이 실행에서 발생한 새 불가능성 정리로 바꾸지 않는다. 기존 전체 검증을 반복하지 않았고 최근 CI/백업 읽기를 새로운 science run 수로 합산하지 않았다.

NCP에는 `HANDOFF_KO.md`의 완성된 Git-only h4 event명령을 넘긴다. h2 low-z153,327step도 기존 구현이 완성되어 있으며 R3M raw 복구와 실제 새 hostallocation이 필요하다. 그 이후 h4 U4/U5/U6/low-z 연결 및 전체 h/h2/h4 comparator는 실제 event와 coverage를 입력으로 진행한다. 원래 h U5 HOLD_9_FAIL, h2 HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI_activation=false를 유지한다.
