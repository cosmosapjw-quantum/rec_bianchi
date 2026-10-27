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
