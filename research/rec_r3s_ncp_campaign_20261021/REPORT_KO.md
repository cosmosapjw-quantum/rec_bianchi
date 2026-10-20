# REC R3R 종료와 R3S NCP 후속 연구

## 상태

**R3R exact spectral-stream 최적화와 CI 복구를 완료했다.** R3S는 같은 코드를 NCP에서 검증할 수 있도록 유한 작업 묶음과 자원 감독을 구현했다. 첫 고정 source의 45 PASS에 deadline 경로의 신규 두 계약을 추가해 고유 계약 47개를 확인했다. 영향받는 더미 세 경우의 재검증은 고유 수에 더하지 않는다. 이 보고서의 최종 상태는 `EVIDENCE.json`, `DAG.json`, `receipts/CLAIM_GATE.json`을 함께 따른다.

실제 NCP 실행은 연결 도구의 월 사용량 한도 때문에 **NOT_RUN**이다. 연결된 장치가 사용자가 지정한 64 CPU/128 GB NCP인지도 확인하지 못했다. 미확인 환경을 샌드박스 결과와 같은 것으로 취급하지 않는다. Google Drive의 새 보존 의무도 미완료이며, Dropbox와 Library의 ACK/전체 readback은 별도로 기록한다.

## 1. 최신 결과를 먼저 복구한 결과

새 코드를 쓰기 전에 기존 대화, GitHub branch/PR/receipt, Drive·Dropbox·Library를 조사했다. R3P 최종 HEAD는 `888d56d72579d1e1fd30f66abe02d9f91809a767`이다. PR110은 draft/unmerged다. 그러나 R3P 인계문만으로 현재 상태를 고정하지 않고, PR111과 백업에서 실제 NCP 반환을 발견해 먼저 분석했다.

R3Q h4 첫 사건+2의 실제 source는 `1ad0380110621446c42df9d995fd85db3a6c7e7a`다. 1,511 accepted continuation steps, 6,044 FULL 평가 뒤 source index74411까지 도달했다. 기존 독립 판정은 `PASS_SCOPED_H4_FIRST_EVENT_PLUS_TWO`다. CPU31.315760764 s/wall31.46869331 s를 기존 receipt의 측정 범위에서 재사용한다. 새 전체 h4 적분으로 세지 않는다.

같은 복구 과정에서 h2 저적색편이 반환의 153,327 accepted steps/153,328 states/43 checkpoints도 확인했다. 이 실행의 과거 CPU60.755865 s는 당시의 별도 600/900 allocation 아래 기록된 값이다. 현재의 60-second cap 통과 결과로 바꾸지 않는다. compact 반환본에는 일부 원래 native CSV·worker log·top-level exit 자료가 없으므로 기존 reviewed 결과를 새 exhaustive audit로 승격하지 않는다.

재개 후 다시 확인한 GitHub 범위에서는 이 대화의 R3R CI 수정·게시 이외의 새 외부 과학 반환을 찾지 못했다. 이는 전체 대화나 모든 NCP 디렉터리의 부재 증명이 아니다. 과거 대화 lookup의 service error와 현재 NCP 도구 quota는 각각 미확인 범위로 남겼다. 실제 NCP 활성 session PID1579402는 소유 작업을 식별하지 못했으므로 중단하지 않았다. 상세 범위는 `receipts/INTAKE.json`과 선행 R3R recovery receipts에 있다.

## 2. h2 endpoint의 수치적 제한을 정확히 분류

원본 C `rec_interp1d`의 마지막 출력에서는 raw index211715.47262308892를 source 규칙에 따라 ix211714로 clamp하고, 원래 4점 cubic의 s=1.4726230889209546을 사용한다. 필요한 index는 **211713, 211714, 211715, 211716**이며 네 상태가 모두 있다. 이 경우의 s를 [0,1]로 clip하거나 가상의 다섯 번째 상태를 채우면 원본 operator가 바뀐다.

R3R은 실제 저장 endpoint와 원본 stencil을 연결하여 xe/Tm float-hex를 재현했다. Python/native 차이는 각각 약3.876e-18/2.533e-16이었다. 이 교정은 불필요한 추가 negative-z RHS 실행 요구를 제거한다. 전역 격자 수렴성을 증명하거나 다른 stage의 nodewise 오차를 제공하는 결과는 아니다.

## 3. R3R에서 실제로 줄인 비용

R3R은 짧은 실제 profile32를 바탕으로 최대 세 후보를 비교하고 **실제 spectral stream에 NumPy ratio 배열 경로를 연결하는 후보 B**를 선택했다. profile의 cProfile 값은 elapsed attribution이며 exclusive CPU 시간이라고 바꾸지 않았다. 감사 comparator의 inclusive elapsed0.252768103 s/exclusive elapsed0.146397774 s가 실제 연결 지점을 뒷받침했다. 이 profile만으로 전체 production 비용 분율을 확정하지 않았다.

`scripts/r3r_stream_audit.py`는 원래 scalar parsing 순서, scalar Planck `expm1`와 입력 연산 순서, 원래 tolerance, guard schedule과 첫 오류를 보존한다. 정상 lane은 별도 binary64 ufunc로 subtract/abs/two products/sum/division을 수행하고, 예외 block은 원본 scalar 순서로 재평가한다. default block512/max625이며, 명시적으로 관리하는 NumPy data payload 상한은 각각30,720/37,500 bytes다. 이는 Python 객체·RSS를 포함한 전체 메모리 수치가 아니다.

실제 과학 실행 source는 `1313b1f1b2c081d57bcce9c60e757ef79110df91`이다. 저장된 전체 CSV97,935 records 중 spectral25,000 lane을 읽은 다섯 paired rounds의 결과는 다음과 같다. open·parsing·allocation·callback·최종 verdict가 측정에 포함되며 setup·hash·별도 warmup은 제외된다.

| Backend | CPU 중앙값 | Wall 중앙값 | Paired CPU 가속비 중앙값 |
|---|---:|---:|---:|
| Legacy | 0.109308013 s | 0.109321077 s | 1.0000 |
| R3R NumPy | 0.080130212 s | 0.080153802 s | 1.364129837 |

모든25,000 native binary64 lane의 차이는0이었다. 각200,000-byte trace의 SHA256은 `c174927905389fa933dc4bf5d3e89cfc32535e0721bbd58196101a1164c2bf3c`이고, verdict·maxima float-hex·ordered guard/diagnostic trace도 일치했다. **측정된 가속은 저장 스트림 감사 경로의 약1.364배**다. 전체 HyRec 적분 또는 production 가속률은 측정하지 않았다.

새32-step NumPy pilot은 32 accepted/128 FULL/9 common-input PASS, same-h PASS, source/input104개 UNCHANGED, exit0이었다. 전체 launcher CPU3.857951 s/wall3.914853461 s였다. status는 `SMOKE_ONLY`, `CAP_BEFORE_EVENT_PLUS_TWO`이며 사건 경계의 이후 계산이나 전체5210-step 실행은 없다. baseline과6개 raw 파일,10개 NPY payload,7개 semantic field를 대조한 기존 결과를 재사용한다.

RSS는 서로 다른 범위를 구분한다. 별도 fresh audit process의 rusage peak는 legacy88,875,008 B/NumPy88,887,296 B로 각1회 관측이다. 12 KiB 차이를 안정적인 메모리 증가나 감소의 추정치로 해석하지 않는다. 실제 pilot의 바깥 polled process-tree RSS는324,034,560 B였고 내부 worker 계측은305,954,816 B였다. 표본 기반 RSS는 정확한 aggregate peak가 아니며, process별2 GiB AS hard cap과도 다르다.

R3R cost·ratio·binary64 difference·RSS 그림은 선행 `rec_r3r_followup_costs_20261020/figures/`에서 재사용한다. 다시 측정하거나 새 실험으로 세지 않는다.

## 4. R3R CI 실패의 원인과 종료

처음 PR112 일반 회귀에서는 두 trace 검사만 실패했다. 같은 pytest process가 앞선 전체 테스트에서 사용한 CPU를 benchmark 모듈의 전체 예산 검사에 넘긴 것이 원인이었다. ratio 또는 물리 결과의 불일치는 아니었다.

두 기존 trace 검사를 fresh bounded subprocess에서 실행하도록 테스트 코드만 수정했다. 별도 pycache, 입력 before/after hash와 raw child result를 보존하며 기존 budget predicate는 그대로 두었다. 실제 CI 수정 source `70a53396e910869ea069e184a44f1fb21cb47a0a`에서 일반 회귀 **1038 PASS/103 SKIP/72 subtest PASS**, 전용 R3R **60 PASS/1 SKIP**가 반환됐다. 전용 CI의 skip을 로컬 성공과 섞지 않는다. R3R 신규 고유 계약 수는 **61**이며 반복 CI 건수를 더하지 않는다.

최종 R3R metadata HEAD `bf6bb95c58182529ad3d773a1dd0ab4f0fc7c70b`의 두 PR-triggered CI도 SUCCESS다. 독립 감사는 원래 과학 결과, source closure, 최초 실패 로그와 실제 수정 CI 로그를 연결해 scope 안의 P1/P2를 닫았다. 복구 중 준비한 로컬 formal003은 실제 source70a CI 반환으로 대체하여 **NOT_RUN**으로 남겼다.

## 5. R3S의 선택과 구현

사용자가 요청한64 CPU/128 GB NCP 후속 작업에서는 후보 C, 즉 **기존 구현의 제한된 새 플랫폼 검증**을 선택했다. 추가 solver 내부 최적화 또는 새 Rust SIMD 이식은 새로운 비용·정확성 근거를 요구하므로 이번 묶음에 섞지 않았다. SciSpace로 task scheduling 문헌 후보를 찾고 Exa로 primary abstract·Python/Linux 문서를 확인했다. 새로운 ODE solver를 HyRec 시간 적분기에 이식하지 않았다.

`scripts/run_r3s_ncp_campaign.py`의 실행 job은 다섯 개다.

| Job | 선행 결과 | 실행 방식 |
|---|---|---|
| `trace_original` | 현재 source/input/host gate | 다른 trace와 병렬 |
| `trace_interleaved` | 현재 source/input/host gate | 다른 trace와 병렬 |
| `saved_stream_benchmark` | 두 trace PASS | campaign 안에서 단독 |
| `h4_legacy16` | 두 trace PASS | 단독 |
| `h4_numpy16` | legacy16 PASS | 단독, 같은 배정 CPU, 최종 raw/NPY byte gate |

현재 독립 frontier의 폭은2다. core 수만큼 같은 작업을 복제하여 이용률을 만들지 않는다. 원래 trajectory의 연속 accepted step은 이전 state·predictor·photon history에 의존하므로 그대로 순차 실행한다. 이 제한은 사용 가능한 고정 DAG의 성질이며 모든 병렬 ODE 알고리즘의 한계라는 주장이 아니다.

코드는 실제 hostname·논리 CPU/RAM·affinity·cgroup 조상 quota·명시적 CPU 소유권, 최신 결과/session intake, fixed Git blob, 전체 raw input SHA, runtime identity를 검사한다. JSON 변경만으로 임의 shell command나 full mode를 열 수 없다. 메모리 admission은 shared-page RSS를 headroom에 다시 더하지 않고 full active/new allowance를 보수적으로 예약한다.

각 job의 **60 CPU/180 wall/2 GiB per-process AS** 제한은 유지한다. 5개 job 전체를 선택하는 새 명시적 campaign allowance는305 CPU/912 wall이며, 이는5개 작업 한도와 supervisor reserve를 합한 값이다. 이전 단일60-second allocation 또는 `CLOSED_HOLD_NOT_RESET`을 늘리거나 초기화하지 않는다. 현재 NCP에서 이 allocation을 시작한 사실은 없다.

guardian/coordinator는 Linux subreaper와 stable process descriptor를 사용해 자신이 시작한 후손만 정리하고 `wait`로 회수한다. source·input·host·runtime·CPU 집합·allocation·출력 경로가 바뀌면 재개를 거부한다. 완료한 같은 캠페인 output은 해시를 확인해 재사용하고 실패·부분 디렉터리는 덮어쓰지 않는다. 원본 numerical runtime은 R3R base 이후 바뀌지 않았다.

## 6. 새 로컬 검증과 독립 감사

첫 고정 R3S source는 `96e8b88d854d1606c6204cefe2f2920f46219dff`, tree `a4c5005fcf93bb98df31b4a39a3431dd01d7daed`다. 이 source에서 새 R3S 계약45개가 모두 PASS했고 skip/fail은0이었다. 전체 CPU3.823868 s/wall3.818103754 s, exit0, source/input114개 UNCHANGED를 실제 wrapper receipt에 기록했다.

세 실제 더미 process case는 각각 병렬 a/b 이후 단독 timed 실행, leader가 새 session 후손을 남긴 경우의 HOLD+cleanup, guardian이 강제 종료된 경우의 입양된 후손 검출+cleanup을 확인했다. 세 경우 모두 owned descendant의 회수를 확인했다. 이 더미는 REC trajectory나 과학 benchmark를 실행하지 않는다. 원래 numerical equivalence는 선행 R3R 결과로 `complete_reused`다.

독립 감사는 고정 Git source114개, frozen100개, raw60개 SHA, JUnit45개, 실제 더미3개와 LIMITS/GUARDIAN/TERMINAL/events를 직접 읽었다. pytest의 `*current` alias symlink를 새로운 case로 세지 않았다. 코드 검토에서 발견한 PID namespace/PID reuse 문제는 실행 전 수정했다.

최종 검토의 one-shot SIGALRM 이후 closeout 경로 지적은 최초45 PASS가 다루지 않은 경로다. 최초 결과를 바꾸지 않고 source `52f884b7b27814f808b9b4f7fd5ac9a3c6283e32`에서 신규 deadline 계약 2개와 영향받는 실제 더미 3개만 검증했다. 다섯 경우 모두 PASS/exit0이며 source/input114개 UNCHANGED다. 신규 고유 계약은 47개다. 누적 CPU7.929026 s/wall7.837205600 s는 최초 실행 비용을 그대로 포함한다. 최종 CODE verdict는 `receipts/PHYS_MATH_CODE_AUDIT.json`, 일곱 축 판정은 `receipts/CLAIM_GATE.json`을 따른다.

실제 더미 raw에서 timeline·CPU/RSS 그림 하나를 PNG/PDF/SVG로 생성했다. 그림 생성의 새 CPU1.834219 s/wall1.847888912 s를 더한 동일 allocation 총계는 **CPU9.763245 s/wall9.685094512 s**다. generation receipt는 실행 당시의 `PENDING_VISUAL_REVIEW`를 유지하고, root 및 독립 reviewer의 직접 시각 검토를 별도 receipt로 연결한다. 원래 60 CPU/180 wall/2GiB 한도와 마지막 2 CPU/3 wall reserve를 유지했다. 이 그림과 더미 시간은 NCP 또는 solver 가속 측정이 아니다.

### 새 고정 source의 실제 CI

source52f884의 전용 CI [39503008348](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/39503008348)는 **47 PASS/0 FAIL/0 SKIP**, 일반 CI [39503008360](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/39503008360)는 **1085 PASS/103 SKIP/72 subtest PASS**였다. 전용 CI archive65,144 bytes의 전체 SHA256은 `8a7ee2c116ca2d55312ca62622d51663df1dbeffea1c90fa49b82f3f3cd25901`이며, 실제89 entries/JUnit47/manifest60개/source114개를 대조했다. 전용 CI 전체 검증 CPU3.438309 s/wall4.533052243 s는 별도 CI allocation의 값이다.

두 CI가 실제 checkout한 commit은 `71a72b76fc0cbfa0b32a63f3061b793e5634f7d4`이고, branch source52f884와 동일한 tree `eb2108cfea0cd33577afed425389cbbce2de1189`를 가졌다. raw Git commit 객체를 별도로 복구해 이를 확인했다. 일반 회귀의242.47 s는 pytest가 보고한 elapsed이며 전체 workflow CPU/wall 또는 과학 benchmark가 아니다. source·metadata HEAD와 synthetic merge SHA를 각각 보존하고 반복 CI를 새 고유 검사로 합산하지 않는다.

## 7. 수학적 결론과 외삽 한계

고정된 비추측 DAG에서 총 작업량W, 가장 긴 의존 경로L, 동질 CPU 수P라 하면 완료 시간은 `max(W/P,L)` 이상이다. 두 독립 read-only 작업의 순서는 전용 출력과 고정 입력·연산 순서 조건에서 바꿀 수 있지만, 시간·RSS·budget 도달 시점까지 같은 것은 아니다.

R3R 감사 가속비a와 그 경로가 전체 비용에서 차지하는 미측정 비중q를 쓰면 조건부 모형은 `S=1/(1-q+q/a)`다. `0<=q<=1,a>=1`에서 `1<=S<=a`이고 q에 따라 단조 증가한다. q=0.1/0.25/0.5의1.0274/1.0715/1.1540은 예시일 뿐이다. 전체 solver의 q를 측정하지 않았으므로 이를 NCP 예측값으로 쓰지 않는다.

Wolfram input과 output은 별도 receipt로 보존했다. symbolic W/L/P를 표시한 부분의 undefined-symbol 경고도 숨기지 않았고, work/span 하한은 `THEORY_KO.md`의 독립 논증으로 제공한다. PHYS-MATH 감사는 이 계산·병렬성 계약의 범위에서만 PASS다.

## 8. 남은 실행·물리 gate

실제 NCP 연결 도구는 월 사용량 한도를 반환했다. 사용자에게 수동 SSH/SCP·다운로드·재업로드를 요청하지 않았고 제한을 우회하거나 알 수 없는 활성 session을 중단하지 않았다. 정상 가용한 연결이 회복되면 새 결과와 CPU 소유권부터 읽고, `RUNBOOK_KO.md`의 준비된 entry point에 실제 host intake와 source/allocation을 전달하면 된다. 현 시점의 NCP 실행 수는0이다.

전체 과학 계산에는 다음 의존성이 남아 있다.

- h4 첫 사건+2 이후 U4→U5→U6 RT→low-z의 stage 구현·검증.
- h2 전체 accepted history의 연속 조립 및 stage/uncertainty provenance.
- 원래 h history의 nodewise C parity와 source input29195 이전 boundary semantics.
- 세 격자의 source-defined endpoint/stencil, canonical target과 signed difference resolution.

현재 `nodewise_C_parity=UNKNOWN`과 `UNCERTAINTY_MISSING`을0 오차로 바꾸지 않는다. 단순히 h4 coverage가 늘어도 global gate가 열리지는 않는다. R3P Rust build의90 CPU s와 R3O build/verifier의 더 큰 기존 envelope도 이60/180/2GiB 묶음에서는 blocked로 분리했다. 이 optional Rust 상태는 NumPy platform job의 준비를 막지 않는다.

기준 namespace도 보존한다. 사용자 R3P h는4.245e-5다. 기존 convergence 모듈의 H0는8.49e-5, level1은4.245e-5, level2는2.1225e-5이므로 모든 이력을 실제 `dlna`와 함께 해석한다.

## 9. 보존과 인계

R3R stage1/2/3 백업은 workspace pruning 이후 연결 소스를 조사하고 GitHub·Dropbox·Library에서 직접 복구했다. Library와 Dropbox에서 세 archive의 전체 SHA를 새로 확인했고, 추출한371개 regular file과344개 manifest-bound 항목을 연결했다. stage1의78 archive entries는77개 payload와 MANIFEST이며 중복 결과 수가 아니다.

R3R Stage4 `REC_R3R_STAGE4_CI_RECOVERY_bf6bb95c_20261021.tar.gz`는469,172 bytes, SHA256 `125043bf82a1d7ac7b398ce284f40b84f7e1c910459bcc49d13ea81190c4e7a0`이다. Dropbox와 Library의 create ACK 및 별도 전체 readback이 PASS다. 고정 Git delta이므로 이전 base chain이 필요하다.

R3S 최종 검증 source의 coordinator SHA256은 `8e53d84479a6aa026cd80f15f8e0a22494cfce69e157a82635b731770df95221`, tests는 `82e11ce853bfd639b33920a9ccc621877199ecc42f25504cec20d3b6b06c1254`, plotter는 `47960422855ca4ff2b86e8645786597cb1fcbc8d9006cc688cc2fb9ed2a87427`이다. source52 이후 최종 증거/보존 metadata를 별도 HEAD로 게시한다.

R3S Stage1 `REC_R3S_STAGE1_SOURCE_96e8b88d_20261021.tar.gz`는374,529 bytes, SHA256 `498ef4dddddc16ce7efc70de75342b261a13b0bdaf020dac31d7695adca64c93`다. 검증·최종 code audit 이전의 source checkpoint라는 역할을 유지한다. 이후 새 source/검증/그림/감사 묶음은 `BACKUP_ACKS.json` 및 PR113 보존 receipt에 연결한다.

Drive에서는 현재 metadata read가 가능하지만 앞선 create 작업의 ACK를 확보하지 못했다. 같은 archive 이름의 조회 결과가 없다는 사실만으로 미완료 요청의 취소 또는 전체 부재를 주장하지 않는다. 기존 `UNKNOWN_NO_ACK`, `NOT_ATTEMPTED`, `UNKNOWN_NO_ACK_TIMEOUT_25S` 기록을 그대로 남겼다. 새 provider SHA가 다르면 같은 보존본으로 취급하지 않는다.

PR112와 PR113은 draft/unmerged다. 실제 source·tree·metadata HEAD, CI, archive IDs와 다음 스레드의 정확한 복구 순서는 `HANDOFF_KO.md` 및 `NEXT_THREAD_PROMPT_KO.md`를 따른다. 모든 항목을 하나의 PASS로 묶지 않고 `CLAIM_GATE.json`의 일곱 축을 각각 유지한다.

## 실제 증거와 원 자료

- 새 로컬 원 명령·stdout/stderr·exit·source/input hash: [첫 검증](receipts/local_validation_001/validation.json), [targeted 검증](receipts/local_validation_002/validation.json), [그림 실행](receipts/plots_001/plotting.json).
- [R3S 수학 계약](THEORY_KO.md), [수학 감사](receipts/PHYS_MATH_AUDIT.json), [코드 감사](receipts/PHYS_MATH_CODE_AUDIT.json), [직접 그림 검토](receipts/VISUAL_REVIEW.json), [새 source의 CI](receipts/CI_FIXED_SOURCE.json).
- 원 HyRec: [Ali-Haïmoud & Hirata, 2011](https://arxiv.org/abs/1011.3758); scalar/NumPy 연산 설명: [NumPy ufunc 문서](https://numpy.org/doc/stable/reference/ufuncs.html). 새로운 적분기를 이식한 것이 아니다.
- 병렬 실행 설계에 참고한 primary source: [Python3.12 subprocess](https://docs.python.org/3.12/library/subprocess.html), [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [subreaper](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html), [pidfd signal](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html).
- SciSpace/Exa 문헌 탐색과 [task granularity 논문 abstract](https://arxiv.org/abs/2602.20561)는 [문헌 receipt](receipts/LITERATURE_AND_ALGEBRA.json)에, Wolfram의 실제 입력/응답은 [별도 receipt](receipts/WOLFRAM_EXACT_INPUT_CHECK.json)에 보존했다. abstract 열람을 full-paper 증명이나 외부 solver 코드 이식으로 확장하지 않는다.

### 원본 text 증거의 archive 매핑

생성 SVG와 원시 CI/git/connector text 12개는 원본 공백을 유지하기 위해 `receipts/ORIGINAL_TEXT_EVIDENCE.tar.gz` 안에 보존했다. 크기42,222 bytes, SHA256 `728048efca0483083401d771b726ca0df38ffcf0cf42b391fc7580e8b8080a78`이며 `ORIGINAL_TEXT_ARCHIVE.json`이 원래 logical path와 각 member SHA를 연결한다. 원래 CI/plot receipt는 그 logical path를 유지한다. 새 checkout에서 원문이 필요한 검토자는 archive와 member SHA를 확인하고 해당 경로로 복구한다. PNG/PDF 및 나머지 raw는 직접 Git 파일로 제공한다. 원문 정규화·receipt 변경·whitespace gate 완화는 하지 않았다.

### 검토된 최종 배송

코드·검증·CI raw·감사·handoff의 배송 commit은 `265b82042e918c2554fbb9d890c8e7a7cce5ebfb`, tree `0478d4489837c9b3ac482be46e6871c8b7aad2cc`이다. `REC_R3S_STAGE2_REVIEWED_DELIVERY_265b8204_20261021.tar.gz`는756,456 bytes/SHA256 `d19c38eb9d4b938851cfef129c71d00a9756e59ba9451d2fe991cdbb7ffddbf0`이며, Library ID `libfile_458442bc4688819186a1f5290a221181`, Dropbox ID `id:BSpOijBcT10AAAAAAD_aJA` 각각의 완료 ACK와 별도 전체 SHA가 PASS다. delta base는96e8b88d, 실제 code/test/plot execution source는52f884b7로 구별한다. 최종 보존 metadata HEAD와 그 자체의 보존/CI receipt는 PR113의 마지막 보존 댓글에 별도로 고정한다.

## NCP 실행 addendum — 2026-10-21

실제 NCP `s1a0e5abed09`(64 logical/physical CPU, total RAM 135,050,526,720 bytes)에서 allocation `REC_R3S_NCP_20261021_001`을 실행했다. 새 계산은 41.782113 CPU초 / 33.843081 wall초였고, 다섯 job 모두 종료했으며 각 job의 60 CPU초/180초/2 GiB 계약과 descendant cleanup을 확인했다. 두 trace는 scoped PASS, saved-stream producer는 25,000 lane·binary64 mismatch 0과 paired median CPU/wall 1.387459x/1.387844x를 냈다. 그러나 producer `PASS_SAVED_STREAM_AUDIT_ONLY`와 runner가 요구한 `PASS`의 enum 불일치로 campaign terminal은 `HOLD`로 유지한다. h4 legacy/NumPy는 각 16 accepted-step `SMOKE_ONLY`이며 same-h parity PASS이다. solver integration은 0이다. 원 U5 HOLD/예산, global convergence NOT_RUN, physical HOLD, production NOT_APPROVED는 불변이다. 상세는 `ncp_execution_001/NCP_RETURN_HANDOFF_KO.md` 및 원시 receipt를 본다.

## Adjudication update — 2026-10-21

Astra-tier independent review accepted the exact-enum adapter patch and the existing saved-stream receipt as `PASS_SCOPED`. The four-case targeted regression passed; no NCP job was rerun. The original `attempt_0001.TERMINAL.json` remains `HOLD` byte-for-byte; see additive `ncp_execution_001/receipts/CAMPAIGN_ADJUDICATION_001.json`. Costs remain 41.782113 CPU s / 33.843081 wall s within the original allocation. All scientific limits, including U5 HOLD, physical HOLD, convergence NOT_RUN, and production NOT_APPROVED, remain unchanged.
