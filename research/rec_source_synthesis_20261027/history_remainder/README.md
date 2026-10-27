# Exact native-real history remainders

This module implements THEORY.md equations (3)–(6) for a finite piecewise-linear
history. `remainder.py` exposes exact rational values, directional slopes, slope
jumps, retiming identities and the negative Peano jump sum for chord errors.
The data clock is exactly `Fraction(eta[0]) + k*Fraction(dlna)`. This is the native
interpolator's real-arithmetic counterpart. The rounded C execution and the old
interpolant through stored eta-array coordinates retain their separate identities.
The right causal endpoint is excluded, including on zero-step requests.

## Frozen execution

Run the commands recorded in `freeze.json` from this directory, only after the
parent's C4 GO. The wrapper commands are `python bounded.py primary` followed by
`python bounded.py plot`. The first runs the small controls and the actual source
binding once; the second reads only saved results. `freeze.json` gives the exact
interpreter/child commands, CPU and wall limits, one-thread environment, 2 GiB
address-space limit and code/input byte identities. The history cumulative ceiling
is 360 CPU seconds. Receipts and raw stdout/stderr preserve actual attempts.
Existing receipts block blind replay. Unknown prior debits require authority.

## Evidence and interpretation

`results/primary001/` will contain JSON and CSV for each retiming, chord, source
binding, stored/native-real knot difference and causal-prefix skip. Rational
numerators/denominators are authoritative; decimal display values support plots.
The direct value calculation and signed jump calculation must agree exactly.
Absolute jump sums bound absolute errors exactly, including cancellations.
The small controls cover affine and nonuniform grids, both directions through an
absolute-value hinge, starting and target knots, zero steps, cancelling jumps,
invalid grids, exterior requests and mutations of the negative sign, starting
atom and omitted curvature/jump. Actual mutation detection is required only when
the actual represented remainder is nonzero.

All fixed source witnesses and original endpoint/anchor metadata are checked.
Counts are derived from admitted samples. Unavailable neighboring cells are
`SKIP_CAUSAL_PREFIX`. A chord uses a within-cell midpoint on an unavailable side.
The native-real nominal anchor and the preserved geometric anchor are reported
separately. The figure displays zero within-cell errors, crossed-knot remainders,
and absolute-jump envelopes, with a separate chord panel.

`physical_epsilon=null` and physical-bound coverage remains **0/313**. No historical
consumer is modified; no native/RHS/IVP, Ks, GEO root or matvec is executed. These
identities establish the represented reconstruction only. Conditional physical
composition needs independent physical value enclosures; physical derivative
claims additionally need derivative control.

## Workflow context

Selected child scope is C5–C8, with parent scientific authority and no recursive
delegation or review. Skill context used: physmath-research-loop 1.3.0 SKILL.md,
references/CODING_LOOP.md C5–C8 and references/POLICY_INTEGRATION.md. Requested
execution model is gpt-6.1-sol; actual runtime model identity is
`UNKNOWN_NOT_EXPOSED`. The constructor's checks do not constitute the parent's
subsequent independent admission review.
