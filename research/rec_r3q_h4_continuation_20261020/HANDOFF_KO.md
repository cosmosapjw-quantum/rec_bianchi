# REC R3Q: 독립 h4 event continuation 및 h2 low-z 실행 계약

이 문서를 받은 local Codex가 checkout, 입력 취득, 컴파일, 경량 플랫폼 확인과 실제 제한 실행을 직접 수행한다. 사용자가 파일을 미리 내려받거나 경로를 채울 필요가 없다. 실제 실행 전 최근 반환 결과를 조회하여 완료된 동일 campaign은 재사용한다.

## 소스와 완료 결과

Repo는 https://github.com/cosmosapjw-quantum/rec_bianchi 이다. 이 변경의 base는 `research/rec-r3p-exact-acceleration-20261020`, SHA `888d56d72579d1e1fd30f66abe02d9f91809a767`이다. 실행 소스는 **이 문서와 SOURCE_CLOSURE.json을 포함하여 게시된 commit**으로 고정한다. 최초에 전달된 GitHub 문서 URL에서 실제 branch/ref를 읽고 `git fetch origin <branch>:refs/remotes/origin/<branch>`로 명시적 fetch 후 별도 worktree를 준비한다. 기존 작업을 덮어쓰거나 main으로 대체하지 않는다. 실제 `git rev-parse HEAD`, remote ref와 source closure100개 파일을 대조한다. 루트 AGENTS.md는 base에서 존재하지 않았으며, 이후 생성되었으면 해당 지시를 읽는다.

먼저 같은 폴더의 INTAKE_KO.md, THEORY_INTERFACE_KO.md, REPORT_KO.md, EVIDENCE.json, DAG.json, SOURCE_CLOSURE.json 및 INDEPENDENT_REVIEW_KO.md를 읽는다. review 파일이 없거나 미결 지적이 있으면 해당 지적의 교정이 먼저다. base의 `research/rec_r3p_exact_acceleration_20261020/REPORT_KO.md`, HANDOFF_KO.md와 BACKUP_ACKS.json도 소스/백업 provenance에 사용한다.

재사용 완료: R3M h2 FULL U6 5,210step; R3O 독립 h4 72,893개 He rows+8FULL; R3P 15saved audit 및16step smoke. 새 sandbox R3Q는 **그 h4의 다음2개 accepted steps**를 실행했다. 원본 C와 현재 Python의 같은-h 상태·RHS·6,250 photon fields 비교 PASS, source closure100/100, focused stdlib test10methods PASS. 독립 검토의 정확한 범위는 review에 있다. 첫 실제 stage event까지의 실행과 전체 h/h2/h4 비교는 다음 실행 대상이다.

## 가장 먼저 실행할 h4 경로: 모든 입력이 Git에 있음

원본 archive:
`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`
SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

독립 Python checkpoint:
`research/rec_r3o_grid_frontiers_20261019/h4_start_002/python_h4_full_start.npz`
43,904bytes, SHA256 `40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef`.
여기에는 iz72892..72900의9상태, 수용된8 photon columns, He/H 두 RHS씩의 predictor와 stage flag가 이미 있다. h2 보간이나 C 상태 주입이 필요하지 않다. h4 helium 시작 적분을 Python에서 다시 실행하지 않는다. 독립 C oracle만 자신의 초기이력과8열을 재구성해 대조한다.

Python3.11이상, NumPy/SciPy, gcc가 필요하다. 의존성은 현재 repo/환경을 재사용한다. 새 R3Q 경로에는 Rust가 필요하지 않다. BLAS/OMP thread cap1은 runner가 적용한다. 전체 NCP64core/128GiB 중 이 경로는 **한 core**를 배정한다. 다른 repo와 공유하는 host ledger에서 실제 사용 중인 CPU·메모리와 deadline을 먼저 확인한다. 여러 worker가 같은 첫 core를 고르는 것을 피하려면 host coordinator가 할당한 core로 launcher를 `taskset`한다. source의 시간재귀는 직렬이다.

아래는 repo root에서 실행하는 완성된 진입점이다. Codex는 충돌하지 않는 날짜/UTC suffix를 자동으로 붙여 새 output과 allocation ID를 선택한다. 아래 예제의 ID가 이미 존재하면 기존 결과를 읽고 새 실행의 과학적 필요가 있을 때만 새 ID를 쓴다.

```bash
PYTHONPATH=src python -B tests/trajectory/test_r3q_h4_continuation.py
python -B scripts/run_r3q_h4_supervised.py --mode smoke --steps 2 --new-allocation-id REC_R3Q_NCP_PLATFORM_001 --evidence-dir research/rec_r3q_h4_continuation_20261020/ncp_platform_001
python -B scripts/run_r3q_h4_supervised.py --mode event --new-allocation-id REC_R3Q_NCP_EVENT_001 --evidence-dir research/rec_r3q_h4_continuation_20261020/ncp_event_001
```

첫 NCP platform smoke는 컴파일러/호스트 차이 확인용이며, 동일 호스트의 동일 코드/입력 검증이 이미 있으면 재사용한다. event 실행은 그 smoke의 `first_failure=null`, same_h_parity=PASS, closure unchanged와 리뷰를 확인한 뒤 진행한다. 새로운 event allocation은 **600CPU초/900wall초**, smoke는60CPU초/180wall초다. 두 작업을 모두 새로 수행할 때 합계 상한은660CPU초/1080wall초다. 각 allocation 안에 worker closeout5CPU초/12wall초 및 supervisor wall2초를 남긴다. AS한도2GiB는 process별 한도이며 동시 process-tree RSS 총합 한도가 아니다. CPU는 RUSAGE 측정·협력 guard와 자식별 RLIMIT_CPU를 함께 사용하고, supervisor가 owned process group의 wall 종료를 강제한다. host coordinator는 compile 자식을 포함할 메모리 여유를 배정한다. kernel process-tree CPU hard cap을 측정값으로 가장하지 않는다.

원래 U5 예산은 `CLOSED_HOLD_NOT_RESET`으로 유지한다. 이번 두 allocation은 날짜·호스트·CPU 소유권을 기록하는 별도 campaign이다. 소진 후 같은 allocation ID를 새 디렉터리에서 재시작하여 비용을 초기화하지 않는다. `--mode event`는 최대8,192추가 accepted steps/32,768FULL evaluations이며, 첫 He cutoff 또는 H post-Saha off event 이후2단계까지 도달하면 종료한다. 전역 h4종료는 이 경로의 수용 기준이 아니다.

`TERMINAL.json`이 실행 상태와 worker receipt hash를 기록한다. `worker/verification.json`의 `PASS_PENDING_INDEPENDENT_REVIEW`는 event+2와 원본 same-h gate 통과를 뜻한다. `SMOKE_ONLY`, `HOLD_CAP_BEFORE_EVENT_PLUS_TWO`, `HOLD_EXECUTION_OR_RESOURCE`, 실패 원문은 그대로 보존한다. 정상 결과에는 `python_continuation.npz`의 accepted states, prefix8열을 포함한 photon arrays, final predictor, parent checkpoint/source hashes가 있다. timeout에는 flush된 JSONL/bin partial streams가 남는다. partial을 검토 없이 새로운 물리 checkpoint로 승인하지 않는다.

## 고정 방정식·원본 수용 기준

h4=2.1225e-5, z_i=8001exp(-h4*i)-1, 원본 HyRec2012 q=0 cosmology와 atomic/thermal source를 유지한다. source-stage 조건은 accepted input이 소유한다. neutral H 재귀는 `xH1s_next=xH1s-h*(1.25*FH-.25*FH_prev2)`이며, He는 같은 predictor의 +부호이다. H-only에서는 source가 이전 total xe를 넘긴다. post-Saha 유한차분의 `/2./delta`, 원본 C의 `/2./DLNA`까지 순서를 보존한다. trial source 결과는 accepted photon column을 바꾸지 않는다.

기존 compare_state의 xHII/xe 상대5e-9, He 절대5e-10, Tm 상대5e-10; integrated RHS scale-max1 2e-7; photon `1e-7*max(abs(P),abs(C))+1e-10*fBB`를 유지한다. common-input RHS2e-10, Schur residual2e-10, ledger5e-13을 유지한다. tolerance나 stage condition을 바꾸어 기존 gate를 통과시키지 않는다. 최초 비교 실패의 index/field/bin, 출처, 수정 전후 소스를 보존한다.

원본h U5=HOLD_9_FAIL, h2=HOLD_8_FAIL, REI_activation=false다. 첫 event+2 뒤에는 실제 event kind/endpoint/predictor를 근거로 h4 U4→U5thermal→U6RTboundary→low-z 모듈을 연결한다. 현재 runner를 그 전체 구간이라고 표시하지 않는다. h2와h4의 완성 이력이 같은 coverage를 갖추면 PR108 saved-grid comparator를 적용한다.

## 독립적으로 가능한 h2 low-z: 기존 완성 코드를 실행

R3M full5,210을 다시 계산하지 않는다. `REC_R3M_FULL5210_STORED_OWNER_RAW_001.tar.gz`를 현재 host에서 우선 찾고, 없으면 연결된 Drive/Dropbox 또는 이미 인증된 rclone remote로 Codex가 직접 가져온다. 사용자 수동 다운로드는 요구하지 않는다.

- archive232,521,236bytes; SHA256 `8cd5da29521b47d6b715dfa6889ae11d239ef430460deae97824ee32584b80b9`.
- Drive object `173QaPYquHnrWeS_Rxrb1rRPSk0VrGMmx`.
- Dropbox object `id:BSpOijBcT10AAAAAAD_QGw`.
- 필요 member: `python_u6_rt.npz` SHA `5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2`; `native_oracle_stdout.csv` SHA `57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38`; `verification.json` SHA `1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b`.

archive와 필요한 member를 검증하고 traversal/symlink를 거부하여 새 raw 디렉터리에 안전하게 복구한다. ID를 signed public URL로 임의 변환하지 않는다. 인증된 provider 접근이 실제 없으면 그 접근만 정확한 input dependency로 기록하고 Git-only h4 작업을 계속한다.

`python -B scripts/verify_r3o_lowz.py --mode smoke --steps 16 --raw-dir <agent가복구한디렉터리> --evidence-dir <새경로>`가 기존 완성된 첫 명령이다. 이 smoke는20CPU/60wall/2GiB, 내부 복구3CPU/8wall이다. 같은 코드 smoke receipt가 이미 있으면 hash와 platform scope를 확인해 재사용한다.

full은 `verify_r3o_lowz.py --mode full --raw-dir ... --evidence-dir ... --allocation-json ... --smoke-verification ...`로153,327step을 실행한다. allocation JSON은 코드의 validate_allocation을 그대로 충족해야 한다: 실제 새 allocation_id, allow_full_lowz=true, **실제로 확인한** parent_coordination_confirmed/dual_review_acknowledged, historical_budget_status=CLOSED_HOLD_NOT_RESET, smoke receipt와 정확히 같은 source_code_sha256, 현재 UTC issued/expires, cpu_s/wall_s/memory_bytes/recovery_cpu_s/recovery_wall_s. 실행 직전 host coordinator가 잔여 resource와 기존 review를 확인하고 새600CPU/900wall/2GiB, 복구5CPU/12wall allocation을 발행할 수 있다. 만료는 실행 wall900초보다 뒤여야 한다. 확인하지 않은 review/coordination을 true로 써서 gate를 우회하지 않는다. 정확한 budget은 실제 host ledger에도 합산한다.

## R3P 경로 및 백업 복구

R3P full5,210 재실행은 현재 필요하지 않다. 다른 호스트의 Rust audit 플랫폼 검증이 실제 필요할 때만 기존 `scripts/build_r3p_rust.py`의90CPU/180wall/2GiB build를 사용한다. rustc/cargo1.94.1을 side-by-side로 선택한다. 설치된1.99를 내리지 않는다. runner는60CPU/180wall이고 pilot최대128만 지원한다. 일반 회귀전체를 완료 수 증가 목적으로 반복하지 않는다.

U5 checkpoint가 이 경로에 필요하면 capsule `REC_R3L_REVIEWED_U5_CHECKPOINT.zip`,79,241,895bytes,SHA `3b469781e937fa6a543a007088b73fb5b01a420261e9c4daa2d454cb3ae88106`를 Drive `1oYwz16SYxVEV8PW44aygw8yE4X9CCX2I` 또는 Dropbox `id:BSpOijBcT10AAAAAAD_QBA`로 직접 복구한다. `python_u5_thermal.npz` SHA `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b`를 검증한다.

R3P 최종소스3,410파일 ZIP snapshot0b80913b는122,092,525bytes,SHA `edccebf552671489f91e3ec2c31357fb901b73f90e0230d0cbe24a0b1f524521`. Drive parts 순서는 `1U8bHb_S2hIj2QSef_8jbeFXPhPCuxmqj`, `12BRzh-qCz3M5hfvr4xjKg6ndhKzX8aEQ`, `1z6jRDcaAV3BDXFWdtJi81Csxf2ECLXiI`; Dropbox `id:BSpOijBcT10AAAAAAD_SPw`, `id:BSpOijBcT10AAAAAAD_SQQ`, `id:BSpOijBcT10AAAAAAD_SQg`. 부분 hash는 base BACKUP_ACKS.json을 사용한다. 이 ZIP은 이후 R3Q 신규 코드를 포함하지 않으므로 현재 Git patch도 함께 취득한다.

## 반환·게시·DAG

매 실행 단계 뒤 실제 host/compiler/Python/NumPy/SciPy, git/source/input before-after hash, 시작·종료 UTC, exit code, CPU/wall와 RSS의 측정 범위, 최초 실패, verification/terminal 및 checkpoint의 SHA를 보존한다. reviewed scalar 결과·코드·DAG·receipt를 현재 branch에 commit/push하고 실제 remote SHA를 대조한다. 대형 raw는 기존 Drive/Dropbox 규약으로 백업하고 provider ACK/object ID/size/checksum과 실제 읽기 범위를 구별한다. 인증정보·signed URLs를 repo에 기록하지 않는다.

최종 반환은 (i) 실제 완료 stage와 endpoint, (ii) 같은-h검토, (iii) 전역수렴의 남은 coverage, (iv) 사용한 누적 budget과 남은 allocation, (v) Git/backup IDs, (vi) 다음 h4 stage에 넘길 predictor/photon checkpoint를 포함한다. 외부 결과를 받은 다음에는 완료 노드를 재사용하고 변경된 의존성만 확인한다.
