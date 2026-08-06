# PR-04C3 plan — componentwise common-ledger closure

## Classification

`BOUNDED_RESEARCH_AND_IMPLEMENTATION_PLAN / PR-04C3 / v0.57-candidate`

## Entry condition

PR-04C1B/C2 v0.56 has closed the split-domain interface operator at three
source-conditioned snapshots. The exact native face packets, `FR00`/`FB02`
adapters, positive coupled residual, analytic JVP, transported-energy
correction, restart state and branch roots all exist and pass their declared
gates.

The remaining scientific blocker is not local conservation. It is the **claim
level**: v0.56 uses physical native face traces with an unfitted
`q_activity=1` COM BE reference state. This is a valid operator-verification
state, but it is not an independently source-derived physical COM interior
trajectory. v0.54 forbids constructing such a trajectory by an arbitrary
native-to-COM state projection and calling it canonical.

## Fixed conventions

- metric `(-,+,+,+)`;
- hydrogen orthonormal tetrad;
- ordinary `nu` in Hz and explicit `c,h,k_B`;
- homogeneous scalar sector;
- `x=(nu-nu_Lya)/Delta_nu_D`;
- red face `x=-21.25`, blue face `x=+21.25`;
- exact face energy owns transported energy;
- pure representation crossing has zero atomic source;
- no fitted scale, direct state-vector equality, or cross-snapshot averaging.

## Meaning of a common ledger

The snapshots near `z=1300,1100,900` are separate source-conditioned lanes,
not three consecutive timesteps of one integrated solution. Therefore a scalar
sum over snapshots is physically meaningless and can conceal errors by
cancellation.

For snapshot `k` define a ledger vector

```text
L_k = (
  R_N,k,
  R_Egamma,k,
  S_EH,interface,k,
  epsilon_backward,k,
  epsilon_number,k,
  epsilon_JVP,k,
  epsilon_restart,k,
  epsilon_branch,k,
  positivity_margin_k,
  collision_entropy_production_k
).
```

The common ledger is the ordered object

```text
L_common = {z1300: L_1300, z1100: L_1100, z900: L_900}
```

with a single schema, unit registry, sign registry and provenance chain. Its
aggregate gate is a maximum over normalized component magnitudes, never a sum:

```text
epsilon_common = max_k max_j |L_k,j| / S_k,j.
```

Every load-bearing conservation statement must also pass separately at each
snapshot. No error may be rescued by a different redshift.

## C3A — provenance and schema firewall

1. Lock exact SHA-256 values for the v0.55 packet table, v0.56 adapter/coupled
   artifact, v0.50 network, v0.48 background registry and canonical HyRec ZIP.
2. Define one typed ledger schema with explicit units and signs for every field.
3. Record whether each value is algebraic, source-derived, solver-derived or
   diagnostic.
4. Reject missing snapshots, duplicate packet IDs, changed face frequencies,
   inconsistent local `n_H`, or any future-history endpoint.
5. Assert that `q_activity=1` is an operator-verification state and is never
   labelled a native-derived trajectory state.

**Hard gate:** exactly three unique lanes and six unique side packets, each with
one complete provenance chain.

## C3B — source-conditioned action closure

At each snapshot independently:

1. Reconstruct the source-identical native red/blue packet action.
2. Re-evaluate primitive, dense and Schur native actions under their existing
   source guards; preserve their established parity without changing
   normalization.
3. Re-run the 35-state COM collision/interface residual from the v0.56 restart.
4. Record exact native/COM number and face-energy entries with opposite signs.
5. Record zero interface atom source; collision recoil remains separate.
6. Recompute analytic JVP, high-precision reference, positivity, collision
   entropy and branch-root evidence.
7. Serialize/reload the entire common ledger and require exact round-trip.

The native primitive/dense/Schur algebra and COM state are compared through
shared conserved interface variables, not by direct state-vector equality.

## C3C — final closure/no-go decision

### Route A — operator-contract closure

Promote PR-04 complete at the split-domain operator level only if all of the
following hold componentwise at every snapshot:

- exact photon-number cancellation to roundoff;
- exact transported face-energy cancellation;
- exactly zero interface atom source;
- strict occupation and accumulator positivity;
- gross backward error `<1e-11` and independent number closure `<1e-11` when
  strict net Newton is limited by documented float cancellation;
- analytic/JVP relative error `<1e-8`;
- collision entropy production nonpositive;
- exact restart parity;
- all in-step boundary-speed zeros localized;
- primitive/direct/Schur native parity retained;
- no fitted normalization and no direct state remap.

The resulting claim is:

> The source-conditioned scalar split-domain interface contract is conservative,
> positive and differentiable at the declared recombination snapshots.

It is **not** a full recombination-history or native/COM trajectory-parity claim.

### Route B — bounded no-go

If a load-bearing common-ledger field cannot be defined without an independently
source-derived COM interior state, publish a second explicit no-go:

- retain original HyRec as the native transport subsystem;
- retain COM–KHW as an independently verified collision subsystem;
- retain v0.56 local interface tests;
- mark direct multi-snapshot trajectory parity blocked rather than fabricate a
  regularized state map.

## Independent validation

- exact rational/sign identities where possible;
- 100-digit small-system references;
- analytic versus central-difference JVP;
- deliberately permuted, duplicated and sign-flipped packet adversaries;
- a cross-snapshot cancellation adversary that has zero scalar sum but fails the
  componentwise maximum gate;
- compiler-hash policy scanner and unconditional numerical-output hash checks;
- fresh-clone full-bundle verification and feature-bundle fetch/cherry-pick
  rehearsal.

## Durable outputs

- `src/full_bianchi_hyrec/recoil/common_interface_ledger.py`;
- focused tests for schema, componentwise closure and adversarial failures;
- `scripts/run_pr04c3_common_ledger_stage.py`;
- formalism, evidence ledger, hypothesis audit and independent review;
- per-snapshot CSV plus common-ledger JSON/NPZ;
- immutable v0.57 ZIP and SHA-256 manifest;
- state/roadmap/handoff updates;
- self-contained feature Git bundle, full recovery Git bundle and verification
  receipt.

## Completion boundary

PR-04C3 may close PR-04 only at the explicit operator-contract claim level.
Full trajectory integration belongs to PR-05. FLRW recombination-history parity
belongs to PR-06. Those scopes may not be pulled backward into PR-04 by silently
constructing a native-to-COM interior state.
