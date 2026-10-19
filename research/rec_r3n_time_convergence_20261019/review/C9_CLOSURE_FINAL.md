## C9-2 closure verdict: **Closed**

The revised construction-scale padding includes the exact indexed ±4h endpoints, including the late-grid cancellation case at **`j=100015`**, while genuinely outside controls remain outside. **No remaining C9-2 counterexample was found in this targeted closure.** C9-1 and C9-3 retain their previous closed verdicts.

### Checks completed

I ran only the targeted endpoint regression from a fresh snapshot:

```bash
PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/tmp/c9-final-closure.hSHrVX \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -B \
  /tmp/c9-final-closure.hSHrVX/snapshot_final/tests/trajectory/test_r3n_time_convergence.py \
  HistoryTests.test_inclusive_four_h_endpoints_explicit_and_inferred -v
```

**Result: PASS — one test containing six explicit/inferred subcases.**

| Boundary index | Explicit and inferred ±4h endpoints | Outside controls at ±4.00001h |
|---|---|---|
| `30015` | Included; p withheld | Excluded |
| `100015` — previous concrete counterexample | Included; p withheld | Excluded |
| `grid_size(0)-24 = 105835` | Included; p withheld | Excluded |

The corrected regression exercises **12 endpoint checks and 12 outside checks**. The earlier `N−18` test errors were fixture-construction errors; the corrected `N−24` regression passes.

I also independently exercised `compare_histories` with valid, smaller manufactured histories containing **13, 25 and 49 nodes**. For both explicit and inferred boundaries, at `j=30015`, `100015`, and the still-later `105841`:

- Exact ±4h endpoints returned `STAGE_BOUNDARY`, with **p absent for both `xe` and `Tm_K`**.
- ±4.00001h controls returned `RESOLVED_SAME_SIGN`, with p present.

Thus the fix resolves the previous `j=100015` failure and remains effective closer to ln(a)=0. The implementation bases its padding on the magnitude of the terms constructing the coordinate, addressing the cancellation problem identified in C9-2. See [time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/time_convergence.py), `boundary_interval` at line 231.

### Exact reviewed hashes

**Source:** [time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/time_convergence.py)

```text
dace3618b133c8a40a342e8a9b8ffa0981da926911e300671640d0fe2252cfda
```

**Test:** [test_r3n_time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/tests/trajectory/test_r3n_time_convergence.py)

```text
1078c00a9a29ed099ebd7552ba2160d1ac5954ca3690ece21ac765810cc77b48
```

Both main files matched the tested snapshot at the final hash check.

**Read-only confirmation:** All scratch work stayed under `/tmp/c9-final-closure.hSHrVX`. No main-tree or raw files were modified, no physical integration was performed, and I did not rerun the full 45-test suite or reopen the broader audit.
