# PR-05C literature and solver basis

## Original HyRec

Ali-Haïmoud and Hirata's original HyRec calculation treats the radiation field,
atomic level populations and free-electron fraction as a coupled time-dependent
radiative-transfer problem. The canonical October-2012 source stores the
radiation memory on its fixed logarithmic-scale-factor grid. PR-05C therefore
keeps that output grid source-identical and adapts only internal microsteps.

Primary sources:

- https://arxiv.org/abs/1011.3758
- https://cosmo.nyu.edu/yacine/hyrec/hyrec.html

## PETSc implicit DAE contract

PETSc `TSSetIFunction()` defines `F(t,U,Udot)=0` for DAEs, while
`TSSetIJacobian()` requires `dF/dU + a*dF/dUdot`. `TS` uses nonlinear solves for
implicit methods and provides adaptive error control through `TSAdapt`.

- https://petsc.org/release/manualpages/TS/TSSetIFunction/
- https://petsc.org/release/manualpages/TS/TSSetIJacobian/
- https://petsc.org/release/manual/ts/

## Accepted-step and event semantics

`TSSetPostStep()` runs after a successful step; PETSc's documented call sequence
skips `PostStep` when event processing rolls the step back. Post-event step size
must be selected conservatively when the state or equations change, and
`TSAdapt` may still reject a proposed post-event step depending on the chosen
configuration.

- https://petsc.org/release/manualpages/TS/TSSetPostStep/
- https://petsc.org/release/manualpages/TS/TSSetPostEventStep/
- https://petsc.org/release/manualpages/TS/TSStep/

## Numerical implication

The repository's accepted characteristic history cannot be appended at every
arbitrary adaptive microstep without abandoning source parity. The appropriate
bounded architecture is fixed canonical history macro intervals plus adaptive
DAE/collision microsteps, with one transactional append at each successful
macro endpoint.
