# C9 independent code and saved-result review

Unit: **REC-H5-ELECTRON-RESPONSE01**  
Reviewer: `/root/response_c9_audit`  
Date: 2026-10-28  
Verdict: **PASS_SCOPED**, with the original real-model source bridge retained as **FAIL (7/9)** and the provenance limitation below explicitly retained.

## 1. Decision and exact scope

The reviewed implementation computes the 313-component incoming response of the declared frozen represented-coefficient models at the 132 saved source points. Its transpose orientation, source-column support, units, fixed-point affine identity, saved-data discrepancy decomposition, and declared numerical gates are consistent with the source and artifacts inspected. I found no blocking scientific implementation error in this scope.

The original real-formula model has an accepted numerical adjoint calculation and a failed declared source-forcing bridge at seven of nine saved controls. The additional native-prefix coefficient model has its own definition and saved output; its source and scalar bridges pass all nine controls under the unchanged tolerances. This review accepts the two-model comparison and scoped prefix result. It does not relabel the original failed bridge as a pass.

This decision concerns saved fixed-P source-point incoming response. Exact-real nonsingularity, coefficient boxes, inverse-gain bounds, continuous-domain response bounds, physical tubes, and the complete coupled thermodynamic tangent remain their stated provider obligations. QSS03 is not supplied by this unit. The inherited physical count remains **0/313**, canonical count **28/88 with increment 0**, and H6/H7 remain open. Predecessor C10 completion is separate reused evidence, not completion credit for this successor.

## 2. Actual review method and independence

I directly read `CONTRACT.md`, `THEORY.md`, `MODEL_COMPARISON_CONTRACT.md`, `INPUT_MANIFEST.json`, all three Python files, all six execution `RESULT.json` files and resource receipts, `RESOURCE_LEDGER.json`, the prefix model summary, and raw response samples at indices 0, 66, and 131. I also read the original restored `hydrogen.c` source construction and scalar formula, the predecessor build receipt, and the copied scientific admission scope. The original source is under `recovered/electron_source/electron_field/inputs/original/HyRec/` in the shared workspace. After the author's targeted C9 changes, I read the wrapper diff, the preserved old wrapper, the current-environment and PLOTS002 pre-execution snapshots, and directly viewed both final PLOTS002 PNGs.

The separate helper `/root/response_c9_audit/c9_metadata_audit` checked hashes, original-member equality, JSON shapes, binding, finite serialization, counts, identical thresholds, and resource arithmetic. Its findings were incorporated after the main reviewer inspected the corresponding source, result, and ledger material. The helper modified no files.

The review used a separate nonauthor agent, direct source-to-code reasoning, an independent algebraic derivation of the discrepancy identity, and read-only artifact checks. **Neither reviewer imported or executed the scientific modules, reran a solver, reconstructed a numerical source, invoked the native library, or ran a new scientific calculation.** The Decimal/SciPy results cited below are inspected existing execution evidence. The reviewers' hash/schema/arithmetic work is metadata work whose cost was not measured; it is not claimed to have zero cost.

The study's `independent_residual` and SciPy comparisons supply algorithmic independence inside the author's test implementation. Decimal80/120 alone supplies a precision comparison, not a separate implementation. This C9 review supplies separate reviewer judgment; it is not a second numerical reproduction. R6 conclusions and the root summary were not used as substitutes for checking the code and original evidence. Distinct runtime model families were not observed or inferred.

## 3. Source, support, and units

The original `populateTS_2photon` source establishes the following incoming dependence with state order `(2s, 2p, virtual[0:311])` and incoming order `(virtual[0:311], Ly0, Ly1)`:

| Incoming column | Source row | Original real-model coefficient |
|---|---:|---|
| Virtual bin b | 2+b | `V[0][b] * x1 * pi(Dtau[b])` |
| Ly0, column 311 | 1 (2p) | `3*kL*H/nH` |
| Ly1, column 312 | 0 (2s) | `3*kL*H/nH*kBeta` |

The original source locations are `hydrogen.c` at `sr[0]`, `sr[1]`, and `sv[b]` inside `populateTS_2photon`. They agree with `SOURCE_ROWS = (2,...,312,1,0)`, `incoming_coefficients`, `source_direction`, and the source rows retained in both response sets. No incoming radiation term enters A/B/C/V at fixed P and tables in this source construction.

`C_storage[i][b]` is the mathematical lower-left entry `C[b][i]`. Its 2-by-311 storage is preserved. `scalar_row` uses positive `Beta/H` in the first two coordinates because the source scalar is `FH = -(c0 - xr0*Beta0 + c1 - xr1*Beta1)/H`. The sign and placement of q therefore agree with the source. With nH in cm^-3, H and rates in s^-1, and dimensionless populations/incoming departures, M and G have units s^-1, q is dimensionless, lambda has units s, and J is dimensionless, consistent with `d xHII/d ln(a)`.

The parser explicitly validates the native source/library/table identity, fixed FULL/H_STEADY/He-neutral labels, xe=xHII, fsR=meR=1, coordinate order, units, saved-call binding, finite hexadecimal inputs, array shapes, positive physical scales, nonnegative tau, band boundaries, and coefficient-temperature prelude. Native x1 uses the saved binary64 subtraction rather than silently replacing it with an exact-real subtraction. The saved inputs are hashed before and after each study invocation. The copied input files match both the manifest and restored predecessor bytes.

## 4. Adjoint factorization and residual construction

`solve_block(..., transpose=True)` transposes A, uses stored C as the upper-right transpose block and B as the two lower-left columns, and constructs

```
lower_T = (0,) + upper_original[:-1]
upper_T = lower_original[1:] + (0,)
```

These are the correct row-index shifts. The factorization solves V^T against the virtual RHS and both columns of B^T, forms `A^T - Cstored * V^-T * B^T`, solves the 2-by-2 Schur system, and back-substitutes. The primal branch uses the corresponding untransposed blocks. The zero-band disconnected portions of V remain present.

The separately written `study.coordinates` assembles M from original `(row,column)` positions and obtains its transpose by swapping coordinates. `independent_residual` performs sparse multiplication of those entries; it does not replay Schur elimination. SciPy builds a COO/CSC matrix from the same original-coordinate convention and calls an independent sparse solver. I traced these paths separately and found the stored-C convention and band orientation consistent.

The abstract adjoint identity requires exact-real M invertible. The particular no-pivot tridiagonal/Schur implementation additionally requires the stated exact V/elimination conditions. Its observed nonzero Decimal pivots and Schur determinants are numerical diagnostics. The code and contracts do not turn them into exact or interval nonsingularity claims. The transpose is not assigned the original matrix's row diagonal dominance.

The code enforces finite output, nonzero numerical divisors, and the exact-zero denominator rule for residual and source mismatch normalization. Tau=0 takes the polynomial branch without division by tau. The declared finite-data scope is respected. C6's malformed input cases and changed-solution, wrong-transpose, and swapped-Lyman controls are meaningful tests of these implementation paths; the corresponding saved diagnostics are summarized below.

## 5. Two coefficient models and preserved failure

`incoming_coefficients` evaluates the original branch formula in Decimal arithmetic after exact lifting of the saved binary64 tau and source literals. This is a defined real reconstruction. `native_prefix_data` preserves the original binary64 source expression order, including both subtractions surrounding the optical-depth quotient, the left-associative Lyman rate calculation, and the scalar-source grouping. `prefix_coefficients` then lifts the rounded prefixes and multiplies the lifted virtual prefixes in Decimal. The resulting real model leaves M, q, a, and d fixed while changing G.

For the virtual source, the code reproduces `fl(fl(a64*u64)*pi64)`, while its model coefficient is `lift(a64)*lift(pi64)`. For the Lyman terms, the source's `3*RLya*x1` prefix is retained before the Ly-beta factor. This distinction is necessary: cancelling x1 algebraically in the original real model does not recover that native prefix's intermediate rounding. The predecessor build receipt's `-fno-fast-math` and `-ffp-contract=off` flags support the stated source operation order.

The prefix output reuses the 132 saved C7 lambda vectors. No new all-point adjoint solve occurs in `native_prefix_comparison`; the three Decimal120 comparison solves are separately visible in the C8 validation path. Reuse is mathematically appropriate because G does not enter `M^T lambda=q`.

The stored parity evidence reports **44,133/44,133 source entries**, comprising 132 primaries plus nine controls, each of length 313. The bitwise comparison uses packed binary64 values, including the sign of zero. I reviewed this comparison implementation and the stored parity details; I did not rerun it. It supports observed source-output parity on these records and this host. Neither all intermediate native bits nor cross-libm portability follows from that result.

The old C8 `RESULT.json` retains `pass: false`, all seven source-gate failures, and exit code 2. It remains charged in the ledger. The prefix run has a distinct directory, model identifier, output files, and model contract. The source threshold is byte-for-byte identical in both C8 result files. The old C8 result predates the explicit top-level `model` field; its path, original CONTRACT, real response input, and separate prefix contract identify it. It has not been rewritten to add metadata after the fact.

The recorded worst-row diagnostics occur at tau about 1.45e-6, 1.85e-6, and 2.96e-6, where native reconstructed transmission-factor relative differences are about -2.61e-11, +2.40e-11, and -6.88e-12. The diagnostic `expm1` comparisons are at about 1e-17. This supports thin-branch subtraction cancellation as the observed mechanism at these three rows. The second subtraction `1-(1-pi)` remains a separate possible loss mechanism for thick bins; no all-bin dominance claim is made from the three displayed diagnostics. The production C source remains unchanged.

## 6. Numerical evidence and acceptance gates

The following values come from the inspected saved executions, not new reviewer computations.

| Check | Existing evidence | C9 assessment |
|---|---|---|
| Primary records | 132 ordered, distinct writer bindings; 313 J and G entries per point | Consistent with declared scope |
| Total response values | 41,316 per model | Count and finite serialization verified |
| All-point adjoint residual | Maximum 2.6227162888490522e-79; gate 1e-60 | Pass in the declared componentwise backward-residual sense |
| Decimal80/120, original model | Maximum scaled J difference 1.2809732968696686e-78 at 0/66/131 | Pass |
| Decimal80/120, prefix model | Maximum 1.2432792090687374e-78 at 0/66/131 | Pass |
| Independent SciPy adjoint, both models | Maximum scaled response difference about 3.2323150286676381e-14; gate 1e-10 | Pass; three representative points |
| SciPy adjoint backward residual | Maximum about 4.2246186208044063e-16 | Reported separately, correctly |
| Primal directional checks | Ly0, Ly1, alternating virtual at three points; all nine pass in each model | Independent sparse primal and Decimal reciprocity evidence |
| Original source bridge | 2/9 pass; maximum 2.50906774683486e-13 against 1.1368683772161603e-13 | **FAIL retained** |
| Prefix source bridge | 9/9 pass; maximum 3.0139416037426664e-17 against the identical gate | Pass |
| Scalar FH bridge | 9/9 pass in both models under the same termwise absolute scales | Pass |
| Algebraic discrepancy closure | All nine per model below 1e-60; largest about 2.3e-75 | Pass as an algebraic accounting check |
| Wrong transpose control | Normalized residual about 0.36057 | Rejected meaningfully |
| Changed adjoint control | Normalized residual about 0.0049751 | Rejected meaningfully |
| Swapped Lyman support control | Source mismatch about 8.1318e-4 | Rejected meaningfully |

The source bridge is gated separately, so the decomposition cannot convert an arbitrarily wrong G into acceptance by treating its error as an allowed remainder. Independently deriving its signs gives

`q^T DeltaX = lambda_hat^T M DeltaX - r_lambda^T DeltaX`

and `M DeltaX = G du + e_G + (r_c-r_b)`. Adding the saved scalar discrepancies yields exactly the four terms implemented in `validation`: scalar rounding, source reconstruction, saved primal residual, and negative adjoint-residual contraction. The fixed coefficient and point checks make d cancel between the baseline and each control.

The nine saved native controls are zero/negative/doubled scalings of one incoming vector at each of three points. They test one direction per point, not 313 independent native columns. The full response vector is supported by the source-derived sparse G, the complete adjoint equation, all-point residual evidence, and the additional primal directional checks. The 80/120 and binary64 comparisons are numerical checks; they supply no interval forward-error enclosure.

## 7. Interpretation and full-state boundary

For each declared exact-real frozen model and invertible M,

`F(u+du)-F(u) = J^T du`, and `|DeltaF| <= ||J||_1 ||du||_infinity`.

The computed prefix point norms range from approximately 2.061882971775384e15 to 2.193136787518652e15. They measure the defined dimensionless incoming sensitivity at saved points. A maximum over 132 points is not a certified bound over a continuous coefficient or physical domain.

The fixed-point construction is a real affine model. The stepwise binary64 program is a rounding map; its derivative is not being computed. The complete varying-P tangent also requires `dd`, `dq`, `da`, `dG`, and `dM`, with the table cell and optical-depth branch treated consistently. `THEORY.md` includes those terms rather than discarding them. The present scope and inherited physical nulls are therefore coherent.

## 8. Findings and resource review

### C9-F01 — original execution-time code and environment identity was not captured

**Classification:** provenance/reproducibility limitation; nonblocking for the inspected scoped result.

**Target and evidence:** the original five attempt001 resource receipts record commands, limits, exit status, timing, memory, and native-call counts, but do not record the executed source hashes or Python/NumPy/SciPy/libc versions. Original C6–C8 results were retained while later prefix and plotting paths were added to `study.py`.

**Impact:** a review-time snapshot can bind the current code and saved outputs, but cannot by itself establish precisely which historical code bytes produced each run. This is especially relevant to `math.exp` portability. No numerical inconsistency was demonstrated by this omission.

**Disposition:** historical limitation retained explicitly; prospective handling corrected. The author added `C9_CURRENT_ENVIRONMENT_SNAPSHOT.json`, explicitly labeled as a later review snapshot, and preserved the old wrapper under `reviews/source_snapshots/`. The revised wrapper writes code/input/environment identities before launching a new child and binds that snapshot in its resource receipt. The actual PLOTS002 receipt and pre-execution snapshot agree with the current reviewed code hashes. `C9_RECEIPT.json` also binds the currently reviewed artifacts. These additions improve future tracing without manufacturing historical execution identities. No scientific rerun was requested or performed for this correction.

The inspected current environment reports Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, and glibc 2.39. This is later review-time metadata for the original scientific executions and actual pre-execution metadata for PLOTS002. The review snapshot's old code hashes correctly identify its capture before the final wrapper/legend changes; the final hashes are in the PLOTS002 pre-execution snapshot and C9 receipt.

### C9-F02 — cumulative budget limiter has an integer boundary limitation

**Classification:** low-priority execution-wrapper limitation; no effect on these measured runs.

**Target and evidence:** the originally reviewed wrapper used `ceil(remaining)` and an RLIMIT_CPU hard limit of `cap+1`, then rejected a negative remaining balance after the child ended. With less than one second left, that mechanism could permit a child to exceed the exact cumulative allocation before the post-run check.

**Impact and disposition:** **closed for prospective use by the targeted implementation change.** The final wrapper uses `min(30, floor(remaining)-1)`, rejects `cap < 1`, sets the soft and hard CPU limits equal, and retains the measured post-run ledger check. I read the exact diff against the preserved original and verified its byte identity against the previously reviewed hash. The one-second reserve handles the reported boundary defect conservatively; it is not a claim of an exact subsecond CPU measurement. The saved scientific results were unchanged and were not rerun.

All six receipts match their ledger entries. The known child CPU total is **15.866848 s**, including the failed original C8 run and both saved-result plotting attempts, leaving **44.133152 s** of this unit's independent 60 s allocation. Maximum measured child wall time is **4.200537989003351 s**, and maximum reported RSS is **227,340 KiB**. Each child was configured with a 512 MiB address-space limit and single-thread environment variables. All six stderr files are empty. New native calls remain **0**. Parent, model, network, metadata, and packaging costs remain **UNKNOWN_NOT_ZERO**. The predecessor's 4.704676 s and native-call allocation have not been transferred or reset into this unit.

The only `study.py` change during C9 moved the source-comparison figure legend to `center right`. Reversing that exact text change in memory reproduces the previously reviewed source SHA-256, establishing that the scientific implementation was unchanged. PLOTS002 regenerated figures from saved results and exited 0, charging 4.172248 CPU s. Both final PNGs were directly inspected: the legend no longer covers the last transmission-factor diagnostic, and the retained seven original source-gate failures remain visible. No plot appearance is used as numerical acceptance evidence.

## 9. Handoff and closure

There are no blocking scientific findings for this scoped C9 decision. The original source-bridge failure remains an outcome of the original model, the additional prefix result remains separately identified, the historical provenance limitation remains visible, and the prospective wrapper defect is corrected. Further scientific execution is not required by this review. Delivery may proceed with the current code/result identities, explicit historical-provenance limitation, stated full-state obligations, and unchanged physical/canonical ceilings.

This reviewer modified only `reviews/C9_REVIEW.md` and `reviews/C9_RECEIPT.json`. The receipt provides the exact review-time artifact identities and records which checks were read-only. It does not claim an unobserved execution, runtime model family, QSS03 certificate, or publication acknowledgement.
