# REC-HISTORY-01 independent review: pre-execution observations

Reviewer: `/root/independent_review`. Source-author and numerical-harness roles
are separate. This review starts from the frozen contract and original C, without
adopting the constructors' conclusions. No scientific program or prior test was
executed during this phase.

The contract SHA256 is
`dc0e109608edddf458489066be4a1bae83bd2d89134535f2a0303c4c5efbcf35`.
The actual `hydrogen.c` SHA256 is
`421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`.

## Source-level reconstruction

`populateTS_2photon` has fixed-coefficient history dependence only in the RHS.
The virtual coefficients are `Tvv[0][b]*x1s*(1-one_minus_Pib)`; the real-row
coefficients are `3*RLya*x1s*1.664786871919931` for Ly-beta and
`3*RLya*x1s` for Ly-alpha. Therefore the stated `B` and
`dF=Mstar*dX-B*du` have the correct sign and coefficient ownership.

`fplus_from_fminus` maps 314 outgoing channels to 313 incoming channels. It uses
the next higher virtual bin except at the three line gaps; Ly-alpha/beta incoming
come from the first virtual bin above their respective line. Incoming Ly-gamma
is a prescribed thermal boundary, not a fourth unknown incoming line.

The C interpolation uses a strictly past prefix and rejects the last stored
endpoint inclusively. Its early thermal return at `iz<2` is part of source parity.
Linear interpolation preserves the sign interval of its endpoints. Absolute
occupation positivity additionally needs the common transported reference; signed
distortion values must not be clipped merely for being negative.

For the frozen local source, `delta=(xr_p/(3*x1s)-d_in)*A` and
`G_N*H*delta=nH_SI*r0*A*(xr_p-3*x1s*d_in)` follow directly from
`G_N=3*1e6*LYA_FACT`. This is one photon event represented at a boundary. An
additional event injection would count the same photon/energy source twice.

## Concrete pre-code findings communicated to the owner

### F1: native query arithmetic versus mathematically equivalent log difference

Target: incoming-history clock and C-oracle comparison.

Evidence: C evaluates `-log((1+z)*E_source/E_target)`, while the proposed expression
is `eta_face-log(E_source/E_target)`. These are mathematically equal but have
different binary64 rounding. Interpolation multiplies query error by a cell slope,
which can scale as `1/h`. The stipulated `64eps` value gate cannot silently absorb
that different error source.

Minimal correction: use the literal native clock path for source arithmetic parity,
or predeclare and report a separate derivative-times-clock-error term. The scalar
interpolation oracle should receive the same query in both implementations.

Status at this phase: OPEN_IMPLEMENTATION.

### F2: exact-knot directional derivative

Target: `interpolation_jvp` and `at_knot` handling.

Evidence: for `y=[0,1,3]`, `h=1`, query `1`, the left slope is 1 and right slope
is 2. At a negative query direction the directional derivative is -1; using the
floor-selected right-cell slope gives -2. Merely attaching `at_knot=True` does
not make an unqualified returned derivative correct.

Minimal correction: reject nonzero query tangents at knots, or retain both slopes
and explicitly select the appropriate one-sided derivative. Handle the start/thermal
boundary independently, since its values may be discontinuous.

Status at this phase: OPEN_IMPLEMENTATION.

### F3: signed physical departures across public APIs

Target: `line_ledger` and `boundary_jvp` when they reuse `boundary`.

Evidence: only `boundary` originally exposes the positive reference occupation.
A negative departure can have positive total occupation when the reference is
large enough. Calling `boundary` with its zero-reference default would reject
such a valid state.

Minimal correction: pass an optional reference occupation through APIs that
claim physical input admission, or explicitly make a tangent/ledger an algebraic
operation on a state admitted by the caller. Do not clip the departure.

Status at this phase: OPEN_IMPLEMENTATION.

### F4: finite inputs do not ensure finite transformed optical depth

Target: `tau/q` and the corresponding JVP.

Evidence: positive finite `q` arbitrarily close to zero can overflow the ratio.
Products such as `exp(-u)*u` then become floating `0*inf`, although the limiting
analytic contribution is finite. This is a representation issue, not a physics
no-go.

Minimal correction: reject unrepresentable ratio/derived tangent explicitly or
use a stable log-domain/asymptotic representation. Preserve the unrounded log
transmission whenever representable.

Status at this phase: OPEN_IMPLEMENTATION.

## Review boundary

Physical history interpolation accuracy remains an explicit input obligation.
The retained snapshot does not supply a full retarded time series or a same-domain
reference-curvature witness. Manufactured finite cases can verify implementation
and the conditional interpolation bound, but cannot promote that physical gate.
The scalar native history is a valid selected scope; a directional Bianchi
characteristic requires a distinct energy/direction/frame provider.

This pre-review does not close R6/C9. Actual code, saved primary outputs and figures
must be inspected in the same review pass. At most four risk-directed tiny new
review cases may be authorized later within the owner's cumulative allocation.

## Static implementation continuation (before primary execution)

The preserved PREEXEC_ADDENDUM adopts F1--F4 without relaxing an acceptance
threshold. Direct inspection of `code/history_boundary.py` closes all four at
the source level: optional native `z_face` arithmetic, exact-knot rejection for
nonzero query tangents, reference forwarding in both physical APIs, and explicit
transformed-depth/tangent finiteness checks. Native E32/E42 literals and complex
array dtypes are retained. The finite Ly-alpha source/diagonal/outgoing replacement
has the correct exclusive coefficient, and `source_at` uses the updated baseline
as well as the incremental source.

### F5: comparison-vector roundoff enclosure

Target: `run_history_checks.py`, positive-comparison witness block.

Evidence: an initial `32*eps*(abs(M)@abs(v))` reserve did not bound a dot product
with up to 313 terms, so a value named `lower` could not support the stated
certificate. This was a harness-evidence defect, not a physical model defect.

Minimal correction adopted before execution: a deliberately conservative
`gamma_(2*n+4)` with binary64 epsilon, separate uncertainty for the sum of
absolute products, an absolute underflow reserve, and outward `nextafter` steps.
The code now states its arithmetic assumptions and limits the witness to the
one stored native binary64 matrix. It does not claim a physical-history bound.

Status: CLOSED_STATIC. Primary result and stored witness still await review.

No scientific program, compiler, dense solve, or old campaign has been executed
by this reviewer. Final review remains open until saved outputs and actual figures
are available.
