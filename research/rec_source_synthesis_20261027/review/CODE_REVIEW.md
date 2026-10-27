# C9 independent implementation, raw-result and figure review

## Decision

**PASS for the implemented fixed-source HD diagnostics and exact native-real represented-history module.** No current-task blocking defect was found. The parent may advance to its scoped admission and delivery decision without another primary execution or another review cycle.

The decision covers the frozen code, its saved actual results and the two inspected figures. It does not qualify the seven failing HD source lines, supply physical H5 epsilon, or increase the original programme count. Scientific admission remains parent-owned.

## Independence and scope

The controller reported an actual `agent thread limit reached` rejection when requesting a fresh reviewer. Under the supplied repository agent-capacity rule, this completed reviewer was reused. **A fresh C9 thread was not created.** This reviewer knew the prior R6 theory context but did not implement either new module or participate in its primary executions. The current pass is independent of the implementation, with the prior-theory context limitation stated explicitly. Requested identity is Astra reviewer; observed runtime model identity remains `UNKNOWN_NOT_EXPOSED`.

The review used the actual `/workspace/scratch/6104ad84b826/survey_repo/AGENTS_central_ee94bef8.md`, the frozen `CODING_CONTRACT.md` (`7dd2e930cad8bf919a9dbbf90a0426f76ea00eaf6eabf16f3d677b8726d1364e`), unchanged `THEORY.md`, `EXECUTION_FREEZE.json`, all new scientific Python files in `hd_joint/` and `history_remainder/`, their execution receipts, controls, saved JSON/CSV structure and summaries. Packaging helpers being changed elsewhere were outside this assignment.

Skill context used: PhysMath Research Loop 1.3.0 `SKILL.md` already read in the prior turn; `references/CODING_LOOP.md`, selected C9; and `references/POLICY_INTEGRATION.md`, read for this pass. This review preserves the parent's user-locked canonical workflow, criteria and finite review boundary. It creates no new scientific admission gate.

The reviewer changed only this report, `CODE_DECISION.json` and the narrowly scoped `review/code_check/` audit artifacts. No production source, primary raw result, figure or historical result was changed. There was one code/raw/figure pass and one small independent audit of saved records; no recursive reviewer or primary replay.

## 1. HD formula-to-code review

`joint_diagnostic.py::joint_thermal` constructs the source gap, dimensionless energy arguments and mismatch with exact `Fraction` arithmetic from the original decimal literals. The SI factors for `cm^-1` and GHz are correct. It does not compute delta by subtracting rounded `x_E` and `x_nu`. The production expressions match the frozen formulas:

    I = tanh(delta/2)
    D = expm1(-delta)/[-expm1(-x_E)]

The callable treats exact coherence explicitly, returning exact floating zero diagnostics and ratio one. Nonzero diagnostic underflow is rejected instead of being mislabeled as analytic zero. Nonfinite inputs, nonpositive gaps/frequency, negative lower energy, unsupported temperatures, booleans and exponent overflow have explicit failure paths. The actual interface is restricted to the original three temperature nodes and finite representable outputs.

`decimal_reference.py` imports no production function or transformed formula. It independently constructs Decimal energy arguments, evaluates positive Planck/Boltzmann fluxes, and evaluates the original exponential source ratio at 80 digits. Sharing immutable source literals and SI constants is appropriate; the production numerical transformation and arithmetic are different. `run_diagnostic.py` evaluates the small deviation itself relative to the Decimal deviation, separately from its ratio near one. Thus agreement of `1+D` cannot hide an inaccurate tiny D.

The 24 saved actual cases cover exactly eight lines at 50, 100 and 200 K. Recomputing their comparison errors from the saved production values and Decimal references gives:

| Quantity | Maximum relative error | Frozen tolerance |
|---|---:|---:|
| Paired-flux imbalance I | 3.011593202799463e-16 | 2.842170943040401e-14 |
| Source/Planck deviation D | 2.999772662453845e-16 | 2.842170943040401e-14 |
| Source/Planck ratio | 9.196997925947943e-17 | 2.842170943040401e-14 |

All actual I/D sign pairs oppose each other, as required. The maximum magnitudes are `|I| = 8.770964953285911e-7` and `|D| = 1.7541951787469943e-6`.

### Delicate small-deviation cross-check

The reviewer evaluated only two selected delicate cases with a separately written 100-digit calculation, without importing either the production code or its 80-digit reference. With `A=exp(x_E)` and `B=exp(x_nu)`, it used upward flux `1/(B-1)`, downward flux `(1+up)/A`, and deviation `(B-A)/(A-1)`.

- The smallest absolute saved D is line 1 at 200 K: `4.1745971013940654e-12`. Its production relative D error is `1.610389687317524e-16`.
- The maximum relative D-error case is line 1 at 100 K: `5.470240070099096e-12`. Its production relative D error is `2.999772662453845e-16`.

The independently recomputed 100-digit values agree with the saved 80-digit references at roughly `1e-68` relative for these cases. The small deviations retain their significant digits; they are not being recovered from rounded ratios near one.

### Source and control boundary

The source, original parser and original gate evidence are byte-pinned. For every actual case, the exact absolute gap equals the preserved source-gate gap. The unchanged 35 Hz criterion still rejects seven of eight lines. No qualified production line consumer is called. Collider blocks remain separately identified as para- and ortho-H2 with 54 retained rate values, with no mixing or interpolation call. The runner checks source roundtrip preservation.

Saved controls report **21/21 PASS**: three exact-coherence controls, two mismatch signs, thirteen invalid/domain cases and three source/collider/gate preservation checks. No historical 54-rate suite was replayed. The source gate remains `FAIL_ORIGINAL_35_HZ_7_OF_8`, `production_approved=false`, and both collider mixing and temperature extrapolation remain false.

## 2. History implementation and dangerous cases

`remainder.py` converts finite binary64 source values exactly to rationals and supports strictly increasing finite nonuniform grids. Sample-count checks, invalid-grid checks and the half-open causal-domain check precede meaningful evaluations. All production arithmetic for values, slopes, jumps, signed remainders and bounds is rational; conversion to binary64 is confined to display fields.

The directional slope implementation uses right-biased knot selection for positive motion and left-biased selection for negative motion. This is the required one-sided convention at a starting knot. A zero step returns before any derivative request, while still rejecting an invalid query such as the excluded final endpoint. The positive and negative jump weights are respectively `target-knot` and `knot-target`, with strictly crossed knots selected by the two bisectors. These choices omit starting atoms and target zero-weight atoms correctly.

The direct retiming path evaluates endpoint values and subtracts the directional linear prediction. The other path sums slope jumps. These paths share the intended sample/coordinate definitions, but do not evaluate the same remainder expression. For chords, the direct endpoint chord and the negative Peano jump sum are separate computations. Absolute jump sums retain all contributions even when signed sums cancel.

The 30 saved controls include both directions through an absolute-value hinge, the negative-sign mutation, starting-knot and target-knot cases, an included-starting-atom mutation, zero step at the left endpoint, affine/nonuniform grids, a cancelled multi-jump case with positive bound six, a flat source, invalid grids/shapes and the excluded right endpoint. The cancellation check has zero signed remainder and a positive envelope, so the tests do not silently identify the bound with the signed sum.

### Binding to the actual history

`primary.py` pins the history and original query context, retains the outgoing-virtual then outgoing-Lyman source ordering, verifies source indices and metadata, constructs `t_k = Fraction(eta[0])+k Fraction(dlna)`, and requires all frozen cells to match this exact grid. It checks the original stored-coordinate, sample, geometric-alpha, anchor-radius and curvature-coefficient witnesses. The nominal-minus-native-real anchor is reported separately from the preserved stored-geometric anchor.

The actual result contains **313/313 exact-grid witnesses**, **1,240 retimings**, and **313 chords**:

| Case | Executed count | Observed result |
|---|---:|---|
| Within-left | 313 | Exact zero remainder |
| Within-right | 313 | Exact zero remainder |
| Cross-left | 313 | Exact signed identity and bound |
| Cross-right | 301 | Exact signed identity and bound |
| Unavailable right crossing | 12 skipped | `SKIP_CAUSAL_PREFIX` |
| Chord | 313 | Exact negative-Peano identity and bound |

The 12 skipped incoming indices are 134–144 and 311, exactly as expected from the original metadata. Their chords use `(q+t_5126)/2` on the right. The saved rational values verify that these fallback endpoints lie strictly between the query and the excluded endpoint. No future sample or extrapolated target is introduced.

All **614** actual crossed-knot remainders are nonzero, so omitting the jumps would fail every executed crossing. All **626** within-cell remainders are exactly zero. The saved actual chord cases happen to have no strict cancellation: their absolute remainder equals the absolute-jump envelope. This is an observation about these selected queries; the general cancellation behavior is covered by the separate synthetic control.

The actual maxima are `1.8566648889656617e-19` for the retiming remainder and `1.6749900771700771e-19` for the chord remainder, in occupation departure. The largest stored-versus-native-real clock difference is `4.71736365248443e-16` in eta. These are representation quantities, not estimates of a physical history error.

## 3. Independent saved-result audit

`review/code_check/audit_saved.py` is a small standalone reviewer check. It imports neither new production module and reruns neither primary. Its saved `PREEXEC.json` records its scope and limits; `RESULT.json` records the actual outcome and debit.

The audit passed the following checks directly against the saved records:

- Current byte identity of 22 unique frozen source/code/contract paths, and the history result identities recorded before and after plotting.
- All 1,240 retiming signed sums, weights, domain conditions, exact equalities and absolute bounds.
- All 313 chord kernels, signed sums, exact equalities, absolute bounds and fallback endpoint conditions.
- Independent reconstruction of all 313 native-real query values from the original context's binary64 endpoint samples, with exact-grid cell and source-order agreement.
- All 5,127 serialized clock records and other exact/display record consistency.
- Actual case/skip sets, physical-null markers, all 24 HD saved comparison errors, original gate links and the two independent 100-digit delicate HD checks.

This is a raw-result consistency and selected-value audit, not a replacement primary calculation or an independent physical-history simulation. Its outcome is **PASS**.

## 4. Actual figure read

The reviewer opened both PNGs through `view_image`, rather than inferring their appearance from plotting code.

**HD figure:** all three panels are legible. The first two show signed I and D over the three source temperatures on symmetric-log axes, with line identities in the legend. Opposite signs and decreasing absolute magnitudes with increasing temperature agree with the saved data. The separate logarithmic Hz panel visibly retains one green passing line, seven red failing lines and the original 35 Hz threshold. It does not visually suggest source qualification from small thermal diagnostics.

**History figure:** the upper panel distinguishes the exact-zero within-cell series from the crossed-knot remainders and their absolute-jump envelopes. The lower panel shows chord remainders and their Peano bounds, including the sharp final-cell fallback changes. The title records 1,240 retimings, 12 causal skips, 313 chords and physical coverage 0/313. The overlap of markers and bounds is consistent with the exact saved equality in these selected actual cases. Both axes identify occupation departure and the original incoming query index. These saved-output figures support the stated represented-history conclusions.

Both plotting scripts read saved result files; no native or primary science computation is hidden in plotting. Saved history result identities remain unchanged across its plot receipt.

## 5. Resources and admission boundary

| Phase | Measured controlled CPU s | Observed wall s | Peak child/process RSS KiB |
|---|---:|---:|---:|
| HD primary including saved-output figure and measured wrapper | 4.301855738 | Child 4.376630457 | 82,148 |
| History primary including measured supervisor | 6.109471 | 6.151483030 | 69,660 |
| History saved-output figure including measured supervisor | 3.260151 | 3.302582492 | 85,992 |
| This review's independent audit | 0.442506 | 0.397330989 after imports | 59,172 |

The new reviewer audit was limited to 20 CPU seconds, 60 wall seconds, one thread and 2 GiB address space. Its CPU measurement includes process startup/import work and all input parsing/hashing up to the recorded measurement. Final receipt serialization and separate review preparation/I/O overhead remain `UNKNOWN_NOT_ZERO`. The audit debit belongs to the parent's review/integration allocation; it does not reset or transfer any implementation or historical budget. The tools observed exit code zero.

The implementation preserves `physical_epsilon=null`, `physical_bound_coverage=0/313`, `global_physical_completion=null`, `L4_ready=false` and `REI_activation=false`. The reviewed code introduces no IVP, native/RHS call, old Ks reconstruction, GEO root/matvec replay, physical error constant or changed admission tolerance. The original programme remains **32/88** in the scoped working return and **27/88** in shared authority, with a new canonical increment of **zero**.

## Findings and next action

**No blocking or repair-required finding is open.** The prior two theory clarifications are implemented: finite-partition semantics and generic final-cell handling. They are closed and were not expanded into new review requirements. No production-code repair is requested.

The positive transition is the parent's scoped C9/C10 admission and delivery of these numerical diagnostics and represented-history results, retaining the existing physical source gates and proof obligations. No further primary run is warranted by this review.
