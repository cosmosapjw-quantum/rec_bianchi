# Prepared implementation — execution pending

This document describes prepared code, not observed numerical outcomes. No
scientific command, test, primary replay, native solver, IVP, history rebuild,
matrix work or HD work was executed during code preparation. Root owns the
frozen contract, release, independent scientific review and publication.

## Code and equation map

| File | Responsibility |
|---|---|
| `code/interval80.py` | Exact Fraction-to-Decimal conversion; precision80 directed arithmetic; elementary enclosures; derivatives; whole-cell extrema |
| `code/native_reference.py` | Immutable source hash checks, tagged CSV parsing, all313 exact routes/anchors/geometric clocks, reference/chord/bridge packet |
| `code/point_reference140.py` | Separate precision140 original point formulas from raw binary64, original direct native-to-absolute interpolant, no production imports |
| `code/controls.py` | Critical points, ambiguous-overlap lower endpoint, equality, invalid domains, exact toy chords, direct signed bridge and smooth toy defect |
| `code/run_bounded.py` | Immutable attempt directory, single-thread environment/affinity, CPU/address-space limits, wall watchdog, raw logs and runtime receipt |
| `code/plot_results.py` | Saved numerical intervals to curvature/chord and separated bridge/anchor plots |

`read_sources()` checks the five locked source hashes and reads no history
arrays: the35MB original history archive is streamed only for the existing
SHA256 identity. Source energies come from VIRTUAL field2, native temperature
and redshift from META key/value fields, and line energies/native kN from
`hydrogen.h`. CSV/native tokens first reconstruct binary64. `as_integer_ratio`
and Fraction preserve their exact real interpretation before interval rounding.

Each original query record is copied in full into its binding. The code checks
all313 ordered incoming/source routes, including139→311,270→312,310→313,
311→140 and312→271, plus strict stored a<q<b, prefix5127, exact rational
geometric alpha, chord coefficient and old absolute anchor. It preserves
native alpha for identity but never substitutes it for geometric alpha.

## Arithmetic and precise endpoint conventions

All authoritative interval operations use precision80 Context operations,
FLOOR/CEILING for basic operations and four endpoint products for signed
multiplication. Interval negation uses exact Decimal sign copies, avoiding
implicit use of the default Decimal context. Positive exponential, logarithm
and square root endpoints use HALF_EVEN correctly rounded results expanded by
the adjacent precision80 Decimal values. This relies on the Python3.12 Decimal
contract, not on the precision140 comparison as a proof of enclosure:
https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.exp
https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.ln
https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.sqrt

Root explicitly approved the exact identities ln(1)=0, sqrt(0)=0 and exp(0)=1
at each endpoint, including endpoints of nonsingleton intervals. Those exact
values need no neighboring subnormal. All other elementary endpoints retain
the outward-neighbor construction. Invalid/nonfinite/domain errors, overflow,
underflow and subnormal inputs/results are rejected. Production precision never
changes automatically.

Curvature envelopes evaluate endpoints and any conservatively overlapping
critical points. Overlap permits adding a candidate upper bound. A critical
candidate lower bound contributes only when the full critical interval is
proved inside the true cell; otherwise the lower bound uses endpoint candidates.
The left-endpoint-only path needs the explicit interval proof x(a)>r_plus.

## Separate diagnostic and signed bridge checks

The independent module imports no interval or producer formula module. It
reconstructs original raw exact binary64 inputs at precision140, evaluates
occupation values and original derivative point formulas, finds the actual
critical point maxima and evaluates Bchar/BTR/Btotal by original point
differences. Its direct bridge is evaluated from native occupation and absolute
endpoint interpolants. Primary checks containment field by field and checks
both signed direct/decomposed interval expressions against the opposite
independent point form. It retains the separate characteristic and temperature
bridge, split/direct total bridge residual and direct/decomposed anchor residual.

The useful width target is exactly the frozen1e-40 normalized interval width,
with1e-100 denominator regularization. Failure preserves outputs and requests
diagnosis; it does not change precision or admit physical quantities. Both
independent point chord comparisons and outward endpoint comparisons check the
curvature chord bound. All numeric bounds serialize as Decimal strings.

The controls include exact/affine/quadratic chord signs and the sharp factor1/2,
both curvature critical points, x=1, cells on both sides of x=1, singleton cells,
invalid domains and exceptional arithmetic, separate exact characteristic and
temperature equalities, signed perturbations and a smooth Ff(t,f)=f+t,
fhat=t²+3 defect translation. Ambiguous critical-overlap controls use a possible
true cell that excludes the critical point; this discriminates an invalid
critical-candidate lower endpoint from a valid supremum enclosure.

## Frozen execution interface and records

Run from repository root, only after root's C4 release:

```sh
python3.12 research/rec_h5_native_producer_20261027/code/run_bounded.py --mode primary --cpu-seconds 90 --wall-seconds 180 --memory-mib 2048 --output research/rec_h5_native_producer_20261027/results/primary001
python3.12 research/rec_h5_native_producer_20261027/code/run_bounded.py --mode controls --cpu-seconds 60 --wall-seconds 120 --memory-mib 2048 --output research/rec_h5_native_producer_20261027/results/controls001
```

Wrapper validation requires Python3.12 and exactly those mode-specific limits.
The wrapper preserves stdout/stderr, argv, timestamps, code hashes, Python and
platform identity, CPU user/system/wall time, peak RSS, exit status, one-thread
environment, precision and requested-versus-unobserved model identity. Attempt
directories are created exclusively; failed attempts cannot be overwritten.
The cumulative implementation/execution ceiling remains300CPU seconds.

Primary writes `REFERENCE_PACKET.json`, `POINT_REFERENCE140.jsonl`,
`SOURCE_BINDINGS.json`, `SUMMARY.json`, two plotted numerical figures and the
wrapper receipt. Controls write full named control results and a summary;
failed controls preserve their prefix. The authoritative source hashes are in
the packet; output values are interpreted numerically, not by requiring
byte-identical numerical serialization across platforms.

All physical H5 fields stay null: full_state_K, physical_M2, defect, stability,
positive uniform ODE tube, initial error, epsilon and outgoing bound. Physical
coverage stays0/313; H6/H7 OPEN, L4 false and REI activation false. Scalar
occupation sensitivity1 supplies no coupled-state K. Representation positivity,
if proved, is explicitly named and cannot be promoted to an ODE tube.

## Requested execution identity

The controller requested a lower-tier gpt-6.1-sol coding implementer. The actual
runtime model identity is not independently exposed and is not claimed verified.
No Git publication, backup, checkout, reset, clone or worktree operation is
performed by this implementation.
