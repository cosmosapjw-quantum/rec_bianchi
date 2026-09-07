# LOCAL CODEX HANDOFF — REC 다중 bin 연구의 실제 로컬 완결

ROLE=LOCAL_CODEX
WORK_UNIT=REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH
SLICE=LOCAL_NULLSPACE_COMPLETION
REPOSITORY=cosmosapjw-quantum/rec_bianchi
GITHUB_ACTIONS=PROHIBITED

## 0. 목적과 고정 identity

주 대화가 PR79를 읽고 네 보존량, 정상상태 매개화, count density chain 및
추가 photon-axis 검사를 작성했다. container/Python은 시작 전 ClientError여서
새 source는 아직 미실행이다. 원본을 복제하거나 계획만 반환하지 말고 아래
고정 소스를 실제 실행하여, 같은 범위의 결함을 수정·검증하고 Git으로 반환하라.

    EXECUTION_SHA=799bdda907990d13e3c61b2580f6d2855a007c42
    EXECUTION_TREE=fa9db694dfac527f8d6c7779339e1494f1118e87
    DIRECT_PARENT=2e3b73972ee298d44efdfb10016e314f58b0bada
    PARENT_TREE=471442ce757fde701340729cd1abde281fd0db01

이 문서를 담은 delivery commit은 위 source의 문서 전용 child다.
DELIVERY_SHA는 전달받은 이 문서의 immutable blob URL에서 읽는다.
공유 branch는 `research/rec-multi-bin-local-completion-20260907-r1`이다.
최초 수치 실행은 가변 branch가 아니라 위 EXECUTION_SHA에서 수행한다.
이 문서, `SCIENCE_COMPLETION_KO.md`, 기존 PR79 `CONTRACT_KO.md`를 읽는다.
옛 ROOT/HANDOFF_PROMPT.md의 REC-NEXT-03 formal 작업을 재개하지 않는다.

## 1. 승인과 보호 경계

허용: 격리 worktree/자기 결과 branch, 아래 범위의 code repair, 직접 관련
검증, 공개 가능한 결과의 non-force push. 기존 checkout의 dirty/untracked,
인계 branch, PR79 branch, main과 타 세션의 branch는 변경하지 않는다.

수리가 필요한 경우 허용 Python 경로는 다음뿐이다.

    docs/research/rec_multi_bin_affinity_20260907/study.py
    docs/research/rec_multi_bin_affinity_20260907/test_study.py
    docs/research/rec_multi_bin_affinity_20260907/run_study.py
    docs/research/rec_multi_bin_local_completion_20260907/verify_nullspace.py
    docs/research/rec_multi_bin_local_completion_20260907/run_local.py

새 결과/반환문서는 후자의 디렉터리 아래 `local_returns/<UTC-run-id>/`에 둔다.
AUTHORING_STATUS.json은 주 대화 작성 시점의 미실행 기록으로 보존하며,
나중의 실행 결과를 소급 적용하지 않는다.

보호: src, 최상위 tests, archive, 원본 표·정규화·B/mu·정의·단위·부호,
기존 입력/결과와 모든 workflow. 원래 7개와 새 4개 TestID의 검증 의미를
보존한다. 허용오차 확대, skip, 기대값의 구현 출력 대체, 원본 paired/COM
API를 자체 공식으로 바꾸는 수리는 금지한다.

한 repair cycle은 편집 한 번이 아니다. 같은 objective/scope/invariants
안에서 evidence-driven edit -> test -> diagnose -> edit를 자율적으로
수행한다. 수정 없이 같은 실패를 반복하지 않는다. 보호된 물리 의미나
scope를 바꿔야 하면 원래 증거와 정확한 blocker를 남기고 그 변경은 하지 않는다.

merge/ready, force-push/rebase, 권한·가시성 변경, 타 저장소 source,
물리 source/provider 승격, 실제 BASS evolution은 승인되지 않았다.
최종 과학적 수용과 Atlassian 동기화는 주 대화가 맡는다.

## 2. 중복 실행 방지와 환경

먼저 PR79 및 관련 결과 branch의 최신 댓글/반환문서를 읽고 같은
source/dependency cone의 완료된 Git 또는 로컬 결과가 있는지 확인한다.
유효하면 재사용한다. 이 확인에 Actions 조회·다운로드·실행·재실행·dispatch를
사용하지 않는다. 현재 사용할 증거가 없다는 것과 과거 실행 자체의 부재는
구분한다.

기존 Python 3.12 계열 환경에서 numpy, scipy, sympy, mpmath, matplotlib를
확인한다. 후보는 $HOME/cosmo_lab/.venv/bin/python, 프로젝트의 기존 외부
venv, 현재 python3다. 실제 경로와 버전을 기록하며 패키지를 무작정 설치·
업그레이드하지 않는다. 필수 패키지가 없으면 import traceback과 환경
blocker를 보존한다. 무관한 Wolfram/Lean/Rocq 설치나 재라이선스는 하지 않는다.

최초 syntax 검사는 compile()로 수행하여 worktree 내 캐시를 만들지 않는다.
syntax 검사와 실제 수치 검증을 별도로 기록한다.

## 3. 최초 실행

기존 repo 경로를 확인한다. 흔한 경로는 $HOME/Dropbox/bianchi/rec_bianchi다.
그 checkout을 reset/clean/checkout하지 않는다. 아래 REC_REPO와 REC_PY는
현장에서 확인한 실제 경로로 설정한다. 이미 알려진 정보를 사용자에게
다시 묻지 않는다. repo가 없을 때만 별도 새 경로에 정상 clone한다.

```bash
set -euo pipefail
: "${REC_REPO:?confirmed existing rec_bianchi repository path}"
: "${REC_PY:?confirmed installed Python executable with research dependencies}"
EXECUTION_SHA=799bdda907990d13e3c61b2580f6d2855a007c42
EXECUTION_TREE=fa9db694dfac527f8d6c7779339e1494f1118e87
mkdir -p "$HOME/research_runs"
RUN_ROOT=$(mktemp -d "$HOME/research_runs/rec_multibin_local_XXXXXXXX")
git -C "$REC_REPO" fetch --no-tags origin "$EXECUTION_SHA" \
  >"$RUN_ROOT/fetch.stdout" 2>"$RUN_ROOT/fetch.stderr"
test "$(git -C "$REC_REPO" rev-parse "$EXECUTION_SHA^{tree}")" = "$EXECUTION_TREE"
git -C "$REC_REPO" worktree add --detach "$RUN_ROOT/source" "$EXECUTION_SHA"
export PYTHONDONTWRITEBYTECODE=1
"$REC_PY" -B - "$RUN_ROOT/source" <<'PY' >"$RUN_ROOT/syntax_environment.log" 2>&1
from pathlib import Path
import sys
root=Path(sys.argv[1])
paths=[
 'docs/research/rec_multi_bin_affinity_20260907/study.py',
 'docs/research/rec_multi_bin_affinity_20260907/test_study.py',
 'docs/research/rec_multi_bin_affinity_20260907/run_study.py',
 'docs/research/rec_multi_bin_local_completion_20260907/verify_nullspace.py',
 'docs/research/rec_multi_bin_local_completion_20260907/run_local.py',
]
for name in paths:
    compile((root/name).read_bytes(),name,'exec')
    print('syntax',name)
import numpy,scipy,sympy,mpmath,matplotlib
print('python',sys.executable,sys.version)
for module in (numpy,scipy,sympy,mpmath,matplotlib):
    print(module.__name__,module.__version__,module.__file__)
PY
set +e
"$REC_PY" -B "$RUN_ROOT/source/docs/research/rec_multi_bin_local_completion_20260907/run_local.py" \
  --expected-source "$EXECUTION_SHA" --python "$REC_PY" \
  --out "$RUN_ROOT/evidence/attempt01" \
  >"$RUN_ROOT/wrapper.stdout.log" 2>"$RUN_ROOT/wrapper.stderr.log"
WRAPPER_RC=$?
printf '%s\n' "$WRAPPER_RC" >"$RUN_ROOT/WRAPPER_EXIT_CODE.txt"
set -e
printf 'run_root=%s\nwrapper_exit=%s\n' "$RUN_ROOT" "$WRAPPER_RC"
```

source/tree 불일치, syntax/import/preflight failure는 수치 FAIL이 아니다.
중간에서 중단되더라도 원본 로그를 보존하고, 미생성 RESULT를 성공값으로
보충하지 않는다. 원래 7개와 보충 4개 그룹은 별도 subprocess다.
각각 actual returncode, stdout/stderr, RESULT와 exact TestID outcome을
확인한다. wrapper 숫자만으로 전체 검증 성공을 판단하지 않는다.

## 4. 완료 lane 재사용과 자동 수리

기존 7개 그룹의 유효 근거가 같은 dependency bytes에서 이미 보존됐으면
`--only supplement`로 남은 lane만 실행할 수 있다.
PASS_SELECTED_LOCAL_LANE_NOT_FULL_CLOSEOUT은 두 lane 전체 PASS가 아니다.
재사용 근거의 source/result identity와 새 supplement source/result를 분리해
RETURN_HANDOFF에서 수용 근거를 설명한다. 과거 PROCESS나 RESULT를 고쳐
둘 다 새로 실행한 것처럼 표시하지 않는다.

실패가 있으면 원본 로그·source SHA를 보존한다. 수리는 DELIVERY_SHA에서
시작한 별도 자기 결과 branch/worktree에 적용하고, 변경 source를 commit한
뒤 새 output 디렉터리에서 실행한다. commit 메시지에는 항상 [skip ci]를 넣는다.
변경한 behavior의 최소 dependency cone만 재검증한다. 필요한 original/
supplement lane은 재실행하되 PR77/78/완료 ModeB/원본 C-history/전체 repository
시험을 반복하지 않는다. 한정된 source 수리의 최초 실패와 후속 결과는 모두
보존한다. 결과 문서 child를 실제 tested commit으로 쓰지 않는다.

## 5. 수용 조건과 그림

최대 수용은 제조 고정-grid 다중-bin affinity/JVP 및 네 kernel 보존량이다.
원래 7개와 새 4개 그룹의 유효 근거, failures/errors/skips0, 실제 child exit0,
보호 source 불변을 확인한다. 기존 84개와 추가16개는 총100개 방향 사례이며
100개의 독립 unittest 또는 전 정의역 검증이 아니다.

반환할 실제 값: 두 표의 bin별 Delta/총 nodal entropy/read-proxy/공통
population 반례와 raw/normalized 구분; 고정밀 및 step-refinement 차이;
source/JVP/보존 잔차와 척도; 네 좌영벡터와 energy 종속식; 실제 bin3개의
exact rank witness; W^-1 L^T 우 kernel과 비열적 정상상태 네 접방향;
beta=mu/nH 미분 누락 검출 및 추가 photon축16개 비교.

기존 runner의 bin_affinity.png와 aggregate_entropy.png를 실제로 열어
수치 CSV, 축/단위/범례와 대조한다. 그림 생성 실패가 수치 exit0와 공존할
수 있으므로 plot_generated/plot_error/시각검토를 별도로 보고한다.
실제0을 설명 없는 양의 로그 floor로 바꾸지 않는다. 곡선은 고정 상태의
P/Q aggregate 식이며 시간 적분이 아니다. 90mm/180mm 축소에서 읽기 어려우면
표시부만 수정·재렌더링하고, 수치 불변을 확인한 경우 그림 metadata 때문에
수치 검사를 반복하지 않는다. 그림을 못 열면 VISUAL_AUDIT_NOT_PERFORMED다.

가능한 독립 read-only review는 한 번으로 제한하되 물리·수학과 구현·출처를
모두 포함한다. review를 다시 감사하는 메타루프는 하지 않는다. 미완료나
환경 실패도 정직한 durable return으로 게시할 수 있다.

## 6. Git 반환과 Actions 금지

수동 ZIP 재업로드 대신 Git 링크로 반환한다. 자기 결과 branch 예시는
results/rec-multibin-local-<UTC-run-id>다. 공개 가능한 PROCESS/RESULT/
LOCAL_RETURN, 원본 stdout/stderr, CSV/PNG, source diff 및 RETURN_HANDOFF_KO.md를
UTF-8/Git 경로로 읽을 수 있게 게시한다. raw log 공백을 덮어쓰지 않는다.
필요하면 JSON content 문자열로 가역 보존하고 원본 identity를 기록한다.
공개 사본의 host/secret 치환은 명시하고 원본과 byte identity를 주장하지 않는다.
비공개 BASS source/로그/전체 workstation bundle은 공개하지 않는다.

모든 새 commit에 [skip ci]를 넣고 non-force push한다. Actions workflow를
수정하거나 실행·재실행·dispatch하지 않는다. push/pull_request skip은 CI
성공이 아니다. 결과 Draft PR를 만들기 전 default/base branch에
pull_request_target 등의 unskippable trigger가 있는지 확인한다. 있다면
PR를 만들지 말고 exact branch/commit/blob 링크로 반환한다. 자동화 설정이나
권한을 임의 변경하지 않는다. 새 branch만으로도 반환할 수 있다.

게시 후 remote commit/tree, 보호 branch, 변경 경로와 실제 source 내용을
대조한다. publication failure와 수치 failure를 구분한다. 결과는 다음만
간단히 출력하면 된다.

    repository / result branch / Draft PR(생성했을 때만)
    actual execution commit(s)/tree(s)
    result publication commit/tree
    immutable RETURN_HANDOFF_KO.md URL
    actual test/process/plot/review status
    first failure and repairs, or exact remaining blocker

전체 프롬프트나 모든 로그를 채팅에 다시 붙이지 않는다. 주 대화가 고정
링크의 실제 증거를 읽고 수용한 뒤 다음 과학적 결정을 내린다.

성공해도 NO_PASS_REC_PHYSICAL_SPLIT, physical_source_authenticated=false,
provider_admitted=false를 유지한다. merge/ready와 공식 Jira dependency를
변경하지 않는다.
