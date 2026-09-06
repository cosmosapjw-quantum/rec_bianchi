# 작업 스레드 — REC_SPEC03A 실제 ModeB 읽기·분배 호환성 진단

@GitHub @Superpowers @Atlassian Rovo

역할은 WORK_THREAD다. 대화 스레드의 기존 승인 `REC_2S_FULL_BOSE_SINGLE_FIELD_TWO_LEG_RESEARCH`를 유지한다. 다시 모델 승인을 요청하지 않는다. 생산 통합 승인은 아니다.

## 고정 입력과 실제 실행 역할

저장소 cosmosapjw-quantum/rec_bianchi. 이 문서가 포함된 정확한 게시 commit을 DELIVERY_SHA로 기록한다. 인계 commit의 직접 부모는 PR70 완료 `84205ab6a9b4e6d51097a82ec15da4deedfefc41`, tree `6f89ef4b871015912596200ba9aec3f2b2999c63`이어야 한다.

BASS 읽기 기준은 PR127의 `9d1c702ddf58549a06b29965a3d1b790a0c23159`, tree `12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c`다. 이 기준을 production admission으로 부르지 않는다. 시작할 때 같은 진단이 후속 PR에서 이미 끝났는지 한 번 확인하고 중복 구현을 피한다. 문서-only tip 이동과 production blob 변경을 구분한다. 과학적 source 기준을 조용히 바꾸지 않는다.

SOURCE_MAP_AND_RESEARCH_KO.md와 LOCAL_CODEX_PROMPT_KO.md를 전체 읽고 같은 고정 버전으로 local Codex에 전달한다. local이 실행 소스 commit/tree, 실제 명령·로그·결과·그림·bundle을 반환할 때까지 새 수치 PASS를 주장하지 않는다. local을 자동 실행할 도구가 없다면 전달문을 사용자에게 주고 대기 상태를 명시한다.

작업 스레드는 저장소·게시의 단일 작성자이고 local은 계산·소스 commit·원본 증거 반환만 한다. 두 작성자가 같은 branch에 원격 push하지 않는다.

## 범위

새 결과는 `docs/research/rec_spec03a_modeb_diagnostic/` 아래만 추가한다. 연구용 checker·필요한 작은 Rust 호출기·검산 결과·그림·checkpoint를 담는다. 기존 src/tests/archive, 승인 JSON, 원본 HyRec 자료, 과거 PR63–70 증거는 변경하지 않는다. BASS의 모든 파일은 읽기 전용이다. 새 workflow·대규모 manifest·범용 하네스는 만들지 않는다.

권장 결과 branch는 `research/rec-spec03a-modeb-diagnostic-20260906-r1`이다. 이미 있으면 내용을 읽고 덮어쓰지 않는다. 정확한 DELIVERY_SHA에서 새 격리 worktree를 만들도록 한다. 사용자 Dropbox checkout의 dirty/untracked 파일은 건드리지 않는다.

## 이미 완료되어 다시 실행하지 않을 것

PR70의 기본/hires 9사례·네 시험함수·80/120자리·pytest7·ZIP/bundle 전체 검사와 PR63 수치 어댑터 검증을 반복하지 않는다. R10A 전체 hardening, BG02, Rust/JAX/BASS 전체 build, 원본 HyRec C/history와 전체 repository pytest도 이번의 선행 gate가 아니다.

이번 목표는 새 물리 map의 구현이 아니라 실제 로그상태와 radial interpolation이 무엇을 읽고 무엇을 보장하는지 확인하는 한 번의 진단이다. 직접 물리입력 owner가 미확정이면 제조 단위 앵커로 조건부 진단을 진행하고, 그것을 생산값으로 선택하지 않는다.

## 반환물 검토

local은 source-map 문서에 있는 기존 blob을 확인하고, 사용한 파일만 실제 바이트로 해시한다. 반환 ZIP/manifest/bundle의 안전한 수령 검사와 실제 source/실행/결과 parent 관계를 검토한다. source와 publication commit의 metadata 차이는 동일 tree 여부와 구분한다.

실제 결과에서 확인할 것은 다음이다.

- ModeB의 방향 우선 lnf 저장과 pack/unpack; 다른 F[r,a] 경로와 구분.
- q→물리 에너지 질의의 기하 배율·단위앵커 조건.
- 실제 radial.rs의 order2 로그 보간과 독립 정확한 값의 대응.
- 로그 보간 Jacobian 행합5/4 반례; 이를 실제 B로 사용하지 않음.
- 제조 Planck 읽기오차가 full Bose source에 미치는 정확한 반례.
- C/(H*f) 및 JVP의 3/8, -1/8 제조 값.
- 실제 지원 범위, 미확인 공급자와 source-only/실행 결과의 분리.

읽기 경로와 새 함수에 직접 관련된 테스트만 확인한다. 반례가 나온 것이 생산 코드 실패인지, 의도된 유한격자 근사 차이인지 구분한다. 과거 결과를 새로운 test 수에 더하지 않는다. 결과를 맞추기 위한 보간법·꼬리·expected 값·허용오차 변경은 하지 않는다.

## 게시와 동기화

검토된 결과 child만 non-force 게시하고 인계 branch 위의 Draft PR로 보존한다. 고정 인계 branch 자체를 수정하지 않는다. 실제 source/실행/publication commit·tree·부모·변경 경로를 다시 읽는다. merge/ready/rebase/force-push는 하지 않는다.

REC만 append: cloud e1cd4b3d-2781-4a6f-9f58-e35aa48753db, BASS-19, BASS-26, FED-02 page27492353. 최신 댓글을 읽어 중복을 피하고 새 결과·PR을 한 번씩 기록한다. 공식 dependency·상태·타 저장소 snapshot은 변경하지 않는다. GitHub 게시 성공과 Atlassian 성공을 따로 보고한다.

자동 일반 CI가 발생하면 실제 읽은 새 log 범위만 분류한다. 지난 공백 실패를 추정하여 덮어쓰거나 이번 branch에서 수리하지 않는다. 전체 pytest 미실행은 그대로 미실행이다.

## 종료

최대 결과는 `PASS_BOUNDED_MODEB_READ_SCATTER_DIAGNOSTIC`이다. 읽기오차가0이어야만 성공이라는 뜻이 아니고, 정의된 연산·반례·미분·근사오차를 실제로 분리했음을 뜻한다. 실제 명령을 실행하지 못하면 `DIAGNOSTIC_EXECUTION_BLOCKED`와 얻은 자료를 보존한다.

`NO_PASS_REC_PHYSICAL_SPLIT`과 physical/provider=false를 유지한다. 결과를 대화 스레드로 반환하고 이 진단에서 끝낸다. 실제 B·mu·unit owner가 정해졌다고 주장하거나 새 photon/보간/공급자 구현으로 자동 확장하지 않는다.
