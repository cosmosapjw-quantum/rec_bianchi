# Current scientific state — PR-05B1 / v0.59

PR-04 is complete at the source-conditioned split-domain operator-contract
level. PR-05A closes the primitive rate/schema layer. PR-05B1 now fixes the
source-identifiable differential/algebraic/memory structure of the canonical
October-2012 original-HyRec hydrogen solver and proves a bounded no-go for an
invented finite local virtual-radiation time mass.

## PASS results

- The local state in `eta=ln(a)` has size 314 and mass-matrix rank one:
  `x_e` is differential; `Delta x_2s`, `Delta x_2p` and 311 virtual departures
  are algebraic.
- `Dfminus_hist`, `Dfminus_Ly_hist` and `Dfnu_hist` are causal accepted-step
  radiation memory, totaling 625 values per stored slice, and are outside the
  local mass matrix.
- Maximum source electron-rate parity at `z~1300,1100,900`:
  `2.983987151472822e-14`.
- Maximum 100-digit independent arithmetic discrepancy:
  `1.5021187333698988e-13`.
- Maximum source residual and PETSc-style shifted IJacobian discrepancy:
  `3.4992746547891075e-14` and `3.859548117822003e-15`.
- Maximum frozen-coefficient backward-Euler backward error:
  `1.8117642745581107e-12`; minimum physical population remains positive.
- Exact causal-history restart, future-endpoint rejection and fixed-local-state
  Bianchi II / class-B `VI_h` / exceptional `VI_-1/9` firewall.

## PASS_BOUNDED_NO_GO result

A finite local time derivative for a virtual spike requires a finite
`Delta ln(nu)` support or equivalent photon measure. The canonical archive
provides virtual centre frequencies and integrated rates but no finite support
width, cell-edge array or spike shape.

Two positive nonoverlapping support choices, both centered on every canonical
frequency and both compatible with centre-only evidence, produce mass vectors
in the exact ratio 2 while sharing the same zero-width algebraic limit.
Therefore a finite local native-radiation mass is not source-identifiable and
is not fitted or inferred.

## Claim boundary

PR-05B1 closes the source-role registry, rank-one local DAE, algebraic source
solve, causal-memory schema and finite-mass non-identifiability audit. No
compressed Sobolev, diffusion, Schur or history term has been removed. A
physical native/COM trajectory, adaptive integration and FLRW `x_e(z)` parity
are not claimed.

The next stage is **PR-05B2 source-identical causal characteristic-history
block**: exact `fplus_from_fminus` stencils, accepted-step append/rollback,
analytic history JVP and coupling to the rank-one local DAE.
