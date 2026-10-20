# R3P ratio harness and Python binding tests — handoff

## Result and ownership

**82 passed, 0 failed, 0 skipped.** No ratio performance run was started. The parent owns the actual one-CPU microbenchmark under its outer 30 CPU / 120 wall budget. No Rust, ctypes-adapter, builder, existing test, or parent prefix fixture was edited; no commit or push was made.

Created:

- `scripts/benchmark_r3p_ratio.py`
- `tests/trajectory/test_r3p_rust_audit.py`
- `tests/fixtures/r3p_ratio/actual_v_subset.npz`
- `tests/fixtures/r3p_ratio/actual_v_subset.json`
- this handoff

All repository paths below are relative to `/workspace/scratch/afe554957b2e/rec_work`.

## Fixture paths, schemas, provenance

The ratio fixture is **623 actual V lanes** selected from the saved 9,952-lane NPZ by
`sorted(set(range(0, 9952, 16)) | {9951})`. It spans all 32 accepted-step columns and includes an odd tail. No physics was rerun.

- NPZ: `tests/fixtures/r3p_ratio/actual_v_subset.npz`, **20,899 bytes**.
- Metadata: `tests/fixtures/r3p_ratio/actual_v_subset.json`, **4,723 bytes**.
- Combined: **25,622 bytes**, below the requested 1 MiB bound.
- Metadata schema: `rec.r3p.ratio-fixture.v1`.
- NPZ keys: `py`, `native`, `fbb`, `scalar_ratio` (little-endian float64, shape [623]); `source_indices` (little-endian int64, shape [623]).
- `scalar_ratio` is a separately saved ordered Python-binary64 reference derived from those actual input lanes; it is not a physical output or a performance measurement.
- Metadata records the exact subset NPZ SHA, every array's dtype/shape/byte count and raw SHA, source full-array raw SHAs, selection, source NPZ and extraction-receipt paths/SHAs, and the upstream raw CSV/Python-NPZ/verification SHAs copied from that receipt.
- Raw hashes mean SHA256 of **little-endian C-order array bytes without an NPY header**.
- Original NPZ SHA: `83c1099a8fe6862d6e241d675c2077c53492ededcdd7d81050b01b46640296b9`.
- Subset NPZ SHA: `4593660bf42d6223139f15c1c0ab32c57c4fb13a55543e59b25d4599992ee5d1`.
- The source NPZ and receipt were rehashed during extraction. The large upstream raw CSV/NPZ were **not independently reread** for this subset; metadata explicitly attributes their hashes to the saved receipt.

The parent-owned real prefix fixture was consumed without modification:

- `tests/fixtures/r3p_prefix/prefix.npz`
- `tests/fixtures/r3p_prefix/prefix.csv.gz`
- `tests/fixtures/r3p_prefix/MANIFEST.json`, schema `rec.r3p.real-prefix-fixture.v1`
- 24 columns / 7,536 real fields: blocks 0..7, 8000..8007, 16725..16732.
- Tests verify manifest file SHAs, every CSV tag/column/bin, all finite inputs, positive Tr/energy, the independent original scalar expm1/tolerance gate, and exact native-value bits.
- Nine parameter combinations cover all three blocks with 1/2/4 threads, subject to affinity. This run had four assigned CPUs, so none skipped.

## Harness contract and execution boundary

Receipt schema: **`rec.r3p.ratio-benchmark.v1`**.

The runner accepts either the subset metadata or the original `rec.r3p.saved-audit.v1` receipt as input provenance. It requires the declared NPZ hash and, for the subset schema, each input array's raw hash. The actual benchmark should use the original 9,952 lanes.

Methods are:

1. Ordered Python scalar: `abs(py-native)/(1.e-7*max(abs(py),abs(native))+1.e-10*fbb)`, with separate ordered binary64 operations and finite gates.
2. NumPy elementwise ufuncs with the same multiply/add association and finite gates.
3. Parent `PrefixAuditor.ratios` / C ABI `rec_ratio_batch`.

**Saved scalar-associated fbb is used unchanged. There is no NumPy exp/expm1 substitution.** The ratio ABI executes on the calling thread and does not use the local Rayon pool. `--threads 1` creates a direct serial handle. SIMD attribution remains scoped to the separately reviewed emitted binary; the harness itself does not infer SIMD or integration speedup.

Defaults predeclare six trials, 64 repeats per backend per trial, two warmups per backend, and rotating backend order. Each method occupies each ordinal position twice. For 9,952 lanes this is **384 timed calls and 3,821,568 timed lane evaluations per method**. There is no calibration or adaptive repeat count.

Each timed sample includes backend input validation, output allocation, dispatch, repeat bookkeeping, and per-call budget checks. Input loading/hashing, handle or pool setup, finite/bitwise preflight, negative controls, warmups, output checks, and teardown are separately recorded outside samples. All three outputs are bitwise checked before timing; warmups and the last result of every timed sample are also checked. Input mutation and source/binary/receipt changes cause failure.

JSON includes the fixed plan, raw samples, actual completed calls, CPU/wall durations, environment/affinity/thread counts, handle setup/teardown, input NPZ/raw hashes and provenance, binary/build/source hashes, negative-control results, and per-method median sample times. There is no end-to-end audit or physics performance claim.

### Resource and failure behavior

- Requested CPU cap is at most **30 seconds**; wall default is **120 seconds**.
- The runner calls **no `setrlimit`**. It never raises an inherited soft or hard resource limit.
- Effective CPU allowance is the minimum of the requested cap and each finite inherited absolute CPU limit minus already-used process CPU and a one-second reserve.
- CPU/wall checks count from input loading onward and run between calls. The parent outer budget remains authoritative.
- The output is create-only. A valid complete schedule is persisted before handle setup and timing.
- Failures during initial input loading or build verification produce a `FAILED` preparation receipt with an empty sample list. Post-plan failures retain the declared plan and completed/partial sample counts.
- An existing receipt is never overwritten. External process termination can leave the already persisted plan or running receipt; it cannot fabricate a successful result.

## Focused correctness coverage

The gated tests exercise actual ratio data and scalar/NumPy/Rust equality, one-ULP and signed-zero comparison controls, noncontracted tolerance witnesses, scalar tails, finite ratios above one, zero/zero and nonfinite/overflow rejection, shape/dtype/cap rejection, and noncontiguous inputs.

Adapter/ABI coverage includes malformed four-field records, index grammar and overflow, NaN/Inf, positive Tr/energy gates, exact and zero tolerance boundaries, closed/idempotently closed handles, 1/2/4-thread pool reuse and deterministic first errors, explicit speculative attempted-row counts, C layout, null/length/cap/alignment/overlap rejection, and input/output/status canaries.

Guarded hook checks cover original scalar Tr association, watchdog cadence plus block guards, bounded scratch statistics, untouched tail columns, guard interruption before FFI, transactional failed-block output, cumulative 4 MiB text rejection, and **an early bad row followed by EOF**. Receipt controls cover **missing source records, changed library bytes, schema mismatch, and changed vendor SHA**.

The runner's remaining-CPU arithmetic and preparation failure/create-only receipt path are tested without executing benchmark repetitions.

## Exact validation record

The first default-interpreter attempt had no pytest installed. The existing `rec_env` interpreter was then used, without installing anything. The first actual test run found one error in the new test's floating-point association assertion; it was fixed to preserve original scalar association. The final run passed all 82 cases. These are correctness-test logs, not performance measurements.

```json
{
  "cwd": "/workspace/scratch/afe554957b2e/rec_work",
  "final": {
    "command": "taskset -c 4-7 env R3P_BUILD_RECEIPT=/workspace/scratch/afe554957b2e/rec_runs/r3p_build_001/build.json PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 /workspace/scratch/afe554957b2e/rec_env/bin/python -m pytest -q -p no:cacheprovider tests/trajectory/test_r3p_rust_audit.py",
    "exit_code": 0,
    "passed": 82,
    "failed": 0,
    "skipped": 0,
    "stdout": "........................................................................ [ 87%]\n..........                                                               [100%]\n82 passed in 1.65s\n",
    "timing_provenance": "The 1.65s value is pytest's displayed duration, not a measured CPU/benchmark result."
  },
  "initial_focused_run": {
    "command": "taskset -c 4-7 env R3P_BUILD_RECEIPT=/workspace/scratch/afe554957b2e/rec_runs/r3p_build_001/build.json PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 /workspace/scratch/afe554957b2e/rec_env/bin/python -m pytest -q -p no:cacheprovider tests/trajectory/test_r3p_rust_audit.py",
    "exit_code": 1,
    "passed": 79,
    "failed": 1,
    "stdout": "............................................F........................... [ 90%]\n........                                                                 [100%]\n=================================== FAILURES ===================================\n________________ test_prefix_exact_tolerance_and_zero_tolerance ________________\n\nauditor = <r3p_rust_audit.PrefixAuditor object at 0x7f1c38a97950>\n\n    def test_prefix_exact_tolerance_and_zero_tolerance(auditor):\n        case = prefix_case(1)\n        case.py.fill(0.)\n        case.tr.fill(1.)\n        case.energies.fill(1.)\n        for row in range(314):\n            change_value(case, row, \"0\")\n        threshold = np.array([0x3dcffe98461a10da], dtype=np.uint64).view(np.float64)[0]\n>       assert float(threshold) == 1.e-7 * float(threshold) + 1.e-10 / math.expm1(1.)\nE       assert 5.8197676506700295e-11 == ((1e-07 * 5.8197676506700295e-11) + (1e-10 / 1.718281828459045))\nE        +  where 5.8197676506700295e-11 = float(np.float64(5.8197676506700295e-11))\nE        +  and   5.8197676506700295e-11 = float(np.float64(5.8197676506700295e-11))\nE        +  and   1.718281828459045 = <built-in function expm1>(1.0)\nE        +    where <built-in function expm1> = math.expm1\n\ntests/trajectory/test_r3p_rust_audit.py:371: AssertionError\n=========================== short test summary info ============================\nFAILED tests/trajectory/test_r3p_rust_audit.py::test_prefix_exact_tolerance_and_zero_tolerance\n1 failed, 79 passed in 1.37s\n",
    "resolution": "Corrected a new test's regrouped 1.e-10/expm1(1.) assertion to fbb=1./expm1(1.); 1.e-10*fbb. Production Rust/adapter were not edited. Added two runner guard/receipt tests before the final run."
  },
  "initial_interpreter_attempt": {
    "command": "taskset -c 4-7 env R3P_BUILD_RECEIPT=/workspace/scratch/afe554957b2e/rec_runs/r3p_build_001/build.json PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python -m pytest -q -p no:cacheprovider tests/trajectory/test_r3p_rust_audit.py",
    "exit_code": 1,
    "tests_executed": 0,
    "stdout": "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python: No module named pytest\n",
    "resolution": "Used the existing rec_env interpreter; installed nothing."
  },
  "benchmark_runs_by_this_agent": 0,
  "source_hash_capture": "File hashes below were captured immediately after the final correctness run; parent-owned files are read-only observations."
}
```

## Parent benchmark command — not executed here

Run under the parent's outer 30 CPU / 120 wall budget, with one available CPU chosen by the parent. The output must not already exist.

```bash
taskset -c <one-available-cpu> env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/scratch/afe554957b2e/rec_env/bin/python \
  /workspace/scratch/afe554957b2e/rec_work/scripts/benchmark_r3p_ratio.py \
  --fixture /workspace/scratch/afe554957b2e/rec_runs/audit_pilot_legacy/ratio_fixture.npz \
  --provenance /workspace/scratch/afe554957b2e/rec_runs/audit_pilot_legacy/result.json \
  --build /workspace/scratch/afe554957b2e/rec_runs/r3p_build_001/build.json \
  --threads 1 --repeats 64 --trials 6 --warmups 2 \
  --cpu-cap 30 --wall-cap 120 \
  --output /tmp/rec_r3p_ratio_measurement.json
```

The CLI sets OMP/OpenBLAS/MKL/NumExpr thread variables to one before importing NumPy. Importing the helper module for tests does not change those variables.

## File hashes at handoff

```json
{
  "/workspace/scratch/afe554957b2e/rec_runs/r3p_build_001/build.json": {
    "bytes": 8155,
    "sha256": "d53d84663162989f9c6f63731754a253effe8d212bbea84aba222b134c266602"
  },
  "/workspace/scratch/afe554957b2e/rec_work/scripts/benchmark_r3p_ratio.py": {
    "bytes": 21145,
    "sha256": "924873a573f321ec41fd51ada71baa42665b638aad8f3ebb1b65fe42f8df5eab"
  },
  "/workspace/scratch/afe554957b2e/rec_work/scripts/r3p_rust_audit.py": {
    "bytes": 9930,
    "sha256": "9fd0e46ca57ebe2e3bd865479f11004bf73bad7f6ff05637ab34fa53f490dfec"
  },
  "/workspace/scratch/afe554957b2e/rec_work/tests/fixtures/r3p_prefix/MANIFEST.json": {
    "bytes": 997,
    "sha256": "c7187e100da639c811da08d4d8340349289bca21782732334739f9fb6fc81fb7"
  },
  "/workspace/scratch/afe554957b2e/rec_work/tests/fixtures/r3p_prefix/prefix.csv.gz": {
    "bytes": 90194,
    "sha256": "aace922b72ff82ef3f865924f9d6fc9726f7f3d22fae35aebce52f61aa72bea5"
  },
  "/workspace/scratch/afe554957b2e/rec_work/tests/fixtures/r3p_prefix/prefix.npz": {
    "bytes": 119639,
    "sha256": "83df787db4e6d0440ecc329ab3e653aafdb885ceb7813f1b6d34d348ccec73b0"
  },
  "/workspace/scratch/afe554957b2e/rec_work/tests/fixtures/r3p_ratio/actual_v_subset.json": {
    "bytes": 4723,
    "sha256": "3fb2c7d1ce68f84b8fc25fde3c5037efe79c3082a6f7078b9706120ae28cd8cc"
  },
  "/workspace/scratch/afe554957b2e/rec_work/tests/fixtures/r3p_ratio/actual_v_subset.npz": {
    "bytes": 20899,
    "sha256": "4593660bf42d6223139f15c1c0ab32c57c4fb13a55543e59b25d4599992ee5d1"
  },
  "/workspace/scratch/afe554957b2e/rec_work/tests/trajectory/test_r3p_rust_audit.py": {
    "bytes": 31500,
    "sha256": "aa36e6273afda438c7a6675398c7c6b343b4c59704d0c1f03c4e495e1e1e7b35"
  }
}
```

Pinned parent library SHA: `7e6f4bde4497d7771d0f45167d4c7a33a000949d248cab33bbffa126564aaec8`. The unchanged build 001 passed the strengthened `library_from_build` validation in the final test run.
