# Independent source and theory intake — REC continuation 2026-10-26

Reviewer role: independent Astra-tier source/theory reviewer. Observed runtime model identity is not independently observable. This is the preliminary part of one review pass; implementation and raw-result review remain pending. No new source/RHS/IVP/operator evaluation or numerical scientific test was executed for this intake. Retrieval/parsing/tool costs are unmeasured, not zero.

## Source identity and duplication boundary

Read REC PR138 at `4a8e541030ee2cbd02e26ba671083b705d309d49`: `research/program_expansion_20261025/HANDOFF_HD_H5_KO.md`, `RESULT_HD_H5_KO.md`, the H5 `BOUND_INPUT_CONTRACT.json`, `README.md`, `THEORY_BINDING_KO.md`, `inputs/DERIVATION.md`, `code/h5_bounds.py`, and source-context metadata. Also read the PR137 PB01 `THEORY.md` and `NEXT_INPUT_CONTRACT.md`, THERMO01 theory/next contract and `code/source.py`, native `vendor/hydrogen.c`, the history producer/provenance, and HISTORY02R theory, frozen contract, adapter and actual-control code.

H5 producer is genuinely missing continuous source closure, initial/reference error, fixed state norm, whole-domain defect/stability, certified positive lower safe-tube radius and whole-cell curvature. A first cell still needs the initial and retarded-input enclosures. Replacing these by stored interpolation differences, represented-matrix inverse residual or `b_repr` would not close H5. Existing consumer requires a complete 313-query packet and leaves physical admission separate. Replaying its already completed controls is not progress.

HISTORY02R already derives and implements finite constant-shear crossing, crossing tangents, native-Wien reference conversion, a manufactured ten-coefficient angular history and a scalar boundary composition. Its actual-data tests load only a 314 by 24 early h4 history from the different cosmology and evaluate eight interior scalar interpolation cases. `verify_primary.py` lines 74–79 and 112–116 make this explicit. No original-source 313-query propagation-moment composition with the saved KS/PB response is hidden there. PB01 explicitly leaves named physical `DQ`, `DY`, reference and geometry owners open.

## Recommended finite new scientific object

GEO01 may bind the original 313-query represented history to the already implemented characteristic map for a newly declared diagonal constant trace-free shear, an imposed frozen isotropic emitter history, and target-normalized `dOmega/(4*pi)`. Its new science object is the propagated incoming susceptibility and angular moments for these actual represented source inputs. H5 physical uncertainty, anisotropic collision closure, thermal evolution and a coupled history solution remain unprovided.

Native KS is a scalar/isotropic incoming-to-outgoing map. Directional incoming values must not be presented as physical directional collision outputs by applying KS separately to rays. The target angular mean can be passed to the frozen scalar model, with that approximation explicit. Incoming quadrupoles remain radiation propagation data for a later angular collision owner.

## Independent analytic check

Let shear be `b_i(p)=p*v_i`, `sum(v)=0`, positive directional rates `1+p*v_i`, unit target direction `n`, `w_i=n_i^2`, delay `D`, and represented log energy ratio `Lambda`. The root equation is

`D + K(p D) - Lambda = 0`, `K(t)=0.5*log(sum_i w_i exp(2*v_i*t))`.

With `A=sum(w_i*v_i)`, `C=sum(w_i*v_i^2)`, one has `K'(0)=A`, `K''(0)=2*(C-A^2)`. Therefore for the source query shift `dq=Lambda-D`,

`dq'(0)=Lambda*A`,

`dq''(0)=-2*Lambda*A^2+2*Lambda^2*(C-A^2)`.

The normalized source-direction tangent is `Lambda*n_i*(v_i-A)`. It contributes no angular-history derivative when the prescribed emitter is isotropic.

Use the baseline-preserving represented incoming increment

`Delta u = g*dq + W(x*exp(dq))-W(x)`, `W(x)=exp(-x)`.

Then, with `h=g-x*W(x)` and `w2=(x*x-x)*W(x)`,

`u'=h*Lambda*A`,

`u''=h*(-2*Lambda*A^2+2*Lambda^2*(C-A^2)) + w2*Lambda^2*A^2`.

For uniform target solid angle and `S2=sum(v_i^2)`,

`<A>=0`, `<A^2>=2*S2/15`, `<C>=S2/3`.

Thus `<u'>=0`,

`Q'_ij = <(n_i*n_j-delta_ij/3)*u'> = (2/15)*Lambda*h*diag(v)_ij`,

`<u''> = S2*(h*(-4*Lambda/15+2*Lambda^2/5)+w2*2*Lambda^2/15)`.

These formulas are independently confirmed by hand derivation. The proposed 14-direction weights (six axes each `1/15`; eight cube corners each `3/40`) are normalized and reproduce all even angular moments through degree four: `<n_i^2>=1/3`, `<n_i^4>=1/5`, `<n_i^2*n_j^2>=1/15`. This suffices for the derivative identities. It is not a finite-shear angular convergence certificate.

The frozen scalar source is affine in incoming radiation. Consequently its first mean variation vanishes, and its second mean variation is `KS*<u''>` without an additional nonlinear incoming remainder. Changes of source coefficients, thermal state, geometry in the collision law and the true evolving history remain separate.

## Domain and numerical review conditions

1. Preserve original incoming ordering and source routing. Target energies are the 311 virtual-bin energies followed by E21 and E31 for incoming indices 311 and 312. Source outgoing column energies are not interchangeable with target energies.
2. Anchor `q(p)=q_native+Lambda-D(p)` and the reference offset at the exact represented baseline. Record the native-versus-geometric clock arithmetic difference separately. This anchored law defines a represented local chart; it must not silently be called an exact real-energy retarded identity at the rounded baseline.
3. With `V=max|v_i|`, `|p|V<1` gives an all-direction query-shift bound `|dq_j|<=Lambda_j*|p|V/(1-|p|V)`. For each existing conservative PB margin `r_j`, a sufficient common step is `|p|<min_j r_j/[V*(Lambda_j+r_j)]`, with a frozen interior safety factor. Check actual native cell and strict prefix too.
4. Absolute occupation is `f=u0+g*dq+W(x*exp(dq))`; signed departure must not be clipped. An all-direction lower bound is `f0-(|g|+K_W)*D`, where `D` bounds `|dq|` and `K_W=max x*exp(-x)` over `[x0*exp(-D),x0*exp(D)]`. Endpoints suffice unless the interval includes one, in which case include `1/e`. Sampled positivity alone must retain sampled scope.
5. Evaluate increments with a cancellation-safe formula: `g*dq+W(x)*expm1(-x*expm1(dq))`. Compute centered differences from increments. Tiny actual amplitudes require frozen component or operation scales, rather than an absolute `max(1,...)` scale that makes derivative gates vacuous.
6. Very small fixed-cell steps may make binary64 second differences unusable. Independent high-precision finite controls at the frozen step and half-step should use the exact represented chart constants. Recomputing a higher-precision energy logarithm changes the chart unless separately documented.
7. The existing KS interval certificate remains valid in its frozen represented-matrix scope. New logarithm/exponential-derived coefficients are not rigorously enclosed merely because a high-precision oracle agrees. Distinguish analytic moment identities, numerical coefficient evaluation, represented-K intervals and physical uncertainty.

## Pending same-pass review

Read the final frozen contract and implementation before execution; then inspect actual raw outputs, failures, resource receipt and only affected evidence. At most the authorized targeted repair may be accepted. No repeated H02R controls, KS build/639 RHS, PB primary/matvec replay, THERMO01 or HD source controls are justified by this intake.

Physical epsilon/outgoing physical bound remain null; global physical completion remains null; Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED and REI activation false are retained.


## Frozen-contract read — preexecution, same review pass

Read the local GEO01 `FROZEN_CONTRACT.md` version 1 and `THEORY.md` in full after the source/theory intake above. The equations, selected shears, target-normalized angular measure, Q14 derivative-moment scope, target-energy routing, baseline-preserving source/reference chart, fixed-cell step rule, scalar mean-only KS consumption, and represented-m2 interval scope are consistent. The new 60 inclusive child-CPU / 180 execution-wall second allowance is explicit and does not reuse historical allowance. The 96-root Decimal oracle and at most eight reviewer roots are bounded.

**Contract/theory decision: PASS_SCOPED_FOR_IMPLEMENTATION.** No theoretical blocker was identified in the stated controlled-propagation partial. This is not RUN_READY or result admission: implementation read is pending, followed by actual raw-result and figure review in the same pass. No numerical reviewer probe has been executed.

Retain the contract's distinction between analytic identities, finite numerical checks, represented-vector KS enclosure and physical uncertainty. Positive sampled occupations must retain sampled scope. The controlled geometry is newly selected; the inspected BASS return does not supply the missing target-matched physical H6 trace.


## C5 implementation read — same pass, before execution

Read all seven final modules (`common`, `geometry`, `decimal_oracle`, `primary`, `run_bounded`, `figures`, `prepare`) plus `IMPLEMENTATION.md`, input identities and the C5 manifest. The reviewed manifest SHA256 supplied with C5 is `659fb166bcba92656a21673efaa632d3a337da576fc0d15a1d262a38aaea6fa5`; its geometry/oracle/primary identities are respectively `092ff49c3ed442fbfee38b8d1239b3b002436d99098d0240e34e029d0ec83f5f`, `270976cbfd83f8d26d9863eb6910ef3ec089d1c4bc92f825436d7a8a8c04e757`, `2f898e808b9a447f31910a3776c3e8e8ba91b16d767c53a2c65f5dd09fd0d43c`.

The production derivatives implement the independently derived formulas. The separate Decimal path solves the original delay equation using full exponentials and exact represented inputs, without importing the stable shifted root or stable increment. Exact rational angular moments and signed interval dot selection are correct. Native target-energy/source-index routing is explicit. The saved KS number-response coefficients were checked against pinned old `research/rec_history_ks_20261025/code/primary.py`: its `numhat=3e6*LYA*H*(K[311]-delta)` uses the same operation order, justifying this narrowly scoped saved-coefficient equality. The source/event direct incoming subtraction and radiation/atomic sign pair are retained.

Two preparation findings were addressed before any scientific run: (1) the Decimal oracle now uses the strict enclosing bracket `Lambda/(1+2t)` to `Lambda/(1-2t)` to avoid false endpoint signs when an axis root equals the original theoretical bracket endpoint; this is an oracle bracket only, not an enlarged physical query domain, and keeps the same160 iterations, tolerances and input chart; (2) an exception during a finite step saves the current query/ray and all completed arrays, with uncomputed entries marked NaN. The reviewer did not edit implementation code.

The runner requires root RUN_READY, checks the C5 source/input snapshot, sets thread counts before numerical imports, imposes child CPU/address-space limits before start and enforces a wall timeout. Attempt paths cannot be overwritten or automatically retried. Counters are charged before scalar roots and operator actions. Figures read saved results and perform no source/root/operator calculations.

**Preexecution decision: PASS_SCOPED_RUN_READY_RECOMMENDED.** Root may issue RUN_READY for the one frozen primary. No unresolved issue blocks the stated controlled-propagation partial. This is not scientific result admission; raw outcome, resource receipt and actual figures remain to be reviewed in this same pass. Reviewer scientific roots, matvecs, RHS and IVP executed so far:0.

Reporting note: saved `Khat` is the retained approximate point response contained in the KS interval. It need not be the literal arithmetic midpoint of the two interval endpoints; use 'saved point response' in final prose.


## Result and figure review — continuation after recorded executor handover

The earlier reviewer runtime was no longer listed after compaction. This postexecution review continues the persisted review sequence under `/root/geo_review`, with `EXECUTOR_HANDOVER_20261026.json` recording the preserved prior review and exact C5 manifest. It does not claim that the same runtime remained alive. No completed intake or donor scientific calculation was repeated. The reviewer made no production code edits.

Read actual source admission, all analytic/finite summaries, action counts, Decimal roots/check records, exact interval serialization, source snapshots and resource receipts. Direct raw readback found four complete finite files, each313x14 roots, all entries finite and no negative sampled total occupations. All original source/input bytes still match C5. The ordinary-root count is17528; the Decimal oracle has96 unique signed-step roots,48 first/second check pairs (96 scalar derivative assertions), all passing. Ten guards refused, and all35 exact degree<=4 monomial records passed. The maximum root residual5.68221161163024e-14 lies below the frozen5.684341886080802e-14 threshold. This is a passed represented computation, with no tolerance widening or numerical repair.

The v1 analytic first-monopole, quadrupole and second-monopole normalized residuals are2.2115511800211435e-17,1.6575435680669e-16 and1.5945243101680063e-16. Both shears pass; source-direction tangent dot products are exactly zero in the saved evaluation. The first quadrupole susceptibility B is negative for all313 stored coordinates, ranging from-1.23749966262639e-9 to-3.430059646376636e-21. The v1 second mean is positive across all313 coordinates, from1.3712299186086578e-21 to6.150756194831173e-10. These signs describe this controlled fixed-history propagation chart.

The primary Decimal80 oracle's maximum normalized errors are1.5505132806082325e-10 (first) and1.400080738875983e-10 (second), below2e-7. Under explicit root approval, the reviewer separately solved the original delay equation with Decimal90 Newton iteration at query37 with squared direction(4,1,4)/9 and query289 with(1,9,25)/35. Four signed steps per case give exactly8 roots, no production imports and no extra operator/RHS/IVP actions. Both-step finite derivative checks pass with maximum errors1.767175659167328e-11 and1.5648758129079072e-11. Full roots, check pairs, source identity, authorization, command, stdout/stderr and budget receipt are preserved under this review directory. No further probes are needed.

The interval serialization has314 ordered exact rational endpoint pairs with genuinely outward binary64 endpoints, and every saved point output lies within its associated interval. This verifies serialization/readback of the existing exact action; it does not repeat the matrix action. The rigorous scope is only saved K intervals acting on represented binary64 m2. New coefficient evaluation and physical-history uncertainty remain outside that enclosure.

The single-event second number response is-1.7197807608184382e-9 m^-3 s^-1 per lambda^2. Its radiation energy response is-2.8101462107517614e-27 J m^-3 s^-1 per lambda^2, and the atomic entry is its exact negative. Direct incoming subtraction and the saved event coefficient identity are preserved. These are derivatives of the named frozen scalar mean closure, not an evolved anisotropic collision or thermal solution.

Actually viewed `geometry_coefficients.png` and `verification_and_scalar_response.png` via image rendering, and checked their asset identities. Titles, signed scales, query ordering, finite-oracle threshold, units and scoped interval note are readable. The plotted finite second differences are labeled diagnostic, as required. No rendering correction is necessary. Four PNG/PDF assets are present; the PDFs were identity checked, not separately rendered.

Resource receipts: primary1.597416 child CPU seconds/1.6219346620055148 execution wall seconds; saved-data figures3.28598/3.325148428004468; independent roots0.082455/0.1152588989934884. The three subprocess totals are4.965851 CPU/5.062341989003471 wall seconds, within the frozen60/180 allocation. The readback audit separately observed0.075704751 CPU/0.075714149 wall seconds after imports; it is evidence-processing overhead, not an additional scientific run. Unmeasured model, tool, imports, image-rendering and remote IO costs remain unknown, not zero. No numerical failure or repair occurred in this unit.

**Final independent decision: PASS_SCOPED_CONTROLLED_PROPAGATION_PARTIAL.** Admit the controlled geometry-to-original313-history first quadrupole, second monopole and frozen scalar mean response. There is no unresolved material blocker within that declared partial. This review supports R7-R9/C6-C9 completion, while R10/C10 require root's actual final handoff/DAG/publication/delivery records. A code/readback pass is not a publication receipt.

Preserve parent REC-HISTORY PARTIAL; H5 physical epsilon and outgoing bound null; H6 actual target-matched physical trace/geometry/measure/source closure OPEN; H7 total endpoint/source/thermodynamic derivative OPEN. Sampled positivity and finite14ray agreement do not close all-direction positivity or angular convergence. Preserve Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED, L4_ready=false, REI_activation=false and global physical completion null. No new strong no-go claim is made.
