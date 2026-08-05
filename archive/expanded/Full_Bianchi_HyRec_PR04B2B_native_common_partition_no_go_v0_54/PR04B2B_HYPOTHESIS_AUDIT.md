# PR-04B2B hypothesis and adversarial audit

## H1 — unique canonical projection from table centres

The two centre lists uniquely determine source and target cell boundaries.

**REJECTED_SHORTCUT.** The table format stores centres and width-integrated
rates, not numerical edge arrays. Midpoint/Voronoi boundaries are additional
choices, not canonical source metadata.

## H2 — silent high-resolution substitution

The 1493-row table is a nested refinement, so it can define a conservative
restriction to production and then to 17 cells.

**REJECTED_SHORTCUT.** The grids have no exactly shared centres and the
integrated column sums differ. The optional table is a separate reference lane,
not an archive-supplied prolongation/restriction pair.

## H3 — full native measure maps positively to the 17-cell core

A nonnegative map can preserve native mass and moments through order four.

**REJECTED_BY_SUPPORT.** Already `M0` and `M2` are incompatible: any positive
measure on `[-4.25,4.25]` satisfies `M2/M0 <= 18.0625`, whereas the full and
80-bin native measures are far above this sharp bound.

## H4 — discard exterior mass and use two core spikes

The two core-centre contributions may stand in for the full native action.

**REJECTED_AS_NONCONSERVATIVE.** They carry only a small fraction of native
edge mass. Discarding the exterior violates the required zeroth-moment gate.

## H5 — moments through order four identify a unique 17-cell map

Five moment constraints determine seventeen nonnegative target masses.

**REJECTED_BY_IDENTIFIABILITY.** The constraint matrix has nullity at least 12.
A constructive interior witness supplies two distinct strictly positive vectors
with exactly the same five moments. A unique choice requires extra physics or a
regularization objective.

## H6 — choose maximum entropy or minimum transport cost

A regularizer can pick a useful map and be treated as the HyRec projection.

**TRADEOFF / NOT CANONICAL.** Such choices may be numerically useful later, but
are additional closures. Selecting one now would violate the no-output-fitting
and source-provenance contract.

## H7 — split-domain conservative exchange contract

Keep native radiative transport and COM–KHW collision events as distinct
representations and couple only source-derived boundary number/energy fluxes
and explicitly declared moments.

**DEFENDED NEXT ROUTE.** This respects the support no-go, preserves positivity
and conservation, and aligns with the existing interior/near/far architecture.
It remains to be implemented and tested at multiple FLRW snapshots.
