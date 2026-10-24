# Preexecution arithmetic clarification — THERMO01 A1
Root decision before any scientific execution; accepted in independent
source/theory review. This addendum takes precedence over ambiguous references
to native value preservation in FROZEN_CONTRACT/THEORY. No tolerance changes.

## Diagnosis
The literal large-tau expression p=1-(1-exp(-tau))/tau loses significant digits
near the1e-6 switch. Its naive complex evaluation also cancels the imaginary
derivative, with amplification approximately eps/tau^2. Thus h=1e-20 alone
does not supply an adequate independent derivative oracle. This is an
arithmetic evaluation issue in the identified source expression, not evidence
of physical error or a missing history uncertainty supplier.

## Two explicit evaluations
1. Literal-native reconstruction is used only for criterionA against stored
   native blocks/rates/sources and outgoing/F evaluated with stored X0. It uses
   source math.exp evaluation order and source thresholds. No new solve is
   used by this parity view. Old source arrays and recorded results remain.
2. Scientific base, analytic tangent, complex-step oracle and mixed finite
   differences all use the SAME stable evaluation of the same piecewise
   real-arithmetic source equations. Its saved matrix is a newly constructed
   coefficient representation; it is not RESP01's old frozen binary64 matrix.

For tau<=1e-6 retain exactly the native polynomial branches
 p=tau/2-tau^2/6, A=tau-tau^2/2.
For 1e-6<tau<.03 use
 p=sum(k=1..10,(-1)^(k+1) tau^k/(k+1)!), A=-expm1(-tau).
For tau>=.03 use p=1+expm1(-tau)/tau, A=-expm1(-tau).
This changes numerical evaluation, not the native1e-6 physics/formula switch.
The.03 point is only the numerical representation switch; evaluate both
formulas consistently and record branch ownership for all finite differences.

At0<tau<.03 the alternating p-series remainder is bounded by
 tau^11/12!, and its derivative remainder by11*tau^10/12!.
Differentiate the same implemented polynomial. Complex-step evaluates the
polynomial with complex arithmetic and does not call tangent propagation.
At finite complex h the real-source truncation estimate is supported by the
prescribed60digit real probes; no interval certificate for complex/libm is claimed.

If stable expm1 is also used for a Bose denominator, explicitly record this
equivalent value-evaluation choice and keep the literal parity view distinct.
No model parameters, atomic tables, source thresholds, incoming values,
native source file, physical convention, acceptance tolerance or branch surface
is changed. No constant real anchoring correction is inserted.

## Comparisons and claims
CriterionA uses literal-native reconstruction only. B,C,D,E use stable
scientific evaluation consistently. All original numerical thresholds are
unchanged. Save native-vs-stable coefficient and observable gaps as separate
diagnostics; source representation differences do not overwrite previous
records. The six columns are numerically checked derivatives of the stable
evaluation of the source's piecewise real equations, with the small native
polynomial approximation explicitly retained. They do not represent the
derivative of IEEE rounding operations.

The additional literal value view costs zero RHS; primary large-system RHS
remains25. No additional run is authorized. The root and same independent
reviewer will inspect actual gaps and the frozen criteria before admission.

