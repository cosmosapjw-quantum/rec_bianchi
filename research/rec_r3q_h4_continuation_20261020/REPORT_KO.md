# R3Q 독립 h4 continuation 연구 결과

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
