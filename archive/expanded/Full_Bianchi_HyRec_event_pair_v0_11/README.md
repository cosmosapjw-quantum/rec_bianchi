# Full Bianchi–HyRec event-pair architecture v0.11

This bundle is a scalar full-angle architecture prototype for the next
Ly-alpha redistribution step.

## Main result

The conductance is accumulated from one microscopic photon–atom event
and its PT-reversed partner.  It is symmetric before any matrix-level
repair.

Hard residuals:

- event energy conservation:
  1.110223e-16
- event momentum conservation:
  5.051515e-14
- forward/reverse equilibrium edge weight:
  0.000000e+00
- conductance symmetry:
  0.000000e+00
- generator left null:
  3.774758e-15
- equilibrium right null:
  5.929231e-21
- Bose–Einstein action:
  1.026531e-20
- photon+atom four-force:
  0.000000e+00

The anisotropic test has free-energy production

    -2.483667580258e-06,

which is non-positive as required.

## Scope

This is not a production hydrogen kernel.  The scalar amplitude is a
positive Rayleigh-like placeholder.  The artifact verifies the event
pairing, bosonic detailed balance, entropy, Route M/Route C, and
four-force architecture before inserting the full COM-resolved KHW
integrand.

## Files

- `FORMALISM.md`
- `event_pair_prototype.npz`
- `prototype_ledger.json`
- `verify_prototype.py`
- `verify_event_pair.wl`
- `MANIFEST_SHA256.txt`
