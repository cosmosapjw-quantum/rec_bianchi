# R3S: 유한 NCP 플랫폼 배치 실행 계약

## 현재 상태와 범위

이 파일은 `bf6bb95c58182529ad3d773a1dd0ab4f0fc7c70b`에서 열린 별도 R3S 연구 노드의 실행 명세다. 실제 R3S source SHA는 이 coordinator·tests·CAMPAIGN이 함께 게시된 고정 commit을 사용한다. 원래 R3R 수치 실행 source `1313b1f1b2c081d57bcce9c60e757ef79110df91`, CI 격리 수정 source `70a53396e910869ea069e184a44f1fb21cb47a0a`, R3R 최종 보존 base `bf6bb95c…`를 구별한다. 원래 R3R subtree와 적분·감사 runtime은 수정하지 않는다.

현재 연결 장치 `cosmosapjw`가 online이라는 응답은 받았으나, Desktop Commander의 월 사용량 제한이 실제로 반환됐다. 요청된 64 CPU·128 GB NCP인지, 현재 Python/C/Rust 환경과 REC 결과·세션 상태가 어떤지는 확인하지 못했다. 도구가 명시한 제한을 따라 재시도·재연결·우회하지 않는다. PID1579402 세션을 REC 작업이라고 식별하거나 중단하지 않았다. 따라서 이 문서와 `--plan`은 NCP 새 실행이 완료됐다는 증거가 아니다.

기존 R3P 15회 감사·smoke16, R3M full5210, R3Q 첫 h4 사건+2, R3O h2 low-z, R3R25000 lane binary64 비교와 새32-step pilot·감사 benchmark는 `complete_reused`다. 이미 끝난 결과를 64개 코어에 반복 배치하지 않는다. 상세 경로·해시·이전 pending 문구의 대체 근거는 `NCP_PENDING_JOBS.json`에 있다.

## 실행 가능한 frontier

| Job | 직접 선행 | 실행 방식 | 새 작업의 판정 범위 |
|---|---|---|---|
| `trace_original` | 없음 | 두 trace job끼리 병렬 가능 | 기존 실제32-step retained fixture 계약의 새 플랫폼 재검증 |
| `trace_interleaved` | 없음 | 두 trace job끼리 병렬 가능 | 기존 임의 V/A/L interleave 계약의 새 플랫폼 재검증 |
| `saved_stream_benchmark` | 두 trace PASS | 단독 실행 | 저장된 전체 CSV의 open·parse·allocation·verdict 비용. 5 alternating paired rounds, warmup1 별도 |
| `h4_legacy16` | 두 trace PASS | 단독 실행 | 고정 start에서 기존 public launcher의16-step legacy pilot |
| `h4_numpy16` | legacy16 PASS | 단독 실행, 같은 배정 CPU | 같은16-step NumPy pilot와 양쪽 raw/NPY member byte gate |

현재 독립 correctness frontier의 최대 폭은2이고, timed job의 폭은1이다. 각 job을 늘려 64개 코어를 채우지 않는다. 전체 accepted trajectory의 연속 단계는 현재/prev2 RHS와 이미 채택된 photon history에 의존하므로 이 배치가 병렬 적분기로 바꾸지 않는다. 같은16-step pilot의 출력 일치는 전역 수렴성이나 production 속도 개선 판정과 다르다.

고정 allowlist는 `scripts/run_r3s_ncp_campaign.py`에 있다. JSON을 바꿔 `full5210`, 후속 h4 stage, 새로운 shell command, public32-step 초과 모드 또는 임의 thread 수를 실행할 수 없다. 현재 `ready`는 **코드가 준비됐음**을 뜻하며, 현재 host·입력·source·allocation gate를 통과해야 실행된다.

## 자원과 계측

각 job은 기존 제한인 **60 CPU s / 180 wall s / process당2 GiB address space**를 유지한다. 더 낮은 inherited soft/hard limit을 올리지 않는다. job guardian은 56 CPU/168 wall 부근에서 작업을 중단하고 cleanup/receipt reserve를 남기며, 바깥 coordinator도 58 CPU/177 wall 경계를 감독한다. 원래 R3R launcher와 benchmark 자체의 제한도 유지된다.

다섯 job을 전부 선택할 경우 새 캠페인의 명시적 상한은 **305 CPU s / 912 wall s**다. 이는 선택한 `5×60`, `5×180`과 controller/closeout reserve `5 CPU/12 wall`의 합이다. 기존 단일60-second allocation을 늘리거나 과거 비용을 초기화하는 값이 아니다. 부분 선택 시 필요한 직접 선행까지 포함한 job 수 N에 대해 `60N+5`, `180N+12`를 정확히 요구한다. 최종 작은 receipt에는 최소2 CPU/3 wall reserve를 둔다.

CPU admission은 실제 affinity와 cgroup v2의 모든 보이는 조상 `cpu.max` 최소값을 사용한다. 메모리는 `MemAvailable`과 모든 조상 `memory.max-memory.current` 중 작은 값을 사용하며, controller2 GiB와 active/new job의 full allowance를 보수적으로 예약한다. 합산 RSS를 가용 메모리에 다시 더하지 않는다. cgroup v1/hybrid 또는 해석할 수 없는 경로는 fail closed 한다. 논리 CPU64·명목128 GB만으로 사용 가능한 자원을 판정하지 않는다.

두 correctness job은 별도 명시적 CPU ID를 배정받는다. timed job이 ready가 되면 기존 job을 끝낸 다음 그 job만 실행하며, 두 pilot은 동일한 첫 배정 CPU를 사용한다. OMP/OpenBLAS/MKL/NumExpr/Rayon thread 환경 변수는1로 고정한다. 이 coordinator의 host lock은 다른 R3S controller만 조정하므로 별도 production/BASS/REI 작업의 CPU 소유권은 현재 읽기 전용 host intake로 확인해야 한다.

각 job은 새 Python process, 빈 pycache prefix, stdlib bootstrap limit와 Linux subreaper guardian을 사용한다. guardian이 먼저 종료하고 새 session의 후손을 남기면 HOLD하고 owned children을 정리한다. coordinator 역시 subreaper여서 guardian의 비정상 종료 뒤 입양된 후손을 검출한다. 정리는 열린 `/proc/PID` descriptor에 묶인 `pidfd_send_signal`을 사용하고 숫자 PID로 다른 프로세스를 신호하지 않는다. 직접 자식의 PPID를 같은 descriptor에서 확인하고, 종료·wait 후 입양된 자식이 없어질 때까지 반복한다. 지원하지 않는 kernel/권한 환경을 성공으로 표시하지 않는다.

CPU는 기다린 guardian과 그가 reaped한 후손의 rusage, controller의 preflight·setup·verification·최종 hashing 비용을 포함한다. wall은 Python module entry부터 측정하며, 모든 preflight/실행/closeout에 전체 deadline이 적용된다. RSS는25/50 ms 주기 표본과 `wait4.ru_maxrss`를 별도 기록한다. RSS 표본은 shared-page 중복과 표본 간 peak를 갖는 계측이므로 정확한 전역 aggregate memory peak라고 주장하지 않는다. kernel의 process별 AS hard cap과 구별한다.

## 선행 입력과 host intake

새 NCP 접근이 실제로 회복되면 연결된 host에서 **읽기 전용**으로 현재 REC 결과와 활성 작업을 먼저 확인한다. 다음 receipt를 자동 실행 주체가 생성하고, 원본 inventory/session 결과 파일을 보존한다. 사용자가 직접 터미널 명령을 실행하거나 ZIP을 옮겨야 한다는 요구가 아니다.

`--host-intake`는 다음 구조의 실제 JSON을 받는다. 관측 시각은 실행 전10분 이내여야 하며, 기존 matching job이 있거나 배정 CPU가 busy로 기록됐으면 실행을 막고 해당 증거를 먼저 재사용한다. 단, `--resume`가 동일 source/input/host/allocation의 완료 output을 먼저 해시 검증한 job은 허용하며 실제 실행 queue에서 제외한다. 외부에서 발견된 완료 job을 미검증 상태로 이 예외에 넣지 않는다.

```json
{
  "schema": "rec.r3s.current-host-intake.v1",
  "hostname": "ACTUALLY_OBSERVED_NCP_HOST",
  "source_commit": "FIXED_R3S_SOURCE_SHA",
  "observed_unix_s": 0,
  "assigned_cpu_ids": [62, 63],
  "examined_job_ids": ["trace_original", "trace_interleaved", "saved_stream_benchmark", "h4_legacy16", "h4_numpy16"],
  "matching_completed_job_ids": [],
  "busy_cpu_ids": [],
  "inventory_files_sha256": {"/absolute/authorized/host_inventory.json": "ACTUAL_SHA256"}
}
```

위 host·CPU·시각·해시는 설명용 자리표시자다. 과거 NCP의 CPU62/63 배정을 현재의 빈 자원으로 사용하지 않는다. 실제 matching completed job이 발견되면 그 캠페인의 검증된 resume/재사용 경로를 먼저 복구하며, 새 allocation으로 같은 완료 작업을 복제하지 않는다.

저장 스트림 benchmark는 전체 raw를 요구한다. 커밋된 compact fixture는 correctness test용이며 parsing 성능 측정에 대신 넣지 않는다. `--raw-dir`는 R3R stage2 보존본의 `formal_validation_002` NumPy pilot worker를 복구한 디렉터리다.

| 파일 | SHA256 |
|---|---|
| `native_oracle_stdout.csv` | `3f1ab809f7fec021aeccba45c5ab887a82872e66e108e15c4bcb6df14ebb803d` |
| `python_continuation.npz` | `a83f0831c1fb82e2e7d28c85551587671f7aaa0fe3816ff7c4d01953f24c1216` |
| `verification.json` | `b7b9247a9bf5a98884a85a8248cc9b7b30135782b76d2a98c76acb34f7037427` |

처음 profile32의 verification SHA611b…와 위 formal002 receipt SHAb7b…는 서로 다르다. 두 raw 수치 파일이 같아도 receipt를 같은 객체로 취급하지 않는다. 원래 ZIP48cd…와 h4 checkpoint40dd…는 고정 Git source closure에서 확인한다. source/입력의 최종 readback과 Python·NumPy/pytest 배포 metadata·compiled binary·C compiler identity를 보존한다.

## 자동 실행 entry point

계획은 child job을 실행하거나 호출자의 resource limit·affinity를 변경하지 않는다.

```bash
python3 -B scripts/run_r3s_ncp_campaign.py --plan \
  --expected-commit "$R3S_SOURCE_SHA" \
  --raw-dir "$R3S_RAW_DIR"
```

현재 host/source/input gate를 통과한 자동 실행 주체는 검토된 새 allocation과 경로를 다음 entry point에 전달한다. 이 명세 작성 단계에서 NCP 실행이 할당되거나 수행됐다는 뜻은 아니다.

```bash
python3 -B scripts/run_r3s_ncp_campaign.py --run \
  --expected-commit "$R3S_SOURCE_SHA" \
  --allocation-id "$R3S_NEW_ALLOCATION_ID" \
  --expected-host "$R3S_OBSERVED_HOST" \
  --cpu-ids "$R3S_ASSIGNED_CPU_IDS" \
  --host-intake "$R3S_HOST_INTAKE_JSON" \
  --raw-dir "$R3S_RAW_DIR" \
  --evidence-dir "$R3S_NEW_EVIDENCE_DIR" \
  --campaign-cpu-seconds 305 --campaign-wall-seconds 912
```

별도 설치된 pytest 경로가 필요한 경우 `--test-pythonpath`를 명시하고 그 runtime identity를 보존한다. `--jobs`는 위 allowlist의 부분집합만 선택한다. `--resume`는 같은 evidence directory와 allocation ID, 정확한 source/input/host/runtime/CPU 집합/캠페인 상한만 허용한다. `rec_r3s_allocation_registry`는 repository parent에 create-only로 보존되며 같은 ID를 다른 output 디렉터리에 재사용할 수 없다. 기존 terminal의 유한·비음수·단조 cumulative 비용을 차감한다. 완료 output은 해시를 확인해 재사용하고 실패·부분 job 디렉터리는 덮어쓰지 않는다. 닫히지 않은 STARTED attempt는 살아 있거나 비용이 불명확한 실행으로 보존하고 자동 재개하지 않는다.

`events.jsonl`에는 campaign/job start·terminal의 monotonic 시각이 남는다. 각 job에는 실제 argv, exit code, stdout/stderr, LIMITS/GUARDIAN/TERMINAL JSON, output 해시가 남는다. trace에는 JUnit와 기존25000 lane child JSON, benchmark에는 기존 raw benchmark/lane trace, pilot에는 원래 worker CSV/NPZ/partial photons/receipts가 보존된다.

## 여전히 실행 불가능한 연구

R3Q h4의 첫 사건+2 이후 U4→U5→U6 RT→low-z stage 구현과 검토는 존재하지 않는다. source·causal recurrence·stage gate를 먼저 완성해야 하며 현재 배치는 이 단계의 full 명령을 생성하지 않는다. h2는 source-defined endpoint의 **네 상태211713..211716**를 이미 보유한다. 기존 cubic의 `s=1.4726230889209546`을 [0,1]에 clip하지 않으며, 추가 negative-z RHS step을 만들지 않는다.

또한 h history의 `nodewise_C_parity=UNKNOWN`, input29195 이전 regime semantics `UNKNOWN`과 h2 전체 stage provenance가 남아 있다. full h4만 완료해도 `signed_triplet`의 `UNCERTAINTY_MISSING` gate가 열리지 않는다. 검증되지 않은 nodewise 오차를0이나 integer-z aggregate maximum으로 채우지 않는다.

R3P Rust build의90 CPU s, R3O Rust build의240 CPU/480 wall/3 GiB, R3O verifier의3 GiB envelope는 이 배치의 uniform60/180/2 GiB와 맞지 않아 blocked다. 기존 source의 제한을 바꾸거나 현재 toolchain을 내리지 않는다. optional Rust blocker는 NumPy frontier의 실행을 막지 않는다.

`U5 h=HOLD_9_FAIL`, `h/2=HOLD_8_FAIL`, 역사 장부 `CLOSED_HOLD_NOT_RESET`, `REI_activation=false`, 전역 h/h2/h4 `NOT_RUN`, production speedup `NOT_MEASURED`와 readiness `NOT_APPROVED`를 보존한다.

## 검증 상태와 문헌

초기 작성 뒤 R3S source96e8에서45 PASS, source52f884에서 신규2+영향받는dummy3의 targeted5 PASS를 실제 확인했다. 고유 계약은47개다. 실제 검증 명령·source/input identity·CPU/wall·stdout/stderr·exit·독립 감사와 CI는 `EVIDENCE.json`과 해당 receipt에 기록했다. 새 NCP scientific workload는 여전히 NOT_RUN이다. 원본 validation/plot receipt의 상태를 사후 변경하지 않는다. 세 더미 process case는 fresh bounded child에서만 돌며 기존 pytest process의 limit/subreaper를 변경하지 않는다. `--basetemp` 아래 각 case의 `driver.stdout.json`, `driver.stderr.log`, `run/events.jsonl`, job logs/receipts가 timeline plot의 실제 입력이다.

구현 근거는 [Python subprocess 문서](https://docs.python.org/3.12/library/subprocess.html), [Linux PR_SET_CHILD_SUBREAPER](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html), [Linux pidfd_send_signal](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html)이다. 스레드가 있는 parent의 `preexec_fn`을 사용하지 않으며 subreaper 설정을 각 guardian에서 직접 확인한다. PID descriptor의 안정된 process 참조와 전통적인 numeric PID signal의 재사용 race를 구별한다.
