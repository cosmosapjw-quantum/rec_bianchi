# Independent pending global-grid DAG review

## Scope and verdict

**PASS_SCOPED_DAG_REVIEW.** The current 64-CPU/128-GB campaign can schedule independent, already implemented platform jobs. Completing the global three-grid scientific diagnostic requires additional dependent work and evidence. The hardware target does not remove these dependencies or establish an allocation for a full trajectory.

This review read the restored source and the linked historical receipts. It executed no trajectory, numerical benchmark, or previous test suite. Exact inspected file sizes and SHA256 values are recorded in `PENDING_GLOBAL_DAG_REVIEW.json`; historical numerical results are marked `complete_reused`.

## Reuse and remaining dependencies

| Item | Current evidence | Consequence |
|---|---|---|
| R3Q h4 first event plus two | Existing reviewed endpoint at global index 74411 after 1511 accepted continuation steps | Reuse this completed partial history. The existing worker does not implement the full remaining U4/U5/U6/low-z trajectory. |
| R3O h2 low-z endpoint | Existing four-node source stencil at indices 211713–211716 | Reuse the endpoint and the preserved R3R interpretation correction. The earlier “three available states” sentence does not justify another negative-redshift RHS evaluation. |
| Original-h history | The existing adapter copies 105859 independently evolved accepted states | Reuse the trajectory; separately retain its missing nodewise C parity and early stage labels. |
| Complete h2 input | Several independently evolved stage products exist | Contiguous history assembly and stage/uncertainty provenance remain obligations; the low-z endpoint alone is not a complete three-grid input. |
| Complete h4 input | First-event history exists | Implement and validate the subsequent dependent stages before any full three-grid comparison. |
| Global h/h2/h4 diagnostic | Global convergence remains `NOT_RUN` | All three histories, endpoint stencils, canonical targets and uncertainty/boundary gates are required. A completed diagnostic would still require scientific review. |

## Preserved recurrence and parallelism boundary

`primordial_2012_quarter_continuation.py` reads the latest accepted state and accepted spectral history for each update. It evaluates the current FULL column, commits that column once, updates the accepted state and predictor memory, then advances the source index. Its predictor retains the source grouping `1.25 * current_rhs - 0.25 * prev2_rhs`. Post-Saha probes do not commit trial history columns. The stage condition is reevaluated at each accepted input, and the implemented stop is the first event plus two accepted steps.

These dependencies form a serial accepted-step chain. Assigning adjacent accepted indices to different CPUs would require a new algorithm and a new equivalence argument. R3S whole-job scheduling preserves that chain inside each process. Separate saved-stream checks or separate bounded runs may be independent at the campaign level; that independence supplies no measured solver acceleration by itself.

## Missing uncertainty remains a real gate

`prepare_r3o_h_history.py` explicitly records `nodewise_C_parity=UNKNOWN`, omits the `parity_abs_*` arrays, and labels the regime before source input 29195 as `UNKNOWN`. The older integer-redshift aggregate discrepancy is retained as aggregate evidence. It is not converted into a nodewise uncertainty bound.

In `time_convergence.py::signed_triplet`, missing parity or quantization bounds yield `UNCERTAINTY_MISSING` before slope interpretation. Consequently, finishing h4 coverage alone cannot turn every global diagnostic gate into PASS. Boundary coverage, signed-difference resolution and nodewise uncertainty must be supplied or honestly remain unresolved.

The output contract also retains the original four-point cubic stencil and its source clamp. No clipping of the interpolation fraction, resampling of accepted histories, missing-stencil fill or inferred convergence order is introduced. `COMPLETE_DIAGNOSTIC_PENDING_REVIEW` is a coverage/diagnostic status; its own source states that the resolved three-level slope is not an error theorem or physical approval.

## Grid names and claim limits

The user's original R3P reference `h=4.245e-5` and the older convergence module's level names use different bases. In `time_convergence.py`, `H0=8.49e-5`, level 1 is `H0/2=4.245e-5`, and level 2 is `H0/4=2.1225e-5`. Receipts must identify the actual `dlna` and namespace instead of treating every textual `h` as the same grid.

The original U5 holds, `CLOSED_HOLD_NOT_RESET`, `REI_activation=false`, global convergence `NOT_RUN`, physical validity `HOLD` and production readiness `NOT_APPROVED` remain unchanged. This review does not authorize a full-mode run, claim new performance, or verify the actual NCP machine.
