# Scalar Ly-alpha RII reference bundle v0.1

This is a **reference/audit table**, not a production table.

## Contents

- `scalar_RII_reference_table.npz`
  - 41 log-free Doppler-coordinate frequency cells over x in [-10.25, 10.25]
  - 12 Gauss-Legendre scattering-angle nodes
  - cell-integrated unresolved-2p scalar Hummer-II kernel
  - Rayleigh-angle-averaged kernel
  - exact equilibrium-flux detailed-balance projection
- `scalar_RII_ledger.json`
  - normalization, detailed-balance, rate-change and full-kernel/FP diagnostics

## Conventions

- x = (nu - nu_alpha) / Delta nu_D
- H(a,x) = Re[w(x+i a)]
- phi_V = H / sqrt(pi)
- angular phase p(mu) = 3(1+mu^2)/8
- equilibrium cell weight is proportional to
  integral_cell nu^2 exp[-h nu/(k_B T_m)] dnu

## Main audit values

- Max angle-resolved normalization residual for |x| <= 3:
  6.593552e-09
- Angle-averaged normalization residual for |x| <= 3:
  6.613173e-10
- Detailed-balance equilibrium-flux residual:
  1.355253e-20
- Relative detailed-balance flux correction:
  2.866691e-04
- Max total-rate change for |x| <= 4:
  1.062362e-03

The fourth-order Kramers-Moyal approximation becomes rapidly accurate only
when the test spectrum varies over several Doppler widths. The second-order
FP approximation is not accepted automatically; use the ledgered
action-level overlap gate.

## Primary sources used for the formulation

- D. G. Hummer, MNRAS 125, 21 (1962).
- G. B. Rybicki, ApJ 647, 709 (2006), arXiv:astro-ph/0603047.
- C. M. Hirata and J. Forbes, PRD 80, 023001 (2009), arXiv:0903.4925.
- L. Belluzzi and J. Trujillo Bueno, A&A 564, A16 (2014), arXiv:1403.1701.
