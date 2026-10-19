## C9 verdict: Block for fail-closed readiness

**Three substantive findings remain.** The verified R3M h2 adapter result remains valid within its stated scope: it loads 5,211 nodes and returns `INSUFFICIENT_LEVELS`, with levels `[0, 2]` missing, no comparison rows, and the required holds preserved.

The comparator and loader changed during this review. I reviewed the updated files in an isolated snapshot and confirmed that the working files still matched that snapshot at the final check. The updated physics-digest validation and transition-window selection address the earlier cases I investigated; those are **not** outstanding findings.

### 1. P1 — Missing stage or boundary evidence can still produce a resolved p

**Locations:** [time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/time_convergence.py), particularly lines 103, 107, 136, 244 and 256.

Two concrete paths violate the requirement to withhold p when stage or boundary information is unavailable.

**An empty boundary list is treated as established absence of boundaries.** Physical histories with `boundary_lna=[]` and constant `U6_FULL` labels pass validation. The comparator can infer transitions only inside the saved fragment, so it cannot recover an omitted boundary immediately before that fragment.

I used three tiny constant-plus-\(h^2\) histories beginning at coarse index 30000, with a target at index 30001.5. A boundary at index 29999 lies only 2.5 coarse steps from that target. All required interpolation stencils are present.

| Boundary metadata supplied | Classification | `stage_neighborhood` | `p_observed` |
|---|---|---:|---:|
| Empty list | `RESOLVED_SAME_SIGN` | `false` | `1.9999999991111501` |
| Boundary at `X0 + 29999*H0` | `STAGE_BOUNDARY` | `true` | `null` |

This concerns an **empty list**, not an absent descriptor key: an absent `boundary_lna` key already fails loading. The problem is that unknown boundary coverage and a reviewed absence of nearby boundaries have the same representation.

**Empty byte-string stage labels also pass validation.** For `regime=np.full(n, b'', dtype='S1')`, the initial check evaluates `str(b'')`, which is the nonempty string `"b''"`. The subsequent Unicode conversion produces actual empty labels, without validating them again. An empty label is not one of the sentinel labels that suppress p.

With nonempty boundary metadata located safely away from the target, this produced:

```text
regime                 = ""
stage_neighborhood     = false
classification         = RESOLVED_SAME_SIGN
p_observed             = 1.9999999988148645
```

**Impact:** The analyzer can publish a resolved three-level slope without the stage evidence needed to establish that the stencil and its surrounding neighborhood are suitable. The top-level “diagnostic” disclaimer does not satisfy the explicit requirement to withhold p.

**Minimum correction:** Validate stage labels after decoding and normalization, rejecting empty labels. Represent unknown boundary coverage separately from a reviewed empty boundary list, and suppress p when physical boundary coverage is unknown, including the required neighborhood outside a partial history.

**Regression cases needed:** Empty Unicode and byte-string labels; unknown boundary coverage; and a transition just outside a saved fragment but within four coarse steps of an otherwise valid target.

### 2. P2 — The inclusive ±4h boundary mask excludes exact grid endpoints

**Location:** [time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/time_convergence.py), line 257.

The mask uses:

```python
abs(float(xx) - b) <= 4. * H0
```

Subtracting two rounded ln(a) coordinates can place a target nominally exactly four coarse steps away just outside this comparison.

I reproduced this with stage-label changes at coarse index 30015 on all three grids. The comparator inferred the boundaries from those labels. Targets at coarse indices 30011 and 30019 both returned:

```text
nominal offset                 = -4h / +4h
computed abs(target-boundary)/h = 4.0000000000025615
stage_neighborhood             = false
classification                 = RESOLVED_SAME_SIGN
p_observed                     = 1.9999999988148645
```

Thus this is not limited to manually supplied boundary coordinates.

**Impact:** Points belonging to the contract’s inclusive `eta +/-4*hcoarse` neighborhood receive p and are excluded from the `stage_neighborhood` region summary. A discrepancy at such an endpoint can consequently be omitted from that region’s maximum, although it remains in the available-domain maximum.

**Minimum correction:** Make the membership comparison conservative with respect to coordinate rounding—for example, using indexed boundary membership where available, or outward-rounded interval endpoints. This should change only the diagnostic mask, preserving the original grid, interpolation and numerical operators.

**Regression cases needed:** Both exact ±4h endpoints, for inferred and explicit boundaries, together with nearby points genuinely outside the neighborhood.

### 3. P2 — “Create-only” output preservation is not atomic

**Locations:** [compare_r3n_time_grids.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/scripts/compare_r3n_time_grids.py), lines 42, 45, 48, 157 and 182. [probe_r3n_predictor.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/scripts/probe_r3n_predictor.py) has the same check-then-write pattern at lines 47, 49, 110 and 111.

The output guard checks whether a directory is nonempty, then allows an existing empty directory. It does not reserve the destination. Later `write_text()` calls overwrite existing files.

I reproduced the race with two concurrent calls to the unmodified CLI `main()`, using a test scheduling barrier immediately after both passed `empty_output()`. One analyzed a valid one-level fixture; the other analyzed a fixture with an invalid NPZ hash. Both fixtures were tiny, and all output remained in the temporary directory.

Observed result:

```text
first invocation exit          = 0
second invocation exit         = 2
first execution.json SHA       != final execution.json SHA

final files:
  result.json       status = INSUFFICIENT_LEVELS
  failure.json      message = HISTORY_DATA_SHA_MISMATCH
  execution.json    status = INPUT_OR_IMPLEMENTATION_ERROR
```

The second invocation overwrote the first invocation’s execution receipt. The directory ended with artifacts from two different runs.

**Impact:** Concurrent invocations sharing an evidence path can destroy the association between a result and its execution receipt, despite the advertised create-only behavior. Ordinary sequential reruns correctly refuse a nonempty directory; this defect specifically concerns concurrent use of the same destination.

**Minimum correction:** Reserve the evidence destination atomically before either invocation proceeds, or use an exclusive reservation file when pre-existing empty directories must remain supported. Evidence writes should refuse replacement.

**Regression case needed:** Two concurrent attempts at the same evidence destination; exactly one must acquire it, and the other must leave the first run’s files unchanged.

## Validation and scope

The reviewed versions were:

| Scoped file | Reviewed SHA-256 prefix |
|---|---|
| `time_convergence.py` | `37e86b7776716822` |
| `compare_r3n_time_grids.py` | `5f334791261b914f` |
| `probe_r3n_predictor.py` | `7c5972ef459218a1` |
| `test_r3n_time_convergence.py` | `31849fbd299b9570` |

The [frozen contract](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3i_time_refinement_20261016/CONTRACT.json) matches the supplied SHA-256.

Validation completed:

- **All 27 scoped tests passed on the updated snapshot**, including all 18 bit-for-bit comparisons against the archived original C output interpolator. These support the faithful four-point interpolation, global clamp, signed differences and uncertainty-floor behavior exercised by the suite. See [test_r3n_time_convergence.py](sandbox:/workspace/scratch/afe554957b2e/rec_work/tests/trajectory/test_r3n_time_convergence.py).
- The manufactured predictor probe returned `PASS_SCOPED`. Its result retained `three_grid_recombination="NOT_RUN"` and zero physical integrations.
- Loader negative cases rejected wrong NPZ hashes, spacing, origin, out-of-directory data paths, absent or nonfinite boundary metadata, resampled checkpoints, active REI, incorrect source identity, missing physics contracts, and inconsistent physics digests/operators.
- The updated ln(a) window selector retained both thermal-window endpoints, 826 and 846.
- One-level CLI analysis returned exit **0** normally and **3** with `--require-complete`; invalid input returned **2**. Sequential reuse of nonempty output directories preserved the existing files in both scripts.
- Read-only loading of the saved R3M h2 descriptor returned `INSUFFICIENT_LEVELS`, missing `[0, 2]`, with `HOLD_9_FAIL`, `HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, and `REI_activation=false` intact.

**No files in `rec_work`, `rec_raw*`, or `rec_recovery` were modified by this review.** Scratch work stayed under `/tmp/c9-time-review.dUtvR1`. No network access or recombination integration was performed, and no physical h or h4 producer was created. The checkout is not a Git repository in this environment, so the review used the scoped file contents and pinned contract rather than a branch diff.
