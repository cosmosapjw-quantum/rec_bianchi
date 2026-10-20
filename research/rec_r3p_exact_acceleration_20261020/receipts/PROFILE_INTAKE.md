# REC R3P — read-only local profile intake

## Finding and scope

**First target: the native-stream audit, which consumed 21.409138 s / 56.9572% of the completed full-U6 profile.** Begin with invariant reuse and removal of per-record object allocation while retaining the scalar arithmetic and record-state machine. Common-input oracle history packing is the next substantial allocation candidate; its whole measured phase is 9.7416%, with copying versus source evaluation not separately timed.

Inspected checkout: `/workspace/scratch/afe554957b2e/rec_work`, HEAD `368d87ad5de90dde74226ed109c3ba29d9607c84`; tracked tree clean. Locators below are relative to that exact root. All 109 V6 manifest file hashes and all six additional source hashes in the R3M profiles match the checkout. The profile's execution commit is `d0e534b1f5b4bb20fe19875f6d502681b833470d`, not the current documentation HEAD.

Policy read: requested `physmath-research-loop/SKILL.md`, `RESEARCH_POLICY.md`, `CODING_LOOP.md`, `EVIDENCE_AND_HANDOFF.md`, and `RUNTIME_AND_LEGACY.md` (policy 1.0.0). Work performed: parallel local receipt/source/contract reads and hash/accounting calculations. No callable research-agent/spawn tool was exposed; no agents or recursive agents were launched. No integration, benchmark, tests, source edits, or implementation were performed. Parent owns remote backup intake and implementation selection.

Fixed scope: original HyRec October 2012 source; effective step **4.245e-5** (called h2 in receipts), q=0; original atomic/thermal operators, predictor memory, stage guards, and same-h gates; REI=false. Original U5 h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, historical cost `CLOSED_HOLD_NOT_RESET` persist. The full h2 U6 **5,210 steps are complete and must be reused**.

## Actual measured hotspots

Denominator: R3M full profile **37.588099 process-tree CPU s**, measured wall **42.119583 s**. Entries are **exclusive parent + reaped-child CPU**. The earlier verifier receipt ends at 37.570540 CPU s / 42.045047 wall s; mixing its denominator with later profile phases would be incorrect. Pilot denominator: 17.377438 CPU s. Both ledgers report valid accounting and no profiling/closeout errors. Journal closeout hashes match the profile files; linked verification hashes also match.

| Phase | Full CPU s | Full fraction | Pilot fraction | Exact implementation locus; implication |
|---|---:|---:|---:|---|
| Native-stream validation | 21.409138 | **56.96%** | 72.20% | `scripts/verify_r3i_h2_u6_rt_boundary.py:159`, `compare_native_stream`; first optimization target. |
| Owned integration, exclusive | 5.837440 | **15.53%** | 1.64% | `src/full_bianchi_hyrec/trajectory/primordial_2012_owned_u6.py:14`, `integrate_u6_owned`; history gathering, atomic/thermal work and unseparated wrapper overhead. No atomic-kernel breakdown. |
| Common-input source samples | 3.661671 | **9.74%** | 0.94% | `scripts/verify_r3i_h2_continuation.py:143`, `check_one_source` → `scripts/verify_r3i_h2_start.py:141`, `FullSourceCOracle.__call__`; 42 samples. |
| Native run | 3.461247 | 9.21% | 14.66% | `scripts/verify_r3i_h2_u6_rt_boundary.py:141`, `_run`, called by `main` for `native_u6_rt`; includes original C run, text output and wrapper/hash work. |
| Native + common builds | 1.202938 | 3.20% | 6.41% | Same `_run`; compiler commands in `main`, lines 374/379. |
| Observer/accept/attempt callbacks, exclusive | 0.659654 | 1.75% | 0.11% | Same verifier, `AcceptedEvidenceWriter` at line 94 and `main.<locals>.observer` at line 397; nested source/causal checks excluded. |
| Checkpoint load | 0.508769 | 1.35% | 2.74% | `src/full_bianchi_hyrec/trajectory/primordial_2012_refined_u6_rt_boundary.py`, `load_frozen_checkpoint`. |
| Causal link audit | 0.437828 | 1.16% | 0.07% | `scripts/verify_r3i_h2_u6_rt_boundary.py:71`, `causal_link_count`; 5,210 repeated geometry reconstructions. |
| Stored history write | 0.135164 | 0.36% | 0.47% | `scripts/r3l_u6_cost.py:144`, `write_stored_history`, via `HistoryNumpyProxy.savez_compressed`; already optimized. |
| Other setup + unattributed | 0.274250 | 0.73% | 0.76% | Closure/extraction/setup plus 0.181292 s full-run unattributed CPU. |

`owned_integration` **inclusive** is 10.596593 s (28.19%): it already contains sampled source checks, causal checks and callbacks. Do not add inclusive and exclusive rows. Stored write wall is 2.757484 s (6.55% of profile wall, including explicit fsync). Pre-entry CPU 0.700553 s and post-summary profile read/hash/write/fsync, final journal/console, backup and recovery are outside the denominator. These are instrumented phase measurements, not cProfile/line-level measurements; uninstrumented overhead can be charged to enclosing phases.

Primary receipts: [full profile](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3m_u6_full_owner_20261019/receipts/full5210_stored/full5210_stored.r3l_profile.json), [pilot profile](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3m_u6_full_owner_20261019/receipts/pilot128_stored/pilot128_stored.r3l_profile.json), [full verification](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3m_u6_full_owner_20261019/receipts/full5210_stored/verification.json). Timing ownership is explicit in `scripts/r3l_u6_cost.py:185`, `instrument_verifier`, and `PhaseLedger.measure`/`summary`; the launcher is `scripts/run_r3l_u6_profiled.py:51`, `execute`.

## Ranked changes for the parent to choose

### 1. Stream audit: scalar invariant reuse first; bounded block parsing second

`compare_native_stream` handles **5,254,162 prefix fields + 3,256,250 V/A/L fields**, in addition to HE/STEP/control rows. Each prefix field recomputes `c.redshift(RT_IZ+col)` and the same column temperature (line 225). Each spectral field recreates the V/A/L array dictionary (line 274), computes a temperature (281), a scalar `math.expm1` (282), and repeated tag-to-metric mappings (317).

Low-risk first change: hoist immutable dispatch maps; lazily compute the identical scalar temperature once per column/step; reuse each V-bin blackbody factor for its same-step A bin. For this receipt that removes **1,620,310 duplicate blackbody evaluations**, derived from record counts, and changes prefix redshift evaluations from 5,254,162 to 16,733. Keep the original `math.expm1`, operand association, finite checks, max calculation, and ordered exception path. Only O(311) cache space is needed. Overall processing remains O(314P+625N); speedup is unmeasured.

A later bounded parser can amortize CSV splitting/conversion and process a column or capped batch at a time. Preserve exact tag/index/bin order, the 4,096-line CPU-guard cadence, counts, first offending record, END ownership, and the original-average failure/forensic path. Do not materialize millions of Python row objects or replace scalar libm with NumPy transcendental evaluation without bitwise evidence. A malformed or failing block must retain ordered diagnostics rather than validating a later record first. Keep C/Python histories distinct and complete for forensic ownership.

### 2. Small, safe geometry cache

`causal_link_count` calls `_source_edges`, validates energies, allocates source/target arrays, and evaluates `log(src/dst)/4.245e-5` on every input. Cache only this immutable geometry/delay vector against the exact table and step identity. Continue the per-step `emit`, active mask and `floor(emit)+1 <= j-1` guard and count all 313 links. This removes repeated setup allocation/logs within the **1.16%** phase; per-step checking remains O(313). `OwnedFLRWHistory.incoming` already caches its lookback, but recomputes static `rows = self._src[columns]-offset` at line 89; those row indices can also be stored at construction. No future column or interpolation-weight precomputation is needed.

### 3. Common-oracle workspace: substantial allocation opportunity, medium engineering risk

`FullSourceCOracle.__call__` packs F-order accepted views into C order through `np_carray` (line 164). The C adapter `scripts/c_harness/original_hyrec_r3i_h2_u6_rt_boundary_harness.c:256`, `rec_r3b_original_full_step`, then allocates `(311+311+3)*(j+1)` doubles and recopies all accepted virtual/Lyman history before invoking the **unchanged** `rec_HMLA_2photon_dxHIIdlna`.

For the actual 42 sample indices, the Python packing alone copies **2,029,060,464 payload bytes**; the C prefix copy repeats the same volume. The largest sampled C histories occupy 109,270,000 bytes, excluding allocator overhead. These are source-derived work volumes, not measured bandwidth or a subdivision of the 3.661671 s phase.

A separately bound persistent C workspace with explicit row strides/pointers could copy the initial prefix once and only the newly accepted Python columns at subsequent samples: O(314 sum(j_sample)) copying becomes O(314(P+N)). Retained capacity is O(625(P+N)), about 110 MB at this horizon. It requires explicit owner/checkpoint/table identity, reset rules, lifetime control, and strict `iz` bounds. The oracle's own candidate column must never become the next Python accepted history; overwrite it from the actual accepted owner when advancing. Use separate workspaces for distinct forensic owners. Preserve all 42 samples. **C `setup()` already caches the rate tables** (lines 194/197); table rereading is not this problem.

### 4. Owned integration: allocation cleanup only after narrower evidence

`OwnedFLRWHistory.__init__` copies inputs into temporary F-order arrays, then into capacity buffers; `integrate_u6_owned` copies all accepted output histories again at return. `append` validates and copies each candidate before atomic commit. Buffer initialization/final transfer may be streamlined only with independent returned-array ownership and failure atomicity preserved.

Within `full_2012_atomic_source.py`, `populate_original_full_atomic` rebuilds the static 311×5 diffusion input table (line 264); this can be cached by immutable table identity in a separate implementation lane. The original escape factors are evaluated during population and completion, but reuse would need per-snapshot identity and byte checks. These costs have **no separate measured fraction**. The source already caches its canonical table and already solves only an 80-bin tridiagonal block with three RHS plus a 2×2 Schur system (`OriginalFullAtomicSnapshot.instantaneous_schur_solution`, line 154). Reusing factors across different states, changing exp cancellation behavior, or substituting another integrator would alter the contract.

Callbacks are a smaller opportunity: serialize each outgoing field once for both hashing and writing. Preserve source-before-accept order and each partial-evidence flush. Further compression work has low CPU value because stored NPZ is already in use; fsync removal would change durability.

## Completed speed / no-speed evidence to reuse

- **R3K, re-audited by R3M:** actual pair16 legacy/owned CPU 0.323913188 / 0.202954646 s (1.596 ratio); pair128 2.452338713 / 0.328992197 s (7.454 ratio), byte identity reported and raw receipt audit recorded. These are single paired bounded integrations. Source: `research/rec_r3k_owned_validation_20261018/EXECUTION_001.json`, `research/rec_r3m_u6_full_owner_20261019/INDEPENDENT_REVIEW.md`.
- **R3L:** three actual U4 storage pairs, compressed/stored median CPU 0.362180466 / 0.016110076 s (22.4816 write-only ratio), identical NPY members/array bytes; file sizes 9,645,700 / 11,939,450 bytes (+23.78%). Source: `research/rec_r3l_profiled_history_20261019/STORAGE_BENCHMARK.json`. Full compressed-versus-stored U6 comparison was not run.
- **R3M:** full 5,210-step same-h run completed, original average failures zero; separate recorded review is `REVIEW_PASS` for same-h parity. V/A/L maxima are 1.7688723656877556e-5 / 0.01016409195990302 / 1.7690729538503825e-5. Reuse the stored raw; this intake did not repeat the review or integration.
- **Latest local R3O:** `HANDOFF_KO.md` and `rust_ci_4512b19e/numerical/verification.json` retain `speedup: NOT_RUN`. Rust fixed predictor matched 102 C scalar fields; RODAS is exploratory and its xe discrepancy reaches 2.530216356188792 times the original same-h tolerance. Related VigilODE comparison has problem-dependent rankings and shared-host promotion hold; its receipts are context, not HyRec timing evidence. Full h/h2/h4 convergence and production speedup remain unestablished. No literature-based performance or convergence inference was made.

## Preservation contracts and implementation validation needed

**Packaging:** `SOURCE_MANIFEST_V6.json` freezes the original verifier, helper oracles, atomic module, and C harness. Do not edit that baseline or rewrite its manifest to make an optimization pass closure. Follow the existing opt-in adapter pattern: explicit implementation selection, exact clean HEAD and added-source hashes, original reference callable retained, binding restoration on success/failure. Relevant tests: `tests/trajectory/test_r3l_u6_cost.py` (source binding, callback object identity, restored bindings, exclusive accounting, first-error preservation, caps, create-only NPZ/identical members).

**New stream differential tests are needed.** The current U6-specific test file exercises causal/event/cap/partial-write contracts but does not call the U6 `compare_native_stream`. Use parent-recovered saved full/pilot streams and NPZ for audit-only comparison; do not rerun the 5,210-step integration. Compare exact maxima, counts, statuses and empty/nonempty diagnostic bytes. Add bounded corrupt-record cases for unknown/reordered/missing/duplicate/nonfinite records, BASE/STEP/END boundaries, a guard failure, and original-average failures including the 64-failure limit and preserved raw diagnostics. Keep the frozen scalar auditor as the independent baseline.

**History/recurrence:** `tests/trajectory/test_owned_flrw_history.py` covers 313-value byte equivalence, no growing-prefix rescan, caller mutation isolation, read-only views, atomic append/capacity, face-clock rejection, recurrence and no excess source call. `test_r3k_backend_comparison.py` covers real U4/native source snapshots and one-bit corruption; `test_r3k_pair_driver.py` covers independent recurrences, input mutation and incomplete intervals. Workspace changes additionally need multiple checkpoints/owners, sampled-index jumps, C-call failure/reset, and proof that only accepted Python columns are ingested.

**Physics/guards:** retain RT start 36446, U6 input start 53179, stop 58389 before any EMLA evaluation, and `Y[n+1]=Y[n]+h*(1.25*F[n]-0.25*F[n-2])` with both H/T memory pairs. Keep `math.nextafter` at the thermal table endpoint. `test_primordial_2012_refined_u6_rt_boundary.py` fixes predictor tails, checkpoint hash, caps, 313 past-only links, thermal event fields and surviving partial bytes. `test_full_2012_atomic_source.py` fixes immutability, sparse diffusion roles, residuals, scalar-C-libm cancellation behavior at tau=1e-6 and native/source separation. These were inspected, not newly executed.

Recommended implementation selection: **stream scalar caching/dispatch first**, then the small geometry cache; consider persistent oracle storage only with its ownership contracts. Candidate gains are unmeasured. Parent can use the saved raw for comparator development and verification without reopening the completed full-U6 integration.
