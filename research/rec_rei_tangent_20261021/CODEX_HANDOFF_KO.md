# REC → REI tangent: NCP 실행 handoff

이 문서는 REC PR118의 새 세 interior case를 NCP에서 실행하기 위한 인계다.
최종 게시 receipt가 나온 뒤 아래 HEAD·tree placeholder를 실제 40자리 값으로 채워 사용한다.

- PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/118
- branch: `research/rec-rei-tangent-20261021`
- stacked base: REC PR117, `research/rec-rei-trajectory63-20261021`
- project: `research/rec_rei_tangent_20261021`
- physical source: REI PR147 `3b85dedce84d37b3e165da00685a8a984950aafe`
- 최종 runnable REC HEAD·tree: **후속 최종 게시 receipt에서 고정**. Stage A나 임의 최신 HEAD를 대신 넣지 않는다.

## 현재 완료 범위와 새 실행의 의미

Python 구현은 준비됐다. 이 tangent 단위에는 C++/Rust 빌드 단계가 없다.
기존 Python 환경에서 NumPy·SciPy·Matplotlib을 사용한다. 새 네트워크 설치를 기본 단계로 넣지 않는다.

이번 샌드박스에서 새로 실행한 ODE는 synthetic interior seed의
`x∈[0,1e-4]`, 출력 3개인 parent IVP 1회와 augmented IVP 1회, **총 2회**다.
이 tangent 단위의 **NCP 실행은 0**이며, 아래 세 case의 전체
`z=20→2`, 153-node augmented 계산은 **READY_NOT_SUBMITTED**다.
앞선 REI215 native NCP 반환은 별도의 warm owner 근거이며 이 tangent 검증으로 전용하지 않는다.

기존 175-case parameter sweep·`z20→2` trajectory plot은 REC PR117에서 재사용한다.
새 실행은 초기 signed seed에 대한 **세 열의 미분을 동반하는 160-state IVP**다.
저장 state 위에서 계산한 local partial이나 tiny wiring 결과와 전체 구간 초기값 민감도를 구별한다.

| case ID | 초기 `S_F` | 초기 `P_m,F` | 초기 `P_r,F` |
|---|---:|---:|---:|
| `interior_1` | 0.002 | 0.00007 | −0.0002 |
| `interior_2` | 0.006 | −0.00007 | 0.0002 |
| `interior_3` | 0.015 | 0.0002 | −0.0007 |

위 세 좌표는 완료된 pilot 격자에 없는 새 interior 좌표다.
warm729, REC175, unified237, HH1231, HE29, REC U4B와 기존 long prefix/tail을 다시 enqueue하지 않는다.
실행 입력은 `inputs/NCP_TANGENT_CASES.json`의 세 case로 고정한다.

물리 모형은 non-tilted LRS Bianchi I, finite L8, 40-state,
mass fraction 0.1, `m/T_ref=30`, `24×12 Gauss3`, `ne_source=None`이다.
세 tangent는 `(S_F,i, P_m,F,i, P_r,F,i)`를 미분하며,
matter amplitude 직접항 `F_A A_p`와 초기상태 미분을 함께 포함한다.

`sigma=diag(-s,-s,2s)`, `pi_A=diag(-p_A,-p_A,2p_A)`,
`kappa_t=8πG/c²`를 사용한다.
`S_F=√6 s/H`, `P_A,F=√6 kappa_t p_A/H²`는 signed 좌표다.
matter·radiation을 signed 상태로 유지하고 total을 먼저 더한 다음 norm을 취한다.
half-contraction 좌표는 Frobenius 좌표를 `√2`로 나눈 값이다.

## 1. 기존 NCP 실행 환경 사용

사용자가 이미 승인한 NCP Codex/SSH 환경에서 이어서 수행한다. 이 ChatGPT
샌드박스의 실제 NCP 접속·실행은 0이다. 기존 인증 설정을 사용하고
서버 주소나 키 경로를 이 공개 연구 문서에 추가하지 않는다.

## 2. 최종 commit을 새 worktree에 고정

기존 실행 중인 checkout을 변경하지 않는다. 최종 receipt의 HEAD와 tree를 채운 뒤
새 worktree를 만든다. 기존 repository가 없을 때만 새 경로에 clone한다.

```bash
set -euo pipefail

REC_TANGENT_HEAD='<FINAL_REC_HEAD_40_HEX_FROM_RECEIPT>'
REC_TANGENT_TREE='<FINAL_REC_TREE_40_HEX_FROM_RECEIPT>'
REC_TANGENT_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REC_TANGENT_REPO=/root/rec_bianchi

if ! [[ "$REC_TANGENT_HEAD" =~ ^[0-9a-f]{40}$ && "$REC_TANGENT_TREE" =~ ^[0-9a-f]{40}$ ]]; then
    printf '%s\n' '최종 게시 receipt의 HEAD와 tree를 먼저 채워야 한다.'
    exit 2
fi

if ! git -C "$REC_TANGENT_REPO" rev-parse --git-dir >/dev/null 2>&1; then
    REC_TANGENT_REPO="/root/rec_bianchi_tangent_clone_$REC_TANGENT_STAMP"
    git clone --no-checkout https://github.com/cosmosapjw-quantum/rec_bianchi.git "$REC_TANGENT_REPO"
fi

git -C "$REC_TANGENT_REPO" fetch origin research/rec-rei-tangent-20261021
git -C "$REC_TANGENT_REPO" cat-file -e "$REC_TANGENT_HEAD^{commit}"

REC_TANGENT_WORKTREE="/root/worktrees/rec_tangent_${REC_TANGENT_HEAD:0:12}_$REC_TANGENT_STAMP"
mkdir -p /root/worktrees
git -C "$REC_TANGENT_REPO" worktree add --detach "$REC_TANGENT_WORKTREE" "$REC_TANGENT_HEAD"

test "$(git -C "$REC_TANGENT_WORKTREE" rev-parse HEAD)" = "$REC_TANGENT_HEAD"
test "$(git -C "$REC_TANGENT_WORKTREE" rev-parse HEAD^{tree})" = "$REC_TANGENT_TREE"

REC_TANGENT_PROJECT="$REC_TANGENT_WORKTREE/research/rec_rei_tangent_20261021"
REC_TANGENT_OUTPUT="/root/rec_tangent_runs/interior3_${REC_TANGENT_HEAD:0:12}_$REC_TANGENT_STAMP"
REC_TANGENT_FIGURES="${REC_TANGENT_OUTPUT}_figures"
```

`reset --hard`, force push, 기존 worktree 삭제, 다른 작업의 reservation 수정은 필요하지 않다.
후속 receipt와 fetch 결과가 달라졌다면 branch를 무조건 따라가지 않고,
최종 receipt가 지정한 commit의 provenance부터 확인한다.

## 3. 기존 Python 환경과 실행 자원 설정

NCP에서 이미 사용하는 Python 환경을 선택한다. 다음 import 확인은 ODE를 실행하지 않는다.

```bash
REC_TANGENT_PY=python3

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1

"$REC_TANGENT_PY" - <<'PY'
import sys
import numpy
import scipy
import matplotlib
print({
    "python": sys.version,
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
    "matplotlib": matplotlib.__version__,
})
PY

REC_TANGENT_LEASE_DIR=/tmp/bianchi_resource_leases
REC_TANGENT_RESERVED_CPUS=0
REC_TANGENT_RESERVED_MEMORY_GIB=0
```

0은 이 실행에서 **추가로 선언할 외부 예약이 없을 때**의 값이다.
공유 ledger에 없는 별도 CPU/RAM 예약을 알고 있다면 실제 값을 넣는다.
동일 예약을 recognized live lease와 CLI 양쪽에 중복 계상하지 않는다.

실행기는 매 batch 직전에 실제 CPU idle·affinity/cgroup CPU·available RAM을 읽고,
live cooperative lease와 명시적 예약을 반영한다.
공유 schema는 `rec_bianchi.cooperative_lease.v1`이며
`host, pid, proc_start_tick, slots, memory_bytes`를 사용한다.
PID와 시작 tick이 같은 live lease만 차감하고,
unknown·stale·다른 host record를 삭제하지 않는다.

`--max-workers 63`은 NCP 목표 상한이다. 이번 manifest의 실제 최대 동시 case는 **3개**다.
다른 Codex 세션이 있다는 이유만으로 전역 중지하지 않는다.
가용 CPU/RAM과 예약 내에서 입장 가능한 case를 실행한다.
resource admission이 0이면 `DEFERRED_RESOURCES`로 남고, peer lease를 강제로 지우지 않는다.

## 4. 반드시 같은 output namespace에서 plan을 먼저 확인

```bash
"$REC_TANGENT_PY" "$REC_TANGENT_PROJECT/code/ncp_tangent.py" \
    --output "$REC_TANGENT_OUTPUT" \
    --profile ncp \
    --max-workers 63 \
    --lease-dir "$REC_TANGENT_LEASE_DIR" \
    --reserved-cpus "$REC_TANGENT_RESERVED_CPUS" \
    --reserved-memory-gib "$REC_TANGENT_RESERVED_MEMORY_GIB"
```

이 호출에는 `--execute`가 없으므로 새 ODE를 실행하지 않는다.
새 output이면 독립 `RUN_MANIFEST.json`을 create-only로 만든다.
`case_states`에 위 세 case만 나타나는지 확인한다.

예상 신규 상태는 `PLAN_ONLY`와 세 `pending`이다.
기존 결과가 있으면 다음 상태를 그대로 보존한다.

| 상태 | 의미·행동 |
|---|---|
| `complete_reused` | source/code/input identity와 NPZ SHA가 맞는 완료 결과. 재실행하지 않는다. |
| `preserved_failed` | 기존 실패 기록. 자동 재시도하지 않는다. |
| `preserved_attempt` | 완료 receipt가 없는 이전 attempt. 원인 확인 전 재실행하지 않는다. |
| `preserved_claim` | 기존 claim. 다른 실행이나 중단 기록을 보존한다. |
| namespace/identity mismatch | 기존 파일을 덮어쓰지 않는다. identity 차이를 조사하고 새 계약·출력 여부를 결정한다. |

**`NO_PENDING_WORK`나 process exit 0만으로 모든 case가 성공했다고 결론 내리지 않는다.**
이 상태에는 보존된 실패·미완료 attempt가 포함될 수 있다.
완료 판정은 각 `RESULT.json`의 integration receipt와 payload hash에 근거한다.

## 5. 계획과 동일한 명령에 --execute 추가

```bash
REC_TANGENT_RUN_EXIT=0
"$REC_TANGENT_PY" "$REC_TANGENT_PROJECT/code/ncp_tangent.py" \
    --output "$REC_TANGENT_OUTPUT" \
    --execute \
    --profile ncp \
    --max-workers 63 \
    --lease-dir "$REC_TANGENT_LEASE_DIR" \
    --reserved-cpus "$REC_TANGENT_RESERVED_CPUS" \
    --reserved-memory-gib "$REC_TANGENT_RESERVED_MEMORY_GIB" \
    || REC_TANGENT_RUN_EXIT=$?

printf 'tangent runner exit: %s\n' "$REC_TANGENT_RUN_EXIT"
```

고정 실행 계약은 DOP853, `rtol=3e-11`, `atol=3e-13`,
case당 120초 cooperative RHS deadline, controller 900초의 batch admission 기준,
case당 예약 0.5 GiB다. 이 값은 OS hard-kill timeout이 아니다.
각 worker는 spawn 방식, numerical threads 1, nice 최소 10으로 실행된다.
실행기에는 source/code가 실행 전후 동일한지 검사하는 경로가 있다.

출력은 다음 형식이다.

```text
RUN_MANIFEST.json
interior_1/.claim/
interior_1/ATTEMPT.json
interior_1/tangent.npz
interior_1/RESULT.json
interior_2/...
interior_3/...
DISPATCH_<uuid>.json
```

실패하면 `FAILED.json` 및 이미 생성된 원자료를 보존한다.
실패와 미완료 attempt를 지워서 자동 재입장시키지 않는다.
수정이 필요하면 정확한 실패 원인·변경한 code identity·새 실행 범위를 별도 연구 단위로 기록한다.
정상 완료 case는 다음 호출에서 `complete_reused`가 되며 새 ODE가 발생하지 않는다.

`new_jobs`는 worker callable 제출 수다. 실제 ODE 수는 case별 integration receipt에서 읽는다.
OS process exit code가 수집되지 않은 경우에는 `null`이고,
실제 callable 반환 상태인 `task_exit_code`와 구별되어 있다.

## 6. 실제 완료 receipt만 사용해 그림 생성

완료 case가 하나 이상일 때 다음을 실행한다.
미완료 case가 있으면 완료한 case 수를 그대로 보고하고 세 case 완료로 바꾸지 않는다.

```bash
"$REC_TANGENT_PY" "$REC_TANGENT_PROJECT/code/plot_tangent.py" \
    --ncp-output "$REC_TANGENT_OUTPUT" \
    --output "$REC_TANGENT_FIGURES"
```

`plot_tangent.py`는 solver를 import하거나 ODE를 실행하지 않는다.
NCP mode는 다음 실제 schema를 함께 검사한다.

1. `RUN_MANIFEST.json`: `rec_bianchi.tangent_run.v1` 및 자체 identity hash.
2. case wrapper: `rec_bianchi.tangent_result.v1`, `status=COMPLETE`,
   `task_exit_code=0`, 동일 `source_code_identity`.
3. nested integration: `rec.tangent.execution.v1`, `status=COMPLETED`,
   동일 PR147 source commit, 모든 `checks=true`.
4. `tangent.npz`: wrapper가 선언한 SHA256, seed·epoch·array shape,
   시간 순서, redshift 사상, signed sector sum.

각 완료 case에 다음 두 파일을 만든다.

```text
ncp_response_interior_1.png
ncp_response_interior_1.pdf
```

한 그림의 네 panel은 signed observables와 세 초기 seed에 대한
`∂O/∂theta_j`다. 반환 tangent는 **unscaled derivative**다.
적분 내부에서 사용한 seed scales `[0.1,0.0003,0.001]`와 혼동하지 않는다.

새 그림 receipt는 기본적으로
`$REC_TANGENT_FIGURES/PLOT_BUILD.json`에 만들어지고,
schema는 `rec.tangent.plot_build.v1`,
mode는 `completed_augmented_cases`,
첫 상태는 `BUILT_PENDING_VISUAL_REVIEW`다.
실제 PNG를 열어 축·범례·부호·사례 수를 확인한 뒤 시각 검토 결과를 따로 기록한다.
출력 PNG/PDF/receipt가 이미 존재하면 덮어쓰지 않고 중단하므로 새 figure directory를 사용한다.

tiny wiring의 `PASS_SCOPED_WIRING` receipt는 full NCP `COMPLETED`로 바꾸지 않는다.
`observables_signed`는 `[S_F,P_m,F,P_r,F,P_m,F+P_r,F]`이고,
`observable_tangent_signed`의 shape는 `(epochs,4,3)`다.
norm은 signed total을 만든 뒤 마지막에 취한다.

## 7. 반환·보존할 자료

새 full-window 결과를 반환할 때 다음을 함께 보존·게시한다.

- 실제 checkout HEAD·tree와 `RUN_MANIFEST.json`.
- `inputs/NCP_TANGENT_CASES.json`의 SHA256 및 source/code identity.
- 모든 case의 `ATTEMPT.json`, `RESULT.json` 또는 `FAILED.json`,
  생성된 `tangent.npz`와 그 SHA256.
- controller stdout·실제 exit와 `DISPATCH_<uuid>.json`.
- 실제 자원 관측·peer reservation 수·worker admission·worker wall/CPU/RSS.
- 완성된 PNG/PDF, `PLOT_BUILD.json`, 직접 시각 검토 결과.
- 각 case의 `complete`, `complete_reused`, `failed`, `deferred` 상태를 구별한
  새 DAG delta와 create-only backup/provider ACK.

source/code identity가 같고 완료 payload hash가 맞는 계산은 재사용한다.
이전 실패·공유 예약·CPU debit을 재설정하지 않는다.
작은 오차나 solver success를 전체 해의 오차 인증으로 해석하지 않는다.

다음 상태는 이 실행 뒤에도 근거 없이 승격하지 않는다.

```text
Physical HOLD
global convergence NOT_RUN
production NOT_APPROVED
REC U5 HOLD_9_FAIL / HOLD_8_FAIL
CLOSED_HOLD_NOT_RESET
REI_activation=false
```

원래 완료된 REC PR117 pilot과 새 초기값 민감도 결과는 출처를 분리해서 인계한다.
이 새 tangent 모형은 고정 collisionless finite owner이며 full cold EoR,
angular/truncation convergence 또는 production 승인을 의미하지 않는다.
