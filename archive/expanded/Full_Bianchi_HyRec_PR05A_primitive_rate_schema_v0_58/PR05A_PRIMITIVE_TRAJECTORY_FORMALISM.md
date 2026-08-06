# PR-05A v0.58 primitive-rate and bounded trajectory schema

## Scope

PR-05A exposes the canonical October-2012 original-HyRec primitive rate layer, immutable public schemas, a fail-closed ownership/removal theorem, and a source-conditioned one-step algebraic DAE plus COM collision operator. It does **not** claim a time-dependent native radiation trajectory or FLRW recombination-history parity.

## Conventions and units

Metric signature is `(-,+,+,+)`. Ordinary frequency is in Hz. Constants `c`, `h`, and `k_B` remain explicit. Original source temperatures are in eV and recombination coefficients in cm^3/s; public alpha and delta-alpha are converted to m^3/s. Beta, R2p2s and integrated native-bin A coefficients are s^-1.

The canonical source symbol `DAlpha` obeys

```text
DAlpha = Alpha(Tm,Tr) - Alpha(Tr,Tr),
```

and is therefore published as `delta_alpha`, not as a derivative.

## Detailed balance

At `Tm=Tr`,

```text
n_H alpha_i x_e^2 = beta_i x_i,
x_2s = x_1s exp(-E21/Tr),
x_2p = 3 x_1s exp(-E21/Tr).
```

The explicit 2p degeneracy 3 cancels the source `Beta[1]` factor 1/3. Maximum three-lane relative residual: `7.24682370217563401e-15`.

## Bounded DAE contract

The native block remains the canonical algebraic constraint

```text
T_native x_native - s_native = 0,
```

and its direct solution is the PR-05A DAE projection. The COM block is the already-verified interface-off Bose-equilibrium operator. The combined production JVP is the exact block action. Compressed Sobolev/diffusion/Schur/history terms remain active until their explicit replacements are present in the same residual and conservation ledger.

## Cancellation diagnostics

Near `Tm/Tr=1`, delta-alpha is a subtraction of nearly equal alpha values. Raw relative discrepancies are therefore cancellation-amplified and are retained as diagnostics. Hard parity is assessed against the gross alpha/alpha-equilibrium scale; maximum C/Python gross-scaled discrepancy is `1.25452868491684686e-14` and the 100-digit discrepancy is `4.59569986151165642e-15`.

## Claim boundary

This stage proves schema/source/units/JVP/one-step-DAE closure at z~1300,1100,900. Dynamic native radiation, dynamic real populations, joint compressed-term replacement, adaptive integration and xe(z) parity remain PR-05B/C and PR-06.
