# C3 numerical design — frozen source, prepared operations

This design implements the supplied equations and acceptance checks; it does
not select a new physical closure. No numerical execution has occurred.

## Source capture arithmetic

Original archive members stay byte-identical. The instrumenter copies them to
build/source, verifies each exact insertion location, and emits a complete
unified diff. Observation hooks read original evaluated arguments/results.
Native physical expressions, branch predicates, multiplication order, input,
DLNA and table interpolation stay as written. Necessary result/operand storage
must not add evaluations or sequentialize probe operands. The actual runtime
wrapper entry determines call ids, and the wrapper invokes the original
dispatcher exactly once.

All C scalar output uses hexadecimal binary64 serialization or raw IEEE binary64
arrays, with explicit shape/order/endian metadata. No printed decimal truncation
is used as the state source. Required finite fields reject NaN/Infinity rather
than filling them with zero. Undefined/unobserved partition fields serialize
null with a reason, distinct from fixed-neutral helium tagged by the source
branch. Every required H5 endpoint must have a committed xe/Tm row and a final
writer with common thermodynamic inputs.

## Event and writer semantics

The analyzer validates strictly increasing unique call ids, global/local mapping,
known phase/callsite tags, call/write slot agreement and FULL model ownership.
It traverses actual write events and updates W[i]=call_id, preserving overwritten
writers as evidence. Initial-zero versus written slots are separate states.
For selected slots it compares each saved QSS write's actual outgoing/average
values with its associated event and joins final W[i] to final raw arrays.

The selected QSS set is the deduplicated set of radiation-local endpoint integer
indices plus5127. All626 endpoint references and313 original source routes
remain intact in the path packet regardless of time-slot sharing. State/call
differences are recorded as data; they are not silently merged or automatically
declared failures when the contract permits a probe to be the last writer.

## Finite source comparisons

eps64 is exactly2^-52. For each of the old/new outgoing311, average311 and
Lyman3 fields over all7489 retained rows, check

`abs(new-old) <= 512*2^-52*max(abs(new),abs(old))`.

Both-zero entries require exact zero. Compare numeric arrays, report exact-bit
equal counts, maximum absolute/relative differences and every failing position.
This source parity tolerance is frozen and cannot be widened after a failure.
The original target5127 parameter/state fields use the same512eps component
scale; index/energy/route/T0/fsR/meR identities stay exact. Source stdout SHA,
when available, is supplementary evidence rather than the numerical gate.

## Exact discrete recurrence diagnostics

Convert every finite binary64 operand to Fraction.from_float. Preserve X_in,
X_out,h,F_current,F_prev,F_prev2, branch and recorded post-shift memories.
For an actually integrated component define sigma=-1 for xH1s, sigma=+1 for
other components and compute exactly

`rho = X_out-X_in-h*(5*sigma*F_current/4-sigma*F_prev2/4)`.

The exact operation gross is

`G = abs(X_out)+abs(X_in)+abs(h)*(5*abs(F_current)/4+abs(F_prev2)/4)`.

Require abs(rho)<=64*2^-52*G, with G=0 requiring rho=0. The signed component
interpretation follows corrected THEORY eq2. Verify next prev2 equals old prev
and next prev equals current derivative using captured values. Source secant
initialization gets its own record/value/index check; it is not assigned a
past source-call identity. Post-Saha/algebraic updates do not receive rho.

These are discrete arithmetic residuals, not local truncation error or a
physical continuous ODE defect. Do not round-recompute the native update and
subtract that value, because doing so could hide captured-operand mistakes.

## Exact313 represented paths

Keep each old incoming/source route, cell,prefix,stored a,b,q and exact alpha.
Use exact Fractions for a,b,q and each available binary64 endpoint field.
Require a<q<b and positive b-a. Recheck alpha=(q-a)/(b-a) against the original
rational. For each committed and writer-view field independently serialize
left,right,query=(1-alpha)*left+alpha*right,slope=(right-left)/(b-a),
min(left,right),max(left,right). Endpoint identities and the query convex hull
are exact rational checks. No new clock or floating alpha is inserted.

Primary complete writer fields are xe,xHII,TM_eV,TR_eV,H_s_inv,nH_cm3.
Committed xe,Tm_K and available partition values form their own packet view.
Null partition fields stay null rather than producing an invented affine
interpolant. Endpoint positive minima describe the represented affine path;
they supply neither a physical uniform tube nor physical M2. Segment curvature0
is a property of this declared representation only.

##18 controls and stopping rule

Controls1–15 separately refuse: bad source hash; wrong global/local index;
a>=b; outside query; unknown phase; duplicate call id; reversed order; missing
final writer; writer slot mismatch; changed route; missing prev2; wrong use of
prev in a nondegenerate recurrence; nonfinite state; known density-unit mismatch;
wrong neutral-H sign. Controls16–18 positively demonstrate post-Saha separation,
last actual writer after an overwrite, and exact affine endpoint/query/hull
identities. Fixtures must discriminate the named fault; no all-zero recurrence
fixture may stand in for the prev/prev2 or sign controls.

First failure preserves logs and raw prefixes. Input/scientific/convention
ambiguity returns to root. No automatic repair, tolerance/precision change,
repeated capture, solver change or parameter variation is authorized. An
analyzer/figure problem is repaired from saved data only after root authorization.
