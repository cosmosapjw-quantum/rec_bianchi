# R3P scalar stream auditor implementation and parent handoff

Date: 2026-10-20. Checkout: `/workspace/scratch/afe554957b2e/rec_work`.
Base HEAD: `368d87ad5de90dde74226ed109c3ba29d9607c84`.

## Delivered scope

Created only these two repository files under the assigned ownership:

- `/workspace/scratch/afe554957b2e/rec_work/scripts/r3p_stream_audit.py`
- `/workspace/scratch/afe554957b2e/rec_work/tests/trajectory/test_r3p_stream_audit.py`

Both files remain untracked; nothing was staged, committed, or pushed. Parent-owned R3P research and Rust files were left alone. The frozen verifier and manifest were not edited. Importing the new module does not rebind any verifier function or change resource caps. Activation is explicit through the parent's source-bound launcher.

The requested physmath-research-loop skill and relevant research, coding, evidence/handoff, and runtime/legacy references were read before work. No callable agent-spawn facility was available; independent local reads were actually batched, and no recursive agents were used. Prior read-only profile intake is in `/tmp/rec_r3p_profile_intake.md`.

## Public API and activation

```python
from r3p_stream_audit import compare_native_stream, causal_link_count

# The existing nine positional arguments are unchanged.
metrics = compare_native_stream(
    path, result, c, table, source, oracle, source_dir, evidence, guard,
    prefix_auditor=None,  # optional keyword-only argument
)

# Optional independent replacement, with the original signature:
links = causal_link_count(table, j)
```

The module follows the frozen `scripts/verify_r3i_h2_u6_rt_boundary.py` comparator and imports its existing constants, state/RHS/event checks, owner diagnostics, gates, and hash helper. There is no Rust import, build, adapter construction, or implicit activation.

Return keys remain `status`, `counts`, `spectral_fields`, `causal_links`, `maxima`, `original_average_failures`, and `end`; the status remains `PASS_PENDING_REVIEW`. Record order, stage checks, expected row counts, finite-value checks, exception ordering, tolerances, diagnostic fields, and original-versus-decimal gate handling are retained, subject to the explicit nonfinite-prefix correction below. The original 64-average-failure bound and 65th-failure rejection remain.

## Implemented optimizations and boundaries

| Change | Reuse and memory bound | Preservation condition / tradeoff |
|---|---|---|
| Prefix scalar temperature | One `Tr` per current prefix column, invalidated after callbacks | Uses exactly `KB_EV_K*c.T0_K*(1.+c.redshift(RT_IZ+col))`; assumes the physical inputs/redshift calculation are stable between synchronous callbacks. |
| Spectral scalar temperature | One `Tr` per current step/input index | Retains the original expression and input state. A guard or successful forensic callback invalidates the cached index. |
| V/A blackbody factors | At most 311 `(energy, Tr, fbb)` entries for the current index | Reuse only for A at the same index/bin with matching energy and temperature; otherwise recompute. `fbb` is the original Python float from `1./math.expm1(float(energy)/tr)`, with no NumPy recasting. |
| Spectral dispatch | Hoisted result-array map and immutable metric-name map | Array references are refreshed after guards, the prefix callback, and successful owner/gate diagnostics, including when a callback replaces an array. |
| Causal geometry | Four-entry LRU keyed by normalized energy shape and exact float64 bytes | Reuses geometry construction while retaining all live per-step causal checks. Exact-key creation still copies the small energy vector on each wrapper call; no timing benefit is claimed. |

The tolerance, ratio, and maxima expressions retain their original arithmetic and `max` association. The scalar implementation still calls `math.expm1`. Record order/index checks precede cache access, so duplicates and unordered rows cannot exploit cached entries. Callback exceptions retain their original first-failure boundary.

Rows are streamed. Added per-audit cache storage is O(311), independent of trajectory length. The existing `cv`/`cl` histories remain O(314*(PREFIX_COLUMNS+n)) because the independent owner diagnostics and final finite-history check use them; this change does not claim to remove that pre-existing allocation.

`CausalGeometry` is a frozen dataclass whose delay vector is copied into immutable bytes-backed storage. It neither aliases the caller's array nor permits `setflags(write=True)`. Construction uses the original `_source_edges` and `np.log(src/dst)/4.245e-5`. Every call still checks finite delays, delay > 1, active emission indices, and `floor(emit)+1 <= j-1`. Shape/energy mutations create a different cache key and undergo the original geometry validation. No new domain policy for `j` was introduced.

## Parent prefix callback contract

The loop uses `rows = enumerate(stream, 1)` and iterates over that shared iterator. On the first `PV`, with `prefix_position == 0`, the callback runs after generic tag/stage checks and the first PV counter increment, before numerical per-row prefix work:

```python
audited = prefix_auditor(
    first=(line_no, line), rows=rows, result=result,
    c=c, table=table, cv=cv, cl=cl, guard=guard,
)
counts["PV"] = audited["PV"]
counts["PL"] = audited["PL"]
prefix_position = audited["prefix_position"]
# invalidate cached indices, refresh arrays, then continue the outer loop
```

The parent callback must consume exactly `PREFIX_COLUMNS*314` rows including `first`, fill all prefix columns in `cv` and `cl`, and return total PV/PL counts plus the completed prefix position. These totals replace the counters, avoiding double-counting the initial PV. The outer loop resumes with the next unconsumed row. Callback exceptions propagate unchanged without retry or scalar fallback. The callback owns every skipped record check, finite check, scalar arithmetic/gate check, and raw first numerical failure ordering.

For `prefix_auditor=None`, scalar guards remain exactly before processing lines whose 1-based line number is divisible by 4096. Accelerated chunk guard timing is a separate contract: the parent callback must invoke guards at least as frequently as every 4096 consumed lines and preserve ordered numerical failure reporting. The parent owns the bounded <=8/64-column buffer implementation in `scripts/r3p_rust_audit.py`; this module neither imports nor compiles it. Only a protocol fake was tested here; integrated Rust validation remains with the parent.

## Explicit material input-contract correction

The frozen prefix comparator could accept a nonfinite Python-side prefix value: `abs(NaN) > tol` is false and infinity can produce an `inf > inf` comparison that is also false. The optimized scalar prefix now explicitly rejects nonfinite Python-side `py` with `ArithmeticError("C_PREFIX_NONFINITE")`, matching the native-prefix rejection label. This is an intentional tightening, covered by four NaN/infinity cases and documented in the module.

This is the only intentional parser tightening. Existing incidental `IndexError`/`ValueError` behavior for short rows and ignored trailing fields remain. The parent accelerated callback must enforce the same Python-prefix finite requirement.

## Focused verification actually run

Environment: Python 3.12.14, pytest 9.1.1, NumPy 2.3.5, SciPy 1.17.0, using `/workspace/scratch/afe554957b2e/rec_env/bin/python`.

Each invocation used this prefix from the checkout:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout -s TERM -k 0.5s 9s \
  /workspace/scratch/afe554957b2e/rec_env/bin/python -B -m pytest \
  -q -p no:cacheprovider tests/trajectory/test_r3p_stream_audit.py
```

| Added selection/options | Actual result | Revision scope |
|---|---|---|
| `-k 'not malformed' --durations=5` | 31 passed, 26 deselected, 3.37 s | Initial complete implementation, before the final callback array-reference refresh. |
| `-k malformed --durations=5` | 26 passed, 31 deselected, 4.58 s | Same revision; all malformed-stream differential cases. |
| `-k 'guard_mutation or optional_prefix or average_forensic' --durations=3` | 6 passed, 52 deselected, 2.00 s | Final implementation; affected callback boundaries plus newly added array-replacement case. |

All three commands exited 0 without hitting their timeouts. The current file has 58 cases. The earlier 57-case matrix passed across the first two invocations; after the targeted correction the six affected cases passed, including the new 58th case. An all-58 final rerun was not performed, in keeping with the short-test and dependency-aware verification constraints. No test invocation exceeded 10 seconds, and no performance loop or real trajectory was run.

Differential checks compare the entire result tree, including each floating-point scalar's exact IEEE bytes and type, exception type/message, raw and diagnostic JSONL bytes, scalar guard sequence, and unmodified input arrays. Fixtures exercise 1/3/5 indices, signed zero and small finite values, the full 36,447-row HE preamble, and a reduced synthetic photon prefix patched identically in both comparator modules.

The 26 malformed cases cover unknown/grid/stage records, NaNs, short rows, missing/truncated rows, duplicate and unordered prefix/STEP/spectral/END records, and competing faults to verify the first failure. Additional checks cover guard interruption; callback mutations of temperatures, energies, state redshift, and replacement result arrays; average-forensic success and two failure paths; and the original 64-failure cap. Forensic collaborators are controlled test doubles, with a fake binary file used only as a hash fixture, not executed.

Causal tests cover original per-step decisions at representative indices, four-entry eviction, changed energy values/shapes/order/spacing, immutable ownership, and continued execution of the future-index guard on cached geometry. The prefix fake proves shared-iterator ownership, first-row handoff, filled histories, counter replacement, resumption at BASE, identical scalar fake guard timing, and exception propagation. Operation counts demonstrate eliminated repeated evaluations in the synthetic fixture; they are not a wall-time or production speedup result.

## Integrity and handoff

Final identities:

| File | SHA256 |
|---|---|
| `scripts/r3p_stream_audit.py` | `d7a60e225d72626200be5ace2fbd1bf7828c386846b102dbdd5cf30f6ea9da4b` |
| `tests/trajectory/test_r3p_stream_audit.py` | `ad4f07b18197fe6c5dbf4fee04a37ecab2c8df088b4ac349098591b2e93d0326` |
| Frozen `scripts/verify_r3i_h2_u6_rt_boundary.py` | `8f30859e99136a5a916ca046bf553c24943d798ef67e783cc295fb4ef9327b50` |
| Frozen `research/rec_r3i_time_refinement_20261016/h2_u6_rt_boundary_001/SOURCE_MANIFEST_V6.json` | `f02f4e0b39dfafbb7656704cee59b8d95c976e9b55e840141d333be15b452585` |

All 109 frozen manifest file hashes matched in the final integrity review. Both new files passed syntax parsing and trailing-whitespace review. `git diff --name-only` showed no tracked modifications. Review was a same-assistant source/AST comparison with differential evidence, not an independent-agent review.

No physical algorithm, original HyRec2012 source, atomic/thermal operator, step size, stage guard, REI setting, frozen verifier, manifest, or source cap was changed. The inherited conclusions remain h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, and cost `CLOSED_HOLD_NOT_RESET`; the completed 5,210-step full-h2 U6 run was not repeated. This implementation supplies neither a new global-convergence conclusion nor a measured production speedup.

Parent follow-up is the source-bound opt-in activation, bounded Rust callback/adapter integration, and the already assigned actual-prefix/16-step equality and timing benchmark. Those production measurements and integrated Rust checks are intentionally outside this ownership scope.
