# REC 다중 bin — 주 대화 반환 및 자료 수령 전용 Codex 인계

## 현재 연구 결과

작업 `REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH`의 새 수치 실행은 완료다.
[PR79](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/79)의 실제 tested
commit은 `2e3b73972ee298d44efdfb10016e314f58b0bada`, tree는
`471442ce757fde701340729cd1abde281fd0db01`이다. 직접 부모는
`a1acf4037f68131ac4c6068eb0d450ef7e51bc97`이다.

[run34087807264/job101635113796](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34087807264/job/101635113796):
7개 TestID 모두 PASS, 실패·오류·skip 0, exit0. 원본 2s base140/hires408
행과 원본 paired/COM API를 사용했다. 84개 합성 JVP의 최대 scaled 오차는
6.4310422961310704e-15다. 원본 BASS/이전 PR 연구를 재실행하지 않았다.

같은 제조 photon/atom 상태에서 log_control의 nodal entropy 생성률은
base -0.0002603135345552853, hires -0.0002601446373071536 s^-1이다.
일치한 chi 읽기는 둘 다 양수다. 모든 bin을 합쳐도 읽기/분배 불일치가
자동으로 사라지지 않는다. 유리수 5노드 map의 rank는 양쪽 모두3이고
7개 count 변수에서4개 영모드를 가진다. 이 결과는 실제 물리 target의
권위나 우주 재결합의 완전한 열화 결과가 아니다.

읽을 결과: [CHECKPOINT_KO.md](CHECKPOINT_KO.md),
[OBSERVED_RESULT.json](OBSERVED_RESULT.json),
[COUNTEREXAMPLE_SUMMARY.csv](COUNTEREXAMPLE_SUMMARY.csv).
OBSERVED_RESULT와 이 두 행 CSV는 job SUMMARY의 구조화된 readback이며
원본 RESULT/CSV 바이트를 대신하지 않는다. 이 문서가 있는 게시 child는
문서 전용이며 tested source라고 재명명하지 않는다.

## 남은 운영 작업: 기존 artifact만 취득·시각 검토·Git 게시

ROLE=LOCAL_CODEX
TASK=REC_PR79_ARTIFACT_ONLY_INTAKE_AND_GIT_RETURN

주 대화는 코드 작성, 새 수학, hosted 실행, log 검토와 요약 게시를 했다.
현재 container가 process 시작 전에 ClientError를 내므로 이미 내려받은
ZIP의 압축 해제·PNG 직접 검토·전체 raw 파일의 영구 Git 복제를 하지 못했다.
Wolfram 대체 경로도 평가 전에404였다. 이 인계는 그 남은 파일 작업만
맡긴다. 연구 코드의 재실행이나 새 과학 연구를 맡기는 인계가 아니다.

처음 할 일은 이 고정 파일을 포함하는 delivery commit을 Git에서 확인하고
같은 작업의 기존 완료 PR/branch/실행 디렉터리가 있는지 제한적으로 찾는
것이다. 완료 반환물이 있으면 재사용한다. 기존 REC checkout의 dirty/
untracked 파일과 HEAD는 바꾸지 않는다. 새 isolated worktree와
`results/rec-pr79-artifact-intake-<UTC-run-id>` branch를 사용한다.
이 인계문을 전달받은 고정 commit을 DELIVERY로 기록한다. branch의
live head를 과거 tested commit으로 취급하지 않는다.

원본 artifact:

    repo cosmosapjw-quantum/rec_bianchi
    run 34087807264
    job 101635113796
    artifact 10005808072
    file count 10
    ZIP bytes 533789
    ZIP SHA256 d57b26de66d26454733d7a29848fd37381cc86020115a90cdcd1efd0c1530694
    expires_at 2026-10-07T05:42:51Z

[GitHub artifact](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34087807264/artifacts/10005808072).
사용할 수 있는 기존 gh/credential helper로 원본을 직접 내려받는다.
예: `gh api repos/cosmosapjw-quantum/rec_bianchi/actions/artifacts/10005808072/zip`
의 실제 응답을 새 파일에 저장한다. 인증정보나 signed URL을 공개하지 않는다.
`gh run download`로 이미 푼 파일만 있으면 원본 ZIP 해시를 검증했다고
쓰지 말고 개별 파일 검증과 구분한다. 같은 ZIP이 이미 로컬에 있으면
그것을 확인하고 불필요하게 다시 내려받지 않는다.

다운로드 후 다음을 수행한다.

1. ZIP hash/크기와 안전한 member 경로를 검사한다. 절대경로, ../, 중복명,
   symlink, 예상 밖 member를 거부한다. 새 Git 밖 디렉터리에만 추출한다.
2. 원본 SHA256SUMS의9개 파일을 검증하고 OBSERVED_RESULT.json의
   file_sha256_reported_by_runner와도 비교한다. 열 번째 파일은 SHA256SUMS다.
3. 원본 RESULT.json의 source/workflow/tree/부모/7개 TestID/exit0 및
   전후 원본 blob을 확인한다. CASE_SUMMARY/JVP/BIN CSV를 본문 수치와
   대조한다. 이 파일 검사를 science test 재실행으로 세지 않는다.
4. 원래 bin_affinity.png와 aggregate_entropy.png를 실제로 연다.
   축·단위·범례·잘림·겹침, base/hires 곡선 구분, analytic curve와
   API 원본 관측값의 구별을 확인한다. 원래7인치 폭은 약178mm이므로
   그 크기와90mm 축소 가독성을 별도 기록한다. 그림을 못 열면
   NOT_PERFORMED로 반환하고 PASS를 추정하지 않는다.
5. 원본 파일을 그대로 Git에 추가한다. 권장 새 경로는
   `docs/research/rec_multi_bin_affinity_20260907/evidence/original_run_34087807264/`다.
   원본 CSV/JSON/PNG/SHA256SUMS를 재직렬화·공백 정리·덮어쓰지 않는다.
   raw log를 텍스트 정책 때문에 변형해야 하는 경우 원본 ZIP을 먼저
   보존하고 가역적인 JSON 문자열 wrapper를 추가한다. 원본과 wrapper의
   관계 및 두 hash를 기록한다. 새 broad exclusion이나 gate 우회는 금지다.
6. `ARTIFACT_INTAKE_KO.md`와 `ARTIFACT_INTAKE.json`에 실제 파일검사,
   시각 검토, 원본 바이트 보존, 새 변경 파일, 게시 identity와
   `numerical_execution_repeated=false`를 기록한다. 이 source를 실행해
   새로운 numerical PASS가 난 것처럼 적지 않는다.

필요한 수리는 자료 취득·경로·포장·반환의 재현된 결함에만 허용한다.
같은 objective/scope/invariants 안에서 진단→수정→파일 검증을 반복해
완료하고, 사소한 오류마다 재승인을 요구하지 않는다. 최초 오류는 보존한다.
원본 수치/표/코드/허용오차/claim은 바꾸지 않는다. 그림 결함을 발견하면
원본을 보존한 별도 display-only 파생본만 추가할 수 있다. raw data나
source 연산은 재계산하지 않는다. 정확한 변경과 전후 그림 검토를 남긴다.

절대 실행하지 않을 항목:

    run_study.py, test_study.py, 이전 PR70/75/77/78 checker
    새 BASS/native 빌드 또는 source 수정
    새 target refinement 실험, 새 물리 map/provider
    repository-wide pytest/기존 공백 gate 수리

파일이 만료·유실되어 복원할 수 없으면 기존 summary와 과거 실행 PASS는
보존하고 missing raw artifact만 정확히 보고한다. 동일 결과를 재실행해서
원본 artifact라고 바꾸지 않는다.

원격 게시는 본 작업의 새 result branch에만 non-force push하고,
base=`research/rec-multi-bin-affinity-20260907-r1`인 Draft PR로 반환한다.
PR79 source branch, 부모 PR78, main은 변경하지 않는다. merge/ready,
force push, Jira/Confluence 쓰기 또는 자격증명 설정 변경은 하지 않는다.
동시 갱신이 있으면 자기 branch만 다시 확인하고 상대 source를 덮어쓰지 않는다.
쓰기 실패가 실제 발생하면 local diff/bundle을 보존하고 그 blocker를
보고하되, Git 게시가 가능한 동안 수동 ZIP 왕복을 기본 절차로 만들지 않는다.

최종 출력은 Draft PR URL, 고정 ARTIFACT_INTAKE_KO.md URL,
게시 commit/tree, 검증된 원본 ZIP hash, 그림 판정, 남은 blocker다.
사용자는 그 링크만 주 대화에 전달하면 된다. 성공/부분완료 모두 실제
근거를 남기고, 주 대화가 최종 수용을 맡는다.

## 다음 과학 작업은 별도이며 이 인계에서 시작하지 않는다

`REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE`:
같은 원본 2s 표와 같은 연속 reference 상태를 고정하고 photon target의
해상도를 바꾼다. 각 격자의 mu를 한 공통 reference measure에서 만들고
같은 비상수 시험함수의 source pairing 및 JVP로 비교해야 한다.
임의 grid-dependent mu나 차원이 다른 raw source 벡터로 수렴을 주장하지
않는다. 한 transition의 반대칭 비열적 영모드는 그대로 보존한다.

현재 관측은 제조5노드와 원본 표의 한정된 연구 PASS다. 실제 target
권위, 이동 map/event, 시간 적분, angular/polarized kernel, BASS evolve와
provider는 미완료다. `NO_PASS_REC_PHYSICAL_SPLIT`,
physical_source_authenticated=false, provider_admitted=false를 유지한다.
