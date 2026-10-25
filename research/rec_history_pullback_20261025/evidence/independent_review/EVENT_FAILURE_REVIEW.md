# PB01 first-primary event realization finding and minimal repair review

## Disposition

**APPROVE_MINIMAL_SAVED_DATA_EVENT_PAIRING_PENDING_ARTIFACT.**

This is the continuing independent reviewer. The original primary remains
FAILED_FROZEN_CRITERION, exit2. This note does not change that result, declare a
rerun, relax an exact equality, or finalize the unit before the correction artifact
and actual figures have been reviewed.

Sources read: results/primary001/SUMMARY.json, FINITE_CASES.json,
EVENT_METADATA.json; current primary.py event-action/sign gate and composition.py
paired coefficient construction; diagnostics/event_sign001/DIAGNOSTIC.json.
Two actual CASE_*_OUTPUTS.npz files were independently read directly with standard
NPY/ZIP decoding, without NumPy or scientific source import. Their exact stored
floats and file hashes are in PRIMARY_EVENT_RAW_READBACK.json.

## Observed failure

The summary's coefficient/composition event_sign_pair is true. Its
finite_bridge_box_event_pass is false because six of eight finite cases fail the
exact scalar sign-pair condition. The other recorded bridge, finite-box,
derivative/adjoint, toy, domain, identity, query-interval and Taylor conditions
are passing in the first-primary records. They are not rerun by this review.

The saved-data diagnostic reports all 18 used identities unchanged from primary
before/after and the execution manifest. The inherited KS01 event rows, composed
endpoint/query rows, and all paired lower/upper interval endpoints are exact
sign partners. Among the 24 finite/tangent/remainder pairs checked by the original
gate, 6 differ. The additional explicit-tangent diagnostics contain 2 differences.
The discrepancies are 1 ULP except one 2 ULP remainder; the largest reported
relative discrepancy is 3.072393272920423e-16.

Independent direct raw examples:

| Case/vector | Radiation hex | Independent atomic hex |
|---|---|---|
| d1,t=.5 remainder | -0x1.7206e79666e88p-88 | +0x1.7206e79666e87p-88 |
| d2,t=1 tangent | -0x1.04ac2dbade5ffp-80 | +0x1.04ac2dbade600p-80 |

Thus the original exact scalar gate really failed. It is not a display or JSON
artifact. The observed class is different floating point realizations of exact
opposite response rows. A particular BLAS internal reduction/kernel cause was
not traced and is not asserted. Repeating a BLAS action would not be necessary
to establish the stored-data facts above.

## Why paired evaluation preserves the defined mathematics

Let the stored radiation row be R and the atomic row be A. The verified input
relation is A=-R, including the corresponding reversed interval endpoints.
For every exact-real input vector v,

A v = (-R) v = -(R v).

This holds separately for the finite chart increment, its tangent, its mixed
remainder and the explicit endpoint/query tangent. There is one event with
opposite atomic/radiation energy transfers. The equality is already part of
THEORY.md section7 and frozen criterionG.

Let r_hat be the saved finite binary64 radiation scalar from one of those
actions. A canonical pair (r_hat,-r_hat) uses that same approximate event
realization for both owners. Unary negation of a finite binary64 number changes
the sign exactly and adds no dot-product rounding; signed zeros can be retained.
The point estimate is still a point estimate. This operation does not claim
that r_hat is the exact real dot product or replace the inherited interval proof.

Independently reducing A v and R v need not yield an exactly opposite stored pair
when the arithmetic execution paths differ. Keeping that independent result as
a diagnostic preserves useful evidence. It is mathematically valid to publish
the shared event realization as the canonical pair, because the exact-real
operator identity was independently fixed and verified before this repair.

## Minimal admissible correction

Use only the eight already saved case outputs. For each existing
event_finite, event_tangent, event_remainder and event_explicit_tangent vector:

1. Retain the original independent vector unchanged in the first-primary raw.
2. Copy its first four values, including the radiation scalar, unchanged.
3. Set only the canonical atomic value to the exact negation of that same saved
   radiation scalar.
4. Save a new, separately labelled paired-event artifact, with the independent
   atomic value and discrepancy retained as diagnostics.

This is 32 scalar sign assignments, not new matrix-vector or event-dot actions.
No new source coefficient, input trajectory, K application, solve, inverse, RHS,
native build or IVP is needed. The coefficient and interval artifacts stay
unchanged. No full primary rerun or threshold change is proposed.

The correction must preserve the first-primary code, raw outputs, original case
pass flags, SUMMARY status and exit2 receipt. Its own summary must explicitly
compose the unchanged passing evidence with the repaired canonical event
realization; it must not relabel the old primary as an uninterrupted PASS.
Canonical explicit-tangent comparisons may reuse the radiation comparison for
the paired atomic channel while preserving the independent old comparison.

Acceptance of the completed correction requires only its concrete saved-data
artifact/code read: unchanged radiation/non-atomic values, exact paired atomic
values, original diagnostic preservation, original raw identity preservation,
and zero new matrix-vector/source/solve actions. These checks directly close this
finding and do not expand the scientific scope.

## Budget and review scope

The parent reports the one primary cost as CPU1.026527s, execution-wall
1.071611822s, maxRSS92200KiB, 97 point/operator actions, 200 event-row actions and
10 named interval passes. The saved-data diagnostic reports CPU.115s,
wall.165213825999672s and zero new operator/event matvec actions.
These are separate from the unchanged first-primary count.

The independent two-file readback decoded saved floats only. Its in-body timer
reported wall.001083723000192549s and CPU0.0 at the available timer resolution.
That CPU field is not a zero full-host or interpreter-startup cost claim.
No scientific source was imported; no new mathematical operator was evaluated.

Physical epsilon and outgoing physical bound remain null. Physical HOLD,
global_convergence NOT_RUN, production NOT_APPROVED and REI_activation=false
remain unchanged. Actual PNG review is still pending in the same review episode.

