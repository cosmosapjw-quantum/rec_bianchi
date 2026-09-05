# 작업 스레드 인계 — 승인된 단일 복사장 기본/고해상도 비교

@GitHub @Superpowers @Atlassian Rovo

## 목표와 고정 기준

사용자 승인: `/approve REC_2S_FULL_BOSE_SINGLE_FIELD_TWO_LEG_RESEARCH`.
저장소: cosmosapjw-quantum/rec_bianchi.
현재 물리 선택은 연구용 full Bose·한 분포·두 에너지 기여다. 다시 승인 요청하지 않는다. 물리 입력·B·mu·각도 kernel·provider·merge까지 승인받았다고 확대하지 않는다.

이 인계문을 포함한 정확한 게시 commit을 사용자 전달값 또는 GitHub 읽기로 확인하고 DELIVERY_SHA로 기록한다. 그 commit의 source 부모는 PR #68의 `708a9b419a193713240ff3aaa674e6e612ddfb2b`, tree `b6bab967316518f48d3da9b7f192ff03241fd61f`다. 인계 commit과 아래 원래 연구 실행 commit을 구별한다.

- PR67 검산: dc9e9e9394eba314afa13e6db1b0811257e3be55.
- PR68 실제 실행 source: 6158bbf26f9f4aaccdb90c7c0c7bddaaaabe77fd.
- PR68 완료 문서: 708a9b419a193713240ff3aaa674e6e612ddfb2b.

처음 한 번만 최신 PR/branch와 같은 기본-hires 비교가 이미 수행됐는지 확인한다. 완료 successor가 있으면 재구현하지 않고 원본 결과를 수령·검토한다. 문서-only tip 이동을 과학적 오류로 부르지 않지만 과학 source base를 조용히 바꾸지도 않는다. 기존 O1 조사와 O2/O3 비교는 반복하지 않는다.

## 삼분할

대화 스레드는 모델·수학적 범위·다음 작업을 결정했다. 이 작업 스레드는 저장소와 게시의 단일 작성자다. 실제 수학/수치 계산은 local Codex에 아래 LOCAL_CODEX_PROMPT_KO.md와 RESEARCH_PLAN_KO.md를 함께 전달한다.

local Codex는 계산 코드를 작성하고 로컬 source commit, 결과 bundle/ZIP, manifest를 반환한다. 원격 branch를 동시에 쓰지 않는다. 이 작업 스레드는 결과를 받기 전에 실행 완료를 주장하거나 다음 물리 node로 넘어가지 않는다. 직접 local에 명령할 도구가 없다면 정확한 전달문과 고정 source 식별정보를 사용자에게 반환하고 대기 상태로 남긴다. 자동 백그라운드 실행을 약속하지 않는다.

## 허용 경로

새 결과 child의 변경은 `docs/research/rec_2s_base_hires_response/` 아래로 제한한다. 작은 checker, 사례 JSON, 실행 결과, 그림과 최소 checkpoint를 둔다. 기존 src/tests/archive, 원본 표, 과거 evidence, OWNER_REVIEW_CONTRACT.json, 원래 O2/O3 제안, root 하네스 문서는 그대로 둔다. 새 workflow·광범위 manifest·범용 runner를 만들지 않는다.

권장 결과 branch: `research/rec-2s-base-hires-response-20260905-r1`. 이미 있으면 내용을 먼저 읽고 덮어쓰지 않는다. 결과 child는 정확한 DELIVERY_SHA를 부모로 삼아 승인 기록을 포함한다. 운영자 Dropbox checkout은 건드리지 않는다.

## 먼저 읽을 것

AGENTS.md와 docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md를 읽는다. root HANDOFF_PROMPT.md는 옛 REC-NEXT-03 검증 범위이며 이번 연구·게시 승인을 대체하지 않는다. 기존 파일은 수정하지 않는다.

이 디렉터리의 OWNER_DECISION.json, RESEARCH_PLAN_KO.md, LOCAL_CODEX_PROMPT_KO.md를 읽는다.
PR65의 PROVENANCE.json 및 SOURCE_EXCERPTS.txt, PR67의 O2_O3_REVIEW_PROPOSAL.json 및 RESULTS.json, PR68의 ARCHIVE_INVENTORY_READBACK.json과 CLOSEOUT_KO.md를 읽는다.

## local Codex에 넘길 단일 계산

기본/hires 두 표의 원본 설정과 정규화를 확인하고, 계획서에 고정된 동일 f_alpha(E)와 population으로 두 광자 약형 J_r[phi]와 alpha JVP를 비교한다. 모든 식과 9개 복사장 사례, 네 시험함수는 RESEARCH_PLAN_KO.md에 고정돼 있다. 기본/hires 차이를 작게 만들기 위한 조정은 하지 않는다.

생산 함수는 PhysicalTwoPhotonRamanBin을 재사용한다. 기본 loader의 고정 shape/hash를 바꿔 hires를 통과시키지 않는다. 필요하면 연구 디렉터리 안의 입력 parser만 추가한다. 고해상도 NSUBLYA와 정규화는 원본 주석 설정까지 확인하고, 불명확한 값은 보고서에 null로 남긴다. 그 불명확성 때문에 과거 작업을 재실행하지 않는다.

## 반환물의 수령 검사

원본 실행 결과는 RESULT.json, source commit/tree, 실제 명령·종료 코드, package 경로/버전, input member hashes, 수치 CSV, 그림, raw log, 파일별 SHA256SUMS와 source bundle이다. 동일 결과를 다른 metadata로 다시 실행했다고 표시하지 않는다. 수령 ZIP의 실제 bytes와 manifest를 검사하고, 테스트 소스 tree와 게시 tree가 같으면 commit metadata 차이를 분리한다.

판정은 입력 대응·고정 사례 실행·회계 항등식·독립 reference·수치 정확도 증거로 한다. 두 표가 비슷해야만 PASS라는 gate는 없다. 가짜 평형/소거, 두 다리 중복·누락, 독립 companion 함수 사용, 같은 행 번호끼리의 잘못된 비교를 검출해야 한다. 검토는 위험 범위 한 번, 독립 읽기 전용 검토를 실제 사용할 수 있으면 최대 한 번, 표적 수정 한 번 뒤 checkpoint한다.

## 게시와 동기화

검증된 새 child만 non-force로 게시하고 Draft PR을 만든다. merge/ready/rebase/force-push를 하지 않는다. 고정 인계 branch는 변경하지 않는다. source/실행/publication commit·tree·부모·변경 경로를 다시 읽는다. local tested commit이 connector publication metadata와 다르면 같은 tree 여부 및 원본 bundle 보존을 기록한다.

Atlassian에는 결과와 PR만 한 번씩 append한다: cloud e1cd4b3d-2781-4a6f-9f58-e35aa48753db, BASS-19, BASS-26, FED-02 page27492353. 시작 시 최신 댓글을 읽어 중복을 피한다. Jira 상태·공식 dependency·다른 저장소 snapshot은 변경하지 않는다. 댓글 추가 실패와 재확인 실패를 구별하고, 응답이 불명확한 쓰기를 무조건 재시도하지 않는다.

일반 CI가 자동 실행되면 새 log를 읽은 범위까지만 분류한다. 과거 공백 실패와 같다고 추정하지 말고, 수정도 이 연구에 섞지 않는다. 전체 pytest를 실행하지 않았다면 미실행이라고 적는다.

## 종료

최대 주장은 `PASS_BOUNDED_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH`다. 이는 입력 설정이 검증되고 정해진 비교가 수행됐다는 뜻이지 hires가 정답이라는 뜻이 아니다. `NO_PASS_REC_PHYSICAL_SPLIT`, 물리 인증 false, provider false를 유지한다.

결과를 대화 스레드에 돌려주고 이번 한 비교에서 끝낸다. 비교 오차가 크거나 설정이 미해결이면 그대로 연구 결과로 보고한다. B·mu 선택이나 실제 source/evolution 연결을 자동으로 추가하지 않는다.
