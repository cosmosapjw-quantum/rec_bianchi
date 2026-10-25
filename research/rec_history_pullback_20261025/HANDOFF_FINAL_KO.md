# REC-HISTORY-PB01 최종 인계 — S3 후보 20/20, 실제 게시 조건

Workflow: physmath-research-loop built-in1.0.0 / approvedv0.2.
과학 범위는 `COMPLETE_SCOPED_SOURCE_HISTORY_PULLBACK`, 판정은
`PASS_SCOPED_ENDPOINT_QUERY_PULLBACK_AFTER_SAVED_EVENT_PAIRING_REPAIR`다.
부모 REC-HISTORY는 PARTIAL이다. 불변 scienceS2 snapshot은 **18/20**이며,
Companion의 실제 이중 ACK와 중앙 게시·보존 readback을 확보했다. 이 단일 final REC S3
후보가 **실제 게시되면** R10/C10을 포함한 R1–R10+C1–C10=20/20 마감이 성립한다.
게시 전에는 준비된 후보다. 최종 commit identity는 `CONTAINING_COMMIT`으로 결속하고
실제 SHA는 게시 후 PR137 본문과 최종 chat에 기록한다.

## 먼저 읽을 파일

- `delivery/PUBLICATION_STATE.json`: 현재 실제 전달 상태와 남은 마감 순서.
- `delivery/S2_RECEIPT.json`, `delivery/S2_REMOTE_READBACK.json`: S2 게시·이중 백업·원격 검증.
- `delivery/CENTRAL_RECEIPT.json`, `delivery/central/ACTUAL_REMOTE_READBACK.json`: 중앙 게시와 보존 검증.
- `CLAIM_GATES.json`, `REPORT_KO.md`, `SCIENTIFIC_METRICS.json`: 판정과 실제 결과.
- `NEXT_INPUT_CONTRACT.md`, `DATA_LOCATIONS.md`, `BUDGET_LEDGER.json`, `STAGE_PROGRESS.md`.
- `evidence/independent_review/FINAL_REVIEW.md`: 같은 독립 reviewer의 최종 범위 검토.

`delivery/FINAL_COMPANION_RECEIPT.json`에는 실제 companion ACK가 있다.
이 영수증은 포장 이후 생성됐으므로 불변 S2·companion ZIP 안에 포함되지 않는다.

## 실제 게시·백업과 남은 순서

REC 저장소는 `cosmosapjw-quantum/rec_bianchi`, branch는
`research/rec-history-pullback-20261025`, draft PR137이다.
S1 commit은 `ccf3199a27f5d42845a895e6dc4c6a2d500ac8dd`, 최초 실패 보존 S1F는
`7c17b82c06bc42c47a9ec64e9cc5ee52ecb54237`, 실제 scienceS2는
`f9051f10f02582d6b339d8738f1e9796953941d4`다.

S2 archive는 69,336,495 bytes이며 SHA256은
`b43ec958374bb8ba97073c46355dc26131a64261cd5004fa64e65c6565da00d1`이다.
Dropbox `id:BSpOijBcT10AAAAAAD_-Dw` / rev `65ea5beccbee90af03d47`와
Drive `1eHZ_wuG_4J_mgDrBvtRGe2QBpx_kpCAw`의 실제 ACK가 있다.
다운로드한 전체 size/SHA, outer ZIP CRC, 712개 payload 개별 size/SHA/CRC가 PASS다.
이전 KS01 ZIP은 바깥 member identity만 확인했으며 이전 science를 다시 검증하지 않았다.
원 S2 ZIP은 불변이다. 별도로 남은 incomplete PENDING prefix의 관측과 미해결 원인은
`delivery/S2_PENDING_FILE_OBSERVATION.json`에 있다. 그 파일은 두 번째 검증된 archive가 아니다.

중앙 저장소는 `cosmosapjw-quantum/rei_bianchi`, 소유 branch는
`research/orchestration-rec-history-pullback-20261025`다.
Captured base `b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4` / tree
`210f15423ab8f79f691ae8a1a6cc7128b1094bff`에서 실제 commit
`219fe60a3f069dda26e109f6e0cd1fd339c83701` / tree
`8188397a0e94faac70c4352b14cc807b3e384843`로 게시했다.
[PR229](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/229)는 open/draft다.
PR228 donor의 기존 18개 REC observation field를 이월하고 PB01 하나를 추가했다.
원 40 contracts/17 edges/7 authorities, 다른 38개 node, plan status, AGENTS와
고정 handoff를 보존했다. 실제 10개 경로의 blob/size/mode와 보호 subtree readback이 PASS다.
고정 권한은 `rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`이다.
Assembler/renderer/merge/activation은 0이며 canonical branch를 쓰지 않았다.
중앙 관측은 불변 scienceS2 18/20을 기록한다.

Compact companion은 한 번 생성해 실제 이중 전달을 완료했다. 크기는 421,395 bytes,
SHA256은 `e1c252ac62a97c86ab699e2b95111c8963a277c9a86620b6ce544376803d37fd`다.
Dropbox `id:BSpOijBcT10AAAAAAD_-Ew` / rev `65ea60534a9cd0af03d47`와
Drive `1HlxOZOEDLbfEbrtYwaau6pWtRqm11V-E`의 실제 ACK 및 metadata size가 PASS다.
Local whole SHA/CRC/152 payload는 PASS이며 remote whole SHA는 측정하지 않았다.

남은 동작은 이 ACK와 최종 상태를 담은 단일 REC S3 후보의 실제 게시다. 그 게시가
R10/C10과 최종 단위20/20 마감의 조건이다. Identity는 `CONTAINING_COMMIT`이며,
실제 SHA는 PR137 본문과 최종 chat에서 후속 결속한다. Companion의 포장 당시 snapshot은
18/20이고 자신의 ACK나 미래 S3 SHA를 포함하지 않는다. Archive·중앙 commit 재생성은 없다.

## 실제 실행 코드와 현재 코드의 구분

Historical executed-preexec는 `PASS_RUN_READY`, PB01-PREEXEC-001은 CLOSED다.
이 검토를 거쳐 **실제로 한 번 실행한 최초 primary**의 SHA256은
`bc63fd1868710548f27381a6bbaea8d6b445357436a5fdc009e8997c03a66b26`이며,
그때의 18-entry execution manifest SHA256은
`34140f9a776162b13f19b39be0a1353952c1918a5d5fc250a0fdb3dd3c7dc0e0`이다.
첫 primary는 exit2 `FAILED_FROZEN_CRITERION`이었다. 같은 event의 독립 point 합산이
6/8 case에서 1–2 ULP의 sign-pair 차이를 냈다. 원 381개 raw/execution 파일과
독립 atomic 결과를 그대로 보존했다.

후속 saved-data 교정은 저장된 32개 vector에서 radiation을 보존하고
`atomic=-radiation`으로 결속했다. 첫 네 성분은 byte 단위로 동일하며 8/8 case가 PASS다.
새 matvec나 primary 재실행은 없었다. 최초 그림과 교정 그림도 모두 보존했다.
Root와 같은 독립 reviewer가 실제 PNG를 확인했고 최종 A–H는 PASS다.

**현재 소스**의 primary SHA256은
`ac69a3578ff45c0363fcc194ef694135543217f342eb861c06712c5eb6590ebb`,
현재 19-entry manifest SHA256은
`879c8543c679b296a155a6b3202aa900d68657731a423da0e51035756b1c0cd3`이다.
이 소스에는 shared-event helper가 추가됐지만 **수정된 전체 primary는 NOT_RUN**이다.
수락 근거는 최초 passing evidence와 한 번의 saved-data repair이며, 현재 소스의
전체 실행을 검증했다고 해석하지 않는다. 원 executed source, manifest와 diff는
`evidence/implementation_history/event_pair001/` 및 S1에 보존했다.

## 원 입력과 수락 범위

Source는 z=1099.9986525171403, T0=2.728 K,
nH0=.18745798773143102 m^-3이며 313개 query, prefix5127,
626개 서로 다른 endpoint slot을 사용했다. 원 history는 35,239,470 bytes,
SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`이다.

A=KsP, C=Ks diag(g), coordinate adjoint, 정확한 mixed remainder
r_j=(xi_j/h)(dy_Rj-dy_Lj)와 조건부 finite box를 완성했다.
Endpoint norm은 [1.17562722922718,1.1756272292401908],
query norm은 [6.289216981912579e-13,6.28921698191771e-13]이다.
Native-order fraction과 KS01 admission의 산술 차이를 별도 bridge로 보존했으며
이를 physical uncertainty로 사용하지 않았다.

통제된 5개 child의 합은 4.237821 CPU / 4.424445926 execution-wall s,
1 thread, 최대 RSS92,200 KiB다. 별도 측정 reviewer CPU는 .035253 s,
현재 known CPU subset은 4.273074 s, 이전 비용을 포함한 known lineage subset은
36.442061486 CPU s다. Unknown·I/O·remote CAS·전체 turn 비용을 0으로 처리하지 않았다.
97 operator/200 event actions, 10 interval passes, 32 sign assignments를 기록했다.
New RHS/solve/inverse/native/IVP/old campaign replay/primary rerun은 모두 0이다.
정확한 자원 근거와 측정 범위는 `BUDGET_LEDGER.json`을 따른다.

## CI와 보존 이력

REC S2 실제 CI는 `python scripts/verify_repo.py --quick`의 whitespace·EOF 진단으로 RED다.
PB01 소유 evidence/vendor 11개 경로의 12개 경고도 포함하므로 전부 과거 문제라고
분류하지 않는다. 중앙 실제 CI는 `cargo fmt --check`에서 RED이며 이번 중앙 projection의
Rust source 변경은 0이다. Test 단계는 각각 앞선 실패 뒤 SKIPPED다.
수동 CI rerun이나 frozen audit/vendor bytes 정리는 수행하지 않았다.
`evidence/ci/S2_CI_READBACK.json`과 `CENTRAL_CI_READBACK.json`이 실제 run 근거다.
Scoped science PASS와 CI 상태는 별개다. Final S3 CI는 실제 게시 후 별도 조회하며
현재 그 결과를 미리 주장하지 않는다.

Workspace 소실은 `RUNTIME_INTERRUPTION_RECOVERY`, 원인은 UNRESOLVED다.
S0 Git은 남았고 미업로드 S0 ZIP은 소실됐다. S0R은 별도 identity와 실제 ACK를 가진다.
KS01 S2의 206개 payload와 THERMO S2의 485개 payload를 원 bytes로 복원했다.
복원·재구성 등급과 최초 실패를 보존했으며 완료 science를 재실행하지 않았다.

## 다음 실제 입력 의무

H5에는 동일 cosmology의 독립 reference와 불확도, endpoint uncertainty 또는
정당화된 whole-cell curvature/defect bound가 필요하다. H6에는 actual incident trace와
선택한 Bianchi geodesic/direction/frame/measure/volume/clock/source/query owner의
결속이 남아 있다. H7에는 실제 DY, DQ, Dtheta와 reference variation 및
retiming/geometry/thermal-ODE 연결이 필요하다.
Physical epsilon/reference/endpoint/curvature/absolute-history/outgoing bound는 null이다.
다른 cosmology의 finer trajectory, same-h parity, storage equivalence로 H5를 인증하지 않는다.
완료된 THERMO01/RESP01/LINE02/KS01/PB01 및 기존 campaign을 재실행하지 않는다.

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false;
first failed REI raw HISTORICAL_LOCAL_ONLY를 유지한다. Global physical completion은 null이다.
다음 작업은 변경된 의존성과 실제 입력을 확인하고 hypothesis/identity/error allocation/
acceptance/cumulative budget을 동결한 뒤 수행한다. 이 인계는 새 IVP/native runtime,
merge 또는 activation에 대한 승인이 아니다.
