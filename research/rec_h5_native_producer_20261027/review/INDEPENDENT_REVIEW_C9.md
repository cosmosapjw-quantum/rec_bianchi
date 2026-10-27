# REC-H5-NATIVE-REFERENCE01 — independent C9 review

**Decision: PASS_SCOPED.** Admit the six reviewed code modules and saved
`primary001` / `controls001` outputs as the frozen source-specific reference
and representation producer. No code or output repair is requested.

Date: 2026-10-27. Reviewer: separate `/root/native_reference_review`, previously
responsible for R6 and not implementation. Requested tier: Astra; actual runtime
model identity is not independently observable. Parent reports C8 publication
at `4d1ae9391ae0f40deb6dabbeb0edab8cc494ac9a`; this review pins local source
and output bytes directly in `REVIEW_C9.json` and the targeted audit evidence.
Publication/provider receipts are parent-owned evidence, not independently
repeated network verification in this review.

## Reviewed material and method

Read FROZEN_CONTRACT, CODING_CONTRACT, THEORY, C3 NUMERICAL_DESIGN, all six
code modules, primary/control summaries and receipts, saved packet and point
reference data, saved controls, C7 SCIENTIFIC_VALIDATION and C8 REPRODUCIBILITY.
Reused the closed R6 source/mathematical review and its immutable context
identity. Read the applicable PhysMath 1.0.0 C9 instructions. Examined code
paths against the frozen formulas and independently reasoned through enclosure
inclusion, extrema membership, reference cancellation and exact anchor units.

One bounded targeted audit addressed a concrete admission risk: source code,
serialized bound operands and saved evidence could differ from the code/run
summaries being admitted. It imported **no production modules** and did not
re-evaluate exponentials, derivatives, the producer or controls. It parsed
serialized decimals as exact rational numbers, compared source hashes to both
execution receipts, checked the saved bindings against original context rows,
and checked bound composition and scope directly from exported values.

Command, from the existing repository root:

```sh
python3.12 research/rec_h5_native_producer_20261027/review/targeted_saved_artifact_audit.py
```

The sole audit passed: six code hashes match both receipts; 313 complete old
row records are preserved; 11,581 serialized intervals are finite and ordered;
10,016 saved independent point values lie inside their corresponding saved
intervals; 313 exact-rational radius/chord invariants hold; all 38 saved
controls pass; physical scope fields remain unchanged. It also independently
checks all actual direct-bridge signs, convex chord signs and represented
positivity from saved endpoints. This checks the saved evidence and does not
recreate the independent point computations.

Applied ceilings: 30 CPU seconds, 60 wall seconds, 512 MiB address space, one
interpreter thread and one CPU affinity. Measured check block, including data
reads and hashes: **0.560852120 CPU seconds**, **0.567817296 wall seconds**;
maximum RSS 21,868 KiB. Startup/imports before the timer, final serialization,
source-reading commands and external documentation retrieval overhead remain
unmeasured, not zero. Earlier R6 costs and budgets are preserved. No primary,
control, old native, IVP, matrix or certificate run was repeated.

## Enclosure implementation findings

### Exact conversion and immutable source model

`read_sources` verifies the locked input SHA256 values before consuming them.
The tagged CSV parser uses VIRTUAL field 2 and META radiation temperature;
Lyman energies and kN come from the locked header. Its decimal source tokens
first reconstruct their native binary64 values. `fraction64` then converts
those represented values exactly to Fraction, including context hex values.
This is the frozen model, rather than exact literal-decimal constants.

The source and target indexing correctly distinguish the 314 outgoing source
channels from 313 incoming channels, including the five special Lyman routes.
All original cell, query, sample, alpha, coefficient and anchor fields survive
in saved bindings. Exact Fraction arithmetic checks alpha, the chord
coefficient and signed anchor before interval conversion. The native TR is a
separate represented input from the analytic product kN*T0*(1+z).

### Outward arithmetic and elementary dependencies

`interval80.py` uses explicit precision-80 contexts for every authoritative
basic operation, with FLOOR/CEILING endpoint rounding. Integer/Decimal
construction is exact; Fraction conversion divides its exact numerator and
denominator outward. Products evaluate all four endpoint pairs. Reciprocal
endpoints reverse order correctly for either sign of a denominator interval
that excludes zero. Sign reversal uses exact `copy_negate`; absolute-value
endpoint handling is correct in all three sign regimes.

For monotone exp/ln/sqrt, the code evaluates each interval endpoint in the
HALF_EVEN context and expands to adjacent representable numbers. The exact
endpoint cases exp(0)=1, ln(1)=0 and sqrt(0)=0 are handled separately, even
when only one endpoint has that value. This avoids injecting an unnecessary
subnormal neighbor at exact zero. Other nonfinite/subnormal and forbidden
arithmetic signals are refused. Authoritative bounds stay as decimal strings;
float conversion occurs in plotting only.

The primary rounding dependency is supported by the Python 3.12 Decimal
documentation, whose exp and ln entries explicitly promise correctly rounded
HALF_EVEN results. To resolve the less explicit Python sqrt entry, this review
also read the official libmpdec square-root contract: it specifies correctly
rounded HALF_EVEN behavior. The installed Python 3.12 `_pydecimal.Decimal.sqrt`
source separately explains and implements the extra-digit/sticky adjustment
that ensures correct rounding. This source read is supporting evidence, not a
claim that the C runtime executes that Python implementation.

Sources consulted on 2026-10-27:

- https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.exp
- https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.ln
- https://www.bytereef.org/mpdecimal/doc/libmpdec/arithmetic.html#square-root
- Installed `_pydecimal.py`, `Decimal.sqrt`, under the runtime Python 3.12
  standard library; path and hash recorded in REVIEW_C9.json.

The live Python page is patch version 3.12.16 and libmpdec documentation 4.0.1;
the executed receipts retain Python 3.12.14. No runtime-version substitution
or formal verification of the numerical library is claimed. Library rounding
contracts remain the declared trusted dependency of the interval proof.

### Whole-cell extrema, including uncertain membership

Endpoint derivative intervals supply valid upper and lower candidates for the
true supremum. Any possible critical-point overlap adds an upper candidate.
Only a proved contained critical point contributes its lower endpoint to the
supremum lower bound. Thus an uncertain point just outside the real cell
cannot spuriously increase the reported lower bound. The stationary-point
intervals themselves are constructed outward. The left-endpoint monotonic
shortcut requires `xa.lo > r_plus.hi`, a sufficient whole-cell proof.

The controls specifically cover both stationary points, ambiguous membership,
x=1, the singleton zero-curvature case, both curvature sign branches and
invalid domains. In all actual 313 rows the monotonic and convex regimes are
proved, consistent with the saved flags and positive chord enclosures.

### Cancellation, direct identities and radius composition

The production characteristic bridge uses the frozen nested expm1 identity;
its expm1 is an outward exp followed by outward subtraction at 80 digits.
The saved relative-width result demonstrates sufficient precision for these
actual operands. B_TR remains separate and B_total is also compared with its
direct reference difference. The geometric chord uses exact rational alpha;
the old signed anchor is formed exactly before any decimal arithmetic.

The direct absolute interpolant and the derived anchor-minus-chord-minus-
bridge expression are computed separately. Zero inclusion of their residual
is complemented by cross-containment of independent point values. The radius
uses the old anchor once and upper magnitudes of the chord and total bridge;
the curvature-based radius substitutes the chord upper bound once. The audit
checked these upper-radius compositions using exact rational arithmetic on
the serialized endpoints, avoiding a second floating-point comparison.

### Independent point calculation and controls

`point_reference140.py` imports neither the producer nor interval module. It
reconstructs raw source inputs at precision 140, evaluates original reference
differences, and forms the absolute interpolant directly. It also evaluates
the finite extrema independently. Sharing the Decimal library means it is
an independent formulation/precision diagnostic, not an independent numerical
backend or the proof of outward containment. The code and C8 account preserve
this distinction.

The controls discriminate signed multiplication, rational conversion,
elementary endpoints, uncertain extrema inclusion, reference/temperature
matching and shifts, exact affine/quadratic chords, convex-reference bounds,
direct/decomposed bridges and smooth defect translation. Source inspection
finds their expected signs and exact values consistent with the R6 formulas.
All 38 saved outcomes are true; no new control execution was required.

## Resource, results and scientific scope

The wrapper fixes the mode-specific limits, rejects different limit tuples,
creates new output directories exclusively, configures numerical thread
environment variables, applies CPU/address-space ceilings and CPU affinity,
and kills the process group on wall timeout. It preserves executed argv,
runtime versions, hashes, times, exits and stderr. Both saved receipts show
exit 0, no wall timeout, empty stderr and matching six-module hashes.

The admitted saved runs used 8.352353 CPU seconds for primary and 0.130654 for
controls. Primary contains 313 reference rows and 10,016 independent point
containments. Its maximum normalized width is approximately 6.27452884e-60,
below the frozen 1e-40 usefulness target. C7's deterministic representation
interpretation is consistent with the raw output. Plot code converts only
exported numerical values, uses reference/representation labels and does not
affect authoritative bounds; visual inspection is reused from root's recorded
review rather than repeated here.

**No blocking or nonblocking code defect was identified within this frozen
scope.** The R6 clock finding remains closed. Additional numerical runs or
code edits are not requested by this review.

Formal admission keeps **physical coverage 0/313**. `physical_query_bounds`,
`full_state_K`, `physical_M2`, `physical_defect`, `stability_L`,
`positive_uniform_ode_tube`, `initial_error`, `physical_epsilon` and
`physical_outgoing_bound` remain null. Scalar occupation sensitivity 1 and
positive represented reconstruction are correctly typed separately. H6/H7
remain OPEN, L4 false and REI activation false. These outputs supply the known
reference term and deterministic representation conversion for conditional H5
composition; they do not fill the absent physical trajectory/closure operands.

Review is complete. Parent may use this scoped admission for C10 delivery.
