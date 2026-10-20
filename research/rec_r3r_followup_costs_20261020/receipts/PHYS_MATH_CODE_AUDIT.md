# R3R independent PHYS-MATH-CODE audit

**Verdict: PASS_SCOPED.** The reviewed comparator, source-bound launcher, and replay benchmark implement the declared local audit contract. Three P2 findings and one receipt-scope clarification were resolved before this verdict. No open P1/P2 finding remains in this review scope. Formal committed-source regression, benchmark, pilot, and CI receipts remain separate execution gates.

Reviewer: /root/context_intake. The reviewer authored neither the comparator/benchmark nor the supervisor. Methods: direct source inspection, reuse of the independent PHYS-MATH derivation, an actual stale-bytecode counterexample, and five independently executed source-binding probes against a synthetic local Git fixture. No solver or saved-stream performance benchmark was run by this reviewer.

## 1. Exact reviewed source

Final source hashes were read at 2026-10-20 17:41:16 UTC. These working files were still awaiting the implementation commit. A later shipping receipt must bind these blobs to that actual source commit.

| Source | SHA256 | Role |
| --- | --- | --- |
| scripts/r3r_stream_audit.py | 10021e086b9f842dce21cf18a9b1207bdcdc127c56384715b181500db3b9aea8 | Bounded spectral comparator |
| scripts/run_r3r_h4_supervised.py | fe8c946a8b0bdbab53d813c46ce22d188f6a0117b6872607d33032666a8fd85f | Source-bound smoke launcher |
| scripts/benchmark_r3r_stream_audit.py | 4b6f99e085aa016e0bbff3a67673ad3646b53bca793c1b6f7b9c9921547e3dd4 | Saved-stream benchmark |
| scripts/build_r3o_rust.py | d33f4761482720cd822a3006460e9462091c9219180541e78cdc51a4ca35cfd5 | Frozen Budget and closeout code |
| scripts/verify_r3q_h4_continuation.py | 30b415cbf1328c89ac96a864b7bd99b91c2f52fc59481f75cdafaaa70d42261a | Frozen worker and reference |
| research/rec_r3q_h4_continuation_20261020/SOURCE_CLOSURE.json | 0332531f65a2851119f50806cdf7bc384b494b09759fcf5d497d6c1a7d032bcf | 100-file frozen closure |

The initial base was 4a1912b661f4227707ad7efa93df56bfa47f930a. At final inspection HEAD was 46ebb765d2c5c8af6d53c5b59ade1a405d4551be with the same tree eac9172f63a3b4a07181e4c9a97258e680d066b0. Neither metadata identity is substituted for the pending implementation source commit.

The separate PHYS_MATH_AUDIT.md/.json applies to the unchanged comparator blob. Its lane-independence, dimensions, rounding graph, NaN/scalar replay, and signed-zero arguments are complete_reused here.

## 2. Equation-to-code and call path

| Contract | Implemented path | Review result |
| --- | --- | --- |
| Original Planck-scaled ratio | scalar math.expm1 cache plus separate float64 ufunc operations in comparator flush | Original grouping and coefficients retained |
| Independent V/A/L lanes | source-ordered metadata/parsing, at most 625 pending rows | No integration or causal-state update |
| Original first failure | full-block scalar replay; drain before control, guard, EOF, and later input exceptions | Original exception class/message retained within declared input contract |
| State/RHS/branch/event checks | copied control dispatch calls frozen helper functions | No relaxed physics gate |
| Selected audit backend | frozen worker's compare_native_stream is wrapped; branch calls either candidate or captured original | Source-bound callable path; call timing/stats retained separately |
| Actual integration | worker.main receives fixed smoke mode, fixed checkpoint, and requested extra-step count | No event/full adapter or solver substitution |
| Source binding | expected HEAD, Git blob framing, manifest SHA256, before/after checks | Fail-closed file identity |
| Resource supervision | frozen Budget plus stricter inherited-limit adapter | Original ceiling and reserves preserved |

The launcher changes the comparator binding and clamps environmental limits; it does not monkeypatch the atomic source, integrator, observer selection, accepted-state recurrence, same-h tolerances, event criteria, or common-input oracle. The frozen worker records the same source and compiled native/shared-library hashes. R3R does not transplant a new solver.

## 3. Resolved findings

### PMC-F1 — Public step range exceeded the frozen worker's range (P2, implementation)

The initial launcher accepted 1..128 while the frozen worker accepts smoke 1..32. A request for 33..128 would terminate in argument parsing rather than run the advertised pilot. The correction restricts the public launcher to 1..32 and records the user's separate 128-step ceiling. This is a stricter admissible pilot range. The source contains no event/full mode.

Closure evidence: final source inspection and tests/test_r3r_supervised.py rejection cases for 0, -1, 33, 129, 8192 and event mode. Their formal execution belongs to the parent's regression receipt.

### PMC-F2 — -B did not bind imported code to sealed source bytes (P2, implementation/reproducibility)

An independent executed fixture compiled VALUE=1, rewrote the source to same-size VALUE=2, and preserved its timestamp. Python -B imported VALUE=1 from the old timestamp-valid bytecode. With a fresh cache prefix it imported VALUE=2. Both subprocesses exited 0. Thus preventing bytecode writes alone was insufficient for the intended source-identity claim.

The final supervisor creates separate empty, create-only cache prefixes before project imports. Its child receives -B and -X pycache_prefix from process startup; run_worker verifies the expected empty prefix. Existing caches are not removed. The benchmark similarly creates a fresh prefix for CLI execution. This closes the observed stale-bytecode path under the normal public CLI execution contract.

Python documents -B as preventing bytecode writing; sys.pycache_prefix controls both reading and writing in a separate cache tree. [CPython command-line documentation](https://docs.python.org/3.14/using/cmdline.html#cmdoption-B), [sys.pycache_prefix documentation](https://docs.python.org/3.14/library/sys.html#sys.pycache_prefix). The actual counterexample and recovery outputs are preserved in the companion audit JSON, rather than being inferred only from those documents.

### PMC-F3 — Benchmark numerical imports preceded its resource envelope (P2, resource/implementation)

The original benchmark applied limits in main after importing NumPy and project code. The final source calls install_limits only for CLI execution before those numerical imports. It clamps inherited limits downward and installs the work-wall alarm before import. Programmatic imports used by tests do not alter process limits or install an alarm. Source SHA256 4b6f99e0...17e3dd4 was directly checked after this correction.

### PMC-O1 — preexec clamp records are fork-local (receipt clarification, resolved)

A records.append executed in preexec_fn modifies the fork child's list, not the supervisor's list. The clamp itself still applies. The final receipt labels this scope and records actual worker-entry RLIMIT_CPU/RLIMIT_AS values. Worker-main clamp records are retained by that worker. Empty supervisor clamp arrays are not presented as evidence that no clamping occurred.

## 4. Identity admission and receipts

The inspected manifest contains 100 frozen entries, including the original source archive and checkpoint. bind_source examines their union with the new launcher/comparator, frozen Budget module, and manifest itself. For every entry it compares the working file's Git blob identity to the required committed tree; manifest members additionally match their fixed SHA256. Symlink file entries, absent Git entries, wrong HEAD, changed runtime bytes, and inconsistent frozen digests fail.

The public supervisor creates a new evidence directory, preventing reuse of old success files. Its successful closeout requires a returned worker command, SMOKE_ONLY verification, no first_failure, zero binding exit code, unchanged before/after source identity, same_h_parity PASS, and exactly the requested accepted count. Missing or unreadable receipts raise into the failed report. Resource finalization can downgrade an otherwise completed result.

The wrapper temporarily replaces only the selected worker callable and the worker's local resource reference, then restores both. The captured original callable remains distinct from the NumPy candidate. The actual pilot receipt must still show the recorded comparator call and its backend-specific telemetry; this review of control flow is not itself an executed pilot receipt.

Create-only writes use exclusive creation and fsync in the launcher and frozen Budget. A crash, SIGKILL, exhausted inherited limit, or failed final write may leave incomplete evidence; absence of a complete successful receipt cannot be interpreted as PASS.

## 5. Resource correctness and measurement scope

The public launcher allows at most 32 steps under 60 CPU seconds, 180 wall seconds, and 2 GiB per-process address space. Its adapter takes minima with inherited soft/hard limits, so it never raises either inherited bound. The main process installs its own limits and wall alarm before project imports. The worker inherits tighter launch limits; frozen worker requests that would exceed them are clamped.

The unchanged Budget polls the mapped child process tree, includes completed child CPU accounting, and kills the process group on a caught resource failure while the worker remains alive. Its admission checks reserve two CPU and three wall seconds for final receipt writing. The frozen worker also retains its five CPU / twelve wall second recovery allowance. The supervisor's final measurement includes source checking, compilation, audit, and closeout before the final receipt write.

RSS is a 50 ms sampled worker-tree quantity, not an exact peak and not a whole-supervisor aggregate. RLIMIT_AS is a per-process address-space limit. These scopes are explicit in the output. The comparator's separate 60B NumPy-payload bound, B<=625, does not prove total RSS compliance.

The replay benchmark has no solver invocation. Timed trials include opening/parsing the native CSV, comparator allocations, guards, arithmetic, and verdict assembly. Inputs are loaded outside that interval. Warmups are separate and backend order alternates in measured pairs; reports use paired ratios rather than treating pooled trial counts as independent campaigns. Fresh subprocess RSS includes interpreter/import/input setup and therefore is not incremental comparator memory. Final speedup claims require actual formal receipts.

## 6. Independent executions and test-source review

The reviewer ran the actual launcher bind_source function against a small synthetic Git repository, with five unique checks:

1. Matching committed source, manifest, and checkpoint are accepted.
2. A wrong expected commit is rejected.
3. An uncommitted runtime byte change is rejected.
4. A symlink containing identical bytes is rejected.
5. A committed manifest containing an inconsistent frozen digest is rejected.

All five passed. The probe exited 0, used 0.081679 seconds of reaped-child CPU and 0.081587 seconds wall time, and ran zero solver integrations. The synthetic fixture establishes identity-admission behavior; it does not constitute a new scientific computation or a full 100-file physical-source audit. Command, script hash, stdout/stderr hashes, and raw output are preserved as code_audit_binding_probe.*.

The reviewer also inspected both new test files. Their coverage includes actual retained-stream verdict and maximum bits, a separate 25,000-lane native-binary64 trace, original raw input when supplied, legal per-tag interleaving, first-failure precedence, guard mutation, NaN/infinity/subnormal/signed-zero inputs, tolerance neighbors, non-default NumPy error policies, exact HE tags, public step bounds, lower inherited limits, and stale bytecode. Author-reported development outcomes are not counted as this reviewer's executions. Final committed-source tests and CI are separate gates.

## 7. Final claim separation

| Axis | This review establishes |
| --- | --- |
| Mathematical correctness | PASS_SCOPED; prior independent comparator derivation reused with unchanged source |
| Numerical equivalence | Algorithm and test design reviewed; formal paired execution receipt required |
| Implementation correctness | PASS_SCOPED code audit plus five independent identity probes; no open P1/P2 |
| Measured acceleration | NOT_MEASURED_BY_THIS_AUDITOR |
| Memory/resource behavior | Scoped bounds and enforcement paths reviewed; actual pilot/RSS receipts required |
| Physical validity | UNCHANGED_NOT_ESTABLISHED |
| Production readiness | NOT_ISSUED |

The implementation remains an opt-in audit improvement. The historical U5 HOLD failures, closed cost ledger, disabled REI activation, and unresolved global convergence are preserved. No new full5210 allocation or production speedup follows from this review.

