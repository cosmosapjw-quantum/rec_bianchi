# Independent source intake: REC R3P → R3Q → follow-up

## Read-only scope and identity

Read current checkout, source and saved numerical arrays; did not integrate, benchmark, compile a scientific solver, rerun tests, or mutate any provider. No root AGENTS.md exists at the observed checkout. Nested AGENTS.md files occur only under imported atomic source surveys and do not govern this REC lane.

- PR111 source commit: `1ad0380110621446c42df9d995fd85db3a6c7e7a`, tree `efd65193713f19d0e60a0617182b3449c7091510`.
- Actual implementation commit: `8d6a9e40eb509f467b10a22d3a690c57b85b6131`, tree `eba49edd3392f748eb38e51c8739a443fc2bffc3`.
- Results publication: `2236c19ff71b2706696e1985d968b2b841fd55bc`.
- Current observed HEAD: `5b44bb21ce0599e55e0848e5e3ff320c9e8ca172`, tree `9403d3778d0a81e9632cea58e42e59ed9581e980`.
- Branch: `research/orchestration-20261020-next-loop`; inherited R3P base `888d56d72579d1e1fd30f66abe02d9f91809a767`.
- Working checkout was clean at the intake read.

## New actual NCP results to reuse

Read R3Q `NCP_EXECUTION_DELIVERY.json`, `DAG.json`, updated `REPORT_KO.md`, event `verification.json`, `TERMINAL.json`, `INDEPENDENT_REVIEW.json`, and h2 low-z corresponding receipts/source.

1. h4 first event+2: source `1ad03801…`; 1511 new accepted steps, 6044 FULL evaluations; helium cutoff at global iz74409, z1648.1096049064963, followed by 2 H_ONLY updates to iz74411, z1648.0396016895968. Same-h parity PASS under original gates; post-Saha remains true at endpoint. Source closure100/100; independent recorded verdict PASS_SCOPED_H4_FIRST_EVENT_PLUS_TWO. Runner CPU30.196189 s/wall30.345126653992338 s; supervisor-inclusive CPU31.315760764 s/wall31.468693311006064 s. These are different measurement intervals. NCP hostname s1a0e5abed09, affinity63, per-process address cap2GiB.

2. h2 low-z: 153327 accepted steps/153328 states, 43 checkpoints; EMLA86542 updates followed by Peebles66785 updates, transition input iz144931. Same-h state/RHS comparison PASS, no failure. Runner CPU60.755865 s/wall62.63294564798707 s under its historical separately authorized600/900 allocation. This historical allocation does not authorize an enlarged new run here. Final output node iz211716 has z=-2.238689928646398e-5; final RHS was evaluated at positive z=2.0063051384022756e-5.

Directly read saved arrays and computed producer identity match:

| Saved Git artifact | bytes | SHA256 |
|---|---:|---|
| R3Q ncp_event_001/python_continuation.npz |7390437|7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9|
| R3O lowz_ncp_full_001/python_native_lowz.npz |6982148|b25e2cbdafe4037d222116c4985eac95a380552f6799a2b3e950fb499965dbe6|

The h4 NPZ has1512 serialized states,1511 steps, photon arrays311×1519/311×1519/3×1519, and final2×2 predictor. It is the actual next h4 restart dependency. The h2 NPZ has complete state/native arrays and153327 RHS/model rows.

## Material semantic finding: the h2 terminal stencil is already complete

The published h2 independent review asserts `required_terminal_states=4`, `available_terminal_states=3`, and the R3Q report interprets the stop as a missing fourth state. This conflicts with actual source and saved output.

Original HyRec Oct2012 `history.c` sets `nz=floor(2+log((1+ZSTART)/(1+ZEND))/DLNA)`. Original `hyrectools.c::rec_interp1d` computes `ix=floor((x-x0)/dx)` and then clamps to `1<=ix<=Nx-3`; it uses entries `ix-1..ix+2` and leaves `frac=(x-x0)/dx-ix` unclipped. At h2 z=0, Nx211717, raw index211715.47262308892, clamped ix211714, frac1.4726230889209546. Required global nodes are211713,211714,211715,211716.

The saved h2 NPZ contains exactly those last four nodes, with z `[0.00010496835891560252, 0.00006251480409291688, 0.000020063051384022756, -0.00002238689928646398]`. The positive-to-negative bracket includes z=0. `primordial_2012_refined_low_z.py::continue_refined_low_z` returns `STOP_AT_SOURCE_Z0_CUBIC_STENCIL` only if the end is reached and at least four states are retained; fewer states produce `SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL` instead. Its saved verification already reports both interpolated scalars, four indices, and common-input interpolation byte MATCH.

The source-compatible numerical endpoint is therefore complete within the original same-h computation. The exact failure category is **review/report interpretation error**, not physical failure, numerical stencil deficiency, missing execution, or license for an extra RHS at negative redshift. Preserve the old receipt as provenance and publish a scoped correction with original clamp evidence. Global h/h2/h4 convergence remains unavailable because the independent h4 history is incomplete, not because h2 lacks this endpoint stencil.

Also, R3Q top-level EVIDENCE.json intentionally/historically still describes sandbox smoke003 and says ncp_execution/event_execution NOT_RUN. It must not override later actual NCP receipts and current DAG. Add an explicit supersession link rather than erasing that historical record.

## Candidate follow-up targets (at most3)

| Candidate | Why admissible now | Required discriminating work | Kill criterion | DAG effect |
|---|---|---|---|---|
| A. Bounded actual h4 observer/causal-path cost study | Existing reviewed event checkpoint and unchanged exact source path; current implementation copies complete photon prefixes on every FULL callback, although online oracle samples a small subset. | Profile <=128 accepted updates or a bounded replay of saved actual callback inputs; preserve detached callback semantics, sample selection, source/stage ordering and numerical outputs. Compare CPU, wall, RSS and array bytes. | Drop if prefix copies/validation are minor or selective copying changes callback/diagnostic contract. | Establishes actual remaining cost before any exact optimization; can support next h4 stages. |
| B. Connect exact array ratio evaluation to actual spectral audit | R3P independent ratio API is already tested; R3Q compare_native_stream still executes per-row scalar parsing, fBB, tolerance and ratio. | Blocked row parsing/array assembly with original scalar fBB where required; end-to-end parsing+allocation+FFI measurement, identical first failure, maxima and binary64 gates. Do not use isolated110× ratio as predicted solver speedup. | Drop if total audit cost does not improve or error ordering/rounding changes. | Completes an explicit R3P remaining implementation connection. |
| C. Resume independent h4 from reviewed event+2 to its next source stage | The new checkpoint now fulfills the input dependency. Current loader still accepts only immutable start8 at iz72900, and original quarter runner is limited to first event+2. | A strict event-checkpoint adapter and source-identical augmented-state stage continuation, retaining actual2×2 RHS memory and1519 accepted photon columns. New bounded <=128-step same-h C comparison before any external longer campaign. | Reject any checkpoint interpolation/C-state injection, reseeded memory, thermal guard change or new allocation inferred from old600/900 receipts. | Advances the actual missing independent h4 coverage required by three-grid convergence. |

Recommendation: under this user's **remaining bottleneck and numerical limitation** scope, first correct the false h2-stencil blocker as an intake finding, then choose A only if a new bounded profile shows that exact snapshot/validation work materially contributes. B is a good alternative if the available saved native stream makes end-to-end replay cheaper. C is scientifically strongest for eventual convergence but is a separate stage implementation rather than a claimed acceleration and requires an explicit scope choice in the parent plan. Select exactly one main implementation candidate after evidence.

## Local protocol application

Read uploaded04 Adaptive CMB Code Development Protocol,05 DAG Research Executor,07 Figure Residual Error Pass and08 Figure Hostile Audit from project_sources. Applicable subset is contract/source/stage reconstruction, at most3 admissible candidates, one chosen minimal change, PHYS-MATH then PHYS-MATH-CODE review, actual Python-generated plots directly inspected, and adversarial regressions against the claimed invariants. Generic CMB gauge/LoS/Bessel checks are not inputs to the present q=0 recombination optimization.

These older prompts' blanket prohibition on performance work while any physical mismatch remains should be interpreted under the current explicit user instruction: same-physics exact optimization is authorized while original U5 HOLD and global convergence remain recorded. Do not change physics/tolerance to satisfy a speed target. R3P completed tests and full trajectories are reused, not rerun or counted again.

Current new-run cap remains60CPU/180wall/2GiB per process, with reserve, smoke16 or pilot<=128. Whole-process-tree RSS must be measured separately from max individual waited child. Old allocations remain CLOSED_HOLD_NOT_RESET. No additional scientific execution or independent current production validation was performed by this intake reviewer.
