# PR-05 literature and solver basis

## Recombination physics

- Y. Ali-Haïmoud and C. M. Hirata, *HyRec: A fast and highly accurate
  primordial hydrogen and helium recombination code*, Phys. Rev. D 83, 043513
  (2011), arXiv:1011.3758. Original HyRec evolves the radiation field
  simultaneously with level populations and the free-electron fraction and
  exploits the sparse radiative-transfer equations. This is the primary basis
  for treating the primitive atomic/radiation block as a time-dependent system.
- Y. Ali-Haïmoud, D. Grin and C. M. Hirata, *Radiative transfer effects in
  primordial hydrogen recombination*, arXiv:1009.4697. This supplies the
  redistribution/line-transfer context and cautions against replacing the
  transport representation by an arbitrary reduced remap.

## Time integration

- PETSc TS manual and `TSARKIMEX` documentation, v3.25. The TS interface supports
  ODE/DAE residuals, implicit SNES solves and additive implicit-explicit
  decompositions. `TSARKIMEX2C/2D` provide second-order schemes with L-stable
  implicit parts; `1bee` is useful for robust DAE startup.
- PETSc `TSSetEventHandler`, `TSSetEventTolerances` and post-event step controls.
  These are the primary design reference for in-step boundary-speed zero
  localization and conservative continuation after an event.
- SUNDIALS ARKODE/IDA documentation. These provide an independent solver-design
  reference for IMEX/DAE evolution, root finding and matrix-free linear solves.

## Delivery

- Git `git-bundle` documentation. Feature and full-recovery bundles carry Git
  refs and objects for verified offline fetch/clone. They are the only canonical
  patch-delivery format for this project from v0.56 onward.
