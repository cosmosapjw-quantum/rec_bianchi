# PR-05C2A literature and solver basis

## Original HyRec scope

Ali-Haïmoud and Hirata, *HyRec: A fast and highly accurate primordial hydrogen and helium recombination code* (Phys. Rev. D 83, 043513; arXiv:1011.3758) treats the radiation field, atomic populations and free-electron fraction together and includes time-dependent Ly-alpha transfer. This supports retaining the native radiation history as an independent subsystem rather than reinterpreting a scalar history value as a full angular boundary field.

- https://arxiv.org/abs/1011.3758

## Angular closure and positivity

Laiu, Hauck, McClarren, O'Leary and Tits, *Positive Filtered P_N Moment Closures for Linear Kinetic Equations* (SIAM J. Numer. Anal. 54, 2016), provides a relevant positive spherical-harmonic closure family. It is evidence that an angular lifting must be stated as a closure with realizability/positivity conditions; it does not make the scalar original-HyRec history uniquely angle resolved.

- https://epubs.siam.org/doi/10.1137/15M1052871

Han, Huang and Eichholz, *Discrete-Ordinate Discontinuous Galerkin Methods for Solving the Radiative Transfer Equation* (SIAM J. Sci. Comput. 32, 2010), analyzes a discrete-ordinate angular discretization followed by conservative spatial discretization. It supports treating the positive-weight angular grid as a genuine directional discretization rather than collapsing it to a scalar moment.

- https://epubs.siam.org/doi/10.1137/090767340

## Stiff transport and preconditioning

Park et al., *An Efficient and Time Accurate, Moment-Based Scale-Bridging Algorithm for Thermal Radiative Transfer Problems* (SIAM J. Sci. Comput. 35, 2013), uses physics-based preconditioning for time-dependent radiative transfer. This is relevant to the O(1e9) collision/macro stiffness number measured here.

- https://epubs.siam.org/doi/10.1137/120881075

Laiu, Frank and Hauck, *A Positive Asymptotic-Preserving Scheme for Linear Kinetic Transport Equations* (SIAM J. Sci. Comput. 41, 2019), combines spectral angular discretization, micro-macro decomposition, semi-implicit stepping and realizability control. It motivates an asymptotic-preserving alternative if direct block-preconditioned macro solves remain impractical.

- https://epubs.siam.org/doi/10.1137/18M1196297

## PETSc production boundary

PETSc TS represents implicit ODE/DAE systems through `F(t,u,udot)=0`, uses shifted Jacobians and supports event handlers. `TSSetPostStep()` runs after successful steps and is skipped when event handling rolls a step back; conservative post-event steps can be selected with `TSSetPostEventStep()`. These semantics match the accepted-history transaction fixed in v0.60-v0.62.

- https://petsc.org/release/manual/ts/
- https://petsc.org/release/manualpages/TS/TSSetEventHandler/
- https://petsc.org/main/manualpages/TS/TSSetPostStep/
- https://petsc.org/release/manualpages/TS/TSSetPostEventStep/
