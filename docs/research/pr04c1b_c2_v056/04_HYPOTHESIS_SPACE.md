# Phase 4 — Hypothesis Space

## H1 — Direct broad-cell collapse

Map each packet to `FR00`/`FB02` using the finite-cell centroid for number and
energy. Cheap, but changes the declared transported energy and erases the face
trace. Distinctive failure: nonzero energy defect proportional to
`nu_bar_cell-nu_face`. Fatal vulnerability: violates the v0.55 packet invariant.

## H2 — Number deposition plus unresolved exact-energy correction

Deposit number only into the exact outer boundary cell using `n_H q/g`; retain
exact face energy and the cell-proxy difference in a separate accumulator and
ledger. Solve occupations and positive transfer multipliers in one implicit
residual. Distinctive prediction: exact global number/transported-energy
cancellation while the representation correction is nonzero but audited.

## H3 — Explicit operator split

Apply packet transfer explicitly and collision implicitly. Positivity requires a
step restriction or clipping, and conservation/JVP no longer belong to one
residual. Fatal vulnerability: violates the monolithic C2 contract.

## H4 — External-HyRec closure only

Do not deposit into COM; retain original HyRec as an external closure. This is a
valid fallback if H2 cannot pass positivity/JVP/conservation, but it leaves C2
open.

## Cheapest discriminators

- H1 versus H2: compare face energy with mode-centroid proxy; any nonzero
  difference kills H1 as an exact interface representation.
- H2 versus H3: choose a red removal step for which the explicit trial is
  negative; H2 must converge to a strictly positive implicit solution.
- H2 versus H4: exact source-conditioned three-snapshot residual and restart
  closure.
