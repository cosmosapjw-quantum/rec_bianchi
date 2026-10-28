# C2 — 식·자료·코드의 실제 대응

중앙 DAG28/88(+0), 단위 내용12/20. C1의16개 immutable 입력과 R9 계약을 사용한다. 이번 단계는 실제 저장 형식과 함수 경로를 연결하며 아직 새 point call을 수행하지 않는다.

## 데이터 결속 경로

| 자료 | 실제 역할 | 결속 조건 |
|---|---|---|
| SELECTED_SLOTS.txt |132 distinct native local slots |중복/누락 없음 |
| LAST_WRITERS.json |각 slot의 실제 마지막 call id, JSON list |slot로 얻은 id 사용 |
| CALLS.jsonl |dispatcher scalar hex, id,global,slot,phase,site,model, saved dxHII_deta |id와slot 모두 일치 |
| QSS_WRITES.jsonl |real2,virtual311,incoming_virtual311,incoming_lyman2,outgoing/average saved arrays |동일id,slot,정확shape |
| WRITES.jsonl |coefficient_TM_eV,coefficient_TR_eV |동일id,slot;dispatcher prelude 결과와 대조 |
| native_path.json |313query,626endpoint,132native time 및 geometric clock/alpha |각endpoint의finalwriter와같은id/slot |

C1의 locator finding은 WRITES와 QSS_WRITES의 역할을 바로잡아 해결했다. C5는 이 경로를 binder로 구현하고 C6/C7에서 실제132개 입력을 검증한다. Committed node의 xHII=null을 임의 보간하거나 phase를 추측하는 경로는 필요하지 않다. 실제 CALLS에 xe와xHII가 있다.

## 식에서 native 함수까지

1. 원 dispatcher 입력 nH_cm3,H_s_inv,TM_eV,TR_eV를 binary64 hex로 읽는다. history의 Kelvin·m^-3 conversion은 이 입력이 생성될 때 이미 수행되었으므로 다시 하지 않는다.
2. FULL point prelude: ratio=TM/TR;rescale_T(&TR,fsR,meR);TM=ratio*TR. WRITES의 coefficient temperature와 결속한다.
3. Original populateTS_2photon은 원 initialized tables를 읽어 A,B,C,V와sr,sv,tau,Alpha,DAlpha,Beta를 만든다.
4. Original solve_real_virt는 V diagonal/80-bin tridiagonal elimination,2x2 Schur solve,virtual backsubstitution을 수행한다.
5. 원 scalar grouping으로 FH를 계산한다. 이 primary의actualHe-neutral/xe=xHII조건에서 Fe=FH.
6. 원 FULL 함수의 outgoing/average history write는 point API에 포함하지 않는다. New output은 point-level diagnostic과새FH이며physicalcertificate는null상태를보존한다.

원래 source에는 history interpolation이 outgoing history와 earlier times를 읽는 의존성이 있다. 이를 무시한 것이 아니라 actual saved incoming을 explicit argument로 옮겼다. 새로운 완전한 history evolution이나 autonomous full-state coupling을 구현하는 단위는 아니다.

## Numerics와 관측의 경계

B=Trv, C_bi=Tvr[i][b]; Vlower=Tvv[1],Vupper=Tvv[2]. Independent reconstruction은 이 방향을 코드에 명시한다. 초기 미기입 band의0은 원 calloc에서 온다. Original scalar source나 table interpolation을 안정화 명목으로 바꾸지 않는다.

Original source 파일은 입력으로 보존한다. C3의 generated observation copy는 실제 solver가 이미 계산한 divisor를 읽는 hook만 추가한다. Primary 연산의 변경 여부는 generated diff와 C9검토 대상으로 남긴다.

## 오류 분류와 실행 영향

자료 locator 오류는 입력 의존성/문서 mapping 오류이며 physical model이나수치scheme변경이아니다. Source bytes불일치는immutableinput의과학재현성문제로실행전중단한다. Binary64output의bitwise불일치는관측값으로기록하고frozenparity/residual기준으로판정한다. Partialbackupsearch나미관측모델identity는field식의실행불가근거로사용하지않는다.

Compiler/ABI/복원경로 오류는environment/implementation분류로최소수정한다. 허용오차·species scope·solver/closure를변경해야하는실패는root에반환한다. 기존전체캠페인반복은이수정경로에포함하지않는다.
