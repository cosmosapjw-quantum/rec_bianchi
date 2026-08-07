# PR-05C1 literature and solver basis

## Original HyRec

The canonical original-HyRec architecture evolves the radiation field together
with level populations and the free-electron fraction, including full
Lyman-alpha radiative transfer and frequency diffusion.  PR-05C1 therefore
preserves the source-identical accepted `eta=ln(a)` history grid rather than
reinterpreting it as an arbitrary nonuniform adaptive grid.

Primary sources:

- Y. Ali-Haimoud and C. M. Hirata, *HyRec: A fast and highly accurate primordial
  hydrogen and helium recombination code*, arXiv:1011.3758.
- Official HyRec distribution page, including the October-2012 stable release:
  https://cosmo.nyu.edu/yacine/hyrec/hyrec.html

## Implicit DAE convention

PETSc represents an implicit DAE by `F(t,U,Udot)=0`; the corresponding implicit
Jacobian is `dF/dU + a dF/dUdot`.  This is the production boundary targeted by
later PR-05C stages.  PR-05C1 is a deterministic Python audit oracle using the
same residual/Jacobian convention.

Primary documentation:

- https://petsc.org/release/manualpages/TS/TSSetIFunction/
- https://petsc.org/release/manualpages/TS/TSSetIJacobian/

## Accepted-step and event semantics

PETSc `TSSetPostStep()` runs after a successful step and is skipped when event
handling rolls the step back.  `TSSetPostEventStep()` permits a conservative
first step after an event.  These semantics motivate the PR-05C1 rule that
trial microsteps never mutate durable history and that exactly one canonical
history slice is committed only at a successful macro endpoint.

Primary documentation:

- https://petsc.org/release/manualpages/TS/TSSetPostStep/
- https://petsc.org/release/manualpages/TS/TSSetPostEventStep/

## Numerical acceptance rule

The step-doubling controller compares one full backward-Euler trial with two
half trials.  Every trial endpoint must independently satisfy positivity,
backward-error and algebraic-residual gates; a good full trial cannot mask a
bad half trial.  The half-trial gate is protected by an explicit red/green
regression in the recovery closure.
