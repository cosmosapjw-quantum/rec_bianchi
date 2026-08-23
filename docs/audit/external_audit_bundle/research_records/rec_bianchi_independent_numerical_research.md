# Frozen research record: independent mathematical, algorithmic, and coding remedies for rec_bianchi ODE/DAE code

## Pre-registration (frozen before result evidence)

### Research question

Starting only from the current checked-out source and independent numerical-analysis/software-engineering principles, which mathematical formulations, algorithms, and coding contracts can eliminate or sharply reduce the current ODE/DAE failure surfaces, and which falsifiers distinguish a structural remedy from a cosmetic numerical workaround?

### Independence rule

- Do not use the preceding physics-remediation report, its scratch record, or its conclusions as evidence or as expected answers.
- Memory may establish repository identity, dirty-tree custody, and the distinction between a specified witness and executable implementation only.
- Derive every remedy anew from current source, executed micro-experiments, primary numerical-analysis literature, or official version-matched documentation.

### Hypotheses and falsifiers

- N1 CONTRACTED-RESIDUAL: an explicit state partition, independent variable, units, domains, ownership map, and residual/mass-matrix contract makes the mathematical problem well posed enough for solver correctness to be adjudicated. Falsifier: two valid consumers can still interpret the same state or residual row differently, or the index/rank changes without a declared event.
- N2 INVARIANT-AWARE-ADMISSION: componentwise backward error, independent invariants, finite/domain checks, and accepted-state-only transactions eliminate numerical false success. Falsifier: an equivalent unit rescaling changes acceptance, a fabricated success object commits, or a violated invariant remains accepted.
- N3 TRANSACTIONAL-ADAPTIVITY: fine-state local-error control, failure-class-specific step reduction, continuous event localization, rollback, and post-event reinitialization eliminate step/event/history contamination. Falsifier: a rejected trial changes durable state, an event below the ordinary minimum step is skipped, or split and uninterrupted runs enter different branches.
- N4 STRUCTURE-PRESERVING-KERNELS: conservative flux/incidence assembly, positivity-preserving coordinates or updates, equilibrium-fitting, and stable elementary functions remove cancellation, negativity, and tautological-ledger defects. Falsifier: a discrete null state moves, a closed invariant changes, a stable reference disagrees near a removable singularity, or clipping is needed for admissibility.
- N5 NULLSPACE-AWARE-LINEAR-ALGEBRA: nondimensional block scaling, explicit nullspaces, Schur/multilevel preconditioning, and inexact-Newton forcing make stiffness tractable without changing the limiting problem. Falsifier: iteration counts or solution error diverge under grid/stiffness refinement, or the preconditioner changes conserved modes or the asymptotic limit.
- N6 TYPED-RECOVERY-API: immutable accepted objects, closed failure taxonomies, operator/policy identities, and complete restart state prevent ambiguous success and cross-problem continuation. Falsifier: changing any mathematical operator input leaves a restart admissible, failure diagnostics are lost, or a caller can construct an accepted state without revalidation.

### Planned methods and confirmatory experiments

- M1 SOURCE-INVENTORY: mechanically inventory current solver, residual, event, history, acceptance, restart, and test surfaces from current source only; map caller-consumer relationships and source hashes.
- M2 MATHEMATICAL-AUDIT: derive state/rank/conditioning/error/consistency requirements and classify each remedy as theorem-backed, conditional, diagnostic, or invalid workaround.
- M3 ALGORITHM-AUDIT: derive concrete adaptive, event, nonlinear, linear, remap, history, and recovery algorithms with complexity and failure semantics.
- M4 CODE-ARCHITECTURE-AUDIT: design typed APIs, immutable transactions, property/metamorphic/fault-injection tests, independent oracles, and observability contracts.
- X1 CONFIRMATORY-VERSIONS: record exact checkout, dependency versions, source hashes, and dirty-tree custody before external documentation lookup.
- X2 CONFIRMATORY-CONTROLLER: execute bounded existing tests or a source-level probe that determines which step-doubling state is accepted and how non-LTE failures shrink.
- X3 CONFIRMATORY-EVENTS: demonstrate or falsify sign-change-only event incompleteness with multiple/grazing roots under the locally installed solver.
- X4 CONFIRMATORY-STABLE-PRIMITIVES: compare direct and stable formulations of the characteristic transfer phi/JVP functions against a high-precision reference across small and large optical depth.
- X5 CONFIRMATORY-SCALING-RECOVERY: inspect or execute bounded tests for component scaling, nonfinite inputs, fabricated result consumption, and restart/operator mutation.
- M5 PRIMARY-DOCS: consult at most three version-matched official documentation topics plus primary numerical-analysis papers.
- M6 SYNTHESIS: produce an exhaustive issue-family-to-remedy/falsifier/dependency map with implementation-ready pseudocode and claim boundaries.
- M7 INDEPENDENT-REVIEW: one reviewer not told the expected verdict adjudicates every material claim and searches for omissions/overclaims.

### Stopping rules

- Stop when every mechanically identified issue family has a mathematical cause, at least one concrete algorithm/coding remedy, a falsifier, and a claim boundary, or is explicitly unresolved.
- Stop after the declared confirmatory experiments are completed or deliberately reported as unavailable; do not add new confirmatory experiments after observing results.
- Exactly one independent review and at most one reconciliation pass.
- No repository edits, dependency installation, production trajectory, scientific promotion, push, merge, or state mutation.

## Evidence log

### 2026-08-23 X1 and M1 current-source inventory

- E-I1 | source=`git rev-parse/status` | fingerprint=`main@5a09f3797210284f83a1a1adb0e0092d1ac48475 tree 4002915ad851afc2ab71f94a882cc99d81748062` | observation: current source identity is fixed; the only worktree change is the pre-existing user-owned `M state/REMOTE_CHECK_LATEST.json`, which remains outside this work.
- E-I2 | source=`pyproject.toml`, `requirements.txt`, live interpreter | fingerprint=`Python>=3.11; numpy>=2.0; scipy>=1.15; live Python 3.12.3 NumPy 2.4.2 SciPy 1.17.0` | observation: requirements contain lower bounds rather than an exact lock, so official API research must be matched to live SciPy 1.17.0 while reproducibility must record the realized environment.
- E-I3 | source=`AST inventory over src/full_bianchi_hyrec/**/*.py` | fingerprint=`61 Python files; 25 numeric solve/commit call sites; 111 solver/residual/event/history/JVP definitions; 60 state/result/context/restart classes` | observation: the solver surface is distributed across background, recoil, and trajectory modules rather than one integrator, requiring caller-consumer and transaction analysis.
- E-I4 | source=`rg tests` | fingerprint=`49 relevant test files; 363 hits for numerical failure/invariant/restart terms` | observation: test volume is substantial but semantic coverage must be assessed against independent invariants; count alone proves nothing.
- E-I5 | source=`sha256sum current focal files` | fingerprint=`adaptive 4100818b; full-coupled 7424e24f; PTC 4c2ec9ea; native 1144ce0f; characteristic 86cf3d32; history 54102b4e; accepted-parent a467f721; Liouville e1ce23a8; Bose runtime 5ec3472e; split f7d4ad58; background e82bb47e` | observation: later claims can be traced to exact current bytes without relying on earlier reports.
- E-I6 | source=`AcceptedRadiationHistory.accept/sha256/to_bytes` plus `data/pr05b2_source_history_v060.npz` | fingerprint=`7489 slices; 625 float64 history values/slice; 37.445 MB raw tracked history` | observation: immutable `column_stack` append copies the whole prefix and content hashing serializes it again. If 7489 slices are built through this path, array copying alone is at least 140.23 GB cumulatively, before repeated hashes/checkpoints; the accepted-history implementation is quadratic in trajectory length.
- E-I7 | source=`CharacteristicHistoryGrid.locate` one-accepted-slice probe | observation: with `accepted_count=1`, queries before the start, exactly at the sole accepted endpoint, and one full eta unit into the future all returned `thermal_zero=True`. The `count<=1` shortcut precedes the future-endpoint guard and can relabel a future-history read as a thermal boundary value.
- E-I8 | source=`CharacteristicInterpolationStencil.jvp` direction-scaling probe | observation: the same fixed-stencil JVP accepted `delta_eta` directions `1e-5` and `1e-4` but raised `CharacteristicStencilSwitch` after scaling the direction to `1e-3`. A JVP must be homogeneous in its direction away from an active-set boundary; testing whether the unscaled direction at epsilon one crosses a stencil is not a valid differentiability test.

### 2026-08-23 X2 adaptive-controller counterexamples

- E-X2.1 | source=`advance_canonical_macro_interval` executed with a deterministic nonlinear toy step | observation: for one accepted macrostep, the controller returned `[1.0010001, 2.0010000999999997]`, exactly the one-full-step state, while the two-half-step state was `[1.0010000499999998, 2.00100005]`. The local estimator's finer state is discarded.
- E-X2.2 | source=`advance_canonical_macro_interval` executed with `converged=False` and zero LTE | observation: three attempts proposed the identical full width `8e-4` (each accompanied by two `4e-4` half trials) and terminated only at `maximum_attempts`; a nonlinear/domain rejection with zero state difference does not force shrinkage.
- E-X2.3 | source=`AdaptiveBackwardEulerTrial` direct construction plus `source_conditioned_backward_euler_trial` failure branch | observation: the failure branch supplies `+inf,+inf,-inf`, while the result constructor rejects it immediately with `ValueError: backward_error must be finite`; the advertised recoverable failure value is unrepresentable.
- E-X2.4 | source=`advance_canonical_macro_interval` with an event one twentieth of a canonical interval ahead and `minimum_step=interval/10` | observation: event clipping was overwritten by the ordinary minimum step, the trial advanced past the event, and the next loop raised `adaptive event ordering regressed behind the current state`. An exactly known event inside `h_min` is not landable.
- E-X2.5 | source=`advance_canonical_macro_interval` with one rejected negative-population trial followed by accepted positive trials | observation: the state advance succeeded, but the final ledger constructor raised `accepted macro trajectory must remain strictly positive` because the accepted-state minimum had been accumulated over rejected attempts.
- E-X2.6 | source=`advance_canonical_macro_interval` with an endpoint-independent candidate factory | observation: arbitrary history slices filled with `42,43,44` committed with `commit_count=1`; the candidate factory receives only the parent history, so the history payload is not cryptographically or semantically bound to the accepted fine endpoint/operator.

### 2026-08-23 X3 event-completeness counterexamples

- E-X3.1 | source=`SciPy 1.17.0 solve_ivp`, DOP853, a single accepted step `[0,1]` | observation: the continuous event `(t-.25)(t-.75)` has two simple roots inside the step, but identical positive endpoint signs produced `success=True` and zero detected roots.
- E-X3.2 | source=`SciPy 1.17.0 solve_ivp`, DOP853, a single accepted step `[0,1]` | observation: the grazing event `(t-.5)^2` has an even-multiplicity root, but positive endpoint signs produced `success=True` and zero detected roots. Solver success is therefore not event completeness.
- E-X3.3 | source=`background.branch_events.piecewise_linear_roots` arithmetic probe | observation: the fixed dimensionful default `tol=1e-14` reported both endpoints as roots for the nowhere-zero constant series `1e-16`; with `tol=0`, a true sign change `(+1e-200,-1e-200)` was missed because the product underflowed to signed zero. Value-zero tolerance, time deduplication tolerance, and sign comparison must be separate and scale-aware.

### 2026-08-23 X4 stable-primitive counterexample

- E-X4.1 | source=`constant_coefficient_transfer_jvp` versus mpmath 1.3.0 at 100 decimal digits, `f0=.7,j=1.3,t=2,dchi=1` | observation: the exact derivative tends smoothly to `-4`; relative error grows from `3.45e-6` at `chi=1e-6` to `1.06e-1` at `1e-8`, `5.38e2` at `1e-10`, and `6.5e19` at `1e-20`. The direct `1-exp(-chi*t)` and subtractive numerator are catastrophically unstable although the primal transfer uses `expm1`.
- E-X4.2 | source=`BianchiCharacteristicFaceSolver.trace_to_frequency_face` zero-distance probe | observation: equal initial/target frequency returned `f_face=-7` while negative emissivity, negative opacity, and `time_safety_factor=NaN` were all bypassed. The early return occurs before coefficient/domain validation, and the result record validates only direction vectors.

### 2026-08-23 X5 scaling, nullspace, transaction, and restart counterexamples

- E-X5.1 | source=`AcceptedContinuationState` executed mutation probe | observation: mutating `parent.metadata['tag']` changed the SHA-256 of a frozen accepted parent from `f5e5...ade17` to `f93b...e2fc0`; its content identity is not immutable.
- E-X5.2 | source=`PseudoTransientResult` plus `ContinuationTransaction.commit` executed fabrication probe | observation: an externally constructed result with `converged=True`, residual `0`, and arbitrary state `[999]` committed and incremented the history count. Commit does not independently re-evaluate the residual, invariants, or operator identity.
- E-X5.3 | source=`solve_pseudotransient` with one signed variable and no positive entries | observation: a converged result recorded `minimum_positive_value=inf`; `restart_bytes()` then failed with `ValueError: Out of range float values are not JSON compliant: inf`.
- E-X5.4 | source=`_relative_state_scale/_physical_backward_error` executed mixed-scale probe | observation: state `[1,1e-18]` assigned the small component scale `1.49e-8`; its residual `1e-20` was reported as `6.71e-13`, versus `1e-2` when the same component was evaluated alone. Acceptance is coupled to an unrelated large component.
- E-X5.5 | source=`project_left_nullspace` executed scaling probe | observation: the same one-dimensional nullspace basis `[1,0]` worked at scales `1` and `1e-12` but was rejected as numerically zero at `1e-20`; the absolute QR-rank threshold is not invariant to basis normalization.
- E-X5.6 | source=`CoupledCollisionTransportProblem.implicit_step` executed invalid-policy probe | observation: `nonlinear_rtol=inf` accepted an initial state with net residual `0.5000001294`, number residual `0.5`, and energy residual `0.5` as `converged=True`; `max_newton=-1` was also accepted and returned a nonconverged result rather than rejecting the invalid configuration. Solver-policy validation is not fail-closed.
- E-X5.7 | source=`solve_pseudotransient` positive-log line-search probe | observation: a finite residual/Jacobian producing an oversized Newton proposal overflowed in `exp` and escaped as `FloatingPointError` on the first line-search candidate; candidate-domain failures are not caught and converted into backtracking or pseudo-time reduction.
- E-X5.8 | source=`BackgroundSnapshot` scaling/finite probe | observation: at `H=1e-13 s^-1`, a shear tensor with `trace/H=1` was accepted because its tensor check uses a dimensionful floor of `1`; a `constraint_residuals={'gauss': NaN}` mapping was also accepted. Snapshot validation can certify order-unity normalized constraint violations and nonfinite diagnostics.
- E-X5.9 | source=`audit_native_m_matrix` and `EntropyGraphPreconditioner.from_scalar_graph` scale probes | observation: a matrix whose positive off-diagonal was 50% of its maximum entry was classified as an M-matrix, and a 100% asymmetric tiny graph was accepted then symmetrized, because both checks use an absolute floor of `1`. Unit-scale floors can turn structural sign/reciprocity violations into false passes.

### 2026-08-23 bounded baseline tests

- E-T1 | source=`pytest -q -p no:cacheprovider` on adaptive macro, pseudo-transient, physical pseudo-transient gate, characteristic angular, and full-coupled transport tests | observation: all 40 tests passed in 4.49 s. These tests establish baseline behavior but do not falsify E-X2--E-X5; the executed counterexamples occupy untested semantic seams.

### 2026-08-23 M5 version-matched official documentation and primary numerical literature

- E-W1 | official topic 1=`SciPy 1.17.0 solve_ivp` | URL=`https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html` | observation: event detection searches for sign changes over each accepted step and explicitly warns that multiple zero crossings within one step may be missed; `success` means endpoint or terminal-event termination, not event completeness.
- E-W2 | official topic 2=`SciPy 1.17.0 gmres` | URL=`https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.sparse.linalg.gmres.html` | observation: convergence is checked using the true unpreconditioned residual; with `callback_type='pr_norm'`, callbacks count inner iterations while `maxiter` counts restart cycles. Current ledgers therefore need to distinguish inner iterations, cycles, and independently recomputed scaled residual.
- E-W3 | official topic 3=`SUNDIALS IDA mathematical considerations` | URL=`https://sundials.readthedocs.io/en/latest/ida/Mathematics_link.html` | observation: semi-explicit index-one DAE integration requires a declared differential/algebraic partition and consistent `(y0,ydot0)` satisfying `F=0`; constraints are checked after nonlinear solution and cause step reduction; effective Krylov integration generally requires problem-dependent preconditioning of `dF/dy + alpha dF/dydot`.
- E-P1 | primary paper=`Brown, Hindmarsh, Petzold 1998` | DOI=`10.1137/S1064827595289996` | observation: provides a consistent-initial-condition algorithm for a class including semi-explicit index-one DAEs, directly matching the local differential/algebraic partition required here.
- E-P2 | primary paper=`Coffey, Kelley, Keyes 2003` | DOI=`10.1137/S106482750241044X` | observation: pseudo-transient continuation for DAEs has assumptions tied to the actual DAE/mass structure; an arbitrary nonnegative mass diagonal plus least-squares fallback is not automatically covered by that theory.
- E-P3 | primary paper=`Eisenstat, Walker 1996` | DOI=`10.1137/0917003` | observation: inexact-Newton forcing links the inner linear residual to the current nonlinear residual and gives a principled replacement for one fixed GMRES tolerance at every Newton iterate.
- E-P4 | primary paper=`Gustafsson, Lundh, Soderlind 1988` | DOI=`10.1007/BF01934091` | observation: PI step-size control offers a feedback-controller basis for smoother, less oscillatory LTE adaptation than a memoryless factor.
- E-P5 | primary paper=`Shampine, Thompson 2000` | DOI=`10.1016/S0898-1221(00)00045-6` | observation: locating an event and restarting at the event preserves the qualitative integration error under stated regularity assumptions; it does not prove discovery of arbitrary even/multiple roots without a bracket/completeness mechanism.
- E-P6 | primary paper=`Chang, Cooper 1970` | DOI=`10.1016/0021-9991(70)90001-X` | observation: equilibrium-fitted flux discretization can preserve nonnegativity, particle conservation, and the analytic equilibrium for Fokker--Planck-type operators, making it a structural alternative to clipping.
- E-P7 | primary paper=`Higham, Higham 1992` | DOI=`10.1016/0024-3795(92)90046-D` | observation: componentwise backward-error analysis is invariant under diagonal row/column scaling, the property violated by the current global-scale counterexample.
- E-P8 | primary paper=`Knoll, Keyes 2004` | DOI=`10.1016/j.jcp.2003.08.010` | observation: Jacobian-free Newton--Krylov is a nonlinear-solver framework whose scalability depends on physics-based preconditioning; replacing the present dense/diagonal solve by JFNK alone would not remove the conditioning or nullspace blocker.

### 2026-08-23 additional current-source structural findings

- E-I9 | source=`nonlinear_bose_release.apply_nonlinear_bose_operator` and both full-coupled/single-COM admission ledgers | observation: the operator assigns `Q_atom = -Q_gamma` by construction and the admission code then evaluates `norm(Q_gamma + Q_atom)`. That quantity is algebraically zero before any independent atomic-energy/momentum update is checked, so the advertised four-force residual is tautological, not an independent conservation oracle. A valid gate must compute the radiation and matter exchanges through separately assembled update paths and compare them only at admission.
- E-I10 | source=`adaptive_macro.advance_canonical_macro_interval` stepper/candidate interfaces | observation: the stepper receives `(state, h)` rather than `(t, state, h, problem)` and every accepted interval commits the full-step state while the candidate factory sees only the parent history. Therefore the interface cannot faithfully express nonautonomous full-versus-half operator times, nor prove that a durable history slice represents the accepted fine endpoint.
- E-I11 | source=`time_dependent_native`, `dynamic_macro_ownership`, `primitive_trajectory`, and full-coupled identifiability audit | observation: the executable source itself leaves split-domain replacement/Schur ownership unresolved, treats only a source-conditioned subblock as native dynamics, leaves the interface operator unimplemented in the primitive trajectory, and explicitly rejects scalar-history reconstruction when angular degrees of freedom are not identifiable. These are retained formulation/input-information blockers; solver tuning cannot manufacture missing equations, traces, or rank.
- E-I12 | source=`background/evolution_provider.py`, `background/sequence.py`, `background/snapshot.py` plus bounded constructor/provider probes | observation: the background sequence accepted nonfinite `tau` and decreasing cosmic time, the Bianchi-II provider integrated an initial state with strongly negative `Omega`, constraint magnitudes are stored rather than admission-gated, and an `H` override rescales absolute time rather than elapsed time about an anchor. These violate the independent-variable and physical-domain contract before ODE accuracy is considered.
- E-I13 | source=`time_dependent_native.py` and `primitive_trajectory.py` | observation: the local native block is a rank-one semi-explicit DAE (one differential and 313 algebraic variables) only if the algebraic matrix remains full rank. Direct solves record neither scaled rank nor condition/backward error; source derivatives of the algebraic variables are zero despite time-dependent coefficients, and abundance validation omits upper/normalization bounds. Consistent initialization and coefficient-derivative equations are therefore not production-certified.
- E-I14 | source=`causal_history_step.py`, `original_hyrec_physical_flux.py`, `time_dependent_native.py`, and `pseudotransient_continuation.py` | observation: Thomas elimination, a subtractive Schur reduction, explicit small-block solves, and dense direct solves have no pivot/rank/condition/componentwise-residual admission; a singular PTC system silently changes problem semantics to unconstrained `lstsq`. Finite output is not a linear-solve certificate.
- E-I15 | source=`direct_thermodynamic.interpolate_scalar_graph` plus finite-difference probe | observation: the reported derivative is a fixed-density partial derivative, but the default returned value internally interpolates `n_H(T)` and omits `dn_H/dT`; the observed default-path relative derivative discrepancy was about `6.44e-2`, versus `4.27e-10` with density fixed. The midpoint geometric mean can also underflow as `sqrt(a*b)` even when the result is representable.
- E-I16 | source=`causal_history_step._conservation_ledger` and `split_domain_exchange.py` | observation: the history energy ledger defines `redshift_work = energy_target-energy_source` and then verifies the same identity; the split-domain required-process list is generated from the implemented list, fixed FLRW side determines direction, and the bounded `apply` leaves both state arrays unchanged while recording paired ledger applications. These are self-consistency/audit witnesses, not independent conservation or implemented coupling.
- E-I17 | source=`implicit_scalar_bose_step`, `implicit_bose_step`, `solve_coupled_interface`, `full_coupled_adaptive.implicit_step`, and `single_com_macro` | observation: multiple duplicated Newton loops use inconsistent validation, scaling, globalization, invariant admission, and failure behavior. The scalar solver clips log coordinates while differentiating as if unclipped; other paths use global state scales, diagonal preconditioners, fixed GMRES tolerances, or return nonconverged states. Energy/free-energy/entropy diagnostics are often evaluated only after root acceptance.
- E-I18 | source=`background.sequence.boundary_speed_roots`, `characteristic_angular.py`, and `hyrec_spike_transfer.py` | observation: background events are inferred only from stored knots and a piecewise-linear surrogate; the fixed RK4 characteristic detects a stage speed reversal by throwing rather than localizing it, and its bisection refines only the numerical trajectory. Spike transfer explicitly delegates speed-zero localization to an external trajectory owner that does not exist in the current integrated path.
- E-I19 | source=`history_ownership.AcceptedStepTransaction`, `adaptive_macro.TrajectoryRestartState`, `primitive_trajectory`/`coupled_interface` restart payloads, and PTC serializers | observation: history commit validates shape/finiteness but not the candidate residual/invariants; restarts omit some combination of `(y,ydot)`, controller memory, pending brackets, operator/policy/code/dependency identities, flux IDs, and consistent-reinitialization data. The PTC object calls its one-way result serialization `restart_bytes` but has no restore implementation.
- E-I20 | source=`audit_collision_stiffness`, log-coordinate decoders, and existing stability claims | observation: equilibrium spectral radius is only a stiffness diagnostic; it does not cover nonnormality, anisotropic modes, nonlinear states, or establish asymptotic preservation. Log coordinates preserve positivity of representable iterates but underflow can decode to zero and positivity alone proves neither uniqueness, conservation, nor correct stiff-limit dynamics.
- E-I21 | source=`scripts/run_pr04c3_common_ledger_stage.py` and `scripts/run_pr04c1b_c2_coupled_interface_stage.py` | observation: the coupled-interface stage durably writes CSV/restart/NPZ and `DATA_OUT` before its hard aggregate gate, whereas the common-ledger stage materializes intermediate objects early but writes its files only after the aggregate gate. The former is a durable admission-order defect; the latter is an API exposure risk. Both should expose durable payloads only through an admitted object, but they must not be described as the same write behavior.

## M6 synthesis: exhaustive issue-surface-to-remedy map

The following are issue surfaces, not a claim that all rows are statistically independent bugs. Every mechanically inventoried solver/residual/event/history/restart/caller family maps to at least one row. `BLOCKER` means missing mathematics or input information; `DEFECT` means a current counterexample or contract contradiction; `CEILING` means a diagnostic has been interpreted more strongly than it warrants.

### A. Retained formulation and information blockers

| ID | Adjudication and current cause | Structural remedy | Decisive falsifier / claim boundary |
|---|---|---|---|
| R01 | BLOCKER: background, native DAE, and COM collision/transport are separate systems, not one integrated residual. | Define one disjoint `F(t,Y,Ydot; problem, accepted_history)=0` with one owner per row/flux and one JVP/ledger/restart contract. | A non-witness full configuration passes ownership and residual/JVP parity; until then no full-trajectory claim. |
| R02 | BLOCKER: split-domain Schur/replacement is absent; current exchange `apply` is audit-only and leaves states unchanged. | Implement equal-and-opposite interface flux in residual and JVP, with exact-once packet IDs and an atomic/native Schur block. | Interface-on state actually changes, independent number/energy ledgers close, and duplicate/missing packets fail. |
| R03 | BLOCKER: one scalar native history channel cannot identify an angular COM trace. | Supply angular-resolved boundary data or a proved closure with an error bound; otherwise fail closed. | Two angular fields with equal scalar history but different required trace must not map to the same production state. |
| R04 | BLOCKER: a zero-width native spike has no identified finite time measure/mass. | Keep it algebraic or derive a finite-measure closure from independently authorized data; never assign an arbitrary mass. | Grid-width-to-zero convergence gives the declared algebraic limit uniformly. |
| R05 | BLOCKER: temperature/density-continuous operator data and some derivative paths are not identified between compiled nodes. | Compile/interpolate a thermodynamically consistent network with all total derivatives and provenance. | Value/JVP finite-difference parity and detailed-balance null tests pass throughout every interpolation cell. |
| R06 | BLOCKER: background integration is implemented only for the current supported chart/family; unsupported families fail closed. | Add a family-specific state, constraints, chart transitions, and event functions before enabling it. | Cross-chart invariant tensors and constraint propagation agree; labels alone cannot enable a branch. |

### B. Mathematical contracts, scaling, and admission

| ID | Adjudication and current cause | Structural remedy | Decisive falsifier / claim boundary |
|---|---|---|---|
| R07 | DEFECT: there is no single declaration of independent variable, units, domains, differential/algebraic roles, angular tetrad/frame, history/operator generation, and operator identity. | Introduce an immutable `ProblemSpec` plus typed variable/residual-block/frame registry; every solver consumer derives the same row map from it. | Permuting/rescaling components preserves the physical result, while deleting or mutating any required field causes every consumer to reject rather than infer a default. |
| R08 | DEFECT: background `tau`, cosmic time, `dt/dtau=1/H`, and time-origin semantics are incompletely validated. | Require finite monotone coordinates, quadrature consistency, and anchored elapsed-time rescaling; reject ambiguous overrides. | NaN `tau`, decreasing time, and a nonzero-origin scaling probe all fail closed. |
| R09 | DEFECT: negative `Omega`, abundance upper bounds/normalization, and stored constraint magnitudes are not complete admission gates. | Parameterize or explicitly gate the admissible set; add dense boundary events and normalized constraint residuals. | Deliberately negative `Omega`, `x>1`, and violated charge/abundance constraints cannot produce an accepted state. |
| R10 | DEFECT: dimensionful floors of `1` make cosmological tensor, M-matrix, and graph reciprocity checks unit dependent; nonfinite residual metadata can pass. | Use per-quantity physical absolute tolerances plus relative/gross scales and mandatory finiteness. | SI/cgs rescaling gives identical pass/fail; NaN diagnostics fail. |
| R11 | CONDITIONAL BLOCKER: native DAE is index one only while the equilibrated algebraic Jacobian is full rank, yet rank/consistent initialization are not certified. | Row/column equilibrate, RRQR/SVD rank-test, solve consistent `(Y0,Ydot0)`, and record componentwise residual/condition evidence. | Near-rank-loss and inconsistent initial-state fixtures return typed failure, not a finite solution. |
| R12 | CONDITIONAL FORMULATION GAP: the current module explicitly defines a frozen-background DAE whose algebraic residual does not consume `Ydot[1:]`; zero algebraic derivative is therefore not a defect inside that narrow scope. A future nonfrozen trajectory would require `A udot=b_dot-A_dot u`. | Before promotion to time-varying coefficients, differentiate/re-evaluate coefficients or use an implicit DAE residual whose consistent initializer computes and restarts `Ydot`. | A manufactured nonautonomous algebraic solution has the expected derivative and split-restart parity; this falsifier applies only to the promoted nonfrozen formulation. |
| R13 | DEFECT: global max/norm scaling masks weak rows and acceptance changes when an unrelated component is added. | Use row-wise term/gross scales and componentwise backward error; retain block WRMS and max norms. | Mixed-scale and diagonal unit-rescaling metamorphic tests preserve every row's decision. |
| R14 | DEFECT RISK/CEILING: source control flow permits gross-cancellation plus number fallback without requiring the net residual, and the physical adapter calls a global metric componentwise. The executed `rtol=Inf` case belongs to invalid-policy R31, not a finite-policy cancellation proof. | Distinguish roundoff-limited evaluability from root convergence; require componentwise residual plus condition/extended-precision evidence. | With valid finite policy, a well-scaled known nonroot or multiprecision oracle must not pass solely through the fallback; until such a case is executed this remains a source-backed risk, not a demonstrated finite-policy false success. |
| R15 | DEFECT/CEILING: one raw tolerance is compared with relative and dimensionful four-force/entropy quantities; fixed multiples of epsilon are only diagnostics. | Nondimensionalize each invariant with gross+absolute scales and use operation-count/error-bound or mixed-precision oracles. | Unit changes and summation order do not change admission; higher precision agrees. |
| R16 | DEFECT: `Q_atom=-Q_gamma` followed by `norm(Q_gamma+Q_atom)` is a tautological four-force gate. | Assemble radiation and atomic exchange independently and compare only at the acceptance boundary. | Corrupt either update path alone and require the independent ledger to fail. |
| R17 | DEFECT: history energy ledger defines redshift work as the residual it then checks. | Compute work from an independent geometric/transport discretization or a discrete Noether/flux identity. | Perturb the transport update while leaving ledger code untouched; the gate must fail. |
| R18 | DEFECT: structural M-matrix/reciprocity audits use scale floors that accept order-one relative violations. | Test signs/symmetry with scale-homogeneous thresholds, graph connectivity, and interval/high-precision confirmation near zero. | Matrix scaling by any positive scalar preserves the audit; disconnected graphs expose all null modes. |
| R19 | CEILING: spectral-radius stiffness checks, BE L-stability, positivity, and a green root do not establish asymptotic preservation or global accuracy. | Run fixed-macro-step stiffness-limit tests against the reduced equilibrium model plus `h,h/2,h/4` endpoint/invariant convergence. | Error remains uniform as rates scale as `1/epsilon`; otherwise no AP/production claim. |

For state-form backward-Euler rows `G_i=Y_i^{n+1}-Y_i^n-h sum_k R_i^(k)`, a termwise scale is dimensionally valid:

\[
s_i=a_{G,i}+r_i\max(|Y_i^n|,|Y_i^{n+1}|)+h\sum_k|R_i^{(k)}|,
\qquad
\eta_G=\max_i\frac{|G_i|}{s_i}.
\]

For algebraic, flux, and mixed-unit rows, the state-form expression must not be reused: define a row-unit decomposition from the actual equation terms, or use `a_F,i + sum_j |J_eff,ij| s_Y,j` below.

For a general DAE Newton iterate with effective Jacobian
`J_eff=F_Y+alpha F_Ydot`, retain the componentwise perturbation test

\[
\eta_{c}=\max_i\frac{|F_i|}
{a_{F,i}+\sum_j |(J_{\rm eff})_{ij}|s_{Y,j}},
\]

and evaluate algebraic constraints, positivity/bounds, number, energy, independently assembled four-force, entropy sign, and ownership completeness as separate gates. No one scalar may substitute for the others.

### C. Adaptivity, dense events, and rollback

| ID | Adjudication and current cause | Structural remedy | Decisive falsifier / claim boundary |
|---|---|---|---|
| R20 | DEFECT: stepper `(state,h)` cannot represent nonautonomous full/half evaluation times. | Require `(t,state,h,problem,accepted_history_view)` and evaluate every stage at its own time. | Manufactured `y'=t` attains the expected convergence order. |
| R21 | DEFECT: BE step doubling estimates the fine-state error but commits the lower-accuracy full state. | For order `p`, use `(y_hh-y_h)/(2^p-1)` and accept `y_hh`; if committing coarse state, scale its estimate by `2^p`. | Full/half/h/4 convergence rates and returned-state identity agree. |
| R22 | DEFECT: recoverable failure is encoded using infinities rejected by the trial type; other result types require success at construction. | Use a closed `TrialOutcome` sum type with success payload only on `ACCEPTABLE`; preserve finite diagnostics separately. | Every failure class can be constructed, serialized, and consumed without fake states/sentinels. |
| R23 | DEFECT: nonlinear/domain failure with zero LTE need not shrink, and later half trials may run after a prerequisite failure. | Short-circuit dependent trials and apply failure-class-specific contraction independent of LTE. | Zero-LTE nonlinear failure strictly reduces `h` and performs no invalid dependent trial. |
| R24 | DEFECT: rejected-trial minima/errors contaminate an accepted-only ledger. | Keep attempt diagnostics separate; aggregate production extrema only from committed states. | A rejected negative trial followed by a valid retry commits with an accurate accepted minimum. |
| R25 | DEFECT: ordinary `h_min` overwrites a nearer event displacement. | Separate ordinary minimum step from event landing; an event step may be smaller or returns `EVENT_UNRESOLVED`. | An event at `h_min/20` is landed exactly once without overshoot. |
| R26 | DEFECT: endpoint sign sampling misses multiple/grazing roots; product sign underflows; one tolerance mixes event units/time; plateaus have no semantics. | Use explicit sign-bit comparisons and separate `g_atol/t_atol`; certify each accepted segment by enumerating every root of a certified polynomial event representation or by an interval/derivative root-count bound. Otherwise return `EVENT_UNCERTIFIED`; represent plateaus explicitly. | An independent root-count oracle adjudicates double, tangent, plateau, near-coincident, endpoint, and NaN cases. Mere step refinement is insufficient because it can miss the same roots consistently. |
| R27 | DEFECT: background roots use stored output knots; DOP853 has no registered continuous event contract or root certification. | Retain accepted mesh/dense state and use the R26 root-count/interval certificate over every segment; ordinary callbacks alone are not completeness authority. | Output-sampling changes do not affect the certified root set, and that set agrees with an independent analytic/interval root-count oracle; uncertified segments fail closed. |
| R28 | DEFECT: fixed RK4 characteristic throws on speed reversal and its 64 bisections refine only the discrete trajectory; zero-distance early return bypasses coefficient validation; the result type validates directions but not all scalar diagnostics. | Validate every input and result scalar first; use adaptive dense integration and a continuous speed event, then restart at the localized root under the R26 certificate boundary. | Event-time error converges with trajectory order, every result scalar is finite/domain-valid, and invalid zero-distance inputs fail. |
| R29 | DEFECT: adaptive event handling increments counters but has no branch transition, Jacobian/history invalidation, or DAE consistent reinitialization. | At the earliest root, roll back, land, call one-sided transition atomically, increment generation, reset method/order/preconditioner, and solve consistent IC. | Split and uninterrupted runs have identical branch/event callback counts and accepted hashes. |
| R30 | DEFECT: history candidate sees only the parent and is not bound to accepted endpoint/time/operator. | Construct it from `(t_new,Y_new,operator_id,parent_hash,event_generation)` inside the commit transaction. | Arbitrary `42/43/44` history data and stale generations are rejected. |

Existing BE repair pseudocode:

```text
full  = step(t,       y,       h,   P, Haccepted)
if full.failed: return retry(full.reason, shrink_for(full.reason))
half1 = step(t,       y,       h/2, P, Haccepted)
if half1.failed: return retry(half1.reason, shrink_for(half1.reason))
half2 = step(t + h/2, half1.y, h/2, P, Haccepted)
if half2.failed: return retry(half2.reason, shrink_for(half2.reason))
e = (half2.y - full.y)/(2**p - 1)
if scaled_norm(e) > 1: return RETRY_LTE
candidate = assess_all_gates(t+h, half2.y)
if not candidate.admissible: return candidate.typed_retry_or_fatal
atomic_commit(half2.y, history_from(candidate), controller_PI_state)
```

LTE-controlled accepted steps may use a PI controller such as

\[
h_{n+1}=h_n\,\operatorname{clip}
\left(s e_n^{-0.7/(p+1)}e_{n-1}^{0.4/(p+1)},f_{\min},f_{\max}\right),
\]

but nonlinear, linear, domain, invariant, and event failures need separate policies. Event completeness remains unprovable without a derivative/interval/root-count bound; unresolved segments must be labeled `EVENT_UNCERTIFIED`, not silently treated as root-free.

### D. Nonlinear, linear, nullspace, and stable-kernel algorithms

| ID | Adjudication and current cause | Structural remedy | Decisive falsifier / claim boundary |
|---|---|---|---|
| R31 | DEFECT: NaN/Inf tolerances and negative/noninteger iteration settings are inconsistently accepted. | One immutable `SolverPolicy` validates every finite positive tolerance, integer limit, restart size, and ordering before evaluation. | NaN, Inf, negative, bool-as-int, and oversized settings fail at construction. |
| R32 | DEFECT: raw `exp` can overflow/underflow; scalar log clipping makes the residual nonsmooth while its Jacobian assumes no clip. | Use domain-aware transforms with representable bounds, no hidden clipping, and catch trial-domain failures as `+infinity` merit/backtracking. | Near-boundary JVP finite-difference parity and graceful backtracking pass. |
| R33 | DEFECT: several line searches require only raw strict decrease and use a merit different from admission; PTC domain exceptions escape. | Use the same scaled merit for Newton and acceptance, Armijo/filter/trust-region globalization, and a typed domain-rejection path. | Nonnormal/oversized-step problems recover or return a specific reason without state mutation. |
| R34 | PERFORMANCE/OBSERVABILITY CEILING: one fixed GMRES tolerance may oversolve early Newton steps, but SciPy checks the true unpreconditioned residual and the current callback/field explicitly count inner iterations. The missing item is a solver-independent scaled residual/cycle ledger, not proof of wrong GMRES termination. | Use Eisenstat-Walker forcing for efficiency, explicitly record restart cycles plus inner iterations, and recompute the problem-scaled true residual. Use FGMRES only if the preconditioner varies within a Krylov solve. | Scaled true residual and counters agree with a direct oracle across restart cycles; adaptive forcing reduces work without changing admitted states. |
| R35 | CONDITIONAL PERFORMANCE BLOCKER: diagonal/dense graph preconditioning ignores collision components, transport, native algebraic coupling, and conserved coarse modes, but refinement divergence has not been executed. | Treat a physics-block Schur design (transport sweeps, sparse collision solve, small atomic/interface Schur, nullspace correction) as a candidate requiring spectral and refinement validation, not an implementation-ready guarantee. | Iterations remain bounded under grid/stiffness refinement and every conserved mode is unchanged; failure retains the performance blocker. |
| R36 | DEFECT/CEILING: Thomas and Cramer/2x2 paths are unpivoted; NumPy dense LU is internally pivoted but has no explicit condition/componentwise-residual/admission certificate. | Add pivot/near-pivot checks to structured paths, equilibrated pivoted LU/QR or RRQR/SVD near rank loss, extended-residual refinement, and typed singularity. | Near-zero pivot and `[[1,1],[1,1+delta]]` fixtures never yield an uncertified finite answer. |
| R37 | DEFECT: silent `lstsq` changes semantics; nullspace rank uses an absolute basis threshold; RHS compatibility is not checked. | Normalize bases, weighted pivoted QR/SVD with relative singular threshold, check `Z^T b`, and use an augmented/gauged solve or explicit incompatible status. | Null-basis scaling/rotation is invariant; incompatible singular RHS is not projected away. |
| R38 | CONDITIONAL/AUDIT BLOCKER: current PTC is audit infrastructure not yet bound to the production physical residual; it accepts an arbitrary nonnegative mass and least-squares fallback without DAE hypotheses. Mass can legitimately change basin/root selection in a multiple-root problem. | Bind it to a declared DAE mass (zero on algebraic rows), use SER pseudo-time, record rank/compatibility, and require the final unshifted residual/invariants before commit. | Every endpoint satisfies the same unshifted residual and invariants; identical-root selection is required only when uniqueness/basin hypotheses prove it. Incompatible DAEs fail explicitly. |
| R39 | DEFECT: transfer JVP catastrophically cancels at small optical depth. | Set `z=chi*t`, `phi=-expm1(-z)/z`, and evaluate `phi'` with a matched Horner series near zero. | Multiprecision sweep, branch continuity, and JVP homogeneity hold across zero. |
| R40 | DEFECT/API SELF-INCONSISTENCY: the fixed-density partial derivative is valid, but the default value internally uses `n_H(T)` while the co-returned derivative is still declared fixed-density; `sqrt(a*b)` can also underflow. | Make partial versus total derivative explicit in the return type; require density for the partial or include `dn_H/dT` for the total, and use log/scaled geometric means. | Default-total and fixed-density-partial finite differences plus extreme representable means agree with their declared semantics. |
| R41 | PRODUCTION BLOCKER, not a current fixed-grid defect: moving-grid remap/GCL is absent, while the implemented fixed-grid subproblem explicitly refuses that regime. Positivity+number+energy remap is feasible only if `E/N` lies in the new cell-energy convex hull. | For an enabled moving grid, remap photon content in mode-volume coordinates with overlap integration, ALE face velocity, feasibility check, positivity active set, and either support expansion/subdivision or typed `REMAP_INFEASIBLE`. | Constant-state GCL, delta transport, round trip, and feasible number/energy/positivity cases converge; infeasible convex-hull cases fail explicitly. |
| R42 | DEFECT/BLOCKER: required ownership is self-derived, directions are hard-coded by side, and packet application is not exactly-once durable state. | Independent required-process schema; direction from current face speed; immutable flux IDs applied equal/opposite in residual, JVP, ledger, and restart. | Omitted-both-sides, speed reversal, duplicate replay, stale generation, and residual/JVP packet mismatch all fail. |

For the removable transfer singularity:

\[
\phi(z)=\frac{1-e^{-z}}{z},\qquad
\phi'(z)=\frac{(z+1)e^{-z}-1}{z^2}
=-\frac12+\frac z3-\frac{z^2}{8}+\frac{z^3}{30}-\frac{z^4}{144}+\cdots,
\]

\[
F=e^{-z}f_0+j t\phi(z),\qquad
\partial_\chi F=-t e^{-z}f_0+j t^2\phi'(z).
\]

The nonlinear target should use inexact Newton with a scaled merit and a block preconditioner approximating `F_Y + alpha F_Ydot`. For a singular collision block, discover one conservation/null mode per connected component, test compatibility before deflation, and never project an incompatible physical forcing into the range.

### E. Transactions, history, restart, callers, and verification

| ID | Adjudication and current cause | Structural remedy | Decisive falsifier / claim boundary |
|---|---|---|---|
| R43 | DEFECT: `converged: bool` and success-only result constructors cannot preserve a closed failure cause; nonconverged states are still exposed by some APIs. | Sealed outcome union: `ACCEPT`, retry classes, event restart, incompatibility, and fatal classes; only `ACCEPT` exposes durable state. | Exhaustive pattern matching and serialization cover every reason with no sentinel values. |
| R44 | DEFECT: continuation/history commit trusts a fabricated bool or merely finite arrays and does not re-evaluate the operator/invariants. | Commit receives the immutable problem and independently recomputes residual, domain, invariants, endpoint, and operator identity before one atomic state/history/flux update. | A fabricated `[999]` result and arbitrary finite local arrays cannot commit. |
| R45 | DEFECT: frozen continuation metadata is a mutable dict, so its content hash changes after construction. | Deeply normalize JSON scalars/tuples and wrap mappings with `MappingProxyType`, following the accepted-parent precedent. | Mutation is impossible and hashes remain stable under alias attempts. |
| R46 | DEFECT: no-positive PTC states record `Inf`; result bytes are one-way and omit dtype/shape/restore semantics. | Represent N/A as `None`, define a full versioned candidate receipt separately from a restart, and implement length/dtype/shape-checked decoding. | Signed-only state round trip is JSON-safe; truncation/trailing bytes fail. |
| R47 | DEFECT: restart payloads omit controller memory, `(Y,Ydot)`, pending brackets, operator/policy/code/dependency IDs, flux/history generation, and in some cases endpoint coherence; `TrajectoryRestartState` does not compare restart `eta` with the history endpoint although the live context does. | Checkpoint only accepted/event boundaries, discard in-flight attempts, and store complete method/PI memory, provenance, endpoint/history coherence, event brackets, ownership/flux IDs, runtime, schema and payload-integrity manifest. | One-shot versus resume across a rejection and event yields the same accepted hash chain; eta/history mismatch, payload corruption, or any identity mutation fails. |
| R48 | DEFECT: one-slice future history queries return thermal zero before future-range validation. | Validate future/end range before short-history boundary shortcuts. | Every query beyond the accepted endpoint fails, including count one. |
| R49 | DEFECT: history JVP active-stencil test depends on direction magnitude, violating homogeneity. | Freeze the exact primal interpolation stencil for its local derivative; model a stencil switch as an event/generalized derivative boundary. | `J(c v)=c J(v)` over safe scales and one-sided switch tests pass. |
| R50 | PERFORMANCE BLOCKER: immutable `column_stack` plus full-prefix hashing makes accepted-history construction `Theta(M N^2)`. | Fixed-size immutable chunks + hot ring + incremental hash chain/Merkle root; append `O(M)`, queries `O(Q)` or `O(log L)`. | Doubling `N` gives near-2x rather than 4x append work; tamper/rollback/chunk-boundary restart tests pass. |
| R51 | DEFECT/API RISK: the coupled-interface stage durably writes artifacts before its hard gate; the common-ledger stage only constructs intermediates early and writes after its gate. | Invert API ownership: raw attempts are opaque; only `AdmittedStep` can serialize, publish, or feed the next stage. | A rejected coupled step leaves no durable artifacts; static/type tests prevent durable-payload access from every nonadmitted outcome. |
| R52 | REPRODUCIBILITY BLOCKER: only lower dependency bounds are declared. | Record/lock Python, NumPy, SciPy, BLAS, platform, code/operator hashes, thread count, CPU/FMA, rounding mode, and determinism settings. | Call replay bitwise/exact only under the full runtime contract; otherwise require a separately named tolerance-based scientific replay. |
| R53 | MAINTENANCE/RELIABILITY RISK: duplicated loops drift in validation, scaling, failure, and ledger semantics, but different DAE/Schur structures should not be forced through one physical kernel. | Share policy validation, outcome taxonomy, scaling, admission and ledger primitives; inject and keep problem-specific nonlinear/linear kernels separate. | Cross-problem contract tests exercise the same public failure/admission semantics while problem-specific convergence/refinement tests remain valid. |
| R54 | VERIFICATION CEILING: 40 focused tests pass, but current tests omit the executed semantic counterexamples and global/refinement authority. | Add property, metamorphic, fault-injection, multiprecision, stiffness/refinement, replay, and independent conservation oracles. | All falsifier matrix rows below pass without weakening tolerances or claims. |

### F. Independent-review omissions added during the single reconciliation

| ID | Adjudication and current cause | Structural remedy | Decisive falsifier / claim boundary |
|---|---|---|---|
| R55 | HIGH DEFECT/BLOCKER: angular ordinates have no tetrad tag. Collision runtime interprets `grid.directions` in the hydrogen frame and inverse-aberrates it, while frequency transport consumes the same array as normal-frame directions; the coupled residual also omits the finite-tilt angular Liouville term `dot(n_H)^A nabla_A f`. | Add `AngularGrid(frame=HYDROGEN or NORMAL, tetrad_id, measure_id)` to `ProblemSpec`, perform the frame map in one owner, and discretize `D0 f = partial_t f + dot(x) partial_x f + dot(n_H)^A nabla_A f` conservatively with the same residual/JVP/ledger. | Frame-tag mismatch fails construction; runtime/transport face speeds agree to roundoff; constant angular fields have zero angular action; manufactured rigid-rotation harmonics converge; `beta_H=dot(n_H)=0` reduces to the existing zero-tilt path. |
| R56 | HIGH DEFECT: angular-grid, collision-network, line-config and runtime scientific objects incompletely reject NaN/Inf and some frozen records retain caller aliases or writable arrays, so operator identity and derived harmonic matrices can change after construction. | Validate all scalar/array domains before arithmetic, copy-before-freeze every owned array, deeply normalize mappings, and derive harmonic matrices only from the private copied ordinates without making caller arrays read-only. | Field-wise NaN/Inf construction fails; mutation of every preconstruction alias cannot change object bytes/hash/action; internal arrays are nonwriteable while caller arrays retain their original mutability. |

Recommended history design for uniform `eta`: precompute each frequency-ratio lag, retain a hot ring of length `ceil(delay_max/deta)+2`, archive fixed-size immutable chunks, and update

\[
H_n=\operatorname{SHA256}(H_{n-1}\Vert n\Vert\eta_n\Vert\text{candidate bytes}).
\]

This changes total append work from `Theta(M N^2)` to `Theta(M N)` and makes rollback an accepted-head pointer operation. Near-zero delay inside the current implicit interval must become a collocation unknown or split the step; it may not read an unaccepted endpoint.

## Implementation order and kill criteria

1. **P0 fail-close and local correctness:** central policy validation; stable transfer/JVP; frame-tagged, finite, copy-before-freeze scientific inputs; validation before early return; future-history ordering; immutable metadata; typed result states; forbid pre-admission serialization. These are small and directly falsifiable.
2. **P1 mathematical SSOT:** immutable `ProblemSpec`, differential/algebraic partition, units/domains/ownership, componentwise scales, independent invariant ledger, consistent initializer, rank/condition evidence. Keep R01--R06 fail-closed.
3. **P2 transactional integrator:** time-aware fine-state BE repair first, then variable-order BDF/Radau if needed; accepted-only metrics; dense event isolation; transition callback and consistent DAE reinitialization.
4. **P3 scalable nonlinear/linear solve:** shared inexact-Newton engine, block Schur preconditioner, nullspace discovery/compatibility, true-residual and refinement ledgers. Dense reference solve remains an oracle only.
5. **P4 conservative coupled operator:** actual split-domain application, independently required ownership, exactly-once flux IDs, conservative moving-grid remap/GCL, separately assembled matter/radiation exchanges.
6. **P5 durable state:** chunked delay history, complete accepted-boundary checkpoint, exact-environment hash replay and separately named portable scientific replay.
7. **P6 validation:** manufactured DAEs, analytic/stable kernels, adversarial events, unit/null-basis metamorphics, corruption/fabrication fault injection, `h/h2/h4`, grid/stiffness/AP studies, and full one-shot-versus-restart comparisons.

Stop/fail promotion immediately if any of these persists:

- an equivalent diagonal unit scaling changes admission;
- an unresolved/grazing event is reported as absent;
- a rejected/fabricated candidate changes durable state;
- restart changes an accepted hash/event/flux sequence under the exact-runtime contract;
- algebraic rank/compatibility or true Krylov residual is unknown;
- number/energy/four-force/entropy is self-derived rather than independently assembled;
- refinement does not show the declared order or the stiff limit does not approach the reduced model;
- any R01--R06 information/formulation blocker is bypassed by a numerical default.
- a frame-less/mismatched angular ordinate or a post-construction alias mutation can alter an operator.

Invalid workarounds are: loosening tolerances, only increasing iteration counts, globally shrinking `max_step` and calling events complete, clipping/renormalizing after a solve, silent `lstsq`, projecting away incompatible conservation forcing, constructing `Q_atom=-Q_gamma` as a check, adding output knots without continuous-event bounds, installing JFNK without a physics preconditioner, or treating a contract/audit witness as an implemented trajectory.

## Required falsifier suite

- **Contracts/scaling:** SI/cgs and arbitrary diagonal row/column scaling; component permutation; mixed `1`/`1e-18` states; field-wise NaN/Inf/negative policy; abundance/constraint violations; frame-tag mismatch; caller-alias mutation.
- **DAE/linear:** inconsistent initial `(Y,Ydot)`; rank-loss and near-rank-loss; compatible/incompatible singular RHS; null-basis scale/rotation; near-zero Thomas pivot and near-singular 2x2 Schur block; extended-precision residual.
- **Adaptive/events:** nonautonomous `y'=t`; full versus fine state; zero-LTE nonlinear failure; rejected negativity recovery; event below `h_min`; two, tangent, plateau, simultaneous, endpoint, near-coincident and NaN roots; exactly one transition callback.
- **Kernels/JVP:** multiprecision optical-depth sweep; `J(c v)=cJ(v)`; thermodynamic default/fixed-density finite differences; event/stencil one-sided derivatives.
- **Structure:** equilibrium/null-state preservation; independent number/energy/four-force/entropy corruption; disconnected collision graph; conservative remap/GCL; hydrogen/normal-frame speed parity; constant/angular-harmonic Liouville oracles; speed reversal; duplicate/missing/stale flux ID.
- **Durability/performance:** fabricated result, mutable alias, signed-only PTC serialization, corrupted/truncated restart, problem/policy/code/dependency mutation, one-shot versus split across rejection+event, `N` versus `2N` history scaling.
- **Accuracy/limits:** endpoint/invariant/event convergence under `h,h/2,h/4`; grid and angular refinement; rate scaling `1/epsilon` at fixed macro step against the reduced equilibrium dynamics.

## M7 sole independent review and reconciliation

- Review input: the complete R01--R54 record and current checkout, with no expected verdict and prior physics-remediation conclusions forbidden.
- Initial verdict: `FAIL`; family-level coverage was broadly adequate, but two high-severity omissions (finite-tilt frame/angular-Liouville ownership and shallow/nonfinite scientific-input immutability) plus twelve classification/formula/falsifier corrections were required.
- Single reconciliation: R55--R56 were added; R07, R12, R14, R26--R28, R34--R36, R38, R40--R41, R47, R51--R53 and the mixed-row scale formula were narrowed/corrected exactly as adjudicated. No second review or new exploratory experiment was added.
- Reconciled verdict boundary: the reviewer explicitly judged the remaining R01--R54 family coverage adequate conditional on those exact corrections. This is review closure of the research map, not validation of an implementation.

## Claim ceiling after independent review

This record supports a current-source static audit, bounded counterexamples, version-matched API behavior, and implementation-ready numerical designs. It does not implement a remedy, prove nonlinear existence/uniqueness, certify all roots without derivative/interval hypotheses, execute a production trajectory, establish global endpoint accuracy, establish AP behavior, or authorize scientific promotion.
