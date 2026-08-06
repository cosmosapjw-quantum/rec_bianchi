# Current scientific state — PR-05A / v0.58

PR-04 is complete at the source-conditioned split-domain operator-contract
level. PR-05A now closes the canonical primitive original-HyRec rate and public
trajectory-schema boundary and a bounded one-step algebraic DAE/operator lane.

## PASS results

- Byte-locked `Alpha_inf.dat`, `R_inf.dat` and `two_photon_tables.dat` with
  source-order cubic interpolation and SI conversion.
- Canonical `DAlpha` is published as `delta_alpha=Alpha(Tm,Tr)-Alpha(Tr,Tr)`;
  it is not a derivative.
- C/Python non-delta parity: `8.81041472831692531e-13`.
- C/Python delta-alpha gross-scale parity:
  `1.25452868491684686e-14`.
- 100-digit regular/gross-delta parity:
  `7.64138575941129606e-15` /
  `4.59569986151165642e-15`.
- Maximum rate JVP, full block JVP and Saha residual:
  `2.56544607086226293e-10`,
  `6.85319758582802810e-16`,
  `7.24682370217563401e-15`.
- Native source residual and bounded implicit backward error:
  `3.49927465478910753e-14` and
  `3.59968496208872607e-14`.
- Positive M-matrix margins, strict physical positivity, exact photon/atom
  energy and four-force closure, restart, causal history and Bianchi firewall.
- No compressed original-HyRec term is removed before a complete replacement.

## Diagnostic, not failure

Near `Tm/Tr=1`, delta-alpha is a subtraction of nearly equal coefficients. The
raw cancellation-amplified C/Python and 100-digit relative diagnostics are
`2.33767314605714518e-11` and
`4.41495937876043465e-10`. Their
gross-scale errors are at the 1e-14--1e-15 level and are the hard parity gates.

## Claim boundary

PR-05A consumes a real `BackgroundSnapshot`, returns typed
`RadiationFeedback`, projects the canonical native algebraic constraint and
evaluates the interface-off COM equilibrium. It does not yet construct a
time-dependent native radiation/real-population trajectory. PR-05B is next;
adaptive history integration remains PR-05C and FLRW xe(z) parity remains
PR-06.
