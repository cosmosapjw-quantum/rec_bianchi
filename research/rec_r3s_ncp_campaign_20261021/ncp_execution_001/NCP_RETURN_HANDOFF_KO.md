# NCP R3S 실행 반환 (2026-10-21)

- Allocation `REC_R3S_NCP_20261021_001`는 305 CPU초/912 wall초 한도 안에서 시작해 41.782113 CPU초, 33.843081 wall초를 사용했습니다. 원 U5 예산은 `CLOSED_HOLD_NOT_RESET`으로 유지했습니다.
- 실제 장비는 `s1a0e5abed09`, 64 CPU, 총 RAM 135,050,526,720 bytes, 실행 시 usable memory 131,385,700,352 bytes였습니다. cgroup 제한은 CPU/RAM 모두 `max`; 실제 작업은 CPU 62/63에 고정했습니다.
- `trace_original`, `trace_interleaved`: `EXECUTED`, exit 0, scoped PASS.
- `saved_stream_benchmark`: `EXECUTED`; producer exit 0, 25,000 lanes의 binary64 차이 0, median paired CPU/wall ratios 1.387459250445343x / 1.387844484473463x. Campaign verifier가 producer 상태 `PASS_SAVED_STREAM_AUDIT_ONLY`를 받아들이지 않고 `PASS`만 요구해 전체 campaign은 `HOLD`입니다. 재실행은 하지 않았습니다.
- `h4_legacy16`, `h4_numpy16`: 각각 `EXECUTED`, exit 0, 16 additional accepted steps, exact same-h and common-input gates PASS, worker `SMOKE_ONLY`. 이는 U4/U5/U6 완료나 물리적 PASS가 아닙니다.
- `R3Q_h4_first_event_plus_two`와 `R3O_h2_lowz`: `REUSED`, 중복 실행 없음. h4 1511 accepted / 6044 FULL through iz74411; h2 153327 accepted / 153328 states / 43 checkpoints.
- Astra-tier reviewer는 enum 불일치만 campaign 차단으로 보고 최소 exact-enum repair를 승인하는 의견을 냈습니다. 원 terminal HOLD는 보존하고, 구현·회귀검증 및 최종 review를 진행 중입니다.
- `NOT_RUN/BLOCKED`: h4 U4→U5→U6 RT→low-z는 필요한 stage implementation과 원래 U5 gate가 막고 있습니다. h2 full-history assembly/provenance, h nodewise C/early semantics, global three-grid convergence, separate 90/240 CPU build contracts도 미실행/차단 상태입니다.
- 판정: mathematical contract unchanged; numerical platform checks scoped; implementation gate HOLD pending adapter review; performance is saved-stream only; memory caps pass; physical validity HOLD; production NOT_APPROVED.
- Raw receipts and transcripts: `ncp_execution_001/`; canonical results: `NCP_CAMPAIGN_RESULTS.json`, `NCP_EXECUTION_LEDGER.json`, `NCP_FAILURE_LEDGER.json`, `NCP_REMAINING_DAG.json`.

## Closeout 판정

Astra-tier 독립 검토 후 exact producer enum 수용 회귀가 통과하여 benchmark node는 `PASS_SCOPED`로 adjudicate했습니다. 원 `attempt_0001.TERMINAL.json`은 계속 `HOLD`이며 SHA를 바꾸지 않았습니다. 상세는 `receipts/CAMPAIGN_ADJUDICATION_001.json`입니다. allocation 비용은 누적 41.782113 CPU초 / 33.843081 wall초로 보존합니다.

- Backups: Dropbox `id:BSpOijBcT10AAAAAAD_atQ` and new Google Drive object `1w4RYJ56kF3HbDag0n8-_XCuRyKXu52Uy` each ACKed create-only upload; whole readbacks both match `cb51d9500b27b6fb503a3cd5390eb2d32b77142c7d0930de12753325bf19acce` over 21866513 bytes. Prior Drive UNKNOWN_NO_ACK remains separate and unresolved.
