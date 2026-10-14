# REC finite-clock R10 + C8 numerical research closeout

2026-10-15 KST. Selected scope: **R10** (completion/resume of previous REC theory R6–R9) and **C8** (actual numerical error, convergence and resource measurements after the C7 source-clock integration). No new automatic R1 cycle or C9 scientific review. All observations use the user's authenticated Ubuntu research PC.

## 1. Definition, preserved physics, source identities

Non-tilted, normal-comoving, prescribed LRS Bianchi I only. Signature (-,+,+,+), ds²=-c²dt² + a²exp(-2b)(dx²+dy²)+a²exp(4b)dz², proper clock t in seconds; L=ln(a/a_ref), a_ref=1/21, a_end=1/5, s=db/dt and sigma=diag(-s,-s,2s). Frozen physical-density-fixed family H²=H_F²+s², H_F²=H0²(Ωm/a³+Ωr/a⁴+ΩΛ), s=q_ref H_F(a_ref)(a_ref/a)³. SameHDiagnostic is a different explicit counterfactual: H=H_F, s signed remains. Cold original-HyRec chemistry/atomic closures, warm HE18 second cell and REI native Rust histories do not inherit validation from this controlled geometry/source test.

Recent prerequisites: REC R7B exact-node positive-Hermite interpolation theorem, REC R8 102 actual native saved-clock increments/24 over 1e-8, REC R9 v2 mixed floating error erratum, REC C5/C6 source-bound Bianchi I provider implementation (draft PR85), REC C7 real CharacteristicAngularSolver source-clock opt-in (draft PR86). Prior R9 v1 remains historic and is **not** authoritative for floating-error composition. BASS_HE HE18 C1 warm RHS/error transport and signed 5-case q² partial diagnostic are distinct supplier lanes, not transferred to the present cold clock validation.

## 2. C8 numerical defect and smallest constructive repair

A real local RED reproduced a short-interval collapse: a_ref*exp(tau) rounded many distinct successive tau values to the same binary64 a. At represented total Δtau=1e-14 with 256 parts, **211 substeps** collapsed after the exp/multiply round trip. An earlier REC C7 path source.interval(a1,a2) then failed for a1=a2, even though tau1<tau2 and true dt>0. C5 interval(a1,a2) itself remains valid for supplied *distinct a*. The problem is the conversion between clock charts, not a failure of the original frozen physical model.

Correction: add FiniteBianchiILogIncrement with distinct numerical method identity rec_lrs_bianchi_i_positive_rate_hermite_log_interval_v1, AxisymmetricBianchiIBackground.interval_log(l1,l2) using exact supplied represented L endpoints, and bind this to the opt-in CharacteristicAngularSolver._clock_step. Preserve old scale-input interval(a1,a2) and original no-opt-in legacy midpoint-H path, including old model source hash. Add solver.source_clock_method_identity so downstream users must distinguish changed method from bit-preserving cache and historical REI binary identities. Full source-binding checks across all snapshot H/shear/curvature/tilt nodes from C7 remain active.

This correction *eliminates chart-roundtrip collapse* for represented L input. It does not establish an IEEE-754 directed-rounding global error bound, and does not eliminate cases where two input tau endpoints themselves already round to the same float.

## 3. Theoretical R10 closeout: positivity and coupled-source error decomposition

For positive F=1/H and scalar source/opacity j(L)>=0, chi(L)>=0 along a prescribed null ray, occupation obeys df/dL=F(L)[j(L)-chi(L) f(L)]. For constant j,chi over a single physical time interval t>=0:

 T_t(f0) = exp(-chi t) f0 + [1-exp(-chi t)](j/chi), with continuous limit chi=0: f0+j t.

The exact derivative is dT/dt=exp(-chi t)[j-chi f0], hence if both t and t+δt are nonnegative,

 |T_{t+δt}(f0)-T_t(f0)| <= |δt| exp[-chi min(t,t+δt)] |j-chi f0|.   (R10-CLOCK-01)

At fixed chi>0 the update is a convex combination of f0>=0 and j/chi>=0, so positive-clock increments preserve f>=0 and contract deviations from equilibrium by exp(-chi dt). χ=0 uses the exact positive affine limit; this is a *scalar frozen-coefficient* statement, not a multigroup collision or coupled Einstein-HyRec theorem.

More generally let reference f solve F,j,chi and approximate g solve Fhat,jhat,chihat. The **exact algebraic error identity** for e=g-f is

 e'(L) = -F chi e + (Fhat-F)(jhat-chihat g) + F[(jhat-j)-(chihat-chi)g].  (R10-CLOCK-02)

With identical initial f=g, F,chi>=0, the integrating factor yields the a posteriori envelope

 |e(L)| <= integral_{L0}^L exp[-integral_u^L F chi dv] {
   |Fhat-F| |jhat-chihat g| +
   F [|jhat-j|+|chihat-chi| |g|] } du.                        (R10-CLOCK-03)

The mathematical statement separates background clock-rate error from microphysics coefficient/source error. It requires actual numerical bounds for Fhat-F, jhat-j, chihat-chi and a bounded approximate g; these are **not furnished by the finite C8 samples**. Satisfying measured source-clock error alone does not certify the entire reionization solution. The previously proved positive-Hermite *ideal* interval error bound epsilon_h=(30537/384) exp(3h)h⁴ remains exact-node specific; R9 v2 floating composition uses alpha+(1+alpha)*eta_eval, followed conditionally by positive-sum gamma_N. Do not silently set unknown node/evaluator/source errors to zero.

Wolfram15.0.1 directly returned five symbolic residual zeros for the frozen scalar exponential solution, delta-clock derivative, zero-opacity limit, source difference identity, and convex combination. Actual local Wolfram Engine15.0.0 + xTensor1.3.0 gave four exact zeros for baryon current, ionized-current, emission-absorption convective derivative and F/j/chi source decomposition on 4D (-+++) manifold. This is algebraic verification, not an externally independent peer review.

## 4. Actual new C8 numeric execution

New script scripts/measure_axisymmetric_c8.py freezes each binary64 model source parameter and supplied L endpoint as exact dyadics for independent mpmath70 quadrature. It evaluates 5 signed q cases times 6 source-specific intervals, including ΔL=1e-14, near-origin 1e-12, a one-ULP interval near L=.05, two finite interior intervals and a finite full range. **30/30 comparisons passed** with max |relative error| 3.907985e-14 in dt and 3.885781e-14 in signed db. Only true nonzero q cases have a meaningful relative db error. Sample maxima are finite observations, not a supremum or directed interval enclosure.

The actual REC CharacteristicAngularSolver with finite Bianchi I snapshots was compared to a separate analytical-H SciPy DOP853 scalar source IVP and exact conserved-null-momentum finite map. End a=.1, q=.01. For nsteps=64/128/256 with 513 stored snapshots, occupation relative errors are approximately 6.170145e-7,1.542679e-7,3.856785e-8, demonstrating second-order refinement. Geometry depends independently on the snapshot grid: at 65 snapshot nodes even nsteps=256 leaves photon initial energy |relative|≈1.497e-7; with 513 nodes/256 steps it falls to ≈1.261e-9. Thus source temporal convergence and redshift/angular convergence are separate measurements and must not be conflated.

Constant-coefficient opacity scan χ=(0,1e-20,1e-17,1e-12,1e-8) s^-1, emissivity chosen positive or fixed equilibrium, ranged from transparent to strongly saturated (>1e8 optical depth) and passed positivity/exact scalar transfer checks. No nonlinear recombination chemistry, radiation-gas energy/momentum exchange or detailed balance was solved.

Execution-time observation at 257 snapshots and nsteps=128, five repeats per method, on the same running Ubuntu host: first run midpoint-H median ≈0.051545 s, new log-interval ≈0.063564 s (about 23% slower). A separately executed second run, whose complete measurements are the authoritative public C8_RESULTS.json, gave midpoint-H median ≈0.047409 s and log-interval ≈0.059581 s (about 26% slower). Therefore this is **two short noisy local timing repetitions**, not an accuracy-matched whole-solver benchmark or a prediction about independent REI Rust performance. Memory cap, detailed strong-scaling, stiff implicit coupling and full native streaming histories are not proved by these timings.

Code contract: python3 -m pytest tests/trajectory/test_axisymmetric_bianchi_i_c8_numerics.py -q; python3 -m pytest tests/background tests/trajectory/test_axisymmetric_bianchi_i_physical_transport.py tests/trajectory/test_axisymmetric_bianchi_i_c8_numerics.py tests/trajectory/test_characteristic_angular_solver.py tests/trajectory/test_causal_characteristic_history.py -q; PYTHONPATH=src python3 scripts/measure_axisymmetric_c8.py --out /NEW/RESULTS.json. The CLI refuses overwriting an existing output. All input source provenance and standalone outputs are preserved in the private archive and public source where appropriate.

## 5. Scope/next action

Selected **R10 (finite-clock theory closeout) and C8 (numerical accuracy/runtime research) are closed with direct evidence**. This is not closure of the full REC program, nor an invitation to silently begin a new R1–R10 theory cycle. The next coding stage, if separately requested, is C9 independent changed-surface/scientific review: assess log-to-time normalization, snapshot-to-ray coupling, method identity and full radiation/gas source error before any downstream native REI adapter. Need separate evidence and owner action for full reionization AX08 signed histories, AX11 refinements and AX12 source/IC; no changes to their processes, STATE, queues, config, checkpoints.

Current REI owner PR117, observed HEAD 6cbdb57010a79eb3bbbc6a54b7f1a75d466702fd: AX08 owner-progress and PLUS recovery, AX11/AX12 pending, admission NOT_ISSUED. Do not duplicate that launcher or claim REC C8 is an approved producer. HE18 C1 warm second-cell optical and source trajectory are independently progressing and not mixed into our cold scalar/frozen-source test.

Relevant literature: N.J. Higham, Accuracy and Stability of Numerical Algorithms (SIAM 2002), https://doi.org/10.1137/1.9780898718027; P. Fleury, C. Pitrou, J.-P. Uzan, Phys. Rev. D 91 043511 (2015), https://doi.org/10.1103/PhysRevD.91.043511; Egger & Schlottbom, SIAM J. Numer. Anal. 54 (2016), https://doi.org/10.1137/15M1051336, for wider transport error analysis (not exact identification of our scalar method). Novel first-in-literature priority not claimed.
