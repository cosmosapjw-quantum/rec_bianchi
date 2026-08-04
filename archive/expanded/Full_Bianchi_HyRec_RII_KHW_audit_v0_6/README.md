# Full Bianchi–HyRec Lyα KHW amplitude audit v0.6

This bundle adds the near-Lyα non-resonant Kramers–Heisenberg amplitude
series to the exact Lorentz/recoil conditional-event audit.

It does **not** replace the immutable v0.3 conductance baseline.

## Literature input

Lee's expansion writes

    sigma = sigma_T (omega_alpha/Delta omega)^2
            |A0 + A1 delta + ... + A5 delta^5|^2,

where delta = Delta omega/omega_alpha and

    A1/A0 = -0.8961
    A2/A0 = -12.22
    A3/A0 = -52.52
    A4/A0 = -243.8
    A5/A0 = -1210.

The first-order cross-section factor is therefore

    1 - 1.7922 delta.

## Main findings

- Line-centre KH5/baseline opacity ratio:
  9.999999994994e-01
- Maximum absolute opacity change for x in [-4,4]:
  1.560713280854e-04
- Line-centre mean jump change:
  -2.043040995409e-08
  Doppler widths
- Maximum mean-jump change for x in [-4,4]:
  7.246498238311e-05
  Doppler widths
- Maximum KH1-versus-KH5 factor difference:
  2.556060357365e-06

The KHW amplitude correction mainly modifies the incoming opacity in the
wings. Its effect on individual-event redistribution moments is smaller,
but the next stage must test the full finite-volume operator action.

## Files

- `KHW_event_audit_results.npz`
- `KHW_event_audit_ledger.json`
- `audit_KHW_series.py`
- `MANIFEST_SHA256.txt`

## Primary sources

- Lee (2003), arXiv:astro-ph/0308083.
- Lee & Kim (2004), arXiv:astro-ph/0402023.
- Kokubo (2024), arXiv:2308.04959.
- Rybicki (2006), arXiv:astro-ph/0603047.
