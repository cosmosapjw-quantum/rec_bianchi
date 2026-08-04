# Full Bianchi–HyRec physical event-pair prototype v0.12

This bundle replaces the toy v0.11 amplitude by a physical scalar
COM–KHW pole plus the v0.8 smooth bound+continuum background.

## Main reduction

The Maxwellian atom integral is reduced exactly to

1. a closed dynamic-structure-factor prefactor, and
2. one Gaussian integral over the remaining scattering-plane momentum.

A resonance-adapted tangent quadrature is used around the 2p pole.

## Hard residuals

- full amplitude reciprocity:
  3.041465e-12
- forward/reverse log-edge weight:
  2.557954e-13
- conductance symmetry:
  0.000000e+00
- generator left null:
  1.345861e-15
- equilibrium right null:
  1.316560e-15
- maximum relative photon-number residual:
  2.811088e-16

## Scope

- five absorption-anchored frequency nodes
- Lebedev-14 full-angle grid
- scalar unresolved 2p
- node-based rather than finite-volume deposition

The next production slice is 17 frequency cells x Lebedev-26 directions.

## Files

- `physical_event_pair_tables.npz`
- `physical_event_pair_ledger.json`
- `operator_action_tests.csv`
- `quadrature_convergence.csv`
- `FORMALISM.md`
- `verify_prototype.py`
- `MANIFEST_SHA256.txt`
