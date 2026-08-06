# PR-05B time-dependent primitive native/atomic block plan

## Goal

Promote the PR-05A algebraic source-conditioned contract to a genuine
primitive time-dependent original-HyRec radiation/atomic block.  The native
radiation variables and real 2s/2p populations become dynamical; selected
compressed terms are removed only together with their explicit replacements in
one residual and conservation ledger.

## Fixed inputs

- canonical October-2012 HyRec archive and v0.58 primitive-rate registry;
- typed `BackgroundSnapshot`, `AtomicRadiationState`, `RadiationFeedback` and
  `TrajectoryStepLedger` schemas;
- separate original-HyRec and COM--KHW representation-local states;
- v0.57 exact red/blue face packets and v0.56 positive interface operator;
- metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`.

## B1. Differential/algebraic state split

Define a declared semi-explicit DAE

```text
M(U) Udot = F_native_transport
            + F_primitive_atomic
            + F_COM_collision
            + F_interface
            + F_thermatter,
C(U)=0.
```

The mass matrix must identify every differential and algebraic variable.  No
row may change role implicitly with redshift.  Absolute populations use a
simplex/log-ratio or other declared positive parametrization; signed departure
variables remain signed and are never clipped.

## B2. Joint compressed-term replacement

For each of Sobolev Ly-alpha escape, native A1s diffusion,
escape/Schur-compressed Tvv and scalar Dfplus/Dfplus_Ly history feedback:

1. write its exact old residual contribution;
2. write the primitive replacement contribution;
3. prove the limiting correspondence;
4. attach photon-number, energy and atom-four-force ledgers;
5. switch ownership atomically in one commit and one test.

A compressed term remains active whenever any replacement field, Jacobian
block or conservation term is absent.

## B3. Analytic block JVP

Implement

```text
J = dR/dU + shift*dR/dUdot
```

for native transport, real-level kinetics, COM collision, interface and
thermatter feedback.  Test every block separately and the assembled action
against centered differences and 80--120 digit references.  Target relative
residual `<1e-8`; conservation is checked on the unpreconditioned residual.

## B4. Thermodynamic and positivity gates

At source-conditioned z~1300,1100,900 require:

- Saha/Planck null and detailed balance;
- M-matrix or invariant-region evidence for the atomic/radiation linearization;
- strict positivity without post-step clipping;
- photon number and photon+atom energy closure;
- tetrad four-force closure for physical collision events;
- nonpositive collision free-energy production;
- exact restart and future-history rejection;
- interface-off v0.58 parity and interface-on v0.57/v0.56 parity;
- fixed-local-state Bianchi II, class-B and VI_-1/9 firewall.

## B5. Solver boundary

PR-05B may use a fixed one-step backward-Euler/DAE solve to close the dynamic
block.  Adaptive redshift evolution, eventful accepted-step sequences and
refinement belong to PR-05C.  PETSc TS/SNES is the production target for the
subsequent adaptive stage; a dense or SciPy reference lane may be retained only
as an independent verifier.

## Completion decision

PASS only if all selected compressed terms have a complete replacement and the
assembled dynamic residual closes componentwise at all three snapshots.  If a
source variable lacks a physically identifiable time measure, publish a bounded
no-go and keep that term compressed rather than fitting a timescale.
