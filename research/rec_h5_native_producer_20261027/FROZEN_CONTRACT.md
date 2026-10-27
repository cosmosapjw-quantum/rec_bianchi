# R3 frozen claim and input contract
Unit: REC-H5-NATIVE-REFERENCE01. Frozen before numerical execution.

## Result and truth conditions
For every one of the 313 rows in the locked SOURCE_CONTEXT, calculate outward enclosures of the native Wien reference derivatives, whole stored-cell reference curvature, characteristic-query bridge, native-temperature bridge, reference chord and native-to-absolute-interpolant representation bridge. This supplies an actual, source-specific partial H5 observable/reference producer.

All represented binary64 source scalars are interpreted as exact real numbers. The native constants are kN = float(8.617343e-5) eV/K, T0 from SOURCE_CONTEXT source_identity, and the channel energies from the locked native CSV with Lyman energies from hydrogen.h. Do not replace kN with the SI value or insert a population degeneracy into photon occupation. eta = ln(a), photon occupation f and departure y are dimensionless.

## Primary clock and source locks
The H5 row's stored geometric endpoints a,b, recorded query qhat and exact rational alpha=(qhat-a)/(b-a) are primary. These are not replaced by the predecessor's reconstructed native-real clock. The predecessor's results remain valid on their own clock. The R1 README phrase is clarified accordingly; the current candidate already uses the correct clock.

- SOURCE_CONTEXT.json: research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json; SHA256 5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8.
- Native CSV: research/rec_history_geometry_response_20261026/inputs/target_native_snapshot.csv; SHA256 3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7.
- Original history.npz: SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1. Reuse established routing; no history/native primary rerun.
- hydrogen.h: research/rec_history_thermo_20261024/vendor/hydrogen.h; SHA256 e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba.
- original_hyrec_native.py: SHA256 d7bc38346281951fdd5f2677e25f3b558333124a2319786b9b7afb0ab1f7a89c.
- The source CSV is a tagged native format (META, VIRTUAL, REAL, etc.), not a rectangular header CSV. VIRTUAL field 2 is energy_eV; META TR_eV_rescaled is the represented native radiation temperature.
- z=1099.9986525171403 and TRhat=0.25882399309326415 eV retain their exact binary64 meanings. The exact real product kN*T0*(1+z) is a separate quantity.

The complete 313 bindings retain incoming_index, source_index, cell, prefix, exact endpoints/query, geometric_alpha_exact, samples, nominal incoming and prior anchor radius. Incoming indices 0..310 map to virtual energies; 311,312 to E21,E31. Source 0..310 map to virtual energies; 311,312,313 to E21,E31,E41. Special routes 139->311,270->312,310->313,311->140,312->271 must be checked.

## Frozen formulas and domain
For positive E,kN,T0 and a<=q<=b:
x_E(eta)=E*exp(eta)/(kN*T0), w=exp(-x).
w'=-x*w; w''=(x*x-x)*w; w'''=(-x^3+3*x*x-x)*w.
G=f-w; G_f=1; G_ff=G_eta_f=0; G_eta=x*w; G_etaeta=-(x*x-x)*w.

The scalar occupation norm is abs(delta_f). Its coordinate sensitivity is exactly 1. In abs(delta_f)/s_f the factor would be s_f; full coupled-state K is unspecified.

For M1_ref=sup_cell abs(w'), candidates are endpoints and x=1 if possibly inside.
For M2_ref=sup_cell abs(w''), candidates are endpoints and x=(3+-sqrt(5))/2 if possibly inside. Candidate inclusion uses conservative interval overlap. Monotone reduction to the left endpoint is allowed only after an interval proof x(a)>(3+sqrt(5))/2. The x=1 zero and degenerate cell are handled.

For source energy Es and target Et:
qstar=-ln((1+z)*Es/Et); xt=Et/(kN*T0*(1+z)); delta=qhat-qstar.
Bchar=exp(-xt)*expm1(-xt*expm1(delta)).
BTR=exp(-xt)-exp(-Et/TRhat).
Btotal=Bchar+BTR=ws(qhat)-exp(-Et/TRhat).

With alpha from the exact stored geometry:
Jref=(1-alpha)*ws(a)+alpha*ws(b)-ws(qhat).
abs(Jref)<=M2_ref*(qhat-a)*(b-qhat)/2.
ra=uhat-((1-alpha)*yL+alpha*yR).
DirectBridge=(uhat+w_native)-((1-alpha)*(yL+ws(a))+alpha*(yR+ws(b)))
            =ra-Jref-Btotal.
Rbridge=old_anchor_radius + upper_abs(Jref) + upper_abs(Btotal).
Also report the conservative curvature-based radius replacing upper_abs(Jref) with its chord bound. Preserve the old absolute anchor radius exactly.

## Reference translation lemma and physical composition
For y=f-w and Fy(eta,y)=Ff(eta,y+w)-w', exact-reference defect, state error, fixed-norm state Lipschitz bound and translated tube radius are preserved. This is a conditional algebraic result requiring a supplied Ff and path.

For the photon coordinate, y''=partial_eta Ff_j + (D_f Ff_j)Ff - w''. Therefore a supplied whole-tube bound on the physical first two terms can be combined with M2_ref. M2_ref alone is not physical M2. The source archive lacks the required all-time xe,xHII,TM,H state trajectory; the target-face CSV is insufficient for the whole-tube defect/stability calculation.

## Numerical enclosure and independent reference
Production interval arithmetic uses Decimal precision 80. Exact binary64/Fraction input conversion precedes all rounding. Basic operations are directed FLOOR/CEILING, with all four endpoint products for general multiplication. Monotone exp, ln, sqrt are evaluated correctly rounded at HALF_EVEN and expanded by next_minus/next_plus at that precision. Invalid domain, nonfinite values, overflow, underflow or subnormal results are rejected rather than silently accepted. The rounding dependency is primary Python Decimal documentation; higher precision checks are separate evidence, not the enclosure proof.

At least precision 120 independently evaluates original point formulas from raw inputs, without importing the production interval formulas or bridge decomposition. It checks interval containment for all actual rows, and the direct absolute interpolant checks signs and cancellation. Useful interval width target: max width/(1e-100+abs(midpoint)) <= 1e-40 for nonzero physical actual-row derived outputs; zero-containing controls use containment without a relative target. A target failure requests diagnosis, not an automatic precision change or physical acceptance.

Controls cover both curvature critical points; x=1 and degenerate/invalid domains; characteristic and temperature equality; the convex chord coefficient/sign; an exact quadratic chord; direct versus decomposed bridge; a smooth toy defect translation. C4 freezes exact run commands and smaller execution caps before code execution.

## Typed output and admission boundary
reference_bounds: actual 313 enclosures when computed.
physical_query_bounds, full_state_K, physical_M2, physical_defect, stability_L,
positive_uniform_ode_tube, initial_error, physical_epsilon,
physical_outgoing_bound: null.
physical coverage: 0/313; H6/H7 OPEN; L4 false; REI activation false.
No new strong no-go or general novelty claim. Original HD gate and all historical budgets/results remain unchanged. These are deterministic reference/representation inputs for conditional H5 composition.

## Completion criteria
All 313 exact bindings and source locks pass; analytical extrema and chosen controls pass; production enclosures contain independent reference evaluations; signed direct/decomposed bridge agreement passes; independent Astra review accepts this exact scope; raw outputs, code, source ZIP, actual dual backup receipts, DAG return and handoff are published with expected-SHA semantics.
