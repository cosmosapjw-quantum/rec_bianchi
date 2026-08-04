# Full Bianchi–HyRec scalar Ly-alpha RII phase-space reference v0.3

This is an immutable **thermodynamic finite-volume reference**, not yet
the full fine-structure polarized production kernel.

## Main correction relative to v0.2

Meiksin's first-order recoil kernel obeys the Boltzmann part of the
reverse/forward relation but uses the near-line approximation
nu_out / nu_in ≈ 1.  Rybicki's exact photon-number detailed-balance
condition also contains the photon phase-space factor.

The reference kernel therefore includes

    K(out <- in) = (nu_out / nu_in) K_Meiksin(out <- in).

The equilibrium cell flux is integrated directly,

    S_ij = ∫cell_i dnu_out ∫cell_j dnu_in
           K(out <- in) Pi_density(nu_in),

rather than forming a uniformly averaged cell rate and multiplying by a
cell-averaged equilibrium weight afterward.

## Result

- Relative equilibrium-flux asymmetry:
  7.856465e-17
- Without the phase-space factor:
  2.913625e-05
- Generator left-null residual:
  1.143514e-16
- Equilibrium right-null residual:
  5.646096e-17

No posterior detailed-balance symmetrization was used.

## Canonical discrete form

Let Pi_i be the equilibrium cell photon number and S_ij the symmetric
conductance.  The finite-volume scattering operator is

    dN_i/dt = sum_j S_ij (N_j/Pi_j - N_i/Pi_i).

Equivalently K_ij = S_ij/Pi_j and the diagonal is fixed by column-sum
conservation.

## Important interpretation

The phase-space correction also changes the effective frequency-dependent
scattering profile away from line center.  It must not be combined with
an independently frozen Voigt opacity unless the two conventions are
matched explicitly.

## Files

- scalar_RII_phase_space_conductance.npz
- scalar_RII_phase_space_ledger.json
- GENERATOR_NOTES.py
- MANIFEST_SHA256.txt

## Primary references

- Hummer (1962), MNRAS 125, 21.
- Meiksin (2006), MNRAS 370, 2025, arXiv:astro-ph/0603855.
- Rybicki (2006), ApJ 647, 709, arXiv:astro-ph/0603047.
- Kokubo (2024), MNRAS 529, 2131, arXiv:2308.04959.
