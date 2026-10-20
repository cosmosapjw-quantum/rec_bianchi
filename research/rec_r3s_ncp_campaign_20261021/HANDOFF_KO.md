# R3R 완료 · R3S NCP 캠페인 인계

## 먼저 읽을 결론

R3R의 실제 spectral-stream NumPy 연결, 32-step 검증, 독립 감사와 CI 복구는 완료됐다. R3S는 그 구현을 새 NCP 플랫폼에서 검사하는 다섯 작업의 유한 DAG와 자원 감독을 구현했다. 원래 numerical runtime은 R3R base 이후 바뀌지 않았다. R3S 로컬 계약은 최초 45개와 신규 deadline 계약 2개, 합계 **47개**이며 영향받는 dummy 세 경우의 재실행은 고유 수에 더하지 않는다.

NCP 새 실행은 **NOT_RUN**이다. Desktop Commander가 월간 사용량 제한을 반환했고 `do not retry or reconnect`를 명시했다. 연결 장치 `cosmosapjw`가 64 CPU/128 GB NCP인지는 아직 확인하지 못했다. 이 상태를 과거 Python/C/Rust runtime blocker와 혼동하지 않는다. 이 스레드의 Python 실행은 실제 성공했다.

`EVIDENCE.json`, `DAG.json`, `receipts/CLAIM_GATE.json`, `receipts/PHYS_MATH_CODE_AUDIT.json`, `BACKUP_ACKS.json`, `DELIVERY.json`과 PR113의 최신 보존 댓글을 함께 읽는다. 최종 보존 ACK는 그 ACK가 들어 있는 commit의 archive와 자기참조하지 않도록 별도 보존 단계로 연결한다. 현재 branch HEAD는 GitHub에서 실제로 읽어 확인하며, 아래 실행 source와 같은 역할로 쓰지 않는다.

## 고정 identity

| 역할 | Commit | Tree |
|---|---|---|
| R3P 실제 구현·U5 실행 | `e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d` | 선행 R3P receipt |
| R3P code/evidence snapshot | `0b80913bf1c665cc4cfab6dfaa3ea35f815a482f` | 선행 R3P receipt |
| R3P 최종 보존 HEAD | `888d56d72579d1e1fd30f66abe02d9f91809a767` | 선행 R3P receipt |
| 복구한 R3Q/NCP 실행 | `1ad0380110621446c42df9d995fd85db3a6c7e7a` | `efd65193713f19d0e60a0617182b3449c7091510` |
| R3Q base/PR111 | `5b44bb21ce0599e55e0848e5e3ff320c9e8ca172` | `9403d3778d0a81e9632cea58e42e59ed9581e980` |
| R3R 과학 구현·실제 실행 | `1313b1f1b2c081d57bcce9c60e757ef79110df91` | `97423cad509a9604269740132a6ad850faf8f19a` |
| R3R CI 테스트 격리 수정 | `70a53396e910869ea069e184a44f1fb21cb47a0a` | `565550bec51506b2a85c48442b9ab0d69be18be7` |
| R3R 종료 / R3S base | `bf6bb95c58182529ad3d773a1dd0ab4f0fc7c70b` | `64c5f41587733f7e2c05ae5f862bba3a6b753f29` |
| R3S 최초 45-case 실행 | `96e8b88d854d1606c6204cefe2f2920f46219dff` | `a4c5005fcf93bb98df31b4a39a3431dd01d7daed` |
| R3S deadline 수정·targeted 검증·plot source | `52f884b7b27814f808b9b4f7fd5ac9a3c6283e32` | `eb2108cfea0cd33577afed425389cbbce2de1189` |

R3R PR112는 `research/rec-r3r-followup-costs-20261020`, R3S PR113은 `research/rec-r3s-ncp-campaign-20261021`이다. 둘 다 draft/unmerged다. Final metadata HEAD는 `DELIVERY.json`과 PR113의 실제 readback에 별도 기록한다. source52 이후 변경이 source/evidence identity를 바꾸면 새 결과를 먼저 분류하고 기존 47 PASS를 그 source의 실행 결과로 바꾸지 않는다.

## 완료 증거를 재사용할 것

- R3P의 R1–R10/C1–C10, 15회 full 저장 스트림 감사, ratio microbenchmark, smoke16, Python214/Rust18 및 CI는 `complete_reused`다.
- R3M full5210은 기존 완료 결과를 재사용한다. R3L 문서의 오래된 pending 문구 때문에 다시 실행하지 않는다.
- 복구한 h4 첫 사건+2는 1,511 accepted/6,044 FULL, source index74411까지의 기존 scoped PASS다.
- h2 low-z는 153,327 accepted/153,328 states/43 checkpoints의 기존 reviewed 반환이다. 당시 CPU60.755865는 이전 600/900 allocation의 값이며 현재60 CPU 통과가 아니다. compact 반환본에서 빠진 native CSV/exit 자료는 여전히 빠져 있다.
- h2 마지막 원본 cubic은 index211713..211716의 네 상태와 `s=1.4726230889209546`을 사용한다. `s`를 [0,1]로 clip하거나 다섯 번째 상태·추가 negative-z RHS를 만들지 않는다.
- R3R은 CSV97,935 records/25,000 spectral lane의 실제 open·parse·allocation·verdict 경로에서 paired CPU 중앙 가속비 **1.3641298365714964**, wall **1.3638913471290828**을 얻었다. binary64 lane 차이0, ordered verdict/guard 동일, 32-step pilot output gate PASS다. 전체 solver 속도 개선은 측정하지 않았다.
- R3R local61 고유 계약, source70a의 실제 CI 일반1038 PASS/103 SKIP/72 subtests, 전용60 PASS/1 SKIP을 구분한다. 복구 중 formal003은 `NOT_RUN / SUPERSEDED_BY_SOURCE70A_CI_RETURN`이다.

## 이번 새 실행 receipt

`receipts/local_validation_001/validation.json`: SHA256 `1aec53bcb0aa0fe6f0648c4738f345adb8d61ab752d79039e63848794a0d98d8`, 45 PASS, CPU3.823868/wall3.818103754, source96e8, exit0.

`receipts/local_validation_002/validation.json`: SHA256 `fa9382e6e8c71ed425a778ba92a2fac7f589cb82ca6667718ee6e26ac99af44e`, 5 PASS(신규2 + 영향받는 dummy3), 누적 CPU7.929026/wall7.837205600, source52f884, exit0. 양쪽 모두 고정 source/input114개 UNCHANGED다.

`receipts/plots_001/plotting.json`: SHA256 `d3e717d5d26d09679592bd96a46e15b48c270bd014ee297b4f29834d877e1ae2`, 새 plot CPU1.834219/wall1.847888912, 같은 allocation 총 **CPU9.763245/wall9.685094512**. 실제 dummy raw만 읽고 PNG/PDF/SVG 한 그림을 생성했다. receipt의 원래 `PENDING_VISUAL_REVIEW` 상태는 바꾸지 않고 별도 root/independent visual review로 연결한다.

Allocation은 `REC_R3S_LOCAL_VALIDATION_20261021_001`, 전체60 CPU/180 wall/2GiB per-process AS, 최종2 CPU/3 wall reserve다. 이 allocation을 새 디렉터리나 ID 해석으로 초기화하지 않는다. 새 NCP 실행이나 REC integration/benchmark는 이 로컬 R3S 검사에서0회다.

## 고정 source의 실제 CI

`receipts/CI_FIXED_SOURCE.json`을 읽는다. 전용 run39503008348은 실제 JUnit47 PASS/0 SKIP이고, 일반 run39503008360은1085 PASS/103 SKIP/72 subtest PASS다. 실제 checkout `71a72b76fc0cbfa0b32a63f3061b793e5634f7d4`의 tree는 source52f884의 `eb2108cfea0cd33577afed425389cbbce2de1189`와 같다. 전용 raw ZIP65,144 bytes/SHA `8a7ee2c116ca2d55312ca62622d51663df1dbeffea1c90fa49b82f3f3cd25901`, manifest60개와 source114개를 직접 대조했다. 전용 CPU3.438309/wall4.533052243는 별도 CI allocation이다. 일반 suite elapsed242.47을 전체 CPU/wall로 쓰지 않는다. 이후 metadata HEAD의 CI와 이 고정 source의 실행 자료는 구별한다.

## NCP에서 남긴 최소 실행

연결이 정상 가용해진 뒤 자동 실행 주체가 최신 REC 결과·세션·hostname·CPU 소유권·실제 affinity/cgroup·RAM을 먼저 읽는다. 최신 완료 receipt가 있으면 source/command/stdout/stderr/exit/raw/환경과 연결하여 재사용한다. 알 수 없는 active PID1579402를 중단하지 않는다. 수동 SSH/SCP 또는 사용자 ZIP 재업로드를 요구하지 않는다.

검토된 source와 입력을 복구하고 `RUNBOOK_KO.md`에 정의된 host intake를 실제 관측값으로 만든다. 준비된 job은 `trace_original`, `trace_interleaved`, `saved_stream_benchmark`, `h4_legacy16`, `h4_numpy16` 다섯 개다. correctness 동시 폭2, timed job 폭1이며 두 pilot은 같은 배정 CPU를 사용한다. CPU ID62/63은 설명용 예시이고 현재 소유권을 뜻하지 않는다.

각 job 한도는60 CPU/180 wall/2GiB 그대로다. 다섯 개의 새 campaign allowance는 명시적으로305 CPU/912 wall이며 선택된 job 수 N에 대해60N+5 /180N+12이다. 기존 닫힌 allocation을 늘리는 값이 아니며 현재 NCP에서 시작하지 않았다. fresh intake·actual allocation·source/input/host/resource gate가 열리면 coordinator를 그대로 실행한다. 기존 numerical source를 고치거나 Python 배열 경로에 Rust 설치를 강제할 이유가 없다. compiler/NumPy/pytest identity를 새 host에서 독립 확인한다.

전체 CSV input은 R3R Stage2 `formal_validation_002/pilot/worker`에서 복구한다. CSV SHA `3f1ab809f7fec021aeccba45c5ab887a82872e66e108e15c4bcb6df14ebb803d`, NPZ SHA `a83f0831c1fb82e2e7d28c85551587671f7aaa0fe3816ff7c4d01953f24c1216`, verification SHA `b7b9247a9bf5a98884a85a8248cc9b7b30135782b76d2a98c76acb34f7037427`를 확인한다. compact fixture로 parsing 성능을 대신 측정하지 않는다.

## 아직 열리지 않은 연구

h4 첫 사건+2 뒤 U4→U5→U6→low-z는 stage 구현·검증이 필요하다. h2 full accepted history의 조립/provenance, 원래 h의 nodewise C parity와 이른 boundary semantics도 해결되지 않았다. `UNCERTAINTY_MISSING`을0으로 채우거나 h4 coverage만으로 전역 gate를 닫지 않는다. 원래 convergence H0=8.49e-5의 level1=4.245e-5, level2=2.1225e-5라는 namespace를 실제 dlna와 연결한다.

R3P Rust build90 CPU 및 R3O build240 CPU/480 wall/3GiB/verifier3GiB는 현재 uniform60/180/2GiB 묶음에 허용되지 않는다. 기존 hard limit을 올리거나 full5210·global full mode를 열지 않는다. public R3R launcher 범위는1..32 steps이며 user pilot 상한128이 이를 자동 확장하지 않는다.

`U5 h HOLD_9_FAIL`, `h/2 HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, `REI_activation=false`, global h/h2/h4 `NOT_RUN`, production speedup `NOT_MEASURED`, physical validity `HOLD`, production `NOT_APPROVED`를 보존한다.

## 복구와 보존

GitHub source와 고정 Git delta archive를 연결한다. R3R Stage1–4와 R3S Stage1의 Dropbox/Library 전체 SHA는 `BACKUP_ACKS.json`에 있다. Stage1 source96e8 archive는374,529 bytes/SHA `498ef4dddddc16ce7efc70de75342b261a13b0bdaf020dac31d7695adca64c93`; 최종 reviewed delivery는 이후 별도 archive다. delta만으로 전체 repo를 복원할 수 있다는 주장을 하지 않는다.

Drive의 기존 UNKNOWN_NO_ACK/NOT_ATTEMPTED/UNKNOWN_NO_ACK_TIMEOUT_25S 상태를 보존한다. metadata read 성공·검색0개를 upload 완료 또는 미완료 요청의 취소로 해석하지 않는다. 동일한 미해결 write 경로를 무작정 반복하지 않는다. R3P Stage0/Stage2 ZIP의 whole readback NOT_RUN 기록도 유지한다.

다음 스레드용 복사 가능한 요청은 `NEXT_THREAD_PROMPT_KO.md`에 있다. 새 연구 노드는 현재 완료 결과를 `complete_reused`로 연결하고, 새로운 비용·동등성·환경 증거가 지지하는 최대 세 후보 중 하나만 선택한다.

### 원본 text 증거의 archive 매핑

생성 SVG와 원시 CI/git/connector text 12개는 원본 공백을 유지하기 위해 `receipts/ORIGINAL_TEXT_EVIDENCE.tar.gz` 안에 보존했다. 크기42,222 bytes, SHA256 `728048efca0483083401d771b726ca0df38ffcf0cf42b391fc7580e8b8080a78`이며 `ORIGINAL_TEXT_ARCHIVE.json`이 원래 logical path와 각 member SHA를 연결한다. 원래 CI/plot receipt는 그 logical path를 유지한다. 새 checkout에서 원문이 필요한 검토자는 archive와 member SHA를 확인하고 해당 경로로 복구한다. PNG/PDF 및 나머지 raw는 직접 Git 파일로 제공한다. 원문 정규화·receipt 변경·whitespace gate 완화는 하지 않았다.

### Stage2 최신 보존 연결

Reviewed delivery `265b82042e918c2554fbb9d890c8e7a7cce5ebfb` / tree `0478d4489837c9b3ac482be46e6871c8b7aad2cc`, archive `REC_R3S_STAGE2_REVIEWED_DELIVERY_265b8204_20261021.tar.gz`, 756,456 bytes, SHA256 `d19c38eb9d4b938851cfef129c71d00a9756e59ba9451d2fe991cdbb7ffddbf0`을 사용한다. Library `libfile_458442bc4688819186a1f5290a221181` / file `file_000000000b34820ba674ad43b65a12ae`, Dropbox `id:BSpOijBcT10AAAAAAD_aJA`의 전체 readback은 각각 PASS다. Git delta base96e8b88d와 code execution52f884b7를 구별한다. 그 뒤 보존 ACK를 기록한 최종 metadata commit과 archive는 PR113의 실제 최종 보존 댓글을 읽어 복구한다.
