# PR-05B3 — scalar history ownership swap and coupled accepted-step residual

## Inherited result

PR-05B2/v0.60 closes the source-identical scalar characteristic-history
replacement contract:

- exact `hydrogen.c::fplus_from_fminus` channel/stencil registry;
- accepted-history state and source provenance;
- append/reject/rollback/restart transactions;
- analytic fixed-stencil JVP;
- source-order 313-row algebraic solve and electron differential row;
- componentwise photon-number/redshift-energy ledger.

It deliberately leaves the canonical owner active. PR-05B3 performs the first
actual owner transition, without touching the still-unreplaced Sobolev,
`A1s`-diffusion, or completed/Schur `Tvv` terms.

## Primary question

Can scalar `Dfplus`/`Dfplus_Ly` history feedback be transferred from the
opaque canonical callback to the typed PR-05B2 operator exactly once, while the
full accepted-step residual, analytic shifted Jacobian, conservation ledgers,
restart state and source parity remain closed at `z~1300,1100,900`?

## Fixed conventions

- metric signature `(-,+,+,+)`;
- independent variable `eta=ln(a)`;
- ordinary frequency `nu` in Hz;
- `c,h,k_B` explicit;
- homogeneous scalar background;
- local microphysics receives only `BackgroundSnapshot` physical tetrad data;
- signed departures remain signed and are never clipped;
- a pure characteristic crossing has zero atomic source;
- the three snapshot lanes are tested separately and never summed.

## B3.1 XOR ownership registry

Introduce a fail-closed owner enum for scalar incoming-history feedback:

```text
CANONICAL_CALLBACK
TYPED_CHARACTERISTIC_HISTORY
```

Exactly one owner must be active. The residual constructor must reject:

```text
owner count = 0
owner count = 2
owner/source hash mismatch
history schema mismatch
candidate parent mismatch
```

The other compressed terms remain:

```text
Sobolev Ly-alpha escape      -> canonical active
native A1s diffusion         -> canonical active
completed/Schur Tvv          -> canonical active
```

## B3.2 Coupled accepted-step state

Define a single transactional object containing:

```text
BackgroundSnapshot
PrimitiveRateSnapshot
AtomicRadiationState
AcceptedRadiationHistory (read-only parent)
HistoryAppendCandidate (uncommitted)
COM--KHW state/restart payload
owner registry and source hashes
```

The local semi-explicit DAE remains

```text
M Udot - F(U, history; background) = 0,
rank(M)=1,
```

with `x_e` differential and 313 native real/virtual rows algebraic.

## B3.3 Residual-level parity before removal

For each source snapshot, evaluate two isolated lanes from identical bytes:

1. canonical C-derived incoming fields;
2. typed PR-05B2 incoming fields.

Compare, componentwise:

```text
incoming Dfplus / Dfplus_Ly
native RHS
313-state solution
electron dx_e/deta
outgoing virtual/line/average fields
append candidate
number and exact redshift-energy ledgers
```

Only after these agree within the predeclared source arithmetic thresholds may
`CANONICAL_CALLBACK` be disabled in the Python production residual. No source
C file is modified or deleted.

## B3.4 Full analytic IJacobian/JVP

For

```text
R(t,U,Udot,H)=0,
```

implement

```text
J = dR/dU + a dR/dUdot
```

including the fixed-stencil history endpoint blocks. A discrete stencil-index
switch is an event and invalidates the local Jacobian; it must trigger step
localization and solver restart rather than a derivative through `floor()`.

## B3.5 Transaction boundary

A proposed nonlinear step may construct a candidate but cannot mutate accepted
history. The production mapping is:

```text
pre-step/attempt: read parent, build candidate only
successful post-step: commit candidate exactly once
rejected step: discard candidate
rollback/event localization: restore exact parent bytes
coefficient/stencil discontinuity: restart multistep/FSAL history
```

## B3.6 RadiationFeedback and conservation

Return typed SI feedback with at least:

```text
rho_gamma          [J m^-3]
p_gamma            [Pa]
q_gamma^hat{a}     [W m^-2]
pi_gamma^hat{a b}  [Pa]
Q_atom^hat{mu}     [W m^-3]
```

For pure scalar characteristic propagation:

```text
photon number per H conserved
photon energy change = cosmological redshift work
atom source = 0
```

Physical recoil remains owned by collision terms.

## B3.7 Hard gates

At each of `z~1300,1100,900` require:

- XOR owner count exactly one;
- canonical-vs-typed incoming parity;
- native RHS/solution/electron/outgoing parity;
- analytic shifted IJacobian/JVP `<1e-8`;
- implicit gross backward error `<1e-11`;
- exact candidate parent/index and accepted-step append count;
- rejected-step and rollback byte identity;
- future endpoint and nonmonotone history rejection;
- componentwise photon number and redshift-energy closure;
- zero characteristic atom source;
- strict positivity for absolute populations, signed departures unclipped;
- exact restart;
- interface-off v0.60 parity;
- fixed-local-state Bianchi II, class-B `VI_h`, and `VI_-1/9` firewall;
- Sobolev, `A1s`, and `Tvv` current owners unchanged.

## Exit states

- `PASS_PR05B3_SCALAR_HISTORY_OWNER_SWAP`: typed history is the sole Python
  production owner, all residual/Jacobian/transaction/ledger gates pass, and
  other compressed owners remain unchanged.
- `PASS_BOUNDED_NO_GO`: a required residual or conservation correspondence is
  not source-identifiable; retain the canonical owner and publish the blocker.
- `FAIL`: source parity or an inherited gate regresses.

A PASS hands off to **PR-05C adaptive short trajectory**. PR-05C must use an
accepted-step callback for durable history mutation and restart the integrator
at event/stencil discontinuities. Full FLRW history parity remains PR-06.
