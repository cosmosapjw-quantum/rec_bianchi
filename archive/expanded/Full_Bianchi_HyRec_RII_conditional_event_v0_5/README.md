# Full Bianchi–HyRec scalar Lyα conditional-event audit v0.5

This bundle quantifies the correction from the exact special-relativistic
Lorentz/recoil event map relative to the Meiksin first-order update.

It **does not** replace the immutable v0.3 thermodynamic conductance table.

## Main line-centre result

At T_m = 3000.0 K:

- mean exact-minus-Meiksin shift:
  7.045029140732e-06 Doppler widths
- standard deviation:
  1.181022132951e-05 Doppler widths
- exact mean frequency jump:
  -4.394289635901e-04 Doppler widths
- Meiksin mean frequency jump:
  -4.464739927308e-04 Doppler widths
- relative change of the small line-centre drift:
  1.603224e-02

The absolute correction remains tiny.  The percentage is larger because the
line-centre mean drift is a near-cancellation between thermal selection and
atomic recoil.

## What is exact here

- Lorentz boost into and out of the instantaneous atom frame
- atom-frame recoil relation
- outgoing-direction aberration
- final-atom on-shell kinematics
- photon momentum change from the same event quadrature

## What remains approximate

- the absorption-selected atom distribution is the standard
  nonrelativistic Voigt measure
- the full hydrogen Kramers–Heisenberg amplitude is not yet inserted
- no fine structure, J-state interference, alignment, or polarization

## Files

- `conditional_event_results.npz`
- `conditional_event_ledger.json`
- `audit_conditional_event.py`
- `MANIFEST_SHA256.txt`

## Literature anchors

- Meiksin (2006), arXiv:astro-ph/0603855
- Rybicki (2006), arXiv:astro-ph/0603047
- Seon & Kim (2020), arXiv:2005.00238
- Kokubo (2024), arXiv:2308.04959
