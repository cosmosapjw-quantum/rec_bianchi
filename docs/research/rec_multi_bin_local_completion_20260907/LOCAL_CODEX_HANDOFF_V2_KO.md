# LOCAL CODEX HANDOFF V2 — 완료된 PR79를 반복하지 않는 로컬 보충

ROLE=LOCAL_CODEX
WORK_UNIT=REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH
SLICE=LOCAL_NULLSPACE_COMPLETION
REPOSITORY=cosmosapjw-quantum/rec_bianchi
GITHUB_ACTIONS=PROHIBITED

이 V2가 LOCAL_CODEX_HANDOFF_KO.md의 실행 기본값과 최초 실행 SHA를 대체한다.
이전 문서의 보호 경로, 동일 scope 내 자율 수리, 공개 자료 안전, non-force
반환, merge/ready 금지 원칙은 유지한다. READBACK_UPDATE_KO.md를 먼저 읽는다.

## 1. 이미 완료된 것과 실제 남은 것

PR79의 7개 그룹/84개 방향 비교는 이미 완료되었다. 주 대화가 Git에 보존된
구조화 readback의 exact TestID, source/tree, exit0 및 원본 blob을 읽었다.
이를 새로 실행할 이유가 없다. 원본 raw artifact의 별도 회수/전체 manifest
인증/원본 그림 시각검토는 그 readback과 구분하여 아직 미완료로 유지한다.

기존 계산 source:
2e3b73972ee298d44efdfb10016e314f58b0bada
기존 source tree:
471442ce757fde701340729cd1abde281fd0db01
기존 Git 결과 commit:
0db9612b8c1fb2c6c8119f23138ff5efe54fcc06
기존 Git 결과 파일:
docs/research/rec_multi_bin_affinity_20260907/OBSERVED_RESULT.json
기존 결과 Git blob:
a3244d115b7fc5f17b70a14af5aefc4c3b36aad3

현재 남은 실행은 verify_nullspace.py의 새4개 그룹과16개 추가 방향이다.
그 뒤 plot_supplement.py로 저장된 CSV만 렌더링하고 실제 시각검토한다.
새 renderer는 old source/old tests/new tests를 다시 호출하지 않는다.
원래 PR79 자료가 이미 로컬/Git에 있으면 읽을 수 있지만 Actions에 접근해
가져오거나 새 그림을 역사적 artifact의 복구본으로 표시하지 않는다.

## 2. 이번 최초 실행 source

    EXECUTION_SHA=9195f94bf308806ae6e9070f6175b500a1c2ef53
    EXECUTION_TREE=98577a94604efff77c24b89ee3a56a99fd478f16

V2 문서 자신은 이 source의 문서 전용 child다. DELIVERY_SHA는 전달된 V2
immutable blob URL에서 읽는다. 실제 실행 source와 delivery를 혼동하지 않는다.
공유 branch는 research/rec-multi-bin-local-completion-20260907-r1이다.

이 source는 PR79의 실제 계산 source에서 갈라진 독립 branch다. 이후 PR79의
네 결과 문서가 우리 branch에 병합된 것으로 주장하지 않는다. 원본 Python
3개와 src/tests/archive가 두 branch에서 동일한 사실 및 별도 고정 결과 링크를
이용해 완료 근거를 재사용한다. 새 runtime/syntax/4개 시험/그림은 아직 미검증이다.

## 3. 로컬 실행 명령

기존 REC_REPO와 설치된 연구용 REC_PY 경로를 실제로 확인한다. 후보와 환경
검사/격리 원칙은 V1 문서의2절을 따른다. 기존 checkout의 dirty/untracked를
건드리지 않는다. 실제 패키지 경로/버전을 기록하고 무작정 설치·업그레이드하지
않는다. 없으면 환경 blocker를 남긴다. 아래 fetch는 Git 읽기이지 Actions가 아니다.

```bash
set -euo pipefail
: "${REC_REPO:?confirmed existing rec_bianchi repository path}"
: "${REC_PY:?confirmed installed Python with numpy scipy sympy mpmath matplotlib}"
EXECUTION_SHA=9195f94bf308806ae6e9070f6175b500a1c2ef53
EXECUTION_TREE=98577a94604efff77c24b89ee3a56a99fd478f16
PR79_RESULT_SHA=0db9612b8c1fb2c6c8119f23138ff5efe54fcc06
mkdir -p "$HOME/research_runs"
RUN_ROOT=$(mktemp -d "$HOME/research_runs/rec_multibin_supplement_XXXXXXXX")
git -C "$REC_REPO" fetch --no-tags origin "$EXECUTION_SHA" "$PR79_RESULT_SHA" \
  >"$RUN_ROOT/fetch.stdout" 2>"$RUN_ROOT/fetch.stderr"
test "$(git -C "$REC_REPO" rev-parse "$EXECUTION_SHA^{tree}")" = "$EXECUTION_TREE"
git -C "$REC_REPO" show \
  "$PR79_RESULT_SHA:docs/research/rec_multi_bin_affinity_20260907/OBSERVED_RESULT.json" \
  >"$RUN_ROOT/PR79_OBSERVED_RESULT.json"
test "$(git hash-object "$RUN_ROOT/PR79_OBSERVED_RESULT.json")" = \
  a3244d115b7fc5f17b70a14af5aefc4c3b36aad3
git -C "$REC_REPO" worktree add --detach "$RUN_ROOT/source" "$EXECUTION_SHA"
export PYTHONDONTWRITEBYTECODE=1
set +e
"$REC_PY" -B "$RUN_ROOT/source/docs/research/rec_multi_bin_local_completion_20260907/run_local.py" \
  --expected-source "$EXECUTION_SHA" --python "$REC_PY" --only supplement \
  --out "$RUN_ROOT/evidence/attempt01" \
  >"$RUN_ROOT/wrapper.stdout.log" 2>"$RUN_ROOT/wrapper.stderr.log"
WRAPPER_RC=$?
printf '%s\n' "$WRAPPER_RC" >"$RUN_ROOT/WRAPPER_EXIT_CODE.txt"
set -e
printf 'run_root=%s\nwrapper_exit=%s\n' "$RUN_ROOT" "$WRAPPER_RC"
```

수학 실행 전에 V1의 compile() syntax 검사 방식을 적용하되 실제 파일 목록에
plot_supplement.py를 포함한다. 위 source에서 총6개 Python 파일(원래3개+
run_local/verify_nullspace/plot_supplement)을 compile하여 결과를 보존한다.
이 syntax 검사는 numerical PASS가 아니다. 검사 실패 시 source를 고정한
새 repair commit에서 수정·검증한다.

기본 --only all 또는 --only original은 사용하지 않는다. 새 검사가 실제로
기존 생산자의 결함을 드러내어 관련 원래 코드를 수정한 경우에만, 그 변경을
검출하는 PR79 최소 회귀검사를 로컬에서 추가할 수 있다. 이 경우 재실행의
원인, 수정 source SHA와 최초 증거를 명시하며 결과를 보고 oracle/허용오차를
바꾸지 않는다. 모든 [skip ci]/보호 조건을 유지한다.

## 4. 저장된 보충 결과의 그림

새4개 그룹과 actual subprocess exit0가 확인된 뒤에만 다음을 실행한다.
다음 실행은 CSV 후처리이며 기존7개나 새4개를 다시 실행하지 않는다.

```bash
set +e
MPLCONFIGDIR="$RUN_ROOT/matplotlib_cache" "$REC_PY" -B \
  "$RUN_ROOT/source/docs/research/rec_multi_bin_local_completion_20260907/plot_supplement.py" \
  --payload "$RUN_ROOT/evidence/attempt01/supplement/payload" \
  --out "$RUN_ROOT/figures/attempt01" \
  >"$RUN_ROOT/render.stdout.log" 2>"$RUN_ROOT/render.stderr.log"
RENDER_RC=$?
printf '%s\n' "$RENDER_RC" >"$RUN_ROOT/RENDER_EXIT_CODE.txt"
set -e
```

렌더링이 실패하면 수치 결과를 보존하고 해당 표시부만 수정한다. 수치 검사를
재실행해서 그림을 얻지 않는다. RENDER_RECEIPT와 원본 CSV/RESULT/PROCESS의
identity를 대조하고90mm/180mm 두 PNG를 실제로 연다. 겹침/잘림/축소 가독성을
확인한다. 0은 실제0에 표시하고 의미 없는 log floor를 넣지 않는다. 이 그림은
네 photon 좌표 방향의 binary64 오차 진단이며 grid convergence plot, 물리
시간진화 또는 80자리 구현 정확도가 아니다. 필요시 표시부만 미세 수리한다.
기존 PR79 두 원본 PNG의 시각검토를 완료했다고 표시하지 않는다.

## 5. 결과 수용 및 반환

새4개 TestID 전부 실제 PASS, failure/error/skip0, child 실제 returncode0,
보호 source 불변을 확인한다. 원래7개는 고정 Git readback의 재사용으로
분리한다. wrapper의 PASS_SELECTED_LOCAL_LANE_NOT_FULL_CLOSEOUT을 저장소
전체나 새11개 검사 실행 PASS로 바꾸지 않는다.

반환문에는 다음을 구분한다.

- 새4개 검사와16개 방향의 실제 값/원본 로그/PROCESS/RESULT/CSV.
- 네 보존량, count density 미분 누락, 우 kernel과 네 정상상태 접방향 결과.
- 재사용 원래7개 결과의 source/record-kind/byte수령 범위와 미회수 raw artifact.
- 새 CSV 그림 생성과 실제 시각검토, 역사적 PR79 PNG 미검토의 차이.
- 처음 관측한 실패, scope 내 자동 수리, 실제 candidate/source/result identity.

V1의 허용 Python 경로에 새 plot_supplement.py의 표시 수리를 추가한다.
그 밖의 source/과학적 의미/공식 dependency는 바꾸지 않는다. 같은 목표 안의
생산적인 여러 edit-test 반복은 허용하며, 수정 없는 동일 실패 재시도는 하지 않는다.
가능한 독립 read-only review 한 번은 허용하되 review-of-review는 하지 않는다.

자기 results/rec-multibin-local-<UTC-run-id> branch에 공개 가능한 결과와
RETURN_HANDOFF_KO.md를 non-force push한다. 모든 commit에는 [skip ci]를 넣는다.
Actions 실행·조회·다운로드·dispatch, merge/ready, 권한·가시성 변경은 금지한다.
Draft PR는 unskippable trigger가 없을 때만 생성할 수 있다. 그렇지 않으면
branch/commit과 고정 반환문서 링크로 충분하다. 공개 가능한 UTF-8 evidence를
제공하고 private BASS source나 workstation bundle을 게시하지 않는다.
과거 AUTHORING_STATUS 및 V1은 역사적 기록으로 보존한다.

최종 출력은 repository, result branch/PR(있을 때만), 실제 실행 commit/tree,
게시 commit/tree, immutable RETURN_HANDOFF URL, 실제 실행·그림·review·미완료
상태만 전달한다. 사용자 수동 ZIP 왕복이나 별도 작업 스레드는 기본 경로가 아니다.

다음 과학 연구는 공통 reference measure를 고정한 photon target-grid refinement다.
이번에는 그 새 연구를 시작하지 않는다. NO_PASS_REC_PHYSICAL_SPLIT,
physical_source_authenticated=false, provider_admitted=false를 유지한다.
