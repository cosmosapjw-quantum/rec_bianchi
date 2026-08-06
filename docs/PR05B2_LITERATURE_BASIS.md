# PR-05B2 literature and solver basis

- Ali-Haïmoud & Hirata, *HyRec*, arXiv:1011.3758: full Ly-alpha radiative transfer and simultaneous radiation/level/electron evolution.
- PETSc `TSSetPostStep`: accepted-history mutation belongs after successful steps; a rollback skips the post-step callback.
- PETSc `TSRestartStep`: multistep and FSAL methods must restart after state/coefficient discontinuities, including discrete characteristic-stencil switches.
- Nair & Machenhauer, *Conservative Semi-Lagrangian Transport on a Sphere*, DOI 10.1175/MWR-2869.1: point remapping and finite-volume conservative remapping are distinct. PR-05B2 reproduces the canonical point-history operator and does not relabel it a finite-volume remap.
