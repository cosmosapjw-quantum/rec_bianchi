## Targeted C9 closure verdict: **2 closed; 1 remains open**

**All 45 tests in the two `test_r3n_*.py` files passed.** The remaining issue is the existing ±4h endpoint finding: the two-ULP expansion fixes the original index-30015 example but still excludes exact indexed endpoints later on the grid.

| Original finding | Closure verdict | Evidence |
|---|---|---|
| C9-1 — Missing stage/boundary evidence permits p | **Closed** | Decoded empty labels are rejected; missing or insufficient boundary coverage suppresses p; reviewed empty boundary lists remain usable. |
| C9-2 — Exact ±4h endpoints escape the mask | **Open — P2** | Reproduced through `compare_histories` at boundary index **100015**, for both explicit and inferred boundaries. |
| C9-3 — Concurrent output calls overwrite receipts | **Closed** | Exactly one caller reserves the directory; competing and subsequent callers preserve the winning receipt. |

## Remaining C9-2 counterexample

**Location:** [time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/time_convergence.py), `boundary_interval` at line 231 and its use at line 285.

This reproduces the same endpoint defect with the patched implementation:

```python
from full_bianchi_hyrec.trajectory.time_convergence import (
    H0, X0, boundary_interval,
)

j = 100015
b = X0 + j * H0
lo, hi = boundary_interval(b)

print([
    (offset, lo <= X0 + (j + offset) * H0 <= hi)
    for offset in (-4, 4)
])
# [(-4, False), (4, False)]
```

The actual coordinates are:

```text
boundary = -0.4960483128501245

expanded lower bound = -0.4963879128501246
exact indexed -4h    = -0.49638791285012474  → excluded

expanded upper bound = -0.4957087128501244
exact indexed +4h    = -0.4957087128501243   → excluded
```

I also exercised this through **`compare_histories`**, using only 33, 65 and 129 manufactured history nodes. All interpolation stencils were present, and each history declared complete boundary coverage `[X0, 0.]`.

For **both explicit boundaries and boundaries inferred from stage-label changes**, both endpoints returned:

```text
boundary_coverage_known = true
stage_neighborhood     = false
classification         = RESOLVED_SAME_SIGN
p_observed             = 1.9999999988148645
```

**Cause:** Two ULPs of the final interval endpoint do not bound rounding in the larger terms used to construct `X0 + g*h`. As cancellation makes the resulting ln(a) coordinate smaller, its ULP becomes too small to cover that construction error.

**Impact:** The existing finding remains: exact ±4h points can receive p and be omitted from the `stage_neighborhood` region summary. This is a manufactured counterexample within the valid grid domain; I am not asserting that the saved R3M trace encounters this particular boundary.

**Minimum correction:** Base the conservative mask padding on the error scale of the indexed-coordinate construction, or retain indexed positions for these comparisons. Keep the correction confined to diagnostic membership. Extend the existing explicit/inferred endpoint test to index **100015**, retaining the genuinely outside controls.

## Exact closure checks completed

### C9-1: closed

I verified the updated validation and coverage paths in [time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/time_convergence.py) and executed these additional targeted cases:

- Empty Unicode, empty bytes, whitespace-only Unicode, and whitespace-only bytes all raise `REGIME_LABELS_REQUIRED`.
- Missing coverage on all grids, missing coverage on just one grid, and a partial halo return `BOUNDARY_COVERAGE_UNKNOWN` with `p_observed=None`.
- A reviewed empty boundary list with adequate coverage permits a resolved manufactured slope.
- The original outside-fragment event at index 29999 suppresses p at index 30001.5.
- Coverage clipping at both physical-domain endpoints, `X0` and `0`, allows valid reviewed coverage without requiring evidence beyond the physical domain.

### C9-3: closed

I verified the atomic reservation and exclusive write sites in [compare_r3n_time_grids.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/scripts/compare_r3n_time_grids.py) and [probe_r3n_predictor.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/scripts/probe_r3n_predictor.py).

The independent mixed-input concurrency check used one valid descriptor and one invalid-hash descriptor targeting the same directory. Its observed result was:

```text
returns = [0, "OUTPUT_EXISTS_PRESERVE_PRIOR_EVIDENCE"]
files   = [execution.json, result.json]
execution status = INSUFFICIENT_LEVELS
receipt file hashes match = true
```

A subsequent retry left every existing byte unchanged. Both scripts rejected an already-existing empty directory without adding files. Attempting `dump()` over an existing JSON file raised `FileExistsError` and preserved its contents. The NPZ and plot `xb` write sites were inspected; no raw adapter or plot-generation run was needed for this closure.

### Targeted test command

Executed from the isolated snapshot:

```bash
PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/tmp/c9-closure.mVZ0Ks \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -B -m unittest discover \
  -s /tmp/c9-closure.mVZ0Ks/snapshot/tests/trajectory \
  -p 'test_r3n_*.py' -v
```

**Result: 45 tests passed, no failures or skips.** During closure, the saved-trace test changed only its fixture reference from `real_h2_trace_002` to `real_h2_trace_003`; I copied that updated test and fixture into the snapshot and reran the affected test successfully.

The reviewed implementation hashes were:

| File | SHA-256 prefix |
|---|---|
| `time_convergence.py` | `b1c5345b8a059e2f5` |
| `compare_r3n_time_grids.py` | `3c4ed4c80112c528` |
| `probe_r3n_predictor.py` | `bccb6aadbf3a566e` |

Those implementation files matched the snapshot at the final comparison. The frozen contract hash also remained unchanged.

**Read-only confirmation:** All scratch work stayed under `/tmp/c9-closure.mVZ0Ks`. No main-tree, shared raw, or recovery files were modified; no network access or physical integration was performed.
