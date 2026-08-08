# PR-05C2C1A literature and solver basis

- Ali-Haïmoud & Hirata, *HyRec*, arXiv:1011.3758: full Lyman-alpha radiative
  transfer evolves the radiation field with level populations and the free
  electron fraction. This supports treating scalar history and angle-resolved
  Bianchi transport as a coupled evolution problem rather than an instantaneous
  scalar-to-angular reconstruction.
- Laiu, Frank & Hauck, arXiv:1807.06109: positivity and asymptotic-preserving
  structure require explicit realizability/positivity treatment in stiff
  kinetic transport.
- Peng & Li, arXiv:2006.07497: Schur-complement AP formulations are a principled
  route for stiff micro-macro systems, but performance must be measured on the
  actual operator.
- PETSc `TSSetIJacobian`: an implicit DAE supplies
  `dF/dU + a*dF/dU_t`; known nullspaces can be attached to the operator for KSP.

These sources motivate the architecture. None of them supplies the missing
project-specific original-HyRec angular data or replaces direct COM--KHW node
compilation.
