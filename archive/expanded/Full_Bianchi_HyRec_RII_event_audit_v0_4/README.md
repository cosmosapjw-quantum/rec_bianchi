# Full Bianchi–HyRec Lyα event audit v0.4

This bundle does **not** replace the immutable v0.3 conductance
baseline.  It audits the next exact-event step.

## Main result 1: frame-factor firewall

Let

- `D_in = gamma (1 - beta·n_in)`
- `D_out = gamma (1 - beta·n_out)`
- `r_H = nu_out / nu_in`
- `rho_* = nu_out_* / nu_in_* = r_H D_out / D_in`

and use

    dnu_out_* dOmega_out_* =
        D_out^-1 dnu_out dOmega_out.

Then

    D_in rho_* D_out^-1 = r_H.

Thus the H-frame `nu_out/nu_in` factor is the exact transformed
combination of the incident proper-density flux, the atom-frame
Kramers–Heisenberg–Waller frequency factor, and the outgoing
phase-space Jacobian.  An event code must not multiply by both
`rho_*` and `r_H`.

## Main result 2: size of exact-minus-first-order kinematics

At T_m = 3000.0 K,

- b = v_D/c = 2.346818180682e-05
- epsilon = h nu_alpha/(m_H c^2) = 1.086388981443e-08
- mean second-order displacement = 1.173409794417e-05 Doppler widths
- RMS second-order displacement = 2.570812187535e-05 Doppler widths
- standard deviation = 2.287396939306e-05 Doppler widths

The exact event audit is therefore now an action/four-force test at
roughly the 10^-5 Doppler-width scale, not a detailed-balance repair.

## Main result 3: monolithic versus conditional routes

The v0.3 monolithic kernel factors exactly as

    Gamma_b = sum_a K[a,b]
    P[a|b] = K[a,b] / Gamma_b.

Numerical residuals:

- conditional column sum:
  4.440892e-16
- kernel reconstruction:
  1.387779e-17
- generator reconstruction:
  0.000000e+00

A separately frozen Voigt opacity is not identical:

- line-centre relative difference:
  -1.043043e-08
- maximum difference for |x| <= 4:
  5.453528e-05

## Files

- `routeM_routeC_factorization.npz`
- `event_audit_ledger.json`
- `audit_event_map.py`
- `MANIFEST_SHA256.txt`

## Literature anchors

- Meiksin (2006), arXiv:astro-ph/0603855
- Rybicki (2006), arXiv:astro-ph/0603047
- Kokubo (2024), arXiv:2308.04959
- Belluzzi & Trujillo Bueno (2014), arXiv:1403.1701
