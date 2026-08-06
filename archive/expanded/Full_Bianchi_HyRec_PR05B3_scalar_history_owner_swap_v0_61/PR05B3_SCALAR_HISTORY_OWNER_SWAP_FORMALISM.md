# PR-05B3/v0.61 scalar characteristic-history owner swap

## Conventions

Metric signature `(-,+,+,+)`; independent variable `eta=ln(a)`; ordinary frequency in Hz; explicit `c,h,k_B`; homogeneous scalar background. Signed radiation departures remain signed and are never clipped.

## XOR ownership

The scalar incoming-history owner is exactly one of `CANONICAL_CALLBACK` or `TYPED_CHARACTERISTIC_HISTORY`. The production problem is promoted to the typed owner only after exact componentwise source parity. The canonical callback remains callable solely as an isolated audit oracle. Sobolev escape, native `A1s` diffusion and completed/Schur `Tvv` remain canonical.

## Residual and shifted Jacobian

The local rank-one semi-explicit DAE is `R(t,U,Udot,H)=0`. At a fixed characteristic stencil the production action is `dR/dU + a dR/dUdot` plus the exact endpoint blocks inherited from PR-05B2. A discrete stencil switch is an event and is not differentiated through.

## Accepted-step transaction

A nonlinear attempt owns an immutable parent history and one append candidate. `commit()` appends exactly once. `discard()` returns the exact parent. Event rollback restores exact parent bytes and sets `restart_required`. The COM restart payload, local state and local derivative are stored in a deterministic binary transaction payload.

## Conservation

Characteristic photon number per H is conserved componentwise. Photon-energy change is cosmological redshift work. Pure characteristic propagation has zero atom source. RadiationFeedback keeps SI units; physical recoil remains owned by collision terms.

## Results

The maximum shifted-IJacobian discrepancy is `2.12624465852112292e-16`, maximum implicit backward error `4.00610954024109673e-12`, and minimum physical population `4.86080925682533631e-16`. Canonical/typed response differences are zero at all three source snapshots. Transaction restart, rollback and rejection are byte-exact.

## Claim boundary

PR-05B3 completes only the scalar Python history-owner swap. It does not replace Sobolev escape, A1s diffusion or Tvv, and it does not claim an adaptive trajectory, native-derived COM trajectory, full FLRW recombination history, visibility function or CMB parity. PR-05C is next.
