# rec_bianchi ODE/DAE 네 연구 루프 통합 최종 보고서

- 기준일: 2026-08-23
- 구현 기준 HEAD: `5a09f3797210284f83a1a1adb0e0092d1ac48475`
- 기준 tree: `4002915ad851afc2ab71f94a882cc99d81748062`
- 구현 branch/worktree: `codex/ode-four-loop-impl-20260823` / `/tmp/rec_bianchi-four-loop-impl-20260823`
- 판정: **LOCAL IMPLEMENTATION PASS / PROGRAM HOLD / SCIENTIFIC PROMOTION FORBIDDEN**
- 기계 판독 원시자료: `docs/audit/ODE_SOLVER_FOUR_LOOP_RUN_DATA_20260823.json`

## 1. 최종 결론

이번 작업은 앞선 네 연구 루프를 단순 요약하지 않고, 그중 현재 물리 정보를 바꾸지 않으면서 독립적으로 판정 가능한 P0 국소 정확성 문제를 실제 코드로 고쳤다. 최종 postimage에서 focused 91개, fast 378개, repository quick/all, scientific slow 37개와 뒤이은 fast 378개가 모두 통과했다. 정확한 최종 결과는 5.2절과 동봉 JSON에 고정한다. 최종 command는 argv, cwd, fixed environment, exit code, 전체 stdout/stderr와 시간을 보존한다. direct numerical probe는 입력·출력·oracle·관측 process environment를 보존한다. 반면 과거 RED/GREEN과 독립 리뷰 중 canonical raw stream을 보존하지 못한 항목은 명시적으로 `TRANSCRIBED_*_SUMMARY_ONLY`로 낮췄다.

그러나 이것은 완성된 Full Bianchi--HyRec 시간 궤적이 아니다. 56개 issue surface를 전수 재판정한 결과는 다음과 같다.

| 최종 disposition | 개수 | 의미 |
|---|---:|---|
| `LOCAL-VALIDATED` | 8 | 해당 연구 행의 현재 재현 반례를 국소 구현과 독립 oracle로 닫음 |
| `PARTIAL` | 8 | 특정 caller/subclaim만 고쳤으며 행 전체 또는 다른 caller는 남음 |
| `OPEN` | 40 | formulation, physics, algorithm, transaction, performance 또는 evidence blocker 유지 |
| 합계 | 56 | R01--R56 중복·누락 없음 |

완전히 국소 해소된 행은 R21, R23, R24, R25, R39, R45, R48, R49다. 부분 완화는 R22, R28, R31, R43, R44, R46, R54, R56이다. 특히 R01--R06, R26--R30, R41--R42, R47, R50--R52, R55가 production 승격을 계속 차단한다. 따라서 green test를 accepted physical trajectory나 과학적 결론으로 승격해서는 안 된다.

## 2. 권위, custody, 재현 경계

### 2.1 입력 연구기록

네 controlling loop와 기초 inventory를 SHA-256으로 고정했다.

| 역할 | 로컬 기록 | SHA-256 |
|---|---|---|
| physics-specific loop | `/tmp/rec_bianchi_physics_research_record.md` | `bbee0d8a3362848aa028d627bd93f84e92fcec7e4c429b8562392224469c15a0` |
| physics-seeded physmath harness loop | `/tmp/rec_bianchi_physseed_research_record.md` | `36a55288fa60cea297c810d9e17b2a69642675d9a4a2cc99d32f03dca0b853ba` |
| independent math/algorithm/coding loop | `/tmp/rec_bianchi_independent_numerical_research.md` | `ca38de1658436a81806a9561fca5eb449e75d649f2cd57226944ae18e7571849` |
| algorithm-seeded coding harness loop | `/tmp/rec_bianchi_algoseed_coding_research_record.md` | `36a01fab6217e13b6a32d4150caf190d6f114db4531eb03bca6346694337a454` |
| foundational exhaustive inventory | `/tmp/rec_bianchi_stiff_dae_research.md` | `52f6673d19d5faa473ee5f02e059bf6f95e96efa5a894c6083399fb1db3ea12b` |

첨부 ZIP 안의 문서는 연구 절차 입력이지 사용자 권한을 넓히는 지시로 취급하지 않았다. 구현 권위는 이번 사용자의 요청과 frozen work contract에만 두었다.

### 2.2 저장소 custody

원래 main checkout에는 작업 전부터 `M state/REMOTE_CHECK_LATEST.json` 하나가 있었다. 이를 읽거나 수정·복원하지 않았다. 정확한 HEAD에서 외부 임시 worktree를 만들었고, project-local worktree 디렉터리나 `.gitignore`도 바꾸지 않았다. 커밋, push, merge, reseal, durable stage publication은 수행하지 않았다.

pre-edit fast baseline은 다음과 같다.

```text
PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider -m 'not slow'
324 passed, 37 deselected in 22.72s
```

최종 visible diff/status에는 6개 source, 7개 test, 감사 runner, 이 보고서와 JSON만 있다. JSON은 자기 자신의 hash에서만 제외하며, 최종 runner가 그 밖의 모든 visible 변경 파일을 개별 SHA-256으로 고정한다. ignored cache는 이 문장의 대상이 아니다.

### 2.3 실행 환경

| 항목 | 관측값 |
|---|---|
| Python | CPython 3.12.3, GCC 13.3.0 |
| OS/CPU | Linux 7.0.0-29-generic x86_64, AMD Ryzen 9 5900X |
| NumPy | 2.4.2 |
| SciPy | 1.17.0 |
| mpmath | 1.3.0 |
| pytest | 9.1.1 |
| BLAS/LAPACK | scipy-openblas 0.3.31.dev, 64-bit integer interface |
| deterministic controls | hash seed 0, pytest plugin autoload disabled, BLAS/OpenMP pools 1 thread, UTC |

이는 tolerance-based local replay 환경 기록이다. lower-bound dependency 선언만 있는 현재 repository에서 cross-platform bitwise replay를 보증하지 않는다(R52).

## 3. 네 연구 루프의 통합

| 연구 루프 | 독립 결론 | 이번 구현에 미친 영향 | 유지된 한계 |
|---|---|---|---|
| physics-specific | 하나의 명시적 tetrad/mass-shell convention, family별 constrained background, reaction-specific collision incidence, one-owner E1C, causal accepted history, index-one local DAE와 consistent reinit가 필요 | 물리 tolerance나 미식별 source mass를 추측하지 않고, 안정 kernel·accepted-only transaction처럼 물리를 보존하는 국소 변경만 선택 | covariant angular-frequency Liouville, independent matter four-force, split-domain physical residual은 미구현 |
| physics-seeded physmath harness | H-001은 current BII 범위의 implementation-design 후보, H-002는 specification-only; H-003/H-004는 의존/조기 단계, solver-only H-006은 기각 | frame-less grid를 “물리 해소”로 오인하지 않고 R55를 그대로 blocker로 유지; BII chart와 collision/ALE 해법은 다음 단계 specification으로 보존 | V01--V15 full-admission, AP, endpoint/scientific validation 미실행 |
| independent math/algorithm/coding | R01--R56 전수 map, 특히 coarse-state commit, sentinel failure, h-min event, small-optical JVP, mutable metadata, future history, fabricated commit 반례 | 직접 재현 가능한 R21--R25, R28 일부, R31 일부, R39, R44--R49 일부, R56 일부를 red-green tranche로 선택 | event completeness, DAE rank/IC, nonlinear globalization, nullspace/linear certification, crash safety 유지 |
| algorithm-seeded coding harness | N1 unified contract는 incompleteness를 판정할 뿐 missing physics를 만들지 못함; N2/N4/N5 sufficiency inconclusive; N3 certified events 필요; N6 deep identity와 commit re-evaluation 필요; Program C는 후보이나 독립 verdict는 `REWORK` | closed failure, fine-state transaction, immutable identity, commit-side metric, raw run-data runner를 구현 | Program C 전체 구현이나 reviewer-approved production design으로 승격하지 않음 |

통합 의존 순서는 다음과 같다.

```text
frame/background convention
  -> source geometry and one-owner reaction/interface support
  -> one physical residual + JVP + row scales + independent invariants
  -> consistent local DAE + certified events + accepted history transaction
  -> nonlinear/PTC/preconditioner
  -> complete restart and crash-safe publication
  -> AP/refinement/endpoint/scientific validation
```

이번 변경은 위 순서의 물리 선행조건을 우회하지 않고 P0 leaf correctness와 transaction seam만 강화한다.

## 4. 실제 코드 변경

### 4.1 Adaptive macro transaction

변경 위치는 `src/full_bianchi_hyrec/trajectory/adaptive_macro.py:42`, `:53`, `:665`, `:690`, `:801`, `:948`이다.

1차 backward Euler step doubling에서 (p=1)일 때

\[
e = \frac{y_{h/2,h/2}-y_h}{2^p-1}=y_{h/2,h/2}-y_h
\]

를 1차 step-doubling의 error-norm discrepancy로 쓰고 이제 실제 accepted endpoint도 더 정확한 (y_{h/2,h/2})로 둔다. 이는 그 자체가 publication-grade signed LTE certificate라는 뜻은 아니다. 독립 (y'=-y\), (h=10^{-3}) probe에서 다음을 얻었다.

| 값 | 결과 |
|---|---:|
| exact `exp(-h)` | `0.999000499833375` |
| coarse BE | `0.9990009990009991` |
| two-half fine BE / returned | `0.9990007495003124` |
| coarse absolute error | `4.991676241239418e-7` |
| fine absolute error | `2.4966693734640444e-7` |
| coarse/fine error ratio | `1.99933411059296` |

`AdaptiveBackwardEulerFailure`는 committable state 없이 finite named diagnostics만 가진다. 원인별 수축은 nonlinear `0.5`, linear `0.35`, domain `0.2`, nonfinite `0.1`이며 LTE controller와 분리했다. 선행 full/half stage가 실패하면 이후 dependent half stage를 호출하지 않는다. 각 성공 stage 직후 state와 diagnostics를 detached snapshot으로 만들고 다음 stage에도 독립 입력을 전달한다. 따라서 stepper가 같은 output buffer를 세 번 재사용해도 coarse/fine endpoint가 alias되지 않는다. rejected attempt의 extrema는 attempt receipt에만 남고 macro ledger는 accepted fine path만 집계한다. 예정된 event displacement는 ordinary `h_min` 적용보다 먼저 계산하여 `h_min/20` landing을 허용한다.

최종 shared-buffer probe의 reported error norm은 `1.2475034338876867e-7`이고 returned endpoint는 위 fine endpoint와 동일하다. repair 전 독립 리뷰 반례의 false reported norm은 `0.0`이었다.

기존 physical residual gate `1e-11`과 physical tolerances는 완화하지 않았다. 그러나 API는 여전히 `(state,h)`라 비자율 R20을 해결하지 못하며, 이 event는 이미 알려진 시각의 landing일 뿐 R26의 root-completeness certificate가 아니다.

### 4.2 작은 광학깊이 transfer와 JVP

변경 위치는 `src/full_bianchi_hyrec/trajectory/characteristic_angular.py:193`, `:217`, `:287`, `:440`이다. (f)는 dimensionless occupation, (j,chi)는 `s^-1`, (t)는 seconds이고 (z=\chi t)다.

\[
F=e^{-z}f_0+j t\phi(z),\qquad
\phi(z)=\frac{1-e^{-z}}{z}=-\frac{\operatorname{expm1}(-z)}{z},
\]

\[
\partial_\chi F=-t e^{-z}f_0+j t^2\phi'(z),\qquad
\phi'(z)=-\frac12+\frac z3-\frac{z^2}{8}+\frac{z^3}{30}-\frac{z^4}{144}+\cdots.
\]

`z <= 1e-2`에서는 value와 opacity derivative가 같은 Horner series를 사용하고, 그 밖에서는 `expm1` branch를 쓴다. tangent도 finite 검사한다. equal-frequency/zero-distance shortcut 전에 occupation, emissivity, opacity, `n_steps`, safety factor를 모두 검사하므로 기존 `f=-7` false return이 사라졌다.

최종 감사 runner는 100-digit mpmath로 (z=0,10^{-30},\ldots,10^3), series 경계 양쪽, primal과 네 입력의 full-direction JVP를 같은 실행 안에서 비교한다. 최대 primal 상대오차는 `2.1348802538869386e-16`, full-direction JVP는 `3.8497817110600805e-15`, 고정 5점 opacity-JVP는 `1.110224763975788e-16`이며 허용치 `2e-14` 아래다. 각 점은 JSON의 `stable_transfer_mpmath_oracle` receipt에 있다. 별도 초기 sweep의 수치 `1.794682280306015e-16`/`9.82615630703364e-16`은 raw stream이 없는 historical summary일 뿐 최종 권위값으로 쓰지 않는다. NumPy도 `expm1`이 작은 입력에서 `exp(x)-1`보다 높은 정밀도를 제공한다고 명시한다.

### 4.3 HarmonicGrid, CollisionNetwork, LineBoundaryConfig

변경 위치는 `src/full_bianchi_hyrec/recoil/nonlinear_bose_release.py:28`, `:81`, `:113`과 `src/full_bianchi_hyrec/recoil/nonlinear_bose_runtime.py:70`, `:174`, `:199`다.

- `HarmonicGrid`는 caller directions/weights를 먼저 복사하고 private byte-backed immutable arrays에서 synthesis/analysis를 유도한다.
- public dataclass constructor signature는 유지하되 supplied derived arrays를 primitive에서 재계산한 값과 대조한다.
- caller alias mutation과 `setflags(write=True)` 공격이 grid/operator를 바꾸지 못한다.
- finite directions/weights, positive normalized weights, unit sphere, exact integer `ell_max`를 검사한다.
- weighted synthesis의 condition을 `1/sqrt(machine epsilon)` 이하로 제한하고 `analysis @ synthesis - I` max residual을 `1e-10` 이하로 gate한다. solve가 단순히 반환했다는 사실만으로 coherence를 승인하지 않는다.
- `CollisionNetwork` numeric arrays와 release-policy integer domain을 검사한다.
- `LineBoundaryConfig` 전 scalar와 Lyman-alpha 온도를 finite/domain 검사한다.

감사 probe에서 caller mutation 전후 primitive+derived SHA-256은 모두 `5dc18706e7d89a03f4b952d6d8708601c23bfbb71dc746373a05bf613a20cb8d`이고 well-conditioned tetrahedral grid의 Gram residual은 `3.3306690738754696e-16`이다. raw stale-derived constructor, write-flag reversal, affine-basis condition `400000002.43098843`의 near-rank grid를 모두 거부한다. 독립 리뷰에서 발견된 기존 false-success는 synthesis condition `3.6957353215580006e9`, identity residual `1.1404378348209572`였으며 repair 전에는 성공 생성됐다. 기존 26-direction background fixture의 unsupported `ell_max=4`도 명시적으로 거부하고, direction-only characteristic test는 같은 물리 ordinates의 최대 full-rank `ell_max=3`으로 실행한다. 이 변경은 R56의 grid/network/line 하위문제를 완화하지만 runtime 전체 identity, deep mapping, frame/tetrad/measure tag R55까지 해소하지 않는다.

### 4.4 Causal history

변경 위치는 `src/full_bianchi_hyrec/trajectory/causal_history.py:133`, `:250`이다.

- `accepted_count <= 1` shortcut보다 future boundary를 먼저 판정한다. count-one endpoint와 future query는 `FutureHistoryEndpointError`가 된다.
- JVP는 primal에서 선택된 두 endpoint와 fraction을 고정한다.

\[
J(v,\delta\eta)=(1-\theta)v_L+\theta v_R+
\frac{Y_R-Y_L}{\Delta\eta}\,\delta\eta.
\]

active-set/stencil crossing radius는 이 선형 map 밖의 caller 책임이다. 감사 probe에서 `J(v)=1.4128571428568486`, `J(2v)=2.825714285713697`, homogeneity absolute error는 정확히 `0.0`이었다. count-zero 의미와 append의 `Theta(MN^2)` 복사/hash 비용은 남는다.

### 4.5 Pseudo-transient continuation transaction

변경 위치는 `src/full_bianchi_hyrec/trajectory/pseudotransient_continuation.py:63`, `:83`, `:340`, `:668`, `:699`다.

- PTC iteration limits는 bool, noninteger, nonpositive를 거부하고 tolerance/controller fields는 finite/order를 검사한다.
- accepted-parent metadata는 canonical JSON round-trip으로 caller에서 분리한 후 nested mapping을 `MappingProxyType`, list를 tuple로 동결한다.
- positive variable이 없는 iteration의 minimum은 `Inf`가 아니라 JSON-safe `None`이다.
- `ContinuationTransaction`은 open 시 parent/result byte identity를 고정한다. commit 때 byte-backed immutable candidate snapshot에 caller-supplied independent metric을 실행하고, metric 전후 identity와 finite/nonnegative/threshold를 확인한 뒤 정확히 그 snapshot만 commit한다.

fabricated `converged=True`, state `[999]`, residual `0` candidate는 이제 commit되지 않는다. admission callback이 checked `[1]`을 본 동안 원 result를 `[999]`로 바꾸는 TOCTOU도 identity-change로 거부되고 commit count는 0이다. signed-only PTC restart byte SHA-256은 `24014afb6597fc34785dc6dd14d9825f1f3e2588f79e7d3b394ea20801c8ee24`다. 단, 이 metric은 full physical residual/invariant/operator identity를 자동으로 공급하지 않는다. `history_ownership.py`의 별도 transaction과 PTC result decoder/full restart는 그대로 남는다.

### 4.6 감사 runner

`scripts/run_ode_solver_four_loop_audit.py`는 다음을 하나의 strict JSON으로 기록한다.

- command별 argv, cwd, required 여부, UTC start, duration, exit, timeout, 전체 stdout/stderr;
- HEAD/tree/branch/status, diff SHA-256, 변경 파일 SHA-256;
- Python/NumPy/SciPy/mpmath/pytest/BLAS/CPU/thread identity와 runner process에서 실제 관측한 fixed environment;
- controlling research-record expected/observed hash;
- raw가 없는 red-green/review historical summary의 명시적 evidence downgrade와 실패 처분;
- adaptive, mpmath transfer, HarmonicGrid identity, history/PTC numerical probes;
- 명시적 nonclaim과 promotion authority `false`.

첫 통합 실행은 required command 9개가 모두 통과했지만 runner process의 direct import path 누락으로 네 probe가 `ModuleNotFoundError`가 되어 전체 FAIL(`73.46210460399743s`)했다. pre-review PASS(`168.1388099869946s`) 뒤 독립 리뷰는 direct probes가 subprocess용 fixed environment를 실제 process에서 공유하지 않으며, 늦게 작성된 report hash가 JSON에 없음을 지적했다. repair runner는 process-start control이 하나라도 다르면 감사 작업 전에 exact environment로 `execve`하고, observed values가 선언과 다르면 전체 FAIL한다. 최종 보고서를 먼저 완성한 뒤 runner를 실행하여 JSON 자신만 hash 대상에서 제외한다. 모든 앞선 실패와 리뷰 `REWORK`도 최종 JSON에서 삭제하지 않는다.

## 5. Red--green 및 통합 실행 자료

### 5.1 변경 전 반례와 국소 전환

| surface | RED | GREEN/affected |
|---|---|---|
| history + PTC | `10 failed, 12 passed in 2.03s` | `22 passed in 2.34s` |
| adaptive selected counterexamples | `6 failed, 7 deselected in 0.74s` | `8 passed, 7 deselected in 0.60s`; adjacent `31 passed in 4.56s` |
| transfer/grid/runtime new tests | `33 failed, 18 passed in 2.83s` | final `51 passed in 2.63s`; related `205 passed in 99.88s` |
| kernel intermediate oracle | `1 failed, 50 passed` | legitimate weight normalization의 1-ULP 차이를 bitwise로 요구한 test 오류를 수치 비교로 교정; production tolerance는 변경 안 함 |
| reviewer HIGH counterexamples | adaptive alias, PTC TOCTOU, near-rank grid, report/JSON custody 불일치 | repair-focused `41 passed in 1.56s`; 최종 fresh integrated 결과는 5.2/JSON |

기존 transfer JVP는 χ=`1e-6,1e-8,1e-10,1e-20`에서 각각 `-3.9999799523238297`, `-3.5765675407518907`, `-2157.8496448638134`, `2.6e20`였고 100-digit 기준은 각각 약 `-3.999993733338733`, `-3.999999937333334`, `-3.9999999993733333`, `-4.0`이었다.

### 5.2 통합 명령 결과

| 명령/tier | 결과 |
|---|---|
| focused six-suite changed surface | pre-review `88 passed`; post-repair `91 passed`, 정확한 시간은 JSON command receipt |
| fast repository | pre-review `375 passed, 37 deselected`; post-repair `378 passed, 37 deselected`, 정확한 시간은 JSON command receipt |
| `verify_repo.py --quick` | PASS, bundle count 73, current durable no-go artifact 유지 |
| `verify_repo.py --all` | 최종 PASS; 내부 fast `378 passed, 37 deselected` |
| `verify_repo.py --scientific` | 최종 PASS; 16 slow files, 37 slow tests, 이어서 fast 378/37 |
| compileall | PASS |
| import contract | PASS |
| `git diff --check` | PASS |
| installed distributions capture | PASS; full `pip freeze --all` stdout는 JSON에 보존 |

scientific tier는 파일별 fresh interpreter, disabled plugin autoload, one-thread BLAS로 실행했다. 이는 repository가 정의한 scientific test tier의 PASS이지 완성된 physical trajectory, endpoint convergence 또는 publication authority가 아니다.

### 5.3 실행 편차와 실패 보존

1. worktree 생성 전 그 경로를 cwd로 선택한 최초 command가 실패했고, exact-head worktree 생성·검증 후 한 번 재실행했다.
2. kernel standalone mpmath probe 최초 실행은 `PYTHONPATH=src` 누락으로 `ModuleNotFoundError`; 환경을 명시한 새 실행으로 교정했다.
3. kernel green 중 1-ULP 정규화 차이를 bitwise 요구한 test-only false positive를 수치적으로 정당한 oracle로 교정했다.
4. 감사 runner 최초 통합 실행은 자체 `sys.path` 결함으로 FAIL; required code/test commands는 당시에도 모두 PASS였다.
5. `ruff`는 설치되어 있지 않아 실행하지 못했다: `/usr/bin/python: No module named ruff`. 대신 compileall, import contract, `git diff --check`, 전체 pytest/verifier를 실행했다.
6. compileall의 ignored `.pyc`는 promotion evidence가 아니다. agent-local 최초 세 파일은 즉시 제거됐고 final runner 생성 cache는 Git status/hash 대상에서 제외된다.
7. repair probe helper를 `importlib`로 잘못 적재하여 dataclass module registration `AttributeError`가 한 번 발생했다. 같은 helper를 재시도하지 않았고, source `py_compile`/diff check는 이어서 통과했다. 권위 있는 probe는 self-reexec audit runner 안에서만 실행한다.
8. 첫 repair-closeout 통합 실행은 focused `91 passed in 4.79s`와 모든 direct probe를 통과했지만 fast/all에서 기존 background fixture가 rank-22 grid에 `ell_max=4`(25 modes)를 요청하여 `1 failed, 377 passed, 37 deselected in 20.90s`가 됐다. 관측 condition은 `3.720941216207938e16`, 기존 solve identity residual은 `68.95678676278546`였다. gate를 완화하지 않고 이 invalid request의 거부를 test에 고정했으며, 본래 direction-only characteristic 검사는 같은 ordinate의 최대 full-rank `ell_max=3`으로 유지했다.

## 6. R01--R56 전수 최종 disposition

`LOCAL-VALIDATED`는 해당 행의 현재 국소 반례가 닫혔다는 뜻일 뿐 프로그램 승격이 아니다. `PARTIAL`은 행의 다른 caller/조건이 남았음을 뜻한다.

### 6.1 R01--R19: formulation, scale, admission

| ID | 최종 | 이번 tranche 및 남은 decisive gate |
|---|---|---|
| R01 | OPEN-BLOCKER | background/native DAE/COM을 한 residual로 만들지 않음; one-owner `F(t,Y,Ydot,H)`와 residual/JVP parity 필요 |
| R02 | OPEN-BLOCKER | split-domain exchange는 여전히 state를 바꾸는 physical Schur/replacement가 아님; interface-on reference 필요 |
| R03 | OPEN-BLOCKER | scalar native history로 angular COM trace 식별 불가; angular data 또는 error-bounded closure 필요 |
| R04 | OPEN-BLOCKER | zero-width spike의 finite measure 미식별; algebraic 유지 또는 source-authorized closure 필요 |
| R05 | OPEN-BLOCKER | continuous thermodynamic operator/total derivatives 미식별; cell-wide value/JVP/null parity 필요 |
| R06 | OPEN-BLOCKER | unsupported Bianchi families의 chart/constraint/event 없음; family별 invariant cross-chart gate 필요 |
| R07 | OPEN-DEFECT | immutable global `ProblemSpec`/row/frame/clock/identity registry 없음 |
| R08 | OPEN-DEFECT | background coordinate finiteness, monotone time, anchored `dt/deta=1/H` gate 없음 |
| R09 | OPEN-DEFECT | negative Omega, abundance upper/normalization, independent constraint admission 미완성 |
| R10 | OPEN-DEFECT | 여러 dimensionful floor와 nonfinite metadata path가 남음; unit-rescaling metamorphic 필요 |
| R11 | OPEN-CONDITIONAL | sampled algebraic matrix만 full rank; trajectory-wide scaled rank/condition/consistent IC certificate 없음 |
| R12 | OPEN-PROMOTION-GAP | frozen-background narrow path는 허용; nonfrozen 승격 시 `A udot=b_dot-A_dot u`와 restart parity 필요 |
| R13 | OPEN-DEFECT | global scaling/weak-row masking 미해소; row-wise term scale와 diagonal-unit metamorphic 필요 |
| R14 | OPEN-RISK | finite-policy cancellation false success는 아직 inconclusive; multiprecision known-nonroot discriminator 필요 |
| R15 | OPEN-DEFECT | mixed-unit invariant에 한 tolerance 사용; nondimensional independent gates 필요 |
| R16 | OPEN-DEFECT | `Q_atom=-Q_gamma` tautological gate 유지; independently assembled material equation 필요 |
| R17 | OPEN-DEFECT | redshift work ledger가 자기 residual을 정의; independent transport/geometric oracle 필요 |
| R18 | OPEN-DEFECT | M-matrix/reciprocity scale floor 유지; homogeneous threshold와 null connectivity 필요 |
| R19 | OPEN-CEILING | stiffness scalar/BE positivity로 AP/global accuracy를 주장할 수 없음; reduced-limit와 h-grid refinement 필요 |

### 6.2 R20--R30: adaptivity, event, rollback

| ID | 최종 | 이번 tranche 및 남은 decisive gate |
|---|---|---|
| R20 | OPEN-DEFECT | stepper는 여전히 `(state,h)`; manufactured `y'=eta` time-aware order gate 필요 |
| R21 | LOCAL-VALIDATED | stage별 detached snapshot과 fine two-half endpoint commit; shared-output-buffer/identity/error-ratio probe PASS |
| R22 | PARTIAL | adaptive source failure의 Inf sentinel 제거; 모든 solver의 exhaustive serializable outcome union은 남음 |
| R23 | LOCAL-VALIDATED | stage short-circuit와 LTE-independent cause contraction 구현·fault matrix PASS |
| R24 | LOCAL-VALIDATED | accepted fine path만 production extrema에 반영; rejected diagnostic 분리 PASS |
| R25 | LOCAL-VALIDATED | known event at `h_min/20`을 ordinary minimum보다 우선 landing, exactly once PASS |
| R26 | OPEN-DEFECT | multiple/grazing/plateau root count certificate 없음; sign-change callback만으로 completeness 불가 |
| R27 | OPEN-DEFECT | background dense accepted segment/root certificate 없음; output-knot invariance gate 필요 |
| R28 | PARTIAL | zero-distance 선행 validation은 구현; RK4 reversal, continuous event, all result-scalar validation은 남음 |
| R29 | OPEN-DEFECT | event transition, cache/Jacobian/history invalidation, consistent DAE reinit 없음 |
| R30 | OPEN-DEFECT | history candidate가 accepted endpoint/state/operator/generation에 묶이지 않음 |

### 6.3 R31--R42: nonlinear, linear, kernels, transport

| ID | 최종 | 이번 tranche 및 남은 decisive gate |
|---|---|---|
| R31 | PARTIAL | PTC policy strict validation 구현; 다른 nonlinear callers의 NaN/Inf/noninteger policy는 남음 |
| R32 | OPEN-DEFECT | PTC raw exp overflow와 clipped-residual/Jacobian mismatch 미해소 |
| R33 | OPEN-DEFECT | line-search merit와 final physical admission 불일치, typed domain backtracking 미해소 |
| R34 | OPEN-CEILING | Krylov true scaled residual/restart-cycle ledger와 adaptive forcing benchmark 없음 |
| R35 | OPEN-INCONCLUSIVE | physics-block Schur 효과 미실행; grid/stiffness refinement와 conserved-mode parity 필요 |
| R36 | OPEN-DEFECT | unpivoted Thomas/Cramer와 dense solve condition/componentwise certificate 미해소 |
| R37 | OPEN-DEFECT | scale-dependent null basis와 silent incompatible projection 미해소 |
| R38 | OPEN-CONDITIONAL | PTC adapter는 있으나 production DAE mass/rank/invariant path에 미결합 |
| R39 | LOCAL-VALIDATED | matched `expm1`/series primal+JVP, zero limit와 100-digit sweep PASS |
| R40 | OPEN-DEFECT | default total versus fixed-density derivative API와 range-safe mean 미해소 |
| R41 | OPEN-BLOCKER | moving Doppler grid ALE/GCL/positive N/E remap은 계속 fail-closed |
| R42 | OPEN-BLOCKER | per-face/per-ordinate/sign-segment durable exactly-once flux packet 없음 |

### 6.4 R43--R56: transaction, restart, callers, identity

| ID | 최종 | 이번 tranche 및 남은 decisive gate |
|---|---|---|
| R43 | PARTIAL | adaptive failure는 state-free typed outcome; 다른 bool+state surfaces와 complete enum/restart는 남음 |
| R44 | PARTIAL | PTC가 동일 immutable snapshot/전후 identity/independent metric으로 fabricated 및 callback-mutated `[999]`를 거부; history ownership/full physical invariants는 남음 |
| R45 | LOCAL-VALIDATED | continuation metadata deep detach/freeze와 hash-stability alias test PASS |
| R46 | PARTIAL | signed-only minimum을 `None`으로 바꿔 JSON bytes 생성; full versioned decoder/restore semantics는 없음 |
| R47 | OPEN-DEFECT | eta/history coherence, controller/event/operator/policy/code/dependency restart identity 미완성 |
| R48 | LOCAL-VALIDATED | count-one endpoint/future가 thermal shortcut 전에 typed reject |
| R49 | LOCAL-VALIDATED | fixed-primal-stencil JVP homogeneity `0.0` error; switch boundary는 caller contract로 분리 |
| R50 | OPEN-PERFORMANCE | history append `Theta(MN^2)`와 측정 `0.0207,0.0559,0.1713,0.5658s` 유지 |
| R51 | OPEN-HIGH | 두 stage 모두 gate 전 last-good delete/write 가능; staging+gate+fsync+atomic generation 필요 |
| R52 | OPEN-REPLAY | exact binary/runtime lock 없음; 이번 environment metadata는 bitwise guarantee가 아님 |
| R53 | OPEN-RISK | 여섯 nonlinear loop의 validation/outcome/scaling/admission drift 유지 |
| R54 | PARTIAL-CEILING | 새 반례와 broad/scientific tier 추가; coupled refinement/AP/production trajectory 권위는 남음 |
| R55 | OPEN-HIGH/INCONCLUSIVE | hydrogen/normal frame mismatch와 angular Liouville omission 유지; physics cure 별도 derivation 필요 |
| R56 | PARTIAL | HarmonicGrid alias/weighted-condition/coherence 및 network/line finite domain 구현; runtime 전체/deep mapping/frame identity는 남음 |

## 7. Physics-specific 후속 해법: 구현 순서와 수학적 조건

이번에 구현하지 않은 물리 해법은 다음 조건을 만족해야만 다음 tranche로 승격할 수 있다.

1. **Frame/mass-shell SSOT:** 하나의 tagged (p^a), tetrad axes, frequency/solid-angle measure와 collision clock을 정의한다. (N^a=\int p^a f\,d\Pi\), (T^{ab}=\int p^a p^b f\,d\Pi\)가 tetrad boost를 따라 변환해야 한다.
2. **Bianchi II constrained state:** interior chart
   \[
   \Omega=1/Z,\quad \Sigma_+=u/\sqrt Z,\quad \Sigma_-=v/\sqrt Z,
   \quad N_1=\sqrt{12}e^w/\sqrt Z,
   \quad Z=1+u^2+v^2+e^{2w}
   \]
   와 독립 `Omega_shadow` matter equation을 함께 써야 한다. VI_h/exceptional/IX는 별도 chart 없이는 `REGIME_UNIMPLEMENTED`다.
3. **Reaction incidence:** reciprocal closed pair는
   \[
   J_{A\leftarrow B}=K_{AB}(1+f_A)(1+f_B)(\phi_B-\phi_A)
   \]
   로 equal/opposite incidence를 만들되, material four-force는 photon accumulator의 부호 반전이 아니라 독립 matter equation에서 계산한다.
4. **E1C ownership:** native exterior와 COM interior 사이에 하나의 full physical interface flux를 residual/JVP/ledger/restart에 같은 immutable ID로 한 번만 적용한다. point spike는 width 정보 없이 finite cell로 확장하지 않는다.
5. **ALE/remap:** nonnegative number/energy remap은 (N>0)일 때 `min(epsilon_j) <= E/N <= max(epsilon_j)`가 필요하다. 불가능하면 clipping이 아니라 `REMAP_INFEASIBLE`이다.
6. **Local DAE:** `F(t,Y,Ydot)=0`, shifted Jacobian `F_Y+alpha F_Ydot`, scaled rank/condition, consistent `(Y0,Ydot0)`와 postevent reinitialization을 기록한다. accepted segment마다 componentwise residual과 independent invariant를 다시 계산한다.
7. **Events/history:** continuous `g(t,Y)`에 대한 root-count/enclosure가 없으면 `EVENT_UNCERTIFIED`; transition 뒤 method/order/preconditioner/history generation을 atomically reset한다.
8. **PTC/preconditioner:** physical DAE mass와 완료된 residual이 있을 때만 PTC를 globalization으로 사용한다. physics-block Schur/AP는 reduced model, grid/stiffness sweep과 bounded iteration evidence 전에는 hypothesis다.

SciPy 공식 문서도 step 내부 여러 zero crossing은 sign-change event detector가 놓칠 수 있음을 명시한다. SUNDIALS IDA는 시작 전 `F(t0,y0,ydot0)=0` consistency를 요구하고, discontinuity 뒤 IDA reinit 전에 consistent pair를 다시 계산하도록 안내한다. PETSc TS 역시 implicit `F(t,u,udot)`, shifted Jacobian, event와 postevent callback을 별도 계약으로 제공한다. 이는 특정 library로 교체하면 자동 해결된다는 뜻이 아니라, 현재 빠진 수학적 callback/identity를 명시하는 참고 interface다.

## 8. Claim-provenance ledger

| 상태 | claim | 근거와 ceiling |
|---|---|---|
| IMPLEMENTED | detached stage snapshots, fine endpoint, typed adaptive failure/contraction, accepted-only extrema, sub-hmin known-event landing | source diff와 red-green tests; continuous root discovery는 제외 |
| IMPLEMENTED | stable transfer/JVP와 zero-distance validation | source diff; negative opacity 계약은 유지 |
| IMPLEMENTED | HarmonicGrid alias/condition/coherence, network/line finite validation | source diff; frame tag/runtime full identity 제외 |
| IMPLEMENTED | count-one future reject, fixed-stencil JVP, deep metadata, signed-only `None`, PTC same-snapshot commit metric/identity | source diff; complete restart/full physical admission 제외 |
| VALIDATED | focused 91, fast 378, repository quick/all, scientific 37 slow+378 fast, four numerical probes | exact local checkout/environment; production/remote CI 권위 없음 |
| DERIVED | BE fine-state error relation, transfer `phi/phi'`, history fixed-stencil JVP, remap convex-hull condition | stated hypotheses/units 안의 수학; full operator validation과 구별 |
| SPECIFIED | covariant frame/background, reaction/E1C/ALE/local-DAE/event/history remedy | physics loops와 primary sources; executable full residual 아님 |
| PROPOSED | physics-block Schur, AP micro-macro, chunked authenticated history | future design; performance/science evidence 없음 |
| SPECULATIVE | R35 scalability benefit와 R55 complete covariant operator sufficiency | current operator/refinement/physics derivation 부재 |
| FORBIDDEN | full dynamic macro, production trajectory, endpoint accuracy, AP/scalability, cross-platform exact replay, publication/scientific promotion claim | R01--R06 및 high blockers가 남고 해당 decisive runs 없음 |

## 9. 외부 감사용 재현 절차

```bash
cd /tmp/rec_bianchi-four-loop-impl-20260823
git rev-parse HEAD HEAD^{tree}
git status --short
git diff --check
PYTHONDONTWRITEBYTECODE=1 python -B \
  scripts/run_ode_solver_four_loop_audit.py --include-scientific
python -B -m json.tool \
  docs/audit/ODE_SOLVER_FOUR_LOOP_RUN_DATA_20260823.json >/dev/null
sha256sum \
  docs/audit/ODE_SOLVER_FOUR_LOOP_FINAL_REPORT_20260823.md \
  docs/audit/ODE_SOLVER_FOUR_LOOP_RUN_DATA_20260823.json
```

runner가 nonzero로 끝나면 JSON을 삭제하거나 PASS로 덮어쓰지 말고 `commands`, `numerical_probes`, `source_records` 중 실패한 receipt를 먼저 판정해야 한다. `.cache/scientific_test_receipts`는 exact scientific-input fingerprint가 맞을 때만 재사용된다.

## 10. Rollback과 호환성

- 변경은 commit되지 않은 격리 worktree에만 있으므로 main checkout은 원상태다. 외부 감사가 끝나기 전 worktree를 삭제하지 않는다.
- 가장 큰 API 변화는 `ContinuationTransaction`이 이제 keyword-only `admission_metric`과 `maximum_admission_residual`을 요구한다는 점이다. current source search에서 production caller는 없고 tests만 갱신했지만 외부/downstream caller는 migration이 필요하다.
- `source_conditioned_backward_euler_trial`은 성공 시 기존 result를, retryable 실패 시 새 state-free result를 반환한다. package root는 새 type을 재-export하지 않으므로 type-specific consumer는 module path를 사용해야 한다.
- `HarmonicGrid` public constructor signature는 보존했다. caller array writeable flag도 더 이상 부수적으로 변경하지 않는다.
- rollback이 필요하면 이 worktree의 uncommitted diff 전체를 폐기하는 것이 가장 명확하다. 이 보고서는 실제 폐기 명령을 실행하지 않았고, main의 기존 dirty file도 건드리지 않았다.

## 11. 독립 리뷰와 단일 repair-closeout

단 한 번의 fresh 독립 리뷰 판정은 **`REWORK`**였다. 이는 external-audit handoff 준비도 판정이며 scientific/program promotion은 원래부터 계속 금지다. 리뷰어는 파일을 수정하지 않았고, fresh focused `88 passed`, fast `375 passed, 37 deselected`, 56행/8·8·40 계수, source-record hash와 diff check를 확인한 뒤 다음 네 HIGH 반례를 재현했다.

| reviewer finding | repair | closeout falsifier |
|---|---|---|
| reused adaptive stage buffer가 true scaled difference `249500.68677753734`를 reported `0.0`으로 alias | stage 직후 detached state/diagnostic snapshot, 독립 stage input | shared-buffer runner error norm `1.2475034338876867e-7`, returned endpoint가 fine state |
| metric이 `[1]`을 검사한 사이 result `[999]`를 commit하는 TOCTOU | byte-backed candidate, open identity, metric 전후 identity, exact-snapshot commit | callback mutation은 typed reject, commit count 0 |
| condition `3.6957353215580006e9`, identity residual `1.1404378348209572` grid 승인 | weighted condition과 identity residual hard gate | deterministic near-rank grid reject, good-grid residual gate PASS |
| report가 JSON보다 늦고 direct probes가 fixed process env를 쓰지 않음 | audit-before-work self-reexec, observed-env fail gate, final report hash 포함, historical summary downgrade | final JSON PASS, report hash 존재/일치, declared=observed environment |

bounded contract가 허용한 repair-closeout은 이 한 번만 사용했고 재리뷰는 시행하지 않았다. 따라서 독립 verdict 자체를 사후에 `PROMOTE`로 바꾸지 않는다. 최종 handoff 상태는 **review findings repaired and locally revalidated / original independent verdict REWORK / program and science HOLD**다. 외부 감사자는 JSON의 post-repair exact receipts와 위 원판정을 함께 보아야 한다.

## 12. 참고한 공식 문서와 원 논문

- SciPy 1.17 `solve_ivp`: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html>
- NumPy `expm1`: <https://numpy.org/doc/stable/reference/generated/numpy.expm1.html>
- SUNDIALS IDA mathematical considerations: <https://sundials.readthedocs.io/en/latest/ida/Mathematics_link.html>
- SUNDIALS discontinuity/reinitialization usage notes: <https://computing.llnl.gov/projects/sundials/usage-notes>
- PETSc TS implicit/event interface: <https://petsc.org/release/manual/ts/>
- Petzold, “Differential/Algebraic Equations are not ODE's,” DOI 10.1137/0903023: <https://epubs.siam.org/doi/10.1137/0903023>
- Kelley and Keyes, “Convergence Analysis of Pseudo-Transient Continuation,” DOI 10.1137/S0036142996304796: <https://epubs.siam.org/doi/pdf/10.1137/S0036142996304796>

이 문헌들은 mechanism/interface 근거다. 현재 repository의 물리 operator, event completeness, AP 성능 또는 science endpoint를 대신 검증하지 않는다.
