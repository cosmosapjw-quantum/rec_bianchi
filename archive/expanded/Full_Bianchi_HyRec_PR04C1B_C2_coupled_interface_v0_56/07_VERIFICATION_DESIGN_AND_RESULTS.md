# Phase 7 — Verification Design and Results

Verification triangulates four independent routes: analytic JVP versus central
difference, exact number/energy ledgers, a 100-digit two-state mpmath solve, and
piecewise-linear Bianchi branch localization. The largest JVP relative error is
`1.279553711820355e-09` and the largest float/high-precision solution discrepancy is
`3.694332974648189e-15`. Every selected Bianchi II, class-B VI_h and exceptional
VI_-1/9 history contains localized red and blue roots; endpoint-only assignment
produces a nonzero integrated-flux error in every lane.

The compiler-dependent executable hash is additionally protected by a repository
AST policy scanner. Numerical-output hashes remain unconditional scientific
gates; executable hashes remain conditional on the pinned compiler identity.
