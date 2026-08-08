# PR-05C2C0 literature basis

This stage uses primary literature and official solver documentation only for
load-bearing external claims.

1. **Original HyRec:** Y. Ali-Haïmoud and C. Hirata, *HyRec: A fast and highly
   accurate primordial hydrogen and helium recombination code*, Phys. Rev. D
   83, 043513 (2011), arXiv:1011.3758.  It establishes simultaneous evolution
   of radiation, level populations, and free-electron fraction with full
   Lyman-alpha radiative transfer in the isotropic primordial-recombination
   problem.
2. **Bianchi radiative transfer:** A. Pontzen and A. Challinor, *Bianchi Model
   CMB Polarization and its Implications for CMB Anomalies*, arXiv:0706.2075.
   It derives photon radiative transfer in homogeneous anisotropic Bianchi
   models and supports treating the photon distribution as a phase-space field
   whose angular structure is transported by geometry.
3. **General covariant radiation hierarchy:** A. Challinor, *Microwave
   background polarization in cosmological models*, arXiv:astro-ph/9911481.
   It gives an exact 1+3 covariant multipole formulation in general spacetime.
4. **Bosonic structure preservation:** P. A. Markowich and L. Pareschi, *Fast
   conservative and entropic numerical methods for the Boson Boltzmann
   equation*, arXiv:1009.2748.  It motivates retaining conservation, entropy
   inequality, and generalized Bose-Einstein equilibria simultaneously.
5. **Entropy moment closures:** P. Monreal and M. Frank, *Higher order minimum
   entropy approximations in radiative transfer*, arXiv:0812.3063; M. Frank,
   C. Hauck, and E. Olbrant, *Perturbed, Entropy-Based Closure for Radiative
   Transfer*, arXiv:1208.0772.  These support positivity/realizability-aware
   reduced models but do not turn missing directional information into source
   data.
6. **Positive asymptotic-preserving transport:** M. P. Laiu, M. Frank, and
   C. Hauck, *A Positive Asymptotic Preserving Scheme for Linear Kinetic
   Transport Equations*, arXiv:1807.06109.  It supports the micro--macro,
   realizability, and positivity principles used in the preconditioner
   contract.
7. **Schur AP formulation:** Z. Peng and F. Li, *Asymptotic preserving
   IMEX-DG-S schemes for linear kinetic transport equations based on Schur
   complement*, arXiv:2006.07497.
8. **PETSc DAE interface:** official PETSc `TSSetIFunction` and
   `TSSetIJacobian` documentation.  The implicit Jacobian is
   `dF/dU + a dF/dUdot`, and known operator nullspaces may be attached with
   `MatSetNullSpace`/`MatSetTransposeNullSpace`.

Literature is used to constrain method classes and claim language.  The actual
edge identities, characteristic formal solution, positivity limiter, and
spectral-equivalence theorem are derived and machine-checked in this repository.
