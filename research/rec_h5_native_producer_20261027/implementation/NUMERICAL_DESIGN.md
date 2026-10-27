# C3 numerical design
## Exact source model to interval evaluation
There is no new physical closure or time discretization. Each row reuses the exact stored H5 geometric cell and reference law. The only numerical approximation is finite Decimal evaluation enclosed outward at80 digits. Binary64 source values first become exact rationals. Rational-to-Decimal endpoints use directed division; all later arithmetic is directed, including sign-changing products and quotients. Endpoint/query identity and the old anchor are checked in Fraction before numerical rounding.

For increasing elementary functions exp,ln,sqrt, correctly rounded HALF_EVEN endpoint values are expanded by one adjacent representable value. The authoritative dependency is Python Decimal's documented correctly rounded elementary behavior, with actual runtime recorded. Exact endpoint identities ln(1)=0,sqrt(0)=0,exp(0)=1 are represented exactly. They apply to endpoints of general intervals too. Nonfinite, subnormal, underflow, overflow, invalid logarithm/square-root and zero-containing denominator are rejected. This is a clarified edge treatment, not a precision/model change.

## Whole-cell extrema and uncertain membership
The analytic finite candidate theorem replaces a sampled grid. Interval overlap conservatively includes any possible critical point for the upper supremum bound. The lower supremum bound uses endpoint candidates, plus only critical points whose actual membership is proved; a merely possible critical point cannot raise that lower endpoint. In the proved regime x(a)>r_plus both derivative magnitudes decrease, so the exact maximum occurs at a. This branch is used only after an interval comparison.

This distinction matters if a cell endpoint uncertainty overlaps a stationary point just outside the true cell. The code is instructed to use endpoint lower bounds and all candidate upper bounds, which safely handles the ambiguity without a precision scan. A focused overlap control addresses this concrete risk.

## Conditioning and signed differences
Tiny characteristic and native-temperature bridges are not formed by subtracting binary64 outputs. The characteristic bridge uses nested expm1 intervals; expm1 itself is exp followed by an outward subtraction at80 digits, ample working precision under the frozen usefulness criterion. Native temperature is kept separate, and the total is compared with an independently evaluated original difference at140 digits. A zero-containing interval is reported as such without a forced sign.

The chord uses the exact rational alpha. Its curvature bound uses the preserved exact pointwise coefficient (q-a)(b-q)/2. The signed old anchor is evaluated exactly as a rational; only its outward interval representation enters the new bounds. Direct absolute interpolation and the derived decomposition are computed independently in the point reference to detect sign/cancellation errors.

## Scope and controls
Actual-row interval containment and relative width<=1e-40 (with denominator1e-100+abs(midpoint)) test precision utility. They complement, rather than replace, directed-rounding enclosure. Zero controls use containment. Analytic controls probe both critical points, x=1, singleton/invalid domains, exact characteristic/native-temperature equality, quadratic/affine chord and toy defect translation. Scalar occupation K=1 and represented positivity, when reported, do not become coupled-state K or an ODE tube.

No sweep, new physical tolerance, source replacement or old primary replay is introduced. A concrete failure will be preserved and diagnosed before a bounded targeted repair.
