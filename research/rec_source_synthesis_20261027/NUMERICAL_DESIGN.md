# C3 — numerical design and error accounting

## Thermal diagnostics

Construct all source literals and exact SI constants as rational numbers. Define xE and xnu as positive dimensionless values. Compute delta as their exact rational difference, then convert to binary64 for the final elementary functions. Subtracting the separately rounded floating-point x-values would expose the small mismatch to cancellation.

Production computes `I=tanh(delta/2)` and `D=expm1(-delta)/[-expm1(-xE)]`. The denominator is positive for xE>0. Thus I has the sign of delta, and D has the opposite sign. Near coherence, `I ~ delta/2` and `D ~ -delta/(1-exp(-xE))`; the formulas preserve the small difference without subtracting two nearly equal exponentials. The implementation must handle exact delta=0 separately as an analytic zero and reject nonfinite/nonpositive physical inputs.

The independent reference has80 Decimal digits and evaluates the two positive rates before differencing them. It also evaluates the original exponential source ratio. It does not call the production functions or import their stable identity. This cancellation is acceptable in the high-precision reference and is deliberately independent of the production route. Source rationals are evaluated at the requested precision; no observational source precision is fabricated.

Each nonzero I,D is checked in its own relative scale against128eps64. Compare ratio1+D as a ratio as well, but retain D's separate test. Plot signed I,D by line and temperature; display the historical frequency gate in a distinct panel with Hz units. No time stepping, temperature interpolation or collider averaging occurs.

## Represented-history diagnostics

Exact rational arithmetic fixes the scientific comparison at the represented-function level. Build only the native clock knots required for the fixed prefix and source values required for local queries. Reusing a source value is safe because its immutable binary64 value is exactly converted to a rational. Avoid constructing a full channel×time Fraction matrix.

For a query q and target q+d, evaluate P at the endpoints and the directional slope directly. Separately enumerate strictly interior knot jumps and their travel-direction weights. Equality of these two rational expressions is the acceptance criterion. An absolute-jump sum bounds the signed sum by the triangle inequality. This handles knot corners explicitly; a cellwise second derivative of zero cannot bound a nonzero crossed-knot error by itself.

For each chord, independently evaluate its linear interpolant at q and compare with the negative Peano jump sum. Exact ordering a<q<b and the strict causal domain are checked before evaluating any expression. A target exactly at an interior knot is valid and its atom has zero weight. A starting knot uses the slope on the direction of travel and excludes its atom. Zero movement returns zero without requesting a nonexistent exterior derivative.

The sampling plan is derived from actual cell locations. Two within-cell midpoints exist for each strictly interior query. Adjacent-cell crossing midpoints are used only where that cell exists in the fixed causal prefix. Chord endpoints use a within-current-cell fallback on a missing side. Unavailable right crossings are classified SKIP_CAUSAL_PREFIX, never extrapolated. Actual counts, rather than predicted counts, are recorded by the runner.

## Distinct error objects

| Object | Treatment and admissible conclusion |
|---|---|
| HD source inconsistency | Measured from fixed energies/frequencies; original35Hz tolerance unchanged |
| HD binary64 roundoff | Compared with independent Decimal80; no inference of source accuracy |
| Source sampling/interpolation representation | Exact finite piecewise-linear function chosen and named explicitly |
| Native clock reconstruction | Exact-real eta0+k*dlna differs from rounded C operations and stored eta-array knots; report coordinate and anchor differences |
| Jump cancellation | Exact signed remainder and nonnegative absolute sum recorded; ratio interpreted only when meaningful |
| Display rounding | Rational source records remain authoritative; floats support CSV/plots |
| Physical history approximation | No endpoint physical enclosure or smooth physical curvature supplied by this representation test |
| ODE discretization/global convergence | No new solver or IVP runs; global physical convergence NOT_RUN |

The small affine/hinge/cancellation controls and sign/drop-jump mutations directly target the changed implementation. Successful old parser,54DB,24LTE,KS01,GEO01 and native histories are not rerun. Runtime wrappers debit every actual scientific/test/plot process; a failed attempt is retained and a diagnosed repair uses the same cumulative budget.

The design gives finite exact representation checks and a fixed-precision floating-point diagnostic check. It makes no generic convergence-rate or whole-system stability claim.

