# PR-05B2/v0.60 source-identical causal characteristic history

## Conventions

Metric signature `(-,+,+,+)`; `eta=ln(a)` increases toward the future; ordinary frequency `nu=E/h` is in Hz; `c,h,k_B` remain explicit. The stored `Dfminus`, `Dfminus_Ly`, and `Dfnu` values are signed dimensionless occupation departures and are not clipped.

## Source-identical query

For each source/target pair,

```text
eta_query = -ln[(1+z) E_source/E_target]
y_query   = (1-lambda)y_left + lambda y_right.
```

The registry has exactly 313 queries per snapshot: 308 virtual-to-virtual, three line-to-virtual, and two virtual-to-line. A query at or beyond the last accepted endpoint fails closed.

At fixed stencil, the exact JVP is

```text
dy_query = (1-lambda)dy_left + lambda dy_right
          + (y_right-y_left) deta_query/DLNA.
```

A discrete stencil-index switch is an event and is not differentiated through.

## Accepted-step transaction

The local solve reads an immutable history prefix, constructs incoming radiation, solves the 313 algebraic rows, evaluates `dx_e/deta`, and creates a `HistoryAppendCandidate`. Rejected attempts do not mutate the parent. Acceptance appends one canonical `eta` slice. Rollback and binary restart reproduce the exact prior bytes.

## Conservation and dimensions

Along a homogeneous FLRW characteristic, `nu_source/nu_target=(1+z_source)/(1+z_target)` and `n_H` scales by the cube of the same ratio. Thus `8*pi*nu^3/(c^3*n_H)` is invariant and the photon number per H is preserved. The photon-energy difference is cosmological redshift work. Pure characteristic propagation has zero atom source.

## Results

The deterministic history contains `7489` accepted slices and `4680625` stored values. Maximum native residual is `3.49927465478910753e-14`, electron-rate discrepancy `2.98398715147282193e-14`, source-order outgoing discrepancy `4.15168034960592653e-12`, and analytic-history JVP discrepancy `4.14421999460273969e-12`.

The z~1300 outgoing relative diagnostic is cancellation-amplified; the corresponding absolute discrepancy is retained in the snapshot ledger. The hard threshold `5e-12` is a source-arithmetic parity threshold, not a physical-error relaxation.

## Claim boundary

PR-05B2 closes the scalar accepted-history replacement contract but does not perform the owner swap. Sobolev Ly-alpha escape, native `A1s` diffusion and completed/Schur `Tvv` remain active. A native-derived COM trajectory, adaptive integration, `x_e(z)` history parity, visibility parity and CMB parity are not claimed.
