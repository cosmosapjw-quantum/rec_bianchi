# R3T-U4B 반환 인계

## 결과

실제 실행 source `a09e1d249d4cf4b706c09571fa7f231c8084c251` (tree `2186e9a53316b040bbfa6a02da09d9378b28baf0`)로 NCP allocation `REC_R3T_U4B_NCP_20261021_001`에서 U4B 32 accepted step을 한 번 실행했다. U4A final checkpoint 74443에서 74475까지 진행했고 event/thermal/RT 경계는 범위 안에서 발생하지 않았다. 자동 U5/U6 진입은 없었다.

동일 invocation의 systemd terminal CPU는 5.375101 s, worker/supervisor 종료코드는 각각 0/0, MemoryPeak 336064512 B, worker RSS 139264 KiB, worker wall 4.165756 s다. 관측 controller 구간 포함 합계는 5.538856 CPU s지만 전체 allocation CPU와 wall은 사전 실패·controller bootstrap/final write·unit stop 이후 구간 누락 때문에 `UNRESOLVED`다. Addendum은 원 receipt를 수정하지 않고 이를 정정한다. I/O bytes는 측정하지 않았다.

## 상태

- `EXECUTED`: U4B bounded 74443→74475 및 scoped same-h/common-input/native/split 검사.
- `REUSED`: U4A 74411→74443 checkpoint와 이전 R3P/R3M/R3Q/R3R/R3S 결과.
- `NOT_RUN`: 경계 crossing, global convergence, speedup, U5/U6.
- `BLOCKED`: 다음 U4 continuation은 이번 단일 allocation 소비 및 자동 연속 금지로 새 resource contract 없이는 시작하지 않음.

독립 검토는 `PASS_SCOPED_U4B_NUMERICAL_RESTART`다. U5 h `HOLD_9_FAIL`, h/2 `HOLD_8_FAIL`, ledger `CLOSED_HOLD_NOT_RESET`, REI false, physical `HOLD`, production `NOT_APPROVED` 유지. PR114 draft/unmerged.

상세 증거: `ncp_execution_001/NCP_CAMPAIGN_RESULTS.json`, `NCP_EXECUTION_LEDGER.json`, `NCP_FAILURE_LEDGER.json`, `NCP_REMAINING_DAG.json`, `NCP_AUDIT_RESULTS.md`, `NCP_BACKUP_RECEIPTS.json`, `receipts/addenda/ALLOCATION_ACCOUNTING_ADDENDUM_001.json`, `evidence/`.

Dropbox create-only backup: `dbx:bianchi/rec_bianchi/20261016/REC_R3T_U4B_NCP_EXECUTION_001_20261021.tar.gz`, provider object `id:BSpOijBcT10AAAAAAD_eiA`, size 16,076,737 bytes. Independent full-object readback SHA256 equals `55a96cd1f82c271e8c2b4946407850fbf46e5578d4bec72c9ba05694d34b56d9`. Google Drive was not attempted; existing `UNKNOWN_NO_ACK` remains unchanged.
