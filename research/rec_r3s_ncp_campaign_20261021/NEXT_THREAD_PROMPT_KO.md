# REC R3R/R3S 이후 연구 재개 요청

$physmath-research-loop $scispace $exa $wolfram

`cosmosapjw-quantum/rec_bianchi`의 R3R 종료와 R3S NCP 캠페인 인계를 이어서 수행하라. production v3/rux, BASS/rec/RUN19, 별도 REI lane과 구분한다.

**첫 행동은 새 실제 실행 반환 확인이다.** GitHub PR110/111/112/113 및 관련 branch/comment/actions, 연결된 이전 대화, Google Drive/Dropbox/Library, 정상 가용한 NCP/다른 실행 스레드에서 새 receipt를 먼저 확인하라. 서비스 error나 quota 때문에 조회하지 못한 범위를 “새 결과 없음”으로 바꾸지 마라. 새 반환이 있으면 actual source/tree, command, stdout/stderr, exit, raw SHA, 검증과 host/compiler/runtime identity를 먼저 분석하라. 사용자에게 과거 대화 복사, 수동 SSH/SCP, ZIP 재업로드를 요구하지 마라.

주요 기준은 `research/rec_r3s_ncp_campaign_20261021/`의 HANDOFF_KO.md, EVIDENCE.json, DAG.json, REPORT_KO.md, CAMPAIGN.json, NCP_PENDING_JOBS.json, RUNBOOK_KO.md, BACKUP_ACKS.json, DELIVERY.json, receipts/CLAIM_GATE.json, PHYS_MATH_AUDIT.json, PHYS_MATH_CODE_AUDIT.json, CI_FIXED_SOURCE.json, local_validation_001/002 및 plots_001 receipt다. PR113의 최신 보존 댓글까지 읽고 **최신 metadata HEAD를 원격에서 실제 확인**하라.

고정 identity를 혼동하지 마라:

- R3P 실제 source e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d / snapshot0b80913bf1c665cc4cfab6dfaa3ea35f815a482f / 최종HEAD888d56d72579d1e1fd30f66abe02d9f91809a767.
- 복구한 R3Q/NCP source1ad0380110621446c42df9d995fd85db3a6c7e7a; PR111base5b44bb21ce0599e55e0848e5e3ff320c9e8ca172.
- R3R 실제 과학 실행 source1313b1f1b2c081d57bcce9c60e757ef79110df91, CI 수정70a53396e910869ea069e184a44f1fb21cb47a0a, 최종basebf6bb95c58182529ad3d773a1dd0ab4f0fc7c70b.
- R3S 초기45검증source96e8b88d854d1606c6204cefe2f2920f46219dff.
- R3S deadline수정·추가검증·plot source52f884b7b27814f808b9b4f7fd5ac9a3c6283e32, treeeb2108cfea0cd33577afed425389cbbce2de1189. 이후 metadata HEAD와 구별한다.
- PR112/113은 draft/unmerged. R3S branch는 research/rec-r3s-ncp-campaign-20261021.

완료된 R3P/R3M/R3Q/R3R를 재실행하지 말고 `complete_reused`로 연결하라. R3R은 실제25,000 binary64 ratio lane 차이0과32-step raw 동등성을 확인했고, 저장된 전체 CSV의 parsing·allocation을 포함한 감사 경로 paired CPU 중앙 가속비1.3641298365714964를 측정했다. 전체 solver나 NCP 가속률은 아니다. R3S local45+신규2=47고유계약, 영향받는dummy3재검증, 실제 그림생성은 동일allocation누적CPU9.763245/wall9.685094512였다. 첫 validation와후속targeted의source역할을보존하고 CI반복을새고유수로더하지마라.

NCP 도구는 이전 스레드에서 월간 사용량 한도와 `do not retry or reconnect`를 반환했다. 장치는 paired/online이었으나64CPU/128GB host인지, actual REC 결과/CPU 소유권은 확인하지 못했다. 알려지지 않은 PID1579402를 중단하지 않았다. 그 제한이 계속되면 재시도·우회하지 말고 나머지 허용된 일을 진행하라. 정상 가용성이 회복되면 과거 runtime blocker를 자동 적용하지 말고 Python/C++/Rust를 필요한 범위에서 독립 확인하라.

NCP에서 코드 수정 없이 준비된 유한 job은 trace_original, trace_interleaved, saved_stream_benchmark, h4_legacy16, h4_numpy16다. 실제64CPU/128GB라는 명칭만으로 병렬도를 키우지 마라. 현재 ready폭2, timed폭1이다. source/input/host/cgroup/메모리/CPU소유권/최신receipt gate, freshhostintake, 명시적새allocation을 갖춘 뒤 `scripts/run_r3s_ncp_campaign.py`를 사용하라. 각job60CPU/180wall/2GiB를 유지하고,5job합계allowance305CPU/912wall은 이전닫힌장부를늘리는값이아니다. 실제host·path·CPU·intake는관측값으로채운다. 완료job은wholehash검증해재사용하고부분실패비용/STARTED상태를초기화하지마라. Rust90CPU이상/3GiB작업은현재묶음에강제로넣지마라.

h2 endpoint의 원본4점stencil은211713..211716, s=1.4726230889209546이다. [0,1] clip·다섯째상태·추가negative-zRHS를만들지마라. 남은h4 U4→U5→U6→low-z stage구현, h2fullhistory조립, 원래h nodewise_C_parity UNKNOWN/이른boundary semantics, UNCERTAINTY_MISSING은별도연구gate다. fullh4coverage만으로전역수렴을PASS시키지마라.

원래HyRec atomic/thermal operator,predictor,causal/stage,same-h tolerance를유지하라. U5원래h HOLD_9_FAIL/h2 HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI_activation=false, globalh/h2/h4NOT_RUN, newproduction speedupNOT_MEASURED, physicalHOLD/productionNOT_APPROVED를보존하라. full5210/fullmode에새allocation을추론하지마라. publicR3Rlauncher1..32단계가실제구현범위다.

각의미있는단계에actualsource/tree·명령/exit/stdout/stderr/hash·입력·CPU/wall/RSS범위·동등성·실패복구·독립감사·raw/plot·GitHub·create-only백업·DAG를남겨라. Drive의기존UNKNOWN/NOT_ATTEMPTED와R3PStage0/Stage2ZIPwholeNOT_RUN은유지하고uploadACK와독립전체readback을구별하라. 가능한코드수정/가벼운검증/감사/push를여기에서완료하고NCP에는컴파일/작은호환수정/허용된실제실행만남겨라. 최종에수학·수치동등성·구현·실측가속·메모리자원·물리타당성·production7축을별도로판정하고다음스레드용handoff를출력하라.
