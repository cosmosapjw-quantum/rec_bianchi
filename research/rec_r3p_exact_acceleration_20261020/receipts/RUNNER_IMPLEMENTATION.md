# R3P source-bound U6 runner: final C9 handoff

Date: 2026-10-20. Checkout: `/workspace/scratch/afe554957b2e/rec_work`.
Status: READY FOR PARENT STAGE2 SOURCE PUBLICATION AND ACTUAL16 SMOKE.
This note supersedes the previous runner handoff, particularly its former preflight/closeout budget exclusions. Code and focused tests are stable; no further repository edits are planned by this worker.

## Owned paths and final identities

Only these three repository paths were changed for the runner task:

| Path | SHA256 at final handoff |
|---|---|
| `scripts/run_r3p_u6_audited.py` | `4e0e2482b163c044b9b1b35a8831a7d57aa6440ad8fac98ec79d00889a6f1bb4` |
| `scripts/run_r3p_u6_supervised.py` | `e22c11253f450b3b4b07cc9212d0ebafb1a2bc0d29844cac14de7f453ab437f9` |
| `tests/trajectory/test_r3p_u6_audited.py` | `d7d5dbc24f9eb1e57ebcfad2788fd315129d15eaba4818116d080bf7fe34d84d` |

No frozen verifier/manifest, old R3L launcher, scalar/Rust adapter, builder, parent documentation, or benchmark source was edited. No commit, push, Rust build, physical integration, C build, or benchmark was performed here. Parent owns source publication and physical smoke. The requested physmath-research-loop coding/evidence policy was applied; existing evidence was reused, independent reads were batched, and no recursive agents were used.

## C9-01: whole-launch supervision and inherited limits

The documented public entry is now `scripts/run_r3p_u6_supervised.py`. Executing `scripts/run_r3p_u6_audited.py` also delegates to this supervisor before numerical imports. Both accept the same CLI options. The existing programmatic runner `execute(...)`, `main(...)`, and argument parser remain usable as worker APIs; their receipts explicitly distinguish inner-verifier limits from public whole-launch supervision.

The supervisor uses the unchanged `build_r3o_rust.Budget` with 60 CPU seconds, 180 wall seconds, and 2 GiB. The existing 2 CPU / 3 wall second final-receipt reserve is retained: the work ledger rejects consumption beyond 58 CPU seconds or 177 wall seconds. There is no 90-second outer limit, no cap increase, and no allocation reset.

The ledger starts before importing the budget helper and numerical worker/parser. The complete worker is a supervised child: source binding, input hashes, existing Rust receipt/library checks, original C compilation and execution, owned integration, native audit, and worker closeout all fall inside its process-tree accounting. Supervisor closeout and worker-receipt hashing are included in final resource accounting. Only final supervisor receipt serialization/fsync is excluded from the measured record and covered by the unchanged reserve. A wall alarm covers supervisor parser/import work and closeout as well. The supervisor's own CPU and address-space limits are capped at the same requested limits while preserving lower inherited limits.

The resource proxy is module-local and temporary. `InheritedResourceLimits` clamps requested CPU/AS soft and hard limits to the inherited values; it never attempts to raise either. Thus the frozen verifier's `(60, 60)` CPU request works under the Budget child's approximately `(58, 59)` inherited allowance. The proxy also covers the frozen verifier's child preexec limit requests through its scoped module binding. The unchanged Budget helper's child preexec resource binding is temporarily proxied as well so an even lower enclosing executor limit is respected. All these bindings restore in `finally`; no frozen source or Budget threshold/monitor/kill method was changed.

Memory scope is explicit in `supervision.json`: **per-process RLIMIT_AS plus polled worker-and-descendant RSS**. The supervisor's RSS is not included in the child-tree RSS total, and this is not an exact aggregate of parent plus child memory. The docstring now says **No Rust compilation** and explicitly acknowledges that the unchanged worker compiles the original C verifier.

For evidence destination `/path/run`, the new create-only supervisor directory is `/path/run.r3p_supervision/`, with `supervision.json`, worker command receipt, and captured stdout/stderr. The original `/path/run/`, `.r3l_phases.jsonl`, `.r3l_profile.json`, and `.r3p_execution.json` remain. The supervisor status describes budgeted worker completion; scientific acceptance still comes from the unchanged original verification receipt. Failures preserve existing partial evidence and do not rewrite the physical verdict.

## C9-02 and C9-03: explicit audit input and failure contracts

The Rust settings receipt records exactly four ASCII comma-separated fields for PV/PL, canonical ASCII unsigned-decimal indices, finite positive temperature/energy, and finite tolerance. It explicitly labels this stricter than legacy and states that legacy trailing-field acceptance and incidental exception types are not preserved.

Earliest logical failure ordering is scoped to the bounded block actually delivered to Rust. Resource, transport, size, and guard aborts may precede errors in undelivered rows. Cached scalar behavior retains the original scalar record order and guard boundaries, with its documented Python prefix nonfinite rejection. The parent owns corresponding adapter docstrings and their implementation; those files were not changed here.

## Preserved source/physical contract

Default mode remains a 16-step smoke from the hash-pinned original U5 checkpoint. Pilot mode permits only 1..128 steps. The original h2 value remains `4.245e-5`; original HyRec2012 atomic/thermal operators, stage guards, REI=false, and original same-h C comparison remain inherited from the frozen path. Historical h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, and `CLOSED_HOLD_NOT_RESET` remain unchanged. There is no full-run or 5210-step path through the bounded CLI.

Exact 40-character commit, clean tracked sources, original checkpoint digest, and original ZIP digest remain mandatory. The V6 manifest and its 109-file closure remain frozen. External ZIP selection changes only the archive's physical location, not its expected bytes. Source extras now include the supervisor in addition to the audited runner/test, scalar adapter/test, parent Rust adapter/build sources, all Rust crate/ABI sources, Cargo lock/manifest, and vendor metadata/archive. Restored historical data remain manifest-hash authenticated without incorrectly requiring them to be tracked.

Cached mode remains default. Rust mode requires an existing successful offline build receipt and matching complete source/vendor/library identities; no Rust compile is performed by this runner. Identity checks occur before use and at closeout. Rust uses a one-thread pool created only inside the comparator after the frozen verifier establishes one-CPU affinity. Comparator result/gates are forwarded directly. Binding and argv restoration, first-failure preservation, create-only evidence, and durable accepted partials remain covered by focused tests.

## Focused verification actually completed

The final whole runner test invocation was bounded by an external nine-second timeout and pinned to CPU 4:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  taskset -c 4 timeout -s TERM -k 0.5s 9s \
  /workspace/scratch/afe554957b2e/rec_env/bin/python -B -m pytest \
  -q -p no:cacheprovider tests/trajectory/test_r3p_u6_audited.py --durations=5
```

Result: **72 passed in 2.84 seconds**, exit 0. This includes all original 61 runner cases plus inherited-limit, scoped-restoration, whole-launch receipt/reserve, failure-retention, and public-dispatch coverage.

After the final documentation and explicit memory-scope field/assertion change, only the affected existing case was rerun with the same command envelope and `-k real_budget_child --durations=1`. Result: **1 passed, 71 deselected in 1.46 seconds**, exit 0. The child call itself took 0.27 seconds. No unrelated coverage was expanded.

That case launches one tiny real Python child using the actual R3O Budget. It records an inherited CPU hard limit below 60, calls the scoped proxy with the frozen `(60, 60)` request, and verifies the limit remains unchanged; it also verifies the 60/180/2GiB receipt, 2/3 reserve, memory-scope fields, successful child return, receipt persistence, and restored helper binding. The other physical/build collaborators remain synthetic. No physical integration, C/Rust compilation, ctypes loading, or performance loop was run. All three final files parse successfully and have no trailing whitespace.

Actual verifier C builders under the inherited clamp and the exact-source physical 16-step smoke remain the parent's next verification. Passing these runner tests does not claim physical convergence or measured integration speedup. Parent benchmark results are separate evidence and were not repeated or reinterpreted.

## Parent command after publication

Publish all three owned paths with the parent's changes, then use the resulting clean exact commit. `REC_R3P_ALLOCATION_ID` identifies the already-authorized bounded allowance; the command creates no new allocation. `REC_R3P_EVIDENCE` must be a fresh absolute path.

```bash
/workspace/scratch/afe554957b2e/rec_env/bin/python -B \
  /workspace/scratch/afe554957b2e/rec_work/scripts/run_r3p_u6_supervised.py \
  --checkpoint /workspace/scratch/afe554957b2e/rec_recovery/u5/python_u5_thermal.npz \
  --source-zip /workspace/scratch/afe554957b2e/rec_work/archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip \
  --expected-commit "$REC_R3P_COMMIT" \
  --new-allocation-id "$REC_R3P_ALLOCATION_ID" \
  --evidence-dir "$REC_R3P_EVIDENCE" \
  --mode smoke --audit-backend rust \
  --build /workspace/scratch/afe554957b2e/rec_runs/r3p_build_001/build.json \
  --block-columns 32 --history-container stored
```

For cached scalar mode use `--audit-backend cached` and omit `--build`. The old public audited filename delegates to the same supervisor; no alternate unsupervised public CLI flag was introduced.
