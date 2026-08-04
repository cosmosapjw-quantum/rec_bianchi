# Full Bianchi–HyRec COM conductance audit v0.10

This is a bounded scalar, angle-averaged finite-volume audit.  It is
not yet the production full-angle kernel.

## Main result

Raw relative equilibrium-flux asymmetry:

- baseline: 7.014931562363e-09
- COM pole: 1.427152708987e-05
- COM full: 1.427152708770e-05

The baseline defect is close to the quadrature/model floor, whereas the
COM defect converges near 1.43e-5.  Increasing frequency, velocity, and
angle quadrature does not remove it.

Therefore a COM amplitude cannot be combined consistently with only the
first-order Hummer-Meiksin frequency map. Exact aberration, the outgoing
solid-angle Jacobian, recoil, and event weighting must be promoted
together.

## Stored tables

Both raw and time-reversal-paired conductances are stored.  The paired
table is an audit carrier, not a production claim.

- `conductance_tables.npz`
- `conductance_ledger.json`
- `operator_action_tests.csv`
- `jump_moments.csv`
- `METHOD.md`
- `MANIFEST_SHA256.txt`

## Literature anchors

- Hummer (1962, 1968): angle-dependent redistribution and moving media.
- Rybicki (2006): detailed balance, recoil, and stimulated scattering.
- Hirata & Forbes (2009): Ly-alpha resonant diffusion and recoil in recombination.
- Kokubo (2024): hydrogen Kramers-Heisenberg cross sections and phase matrices.
- Janett et al. (2023): numerical impact of angle-dependent versus angle-averaged PRD.
