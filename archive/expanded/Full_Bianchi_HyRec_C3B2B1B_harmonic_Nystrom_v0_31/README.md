# Full Bianchi-HyRec C3B2B1-B v0.31

This bundle replaces brute-force Lebedev angular release by a
continuous-mu Legendre/Nystrom reference for the physically normalized
two-level Hummer-II kernel.

## Main results

- reference-to-superreference kernel change:
  1.918220e-12
- endpoint-transform validation:
  1.256141e-13
- harmonic-reference isotropy leakage:
  0.000000e+00
- harmonic-subspace leakage:
  0.000000e+00
- minimum/mean core capture:
  7.251197e-01 /
  9.528240e-01

## 302-point collocation versus continuous-mu reference

- smooth L8:
  7.651790e-04
- narrow core:
  3.646975e-04
- P1:
  8.678086e-08
- P2:
  1.313858e-05

The scalar collision operator can now use the harmonic kernel locally,
while the Bianchi Liouville sector continues to use direction
collocation.

## Status

- continuous-mu Hummer reference: PASS
- coherent-forward split: PASS
- backscatter split: PASS
- ell<=6 quadrature: PASS
- finite-volume incoming frequency: OPEN
- ell_max convergence: OPEN
- recoil/full COM-KHW: OPEN
