# R3T-U4A 반환 handoff

## 판정

새 h/4 U4 restart 구현과 NCP 32-step 검증 결과를 보존했다. 연구 구간은
**`PASS_SCOPED`**, global accepted index `74411 → 74443`이다. 이번 구간에서는
event가 발생하지 않아 `NO_EVENT_WITHIN_BOUND`이며 U4 stage exit를 주장하지
않는다.

독립 결과 검토는 32-step 수치 구간을 `PASS_SCOPED`로 판정했고, 정확한
systemd terminal journal의 관측 자원량을 `PASS_SCOPED_OBSERVED_RESOURCE_BOUNDS`로
별도 판정했다. 원 supervisor `CAP_HOLD`와 SHA는 그대로 보존한다. 다음 실행 전에
terminal CPU-accounting 재조정 결함을 고쳐야 하며, 이번 allocation은 소비되었고
이어 실행할 수 없다.

## 실행 identity

- Allocation: `REC_R3T_U4A_NCP_20261021_001`, 단일 launch.
- Source commit/tree: `44715efbf7822dca28aa367d637b8ba36d3b1558` /
  `5a20935016e521f9768bbdd068300d3fa6dda164`.
- HyRec archive SHA256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- R3Q checkpoint SHA256:
  `7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9`.
- Source closure SHA256:
  `0332531f65a2851119f50806cdf7bc384b494b09759fcf5d497d6c1a7d032bcf`.
- NCP: `s1a0e5abed09`, x86_64, Xeon Gold 5220, 64 logical CPU, affinity 0–63,
  one NUMA node, 135,050,526,720 B RAM total / 131,337,134,080 B available at
  intake. Worker pins to one CPU for the serial causal recurrence.
- Runtime/compiler: Python 3.12.3, NumPy 2.3.5, SciPy 1.17.0, GCC 13.3.0.
- Frozen resource limits: 60 CPU s / 180 wall s / 2 GiB per process; supervisor
  early-kill thresholds 50 CPU s / 150 wall s. No relaunch.

## 결과 요약

- Accepted 32 steps, 128 primary Python FULL evaluations, end global index
  74443, H_ONLY, `post_saha=true`.
- Common-input: 128 C reference comparisons; max scaled RHS
  `2.75968137e-12`; max V/A/L lane tolerance ratios
  `2.60257e-5 / 3.18139e-4 / 5.78427e-6`.
- Native same-checkpoint restart: PASS; max state scaled `3.79652e-14`, H RHS
  scaled `1.61423e-11`, lane tolerance ratio `2.42056e-4`, maximum accepted
  Schur residual `5.860e-16`.
- 16+16 split and one-shot 32 have exact floating-value equality (byte identity
  was not tested). Missing/duplicate/uncommitted history and pre-source stage
  guards pass targeted local tests.
- Systemd terminal journal: scope CPU 5.346 s, memory peak 321.3M, successful
  deactivation. Supervisor wall 5.425340 s. Worker RUSAGE snapshot 4.212451 CPU
  s / 4.218228 wall s stops before final evidence hashing and JSON writes and
  excludes imports/bootstrap/teardown.
- I/O bytes and throughput were not measured; this node is not a performance
  benchmark. Raw native output, accepted records, per-step checkpoints and
  binary causal streams are retained under `evidence/`.

## Status labels

- **EXECUTED:** one R3T-U4A 32-step bounded restart; targeted local tests.
- **REUSED:** R3Q checkpoint/source closure; completed R3P/R3M/R3Q/R3R/R3S
  results. None were rerun.
- **NOT_RUN:** event/post-Saha exit, U4 completion, U5/U6 continuation, global
  convergence, whole-production speedup, physical validity, production
  admission, performance benchmark.
- **BLOCKED:** further U4 work needs a separate reviewed allocation; fix the
  supervisor's cgroup-removal terminal accounting before another invocation.

## Preserved ceilings

Original terminal HOLD SHA
`eaee72446c4f8b2e5ce8de52a8a508e88a3dfb34f3697b070db29af239006625` remains
unchanged. U5 `h=HOLD_9_FAIL`, U5 `h/2=HOLD_8_FAIL`,
`CLOSED_HOLD_NOT_RESET`, `REI_activation=false`, global convergence
`NOT_RUN`, physical validity `HOLD`, and production readiness
`NOT_APPROVED` remain unchanged.

## Artifacts

- Detailed results: `NCP_CAMPAIGN_RESULTS.json`
- Execution/cost ledger: `NCP_EXECUTION_LEDGER.json`
- Failure classifications: `NCP_FAILURE_LEDGER.json`
- Remaining DAG: `NCP_REMAINING_DAG.json`
- Independent audit: `NCP_AUDIT_RESULTS.md`
- Raw execution evidence and receipts: this directory's `evidence/` and
  `receipt/` subdirectories, plus `resource_terminal_readback_*`.
- Provider receipts: `NCP_BACKUP_RECEIPTS.json`. Dropbox upload and whole-object
  SHA readback passed; the new Google Drive path remains `UNKNOWN_NO_ACK` after
  a stalled upload and has no readback. The prior Google Drive unknown object
  is unchanged.
