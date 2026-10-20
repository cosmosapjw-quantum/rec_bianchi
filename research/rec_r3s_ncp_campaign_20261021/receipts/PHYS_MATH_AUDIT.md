# Independent PHYS-MATH audit: R3S finite platform campaign

## Verdict and scope

**PASS_SCOPED_MATHEMATICAL_CONTRACT.** The fixed whole-job DAG, conditional work/span lower bound and conditional Amdahl calculation are mathematically consistent. The original accepted-step recurrence remains the required scientific contract. This verdict establishes neither a new NCP numerical result nor new physical validity.

The reviewer authored neither the coordinator nor its tests. This review uses the actual restored recurrence/comparator source, the R3S manifest and theory note, and the linked preserved receipts. It performs no REC trajectory, saved-stream timing trial or old test rerun. Source hashes and the final code-audit linkage are recorded separately in `PHYS_MATH_AUDIT.json`.

## 1. State, units and retained recurrence

Let the extended state contain the accepted material state, the current/previous RHS memory, accepted photon history and stage variables. The frozen code then advances a single source index through a map of this extended state. This is a statement about the expanded state, not a claim that the material variables alone form a memoryless recurrence.

The independent continuation source retains the predictor grouping `1.25 * current_rhs - 0.25 * prev2_rhs`, current accepted FULL-column ownership and the source stage decision at each accepted input. A post-Saha trial does not commit a photon-history column. Consequently the next accepted state depends on values owned by its predecessor; nominal CPU count cannot remove that edge.

R3S selects existing complete-program invocations. It introduces no atomic/thermal term, force term, interpolation rule, predictor coefficient, stage criterion or tolerance. The 16-step pilot commands use the existing public R3R launcher and the frozen h4 start. The original same-h gate remains required. The distinction between the user's R3P reference `h=4.245e-5` and the convergence module's `H0=8.49e-5` is retained explicitly.

Times in the scheduling model have time units; speed ratios and fractions are dimensionless. In the original spectral ratio, the numerator and the tolerance denominator have the same field units, so the ratio is dimensionless. No dimensional physical quantity is converted by the scheduling layer.

## 2. Conditions for independent whole jobs

Two jobs commute at the scientific-payload level only under the stated hypotheses: identical fixed inputs and source, private outputs, no data dependency between them, no mutation of each other's consumed state, and preserved operation order inside each job. Finite resource limits may change completion or failure timing; CPU/wall/RSS measurements and timestamped logs need not commute.

The ready catalogue contains two independent trace checks. The saved-stream benchmark and the legacy pilot depend on both trace checks; the NumPy pilot depends on the legacy pilot. Timing jobs are mutually exclusive within this campaign. Completed predecessors may be reused only through source/input/identity-linked receipts. Future h4 stages, Rust builds outside the selected envelope and the global convergence diagnostic have no executable builder in this catalogue.

This justifies a first ready width of at most two. It does not justify creating 64 copies of an existing check, running adjacent accepted time steps concurrently, or treating a campaign barrier as exclusive ownership of the whole host.

## 3. Work/span lower bound

In a fixed-cost model, let each job require nonnegative work `w_i`, let `W` be total work, let `L` be the largest sum along a dependency path, and let `P>0` be the number of equally capable processors available to the schedule. Any completed schedule of length `T` processes at most `P*T` work, hence `T >= W/P`. Every dependency path must execute in order, hence `T >= L`. Combining the two inequalities gives

\[
T\ge\max(W/P,L).
\]

These are lower bounds under explicit fixed-cost assumptions. They supply no observed wall time, measured parallel efficiency or theorem excluding different numerical algorithms. For the present catalogue, the timing barrier further prevents the benchmark and two pilots from overlapping. With all five jobs selected, even an ideal schedule retains the sum of those three exclusive durations after the two trace predecessors finish.

File I/O, startup, resource contention and scheduling overhead are not assumed to vanish in an actual receipt. The source-selection rationale therefore supports a finite platform check, not a many-core speedup claim.

## 4. Resource arithmetic

The per-process address-space ceiling remains 2 GiB, and each whole job is supervised under a 60 CPU-second/180 wall-second envelope. For five distinct jobs, the allowance sum is 300 CPU seconds and 900 wall seconds. The proposed separate campaign reserve adds 5 CPU seconds and 12 wall seconds, giving the explicit requested allocation 305/912. This arithmetic creates no execution authorization and does not enlarge one trajectory's public cap.

Admission must reserve the full active and newly launched job allowances against current effective capacity. The final design gives no extra capacity credit for summed RSS: RSS may include shared pages, and it is not an exact amount that can be added back to `MemAvailable` or cgroup headroom. The physical capacity observation is separate from per-process AS limits and sampled process-tree RSS.

No exact aggregate memory-peak theorem follows from polling. Finite polling, caller-owned CPU assignments and supported Linux process enumeration remain implementation conditions to be assessed in the separate code audit. The requested 64-CPU/128-GB target is not a current host observation.

## 5. Conditional Amdahl calculation

Suppose a fraction `q` of an otherwise unchanged baseline cost is accelerated by a factor `a`. Under `0 <= q <= 1` and `a >= 1`,

\[
S=\frac{1}{1-q+q/a}.
\]

The denominator lies between `1/a` and `1`, so `1 <= S <= a`. It equals one at `q=0` and `1/a` at `q=1`. Direct differentiation gives

\[
\frac{\partial S}{\partial q}
=\frac{a(a-1)}{(a+q-aq)^2}\ge0.
\]

The exact new input and response in `WOLFRAM_EXACT_INPUT_CHECK.json` agree with these derivations. The retained undefined-symbol warning concerns the displayed `W/L/P` expression; that display is not used as proof of a scheduling theorem.

The parameter `a=1.3641298365714964` is reused from R3R's measured paired saved-stream CPU ratio. The whole-solver fraction `q` has not been measured. Substituting illustrative fractions therefore produces conditional model values, not an observed or predicted NCP solver speedup. Compiler/library/host changes may also change the component timing parameter itself.

## 6. Numerical and physical claim boundaries

R3R's source-ordered scalar Planck evaluation, separate binary64 operations, ordered failure replay and 25,000-lane byte comparison remain prior evidence. They are not revalidated merely by launching a new scheduling layer. NCP trace, benchmark and matched-pilot results remain `NOT_RUN` until actual source-bound receipts return.

The reused h2 endpoint already has the original four-state cubic stencil. Its historical three-state sentence is corrected by the preserved R3R addendum. Completing the remaining h4 trajectory is still necessary for global coverage, and it is not sufficient: complete h2 history assembly, nodewise C uncertainty and early boundary provenance also remain dependencies. The frozen comparator returns `UNCERTAINTY_MISSING` when required bounds are absent.

The final scientific limits remain U5 original-h `HOLD_9_FAIL`, U5 h/2 `HOLD_8_FAIL`, historical cost `CLOSED_HOLD_NOT_RESET`, global convergence `NOT_RUN`, `REI_activation=false`, physical validity `HOLD` and production readiness `NOT_APPROVED`. Implementation and dummy resource-test verdicts are assessed separately; they cannot raise these physical verdicts.
