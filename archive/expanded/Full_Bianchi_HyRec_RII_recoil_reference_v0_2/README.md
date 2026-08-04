# Full Bianchi–HyRec scalar Ly-alpha RII recoil reference v0.2

This bundle is an immutable **reference/audit baseline**, not a
production redistribution table.

## What changed from v0.1

The recoil-free Hummer-II observer-frame kernel is evaluated at

    x_out -> x_out + epsilon_D (1 - mu)

which is equivalent to Meiksin's first-order recoil shift

    q -> q - epsilon_D (1 - mu),

where q = x_in - x_out and

    epsilon_D = [h nu_alpha/(m_H c^2)] [c/v_D].

At T_m = 3000.0 K,

    epsilon_D = 4.629199613272e-04 Doppler widths.

## Key numerical result

The exact equilibrium-flux correction required after the recoil-free
kernel was

    eps_DB = 2.866691328368e-04

and fell to

    eps_DB = 7.071568539686e-06

after the first-order recoil shift.

The maximum column-rate change for |x| <= 4 fell from

    1.062361965882e-03

to

    1.522219611354e-05.

This is strong evidence that the recoil shift supplies the dominant
thermodynamic asymmetry missing from the recoil-free Hummer kernel.
It is not yet a proof that the stored kernel is the fully exact
microscopic kernel.

## Files

- `scalar_RII_recoil_reference_table.npz`
- `scalar_RII_recoil_ledger.json`

## Formula and convention notes

- x = (nu - nu_alpha) / Delta nu_D
- phi_V = Re[w(x+i a)] / sqrt(pi)
- project-spin/polarization physics is not included in this scalar table
- cell-integrated quadrature is used; point-collocation is forbidden
  near the forward delta limit

## Primary literature

- Hummer (1962), non-coherent scattering redistribution functions.
- Meiksin (2006), Appendix A, recoil shift and asymmetry relation.
- Rybicki (2006), detailed balance and corrected FP equation.
- Belluzzi & Trujillo Bueno (2014), observer-frame angle-dependent
  two-term RII redistribution matrix.
