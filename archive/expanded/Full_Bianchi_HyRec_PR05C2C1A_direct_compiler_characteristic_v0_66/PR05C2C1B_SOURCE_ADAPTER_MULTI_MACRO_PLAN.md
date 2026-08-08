# PR-05C2C1B — physical source adapter, same-cell refinement, and multi-macro closure

## Entry result

PR-05C2C1A directly compiles complete ell<=24 network nodes at z~900, 1100, and
1300, preserves the exact 3000 K anchor, validates ten withheld pair blocks,
and implements an exact-face characteristic angular solver. The selected-pair
withheld error is below 0.3 percent, but full withheld same-cell evidence and a
physical original-HyRec emissivity/opacity adapter remain open. The first
entropy-graph preconditioner candidate is rejected because it is slower than the
diagonal/AP baseline.

## B1. Original-HyRec coefficient adapter

Derive and source-lock the local hydrogen-frame emissivity and opacity used by
the characteristic angular equation. For each term record source line, units,
degeneracy, stimulated factor, detailed-balance partner, and analytic JVP. The
adapter must reproduce the scalar original-HyRec equation in the FLRW isotropic
limit without a fitted scale.

## B2. Full withheld thermodynamic validation

Compile midpoint and refinement nodes for every unordered pair and same-cell
block. Validate fixed topology, reciprocity, number null, BE null, entropy,
four-force, and log-interpolation JVP. Do not infer success for same-cell blocks
from pair-only witnesses.

## B3. Measured scalable preconditioner

Test nullspace-preserving atomic/native Schur, activity P/Q, angular block, and
interface Schur candidates. Select one only if it improves unpreconditioned
residual, Newton and Krylov iterations, wall time, and peak RSS on every locked
lane. A theorem without measured improvement is not a production selection.

## B4. Multi-macro trajectory

Run at least four canonical macro intervals for z~900, 1100, and 1300 across
Bianchi II, class-B VI_h, and exceptional VI_-1/9. Require exactly one history
commit per accepted macro, byte-exact reject/rollback/restart, strict positivity,
number, exact face energy, redshift work, physical collision four-force,
nonpositive free-energy production, event-time refinement, tolerance refinement,
and FLRW reduction.

## Exit

Pass enters PR-06 full FLRW recombination-history parity. Failure to identify a
source coefficient or stable scalable preconditioner produces a bounded no-go;
no empirical normalization or silent closure substitution is permitted.
