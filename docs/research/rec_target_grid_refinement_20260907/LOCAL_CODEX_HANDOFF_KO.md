# Local Codex — REC fixed-measure target-grid research

ROLE=LOCAL_CODEX
WORK_UNIT=REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE
GITHUB_ACTIONS=PROHIBITED
REPOSITORY=cosmosapjw-quantum/rec_bianchi

## 1. 이번 일과 고정 소스

이것은 PR79/80의 재실행이 아니다. 선행 보충은 PR80 댓글5567434296에서 이미
수용됐다. 주 대화는 새 target-grid 연구의 수식, 네 Python 파일, 여섯 검사와
그림 renderer까지 작성했다. 현재 main container/Python의 process-start
ClientError 때문에 새 numerical/syntax/plot 실행만 남았다. 계획을 다시 쓰거나
코드를 복제하지 말고 실제로 실행해 관측 결과를 반환한다.

    EXECUTION_SHA=b468767ff5aae92a7b0e8edc920952042cc3a8ed
    EXECUTION_TREE=7e2a47c8a09502fdb642713bd0c61f576fa1fa69
    DIRECT_PARENT=59dafbd34bc21b1b885c716b7b8cc899636bbd60
    PARENT_TREE=c0d6a862567e111cfe92a6fd5a3c30051180e38e

이 handoff는 위 source의 문서 전용 child다. DELIVERY_SHA는 이 파일의
immutable Git URL에서 읽는다. 실제 실행 source와 delivery/result child를
혼동하지 않는다. 새 shared branch:
research/rec-target-grid-refinement-20260907-r1

먼저 같은 디렉터리 RESEARCH_CONTRACT_KO.md 전체와 AUTHORING_STATUS.json을
읽는다. PR80 결과의 고정 source/claim을 재사용하고 오래된 ROOT handoff의
formal-runtime 또는 physical-face 작업을 시작하지 않는다. 원래7개/84방향,
보충4개/16방향, ModeB/C-history, BASS 자체, 전체 repository suite, 과거 Actions
artifact 수령은 모두 이번 실행이 아니다. 최신 result branch에서 같은 새
TASK/source/dependency 결과가 이미 있으면 재사용한다. 이를 확인하려고 Actions를
조회하거나 다운로드하지 않는다.

## 2. 허용 범위와 수리

새로운 격리 worktree/자기 결과 branch/범위 내 code repair/표적 시험/
non-force 결과 게시가 허용된다. 기존 checkout, shared branch, main, PR79/80,
다른 세션의 dirty/untracked 파일은 건드리지 않는다. 기존 src/tests/archive,
이전 연구 source/evidence, 원본 입력과 모든 workflow는 보호한다.

변경 가능한 code는 이 디렉터리의 refinement.py, test_refinement.py,
run_refinement.py, plot_refinement.py뿐이다. 결과와 수리 설명은
local_returns/<UTC-run-id>/ 아래 추가한다. 최초 AUTHORING_STATUS는 과거
미실행 기록으로 보존한다. 원본 로그·source SHA·실제 exit를 소급 고치지 않는다.

동일 목표/범위/불변식 안의 여러 edit -> test -> diagnose -> edit는 자율
수행한다. 첫 관측 실패를 남기고 실제 원인을 고친다. 편집 한 번만 하고
중단하지 않는다. 반대로 수정 없는 동일 실패를 반복하지 않는다. 물리
정의·원본 표·normalized rate·입력 함수/eta·perturbation·grid·측도를 PASS에
맞춰 바꾸거나 허용오차를 넓히거나 검사를 skip하지 않는다. 독립 oracle을
본체 출력으로 바꾸지 않는다. 계약의 수학적 반례가 발견되면 그 반례와 정확한
claim 범위를 남기고 억지로 통과시키지 않는다.

## 3. 환경과 최초 실행

이전 반환에서 사용한 설치 환경은 /home/cosmosapjw/cosmo_lab/.venv/bin/python,
Python3.12.3, numpy2.3.5/scipy1.18.0/sympy1.14.0/mpmath1.3.0/matplotlib3.11.0이다.
이 값은 과거 receipt이지 현재 환경을 미리 인증한 값이 아니다. 실제 경로와
버전을 읽고 재사용한다. 이번 핵심은 numpy/scipy/mpmath, 그림은 matplotlib가
필요하다. 신규 패키지 설치/업그레이드/라이선스 준비는 하지 않는다. 실제
누락이 있으면 import traceback을 environment blocker로 남긴다.

기존 repository 위치를 확인한다. 흔한 경로는 $HOME/Dropbox/bianchi/rec_bianchi다.
REC_REPO/REC_PY를 실제 경로로 설정하고 아래 명령을 사용한다. repo가 없을 때만
새 격리 경로에 clone한다. 기존 checkout에 reset/clean을 실행하지 않는다.

```bash
set -euo pipefail
: "${REC_REPO:?confirmed existing rec_bianchi repository}"
: "${REC_PY:?confirmed installed research Python executable}"
EXECUTION_SHA=b468767ff5aae92a7b0e8edc920952042cc3a8ed
EXECUTION_TREE=7e2a47c8a09502fdb642713bd0c61f576fa1fa69
mkdir -p "$HOME/research_runs"
RUN_ROOT=$(mktemp -d "$HOME/research_runs/rec_target_grid_XXXXXXXX")
git -C "$REC_REPO" fetch --no-tags origin "$EXECUTION_SHA" \
  >"$RUN_ROOT/fetch.stdout" 2>"$RUN_ROOT/fetch.stderr"
test "$(git -C "$REC_REPO" rev-parse "$EXECUTION_SHA^{tree}")" = "$EXECUTION_TREE"
git -C "$REC_REPO" worktree add --detach "$RUN_ROOT/source" "$EXECUTION_SHA"
export PYTHONDONTWRITEBYTECODE=1
set +e
"$REC_PY" -B - "$RUN_ROOT/source" <<'PY' >"$RUN_ROOT/syntax_environment.log" 2>&1
from pathlib import Path
import sys
root=Path(sys.argv[1]);folder=root/'docs/research/rec_target_grid_refinement_20260907'
for name in ('refinement.py','test_refinement.py','run_refinement.py','plot_refinement.py'):
    compile((folder/name).read_bytes(),name,'exec')
    print('syntax',name)
import numpy,scipy,mpmath,matplotlib
print('python',sys.executable,sys.version)
for module in (numpy,scipy,mpmath,matplotlib):
    print(module.__name__,module.__version__,module.__file__)
PY
SYNTAX_RC=$?
printf '%s\n' "$SYNTAX_RC" >"$RUN_ROOT/SYNTAX_EXIT_CODE.txt"
set -e
# On a nonzero syntax/import result, preserve it and diagnose before numerical execution.
test "$SYNTAX_RC" -eq 0
set +e
"$REC_PY" -B "$RUN_ROOT/source/docs/research/rec_target_grid_refinement_20260907/run_refinement.py" \
  --expected-source "$EXECUTION_SHA" --out "$RUN_ROOT/evidence/attempt01" \
  >"$RUN_ROOT/wrapper.stdout.log" 2>"$RUN_ROOT/wrapper.stderr.log"
WRAPPER_RC=$?
printf '%s\n' "$WRAPPER_RC" >"$RUN_ROOT/WRAPPER_EXIT_CODE.txt"
set -e
printf 'run_root=%s\nwrapper_exit=%s\n' "$RUN_ROOT" "$WRAPPER_RC"
```

과정 중 실패를 fail-closed claim으로 보존한다. source/tree·syntax·import·
process capture 실패는 numerical theorem failure와 구분한다. 실제 child
PROCESS와 RESULT의 source/tree/exit 및 여섯 TestID를 읽는다. 새 worker는
old test 모듈을 호출하지 않으며 한 번의 bounded 연구 suite를 실행한다.
최초 numerical 실패가 있으면 보존한 뒤 scope 내 repair를 새 committed
source에서 실행한다. 결과 자료를 쓰는 worktree와 실행용 clean worktree를
분리하고, 변경한 최소 dependency cone만 재검증한다.

## 4. 수치 결과에서 판정할 사항

예상 census는 테스트6그룹, weak576행, state18행, independent JVP16행,
bin2192행, atomic-table contrast288행이다. 이는 설계값이며 실제값과 대조한다.
PASS_BOUNDED_TARGET_GRID_DIAGNOSTIC은 새 진단 계약의 통과이지 실제 convergence
order나 물리 solver PASS가 아니다.

특히 다음을 실제 CSV 값으로 설명한다.

1. psi=1,u 보존 대조와 psi=u^2,u^4의 signed read/scatter/cross error.
2. chi의 도출된 O(h^2) envelope와 실제 finite-grid error, 해당 JVP.
3. 같은 상태와 같은 direction에서 atomic base/hires reference difference와
   target error difference가 분리되는지.
4. fixed mu의 state quadrature와 weak source의 measure-blindness 음성 대조.
5. affine/odd 상세균형 control이0에 가까운 것을 convergence evidence로
   잘못 세지 않는지. log-control에는 chi의 du 기반 기울기를 강제하지 않는다.

curved case의 psi=u^2,u^4에서 grid별 abs(error)/h^2와 abs(jvp_error)/h^2를
기록한다. 값이 기존 roundoff 비교척도보다 충분히 클 때에만
p=ln(|e_coarse/e_fine|)/ln(h_coarse/h_fine)을 표기한다. 0 또는 roundoff 이하이면
order를 null/ROUNDING_LIMITED로 기록한다. 상태/eta를 다시 선택하거나 점을
제외해 slope2를 얻지 않는다. 관측이 비단조·상쇄·아직 점근영역 아님을
보이면 그대로 기록한다. table-gap plateau는 atomic 참값 오차 인증이 아니라
두 fixed tables 사이의 차이임을 명시한다. 원래 source가 정확히 고정돼 있어도
격자/환경별 출력의 byte equality를 요구하지 않는다.

## 5. 그림은 저장 데이터에서만 생성

새 suite와 실제 process exit가 수용 가능할 때 아래를 실행한다.

```bash
set +e
MPLCONFIGDIR="$RUN_ROOT/matplotlib_cache" "$REC_PY" -B \
  "$RUN_ROOT/source/docs/research/rec_target_grid_refinement_20260907/plot_refinement.py" \
  --run "$RUN_ROOT/evidence/attempt01" --out "$RUN_ROOT/figures/attempt01" \
  >"$RUN_ROOT/render.stdout.log" 2>"$RUN_ROOT/render.stderr.log"
RENDER_RC=$?
printf '%s\n' "$RENDER_RC" >"$RUN_ROOT/RENDER_EXIT_CODE.txt"
set -e
```

네 내용(weak error, weak JVP error, read/scatter/cross budget, atomic table gap)의
90/180mm PNG 총8개가 계획돼 있다. 실제 모든 그림을 열어 입력 CSV와 대조하고
부호/0/축/단위/legend·축소 가독성을 검토한다. symlog 선형영역±1e-14는
표시 변환이며 data floor가 아니다. 겹침·잘림은 표시부만 수리하고 수치
자료가 불변이면 과학 suite를 재실행하지 않는다. 보여준 범위 밖이나
C_i 점별 수렴·Planck IR·시간진화의 결과로 확대하지 않는다. renderer receipt의
작성 당시 NOT_PERFORMED는 후속 VISUAL_REVIEW를 별도로 추가해 갱신한다.

독립 read-only review는 한 번으로 제한하며 물리·수학과 구현·출처를 함께
본다. 그 reviewer의 actual scope/한계를 보존한다. review-of-review, 전체
solver census나 다른 repo 감사는 새로 시작하지 않는다.

## 6. Git으로 반환

결과 branch 예시: results/rec-target-grid-<UTC-run-id>.
모든 새 commit에 [skip ci], non-force push를 적용한다. Actions 실행·조회·
다운로드·dispatch, workflow 수정, force-push, main/기존 branch mutation,
merge/ready, Jira status/dependency 수정은 하지 않는다. 공개 가능한 결과만
게시하고 private BASS source 또는 전체 workstation 자료를 공개하지 않는다.

원본 PROCESS/RESULT/unittest/stdout/stderr/CSV/PNG, 독립·시각검토와 첫 실패,
repair diff와 actual source identities를 함께 보존한다. 원본 stdout 공백을
trim하지 않는다. 필요하면 기존 반환 방식대로 가역 UTF-8 JSON 포장과
복원 바이트/원본 manifest 비교를 별도 기록한다. public packaging과 수치
source repair를 분리한다. 실패해도 exact blocker와 완료 부분을 durable
return으로 남긴다. source 수정이 없으면 빈 SOURCE_REPAIR.diff로 표시한다.

모든 source/figure 결과를 새로 쓴 코드라고 재포장하지 않는다. 실행 commit,
renderer commit, 결과 commit, return-handoff child를 분리한다. 자기 result
branch의 remote commit/tree와 공개 파일을 readback하고
RETURN_HANDOFF_KO.md의 immutable Git URL을 최종 응답으로 전달한다.
사용자 수동 ZIP 왕복은 기본 경로가 아니다. Draft PR는 필요시 base/default
branch의 unskippable trigger가 없음을 확인한 뒤에만 생성한다. branch와
고정 반환 링크만으로도 충분하다.

다음에 무엇을 추가할지는 이 연구의 실제 결과를 주 대화가 수용한 뒤 정한다.
즉시 더 큰 grid sweep, 신규 physical measure/provider, 시간 적분이나
전역 refactor를 시작하지 않는다.

NO_PASS_REC_PHYSICAL_SPLIT
physical_source_authenticated=false
provider_admitted=false
