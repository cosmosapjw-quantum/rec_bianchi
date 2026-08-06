# Phase 2 — Evidence Acquisition

## Canonical repository evidence

- v0.55 `split_domain_exchange.py`: interface packet is evaluated once, applied
  with opposite signs, carries exact face frequency, and has zero atom source.
- `far_scalar_release_v047.npz`: 35 states; `FR00` index 29 with interval
  `[-21.25,-16.25]`, mode measure `1.6400603146104614e18 m^-3`; `FB02` index 34
  with interval `[16.25,21.25]`, mode measure
  `1.6429495492454702e18 m^-3`.
- State momentum scales give mode-weighted finite-cell photon-frequency
  centroids through `nu_bar = p_bar c/h`.
- v0.55 packet table supplies six positive face rates and exact face energies at
  z approximately 1300, 1100, 900, together with `n_H` and source trace values.
- Existing Bose operator has exact scalar number left-null, analytic JVP,
  log-space backward Euler and collision free-energy diagnostics.
- Existing branch-event module performs exact piecewise-linear zero localization
  and signed integration.

## Primary numerical-analysis literature

1. Boon, Glaeser, Helmig & Yotov, *Flux-Mortar Mixed Finite Element Methods on
   NonMatching Grids*, SIAM J. Numer. Anal. 60 (2022), arXiv:2008.09372.
   Structural support: retain nonmatching subdomain representations and use an
   interface flux as coupling variable.
2. Zhang, Huang & Qiu, *High-order conservative positivity-preserving
   DG-interpolation ... radiative transfer*, SIAM J. Sci. Comput. 42 (2020),
   arXiv:1910.11931. Support: conservation and positivity require an explicitly
   defined transfer geometry/operator; neither follows from moments alone.
3. PETSc SNES manual. Support: matrix-free Newton--Krylov may use an
   application-provided Jacobian action and a separate preconditioner; physical
   conservation must be checked on the original nonlinear residual.
4. Hirata & Forbes, *Lyman-alpha transfer in primordial hydrogen
   recombination*, arXiv:0903.4925. Support: Hubble expansion, resonant
   scattering, recoil and time dependence all contribute to frequency-space
   transfer; the Hubble term cannot be silently conflated with collision recoil.
5. Ali-Haimoud & Hirata, *HyRec*, arXiv:1011.3758. Support: the native radiation
   field is dynamically coupled to level populations/electron fraction and must
   remain a first-class subsystem rather than a finite-cell fit.

## Derived dimensional evidence

For an integrated transfer `q_s = dt Phi_N^s` in photons per H, a uniform
angular update of boundary cell `i_s` is

`Delta f_{i_s,a} = sigma_s n_H q_s / g_{i_s}`,

because `sum_a w_a=1` and therefore
`sum_a w_a g_i Delta f_i = sigma_s n_H q_s`.

The exact transported energy is `n_H h nu_face q_s`. The finite-cell proxy is
`n_H h nu_bar_cell q_s`; their difference must remain in a separate unresolved
transport-energy correction. Replacing `nu_face` by `nu_bar_cell` would move
energy without physical justification.

## Missing evidence and bounded interpretation

v0.55 supplies scalar source-identical face packets but not a full
angle-resolved native trace for arbitrary Bianchi trajectories. Therefore v0.56
can close a source-conditioned interface operator and geometry branch gates,
but it cannot claim full dynamic Bianchi-HyRec history integration. That remains
PR-05. This is a scope boundary, not a reason to fabricate an angular closure.
