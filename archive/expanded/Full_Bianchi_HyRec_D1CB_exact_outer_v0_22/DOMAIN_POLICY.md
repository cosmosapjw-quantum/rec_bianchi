# D1C-C scalar domain and boundary policy

## 1. Compact science-core lane

For observables and collision moments restricted to |x| <= 4.25, retain the
immutable |x| <= 10.25 domain.  Its comparison with the exact |x| <= 12.75
extension gives a worst compact/tapered action change of

    1.746503080635e-05

and M1-M4 RMS changes below 1.9e-6.

## 2. Extended moment lane

When moments are required throughout |x| <= 8.25, use |x| <= 16.25.
The comparison with |x| <= 21.25 gives M1-M4 RMS changes below 2.3e-9.

## 3. Boundary-interface lane

Spectra that remain non-equilibrium at the truncation boundary, including
non-decaying smooth modes and wing-localized disturbances, are not assigned a
larger scattering-only domain by convergence extrapolation.  They must export

    L_red, L_blue

and the same-edge photon/hydrogen four-force to the Liouville and true
emission/absorption modules.

## 4. Far-wing background

At |x|=21.25 the fractional detuning is 4.987042953399e-04, only
1.296e-06 below the current fifth-order background gate.  Direct
bound+continuum evaluation is required before this outermost lane is used as a
production physical boundary.
