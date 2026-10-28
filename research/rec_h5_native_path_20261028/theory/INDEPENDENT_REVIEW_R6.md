# REC-H5-NATIVE-PATH01 — independent R6 decision

**PASS_SCOPED after two targeted clarifications.** The finite native
transition/call/slot construction, exact represented reconstruction and
conditional implicit-closure bounds are admitted as theory for the frozen
path-acquisition unit. Numerical acquisition and implementation remain
unexecuted/not admitted by this review.

Reviewer: `/root/native_reference_review`, independently delegated and not
responsible for production implementation. Requested tier Astra; observed
runtime model identity is not independently verifiable. Date: 2026-10-28 KST.

## Reviewed inputs and actual methods

Read FROZEN_CONTRACT.md, CLAIMS.md, CONSTRUCTION.md and THEORY.md. Reused the
source intake in SOURCE_REVIEW.md and independently checked the original
archive's history.c update branches and hydrogen.c QSS/history routines.
Also read hyrectools.c to verify that initially unwritten arrays are actually
zero-initialized with calloc. The earlier source review's exact archive/source
identities and current theory identities are retained in REVIEW_R6.json.

Methods: direct source-to-formula comparison, hand Taylor expansion, endpoint
substitution, induction over ordered slot writes, product-rule implicit
differentiation, induced-norm inequalities and examination of physical claim
dependencies. No numerical check, CAS, build, trajectory or source evaluation
was needed or run. Read/hash and report-writing overhead was not timed and
is not represented as zero CPU. No additional scientific allowance was spent.

## Equations and source mappings checked

### (1) Native recurrence and branch signs

Original history.c uses `1.25*current - 0.25*previous2` before shifting
`previous2=previous; previous=current`. On an established differential branch
this is the n,n-2 formula stated in (1). The ionized-H derivative is subtracted
from xH1s and added to the ionized fraction/electron coordinate; the native
temperature derivative is added to Tm on its actual ODE branch. Algebraic
temperature and post-Saha updates are separately scoped. Derivative-memory
initialization is identified as a secant initialization, not silently
identified with a previously evaluated RHS.

The finite augmented state includes the memory and radiation prefix required
to make this a transition rather than an unsupported memoryless photon ODE.
The recorded compiled call sequence is part of the execution identity.

### Actual call and last-writer theorem

Every FULL hydrogen call calculates the algebraic real/virtual populations,
updates the photon slot and returns its scalar hydrogen derivative. An update
`writer[i]=call_id` on each observed write gives the true last writer by
induction on the actual event sequence. The post-Saha repeated trial writes
and compiler-dependent order of subtraction operands are properly handled
by observation rather than an assumed source-text sequence. Committed node
and writer-input thermodynamic records are kept distinct. The zero-initialized
unwritten-slot category is supported by original hyrectools allocation code.

### (2) Discrete residual and scale

The corrected component convention explicitly converts logged ionized-H
derivatives to neutral-H derivatives with sigma=-1 when X=xH1s; other
components use sigma=+1. The exact rational residual then compares the
appropriate component update. The operation-scale expression is nonnegative
and includes the magnitudes of both derivative terms, input and output.
The 64*eps64 rule is a declared finite-source diagnostic tolerance, not a
derived truncation or physical-error bound. R9 should spell out its exact
eps64 convention in executable inputs, as part of the already planned
numerical coding contract.

### (3) Taylor coefficients

Independent hand expansion gives

    F(t-2h) = F - 2h F' + 2h² F'' - (4/3)h³ F''' + O(h⁴),
    h(5F/4-F(t-2h)/4)
             = hF + h²F'/2 - h³F''/2 + h⁴F'''/3 + O(h⁵).

Subtracting this from the exact increment gives
`(1/6+1/2)h³ X''' + (1/24-1/3)h⁴ X''''`, hence exactly
`(2/3)h³ X''' -(7/24)h⁴ X'''' + O(h⁵)`. Constant and linear F are integrated
exactly in real arithmetic. These conclusions require the smooth branch
specified in the theorem and do not assign physical derivative bounds to the
captured trajectory or cross a native model switch.

### (4) Represented path, derivative and clocks

The corrected alpha_j(t) depends on the path variable t, while alpha_j(q_j)
is the fixed-query weight. Endpoint substitution now gives the stated exact
endpoint identities. The strict interior convex-hull bound and positive-field
preservation follow from the nonnegative partition of unity. The open-segment
derivative is the exact secant, and its knot jump gives the stated
distributional second-derivative contribution for a continuous piecewise
affine reconstruction. These are properties of the declared representation.

Native global/local indices, rounded-z logarithms and old H5 stored geometric
coordinates remain distinct. The integer-index join and original stored
endpoints determine this reconstruction; a new logarithm cannot replace the
old alpha or supply a physical retiming bound.

### (5)–(7) Implicit closure and norm bounds

Differentiating Mv=s gives Mv'=s'-M'v; differentiating again gives
Mv''=s''-M''v-2M'v'. Invertibility yields both formulas. For compatible induced
norms, triangle inequality and submultiplicativity give V0=A*S0, then V1 and
V2 exactly as written. Uniform invertibility and derivative bounds across
the interval are explicit premises. No pointwise matrix residual or finite
path capture is substituted for those uniform premises.

### (8) Output chain rule

For z=(eta,theta,u,v), the formula
`y''=DQ(z) z''+D²Q(z)[z',z']` includes all mixed input terms. The clock
coordinate derivatives 1 and 0 are correct. C2 regularity and a fixed smooth
branch are required; stencil changes retain their boundary/jump obligations.
The populations remain algebraic variables rather than invented independent
photon ODE coordinates.

### (9) Conditional Gronwall connection

Read this formula in the existing forward eta orientation: eta>=eta0, with
the first integral from eta0 to eta and the forcing integral from eta0 to
eta. The source step has positive DLNA. For a specified continuous coupled
F and an absolutely continuous reconstruction, the prior fixed-norm
defect/Lipschitz comparison applies while the exact solution and
reconstruction remain in the admissible tube. Initial error, model/closure
forcing, domain/existence and tube bootstrap remain premises. The present
finite capture and piecewise reconstruction do not fill them. The physical
hold is consequently consistent with the theorem, not an omitted numerical
step in the admitted finite-path result.

## Findings and their closure

**R6-F01 — path-variable ambiguity, closed.** Initial equation (4) fixed alpha
at q_j while subsequently claiming a path's endpoint identities. Impact:
literal use would define a constant-in-q expression and invalidate those
identities. Requested minimum correction was alpha_j(t), with a separate
query weight alpha_j(q_j). Parent made precisely that correction. Independently
read the changed lines and verified both endpoints and derivative.

**R6-F02 — neutral-H residual convention, closed.** Initial equation (2)
referred to any integrated component without explicitly converting the
logged ionized-H RHS for xH1s. Impact: an implementation could report a false
residual failure or reverse the neutral-H update. Parent added sigma=-1 for
xH1s and sigma=+1 otherwise, applying it to both current and previous2 logged
derivatives. Independently read the changed lines; the ambiguity is resolved.

No further theory revision or new numerical check is requested. These two
clarifications preserve the source, clock, state, budget and physical scope.
Original published R5 remains historical evidence; the corrected theory is
the admitted snapshot whose identity is recorded with this R6 review.

## Admission boundary and next action

The finite theorem is ready for the parent-owned coding contract and bounded
lower-tier implementation. Acquisition/source agreement, event chronology,
313 joins and represented-path data remain coding-stage obligations.

Physical H5 coverage stays 0/313. Full physical F/norm/e0/model discrepancy,
whole-domain defect/stability, positive uniform tube and bootstrap, physical
M2/endpoint radii, epsilon and outgoing bound remain unprovided. H6/H7 OPEN,
L4_ready=false and REI_activation=false are retained. Existing native-reference
results are reused; no previous science replay or new no-go claim is admitted.
