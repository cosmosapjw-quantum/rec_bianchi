# PR-05C — canonical-output-grid adaptive short trajectory

## Inherited result

PR-05B3/v0.61 makes the typed characteristic history the sole active Python
owner of scalar `Dfplus`/`Dfplus_Ly` feedback after exact canonical parity. The
local system remains a rank-one semi-explicit DAE in `eta=ln(a)`, accepted
history is immutable during an attempted step, and history commit/reject/
rollback/restart are byte-exact.

## Primary question

Can the source-identifiable rank-one DAE, typed scalar history, COM--KHW
collision state and split-domain interface be advanced through short adaptive
trajectories while retaining the canonical original-HyRec history grid,
accepted-step causality, event localization, positivity and componentwise
number/energy/four-force closure?

## Critical grid decision

The accepted original-HyRec history is source-identical only on the canonical
uniform output grid

```text
eta_n = eta_start + n * DLNA,
DLNA = 8.49e-5.
```

Therefore PR-05C must not append radiation history at arbitrary adaptive times.
Use a two-level stepping contract:

```text
canonical macro interval:  [eta_n, eta_{n+1}]
  adaptive microsteps:     internal DAE/collision/event solves, no history mutation
  macro endpoint:          construct one source-order outgoing candidate
  successful macro step:   commit exactly one canonical history slice
```

A rejected microstep, rejected macrostep or event rollback leaves the accepted
history unchanged. Generalizing the accepted history to a nonuniform grid would
be a new transport discretization and is outside this source-parity stage.

## C1. Adaptive trajectory context

Define:

```text
AdaptiveTrajectoryContext
CanonicalMacroInterval
AdaptiveMicrostepAttempt
AcceptedMacrostepLedger
TrajectoryRestartState
```

The context contains:

- immutable accepted scalar history and its source hashes;
- current `BackgroundSnapshot`/interpolant;
- rank-one local DAE state and algebraic projection;
- log-positive COM occupations and interface accumulators;
- the active typed-history owner registry;
- pending history/COM restart transaction;
- controller state, event registry and deterministic tolerances.

## C2. Reference adaptive method

Implement a deterministic Python reference before any PETSc binding:

1. backward-Euler microstep;
2. two half steps for a step-doubling error estimate;
3. weighted norm with explicit absolute/relative tolerances per state block;
4. accept/reject controller with bounded growth/shrink factors;
5. algebraic constraint projection at every trial endpoint;
6. no clipping of signed departures; log variables for positive occupations.

The reference method is an audit oracle, not the final performance path.

## C3. PETSc-compatible residual and callbacks

Expose the same residual through the PETSc convention

```text
F(eta,U,Udot)=0
J = dF/dU + a*dF/dUdot.
```

Callback ownership:

```text
PreStep / attempt:
  freeze accepted-history parent and create no durable mutation

PostStep after a successful canonical macro endpoint:
  commit exactly one append candidate

postevent / rollback:
  restore parent bytes, update event state, restart the integrator
```

PETSc `TSSetPostStep()` is called after successful steps and skipped on event
rollback; `TSSetIJacobian()` uses the shifted Jacobian above. The Python
reference must emulate these semantics even when PETSc is unavailable.

## C4. Events and discontinuities

Predeclare and localize all roots inside a microstep:

- red/blue boundary-speed zero;
- characteristic stencil/source-index switch;
- background branch or chart switch;
- owner/coefficient discontinuity;
- positivity/invariant-region boundary approached before the trial endpoint.

At an event:

1. localize the earliest root;
2. advance only to the root;
3. do not append a history slice unless the root is also the canonical macro endpoint;
4. apply the event update once;
5. restart multistep/FSAL/controller history;
6. choose a conservative first post-event step.

## C5. Bounded trajectory windows

Run three independent windows centered near the source snapshots:

```text
z ~ 1300
z ~ 1100
z ~ 900
```

Each window must cover at least four canonical history macro intervals and
contain multiple accepted adaptive microsteps. Add synthetic-but-physics-shaped
boundary-speed events to the Bianchi II, class-B `VI_h`, and exceptional
`VI_-1/9` lanes so rollback/restart paths are exercised.

The three windows remain independent evidence lanes and are never summed to
cancel errors.

## C6. Conservation and feedback

For every accepted microstep and macro endpoint record separately:

```text
photon number
exact transported face energy
cosmological redshift work
collision photon/atom four-force
interface atom source (=0 for pure representation crossing)
collision free-energy production
algebraic constraint residual
```

Return typed SI `RadiationFeedback`. Physical recoil remains owned by collision
terms; characteristic and interface propagation do not create an atom source.

## C7. Refinement and reproducibility gates

Require:

- accepted macro history count increments by exactly one per canonical interval;
- no history mutation on rejected microsteps/macros or rollback;
- deterministic replay from restart bytes;
- analytic shifted JVP `<1e-8`;
- accepted-step gross backward error `<1e-11`;
- algebraic constraint residual `<1e-11`;
- strict positivity without clipping;
- componentwise number/energy/four-force gates;
- nonpositive collision free-energy production;
- event-time convergence under timestep refinement;
- trajectory convergence under tolerance tightening;
- fixed-step limit agrees with the PR-05B3 one-step reference;
- interface-off and no-event limits reproduce v0.61 exactly;
- fixed-local-state Bianchi microphysics firewall remains exact.

## Exit states

- `PASS_PR05C_ADAPTIVE_SHORT_TRAJECTORY_PR06_NEXT`: all three short windows,
  event lanes and refinement gates pass.
- `PASS_BOUNDED_NO_GO`: the source-identical fixed output grid and requested
  adaptive dynamics cannot be reconciled without a new transport closure;
  preserve v0.61 and publish the blocker.
- `FAIL`: inherited source parity, conservation or positivity regresses.

A PASS hands off to PR-06 full FLRW monolithic history parity. It does not by
itself claim full `x_e(z)`, visibility-function or CMB-spectrum parity.
