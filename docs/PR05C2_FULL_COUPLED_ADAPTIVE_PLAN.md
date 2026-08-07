# PR-05C2 — full-coupled adaptive short trajectory

## Primary question

Can the v0.62 canonical-macro adaptive controller advance the source-identifiable rank-one original-HyRec DAE together with the 35-state COM–KHW collision state, red/blue split-domain interface and time-dependent `BackgroundSnapshot` characteristics, while preserving causal exactly-once history commits, positivity and componentwise number/energy/four-force closure?

## Fixed conventions and inherited architecture

- Metric signature `(-,+,+,+)`; ordinary frequency in Hz; explicit `c`, `h`, `k_B`.
- Homogeneous scalar background, hydrogen orthonormal tetrad and 1+3 interface.
- Accepted original-HyRec history remains on `eta_n=eta_0+n*DLNA`, `DLNA=8.49e-5`.
- The local native mass matrix remains rank one: `x_e` differential, 313 real/virtual rows algebraic.
- Typed characteristic history is the sole active Python owner of scalar `Dfplus`/`Dfplus_Ly`; the canonical callback is audit-only.
- Sobolev Ly-alpha escape, native `A1s` diffusion and completed/Schur `Tvv` remain canonical.
- COM/interface states remain representation-local; no global native-to-COM remap or fitted normalization.
- Exact interface face frequency, not broad-cell centroid, owns transported photon energy.

## C2.0 Recovery and source lock

1. Start from the v0.62 feature/full bundle and verify exact artifact, source and network hashes.
2. Freeze the v0.48 `BackgroundSnapshot` schema, v0.50 35-state network, v0.57 common ledger, v0.61 owner registry and v0.62 adaptive transaction.
3. Publish an operator-ownership matrix for native atomic terms, COM collision, Liouville transport, interface transfer, thermatter feedback and history mutation. Every term must have exactly one active owner.
4. Do not change an owner unless residual, analytic JVP, conservation ledger and restart state are changed atomically.

## C2.1 Coupled state and adapters

Define a typed `FullCoupledAdaptiveState` containing:

```text
x_e and local derivative
2s/2p + 311 algebraic departures
accepted characteristic history and pending append candidate
35-state x angular-node COM occupation in log variables
red/blue interface accumulators
thermatter/radiation feedback ledger
BackgroundSnapshot interpolant and branch identifier
adaptive controller/event/restart state
```

The local microphysics API may receive only physical tetrad quantities from `BackgroundSnapshot`; Bianchi type labels or chart-internal variables must not enter rate/collision kernels.

## C2.2 Residual and analytic shifted JVP

Assemble

```text
R = R_electron
  + R_real_virtual
  + R_characteristic_history
  + R_COM_collision
  + R_Liouville_boundary
  + R_split_interface
  + R_thermatter
  + R_conservation
```

with PETSc-compatible convention

```text
F(eta,U,Udot)=0
J = dF/dU + a*dF/dUdot.
```

Use exact analytic blocks for primitive rates, fixed characteristic stencils, Bose collision, interface deposition and thermatter feedback. A discrete stencil or branch change is an event, not a differentiable continuation. Compare the production JVP against central differences and an independent high-precision directional reference.

## C2.3 Source-derived background characteristics

For Bianchi II, a class-B representative (`VI_h` or `VII_h`) and exceptional `VI_-1/9`:

1. Load actual `BackgroundSnapshot` sequences from the locked background adapter.
2. Compute hydrogen-frame energy/direction characteristics and red/blue boundary speeds from the snapshot, not synthetic polynomials.
3. Localize every in-step speed zero, branch/chart switch and characteristic-stencil switch.
4. Apply the event update exactly once, restore the parent transaction, restart the controller and limit the first post-event step.
5. At a fixed local hydrogen-frame state, verify exact geometry-independent microphysics.

## C2.4 Adaptive macro/micro integration

Within each canonical macro interval:

1. Freeze accepted history and construct no durable mutation.
2. Evaluate one full backward-Euler trial and two half trials.
3. Require **all three** trials to pass convergence, positivity, backward-error and algebraic-residual gates.
4. Estimate local error from full versus two-half-step states with block-specific tolerances.
5. On rejection, discard all candidate state and leave history bytes unchanged.
6. On event, advance only to the earliest root, perform one event update and restart.
7. At the successful macro endpoint, construct one source-order outgoing slice and commit exactly once.

## C2.5 Componentwise conservation ledger

For every accepted microstep and macro endpoint, record separately:

- photon number per H in native, COM and interface blocks;
- exact interface face photon energy;
- broad-cell centroid correction as an unresolved representation ledger;
- cosmological redshift work;
- physical collision photon/atom tetrad four-force with opposite signs;
- zero atom source for pure representation crossing;
- collision free-energy production.

No sum across `z~1300`, `1100`, `900` may hide a failed component. Aggregate only by maximum normalized component violation.

## C2.6 Validation windows and refinement

Run at least four canonical macro intervals in independent windows near `z~1300`, `1100`, and `900`, plus the three Bianchi event lanes. For each lane perform:

- tolerance tightening by at least factors 1, 1/4 and 1/16;
- event-time refinement;
- fixed-step limit comparison to v0.61/v0.62;
- interface-off and collision-off regression;
- restart at each accepted macro and deterministic replay;
- injected reject/rollback and future-endpoint adversaries.

## Hard gates

```text
all-trial shifted JVP relative error       < 1e-8
all-trial gross backward error             < 1e-11
all-trial algebraic residual               < 1e-11
minimum physical population                > 0 without clipping
accepted history increment per macro       exactly +1
reject/rollback parent-history bytes        exact
restart replay                              deterministic
photon-number residual                      < declared pre-stage threshold
exact face-energy residual                  < declared pre-stage threshold
redshift-work residual                      < declared pre-stage threshold
collision photon+atom four-force            componentwise closed
interface atom source                       exactly 0
collision free-energy production            nonpositive
source-derived event-time refinement        convergent
fixed-local-state geometry firewall         exact
```

Thresholds not already inherited must be declared before the production run. A failed or unidentified coupling measure produces a bounded no-go, not a fitted scale.

## Claim boundary and next decision

PR-05C2 may claim a short source-derived coupled trajectory only in the tested windows and Bianchi lanes. It must not claim full FLRW recombination-history, visibility-function or CMB-spectrum parity. After C2:

- proceed to a PETSc TS/IDA production binding if the Python oracle is not production-equivalent; or
- proceed to PR-06 full FLRW monolithic parity if the reference implementation already meets the production contract and performance is adequate.

## Durable outputs

Implementation, RED/GREEN tests, formalism, ownership matrix, CSV/NPZ trajectories, event and conservation ledgers, adversarial audit, SHA-256 manifest, immutable ZIP, Git commits, self-contained feature Git bundle, full recovery Git bundle, fresh-clone/replay receipts and connector remote receipt.
