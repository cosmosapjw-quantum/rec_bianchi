# PR-05B2 — source-identical causal characteristic-history block

## Decision inherited from PR-05B1

The canonical October-2012 original-HyRec hydrogen solver does not supply a
source-identifiable finite local time-derivative mass for the 311 virtual
spikes. Its source-identifiable structure is instead:

- `x_e`: one differential row in `eta=ln(a)`;
- `Delta x_2s`, `Delta x_2p`, `Delta x_v[0:311]`: 313 algebraic rows;
- `Dfminus_hist`, `Dfminus_Ly_hist`, `Dfnu_hist`: causal accepted-step memory.

PR-05B2 must implement that representation directly. It must not infer finite
cell widths from frequency centres, fit a relaxation time, or relabel a new
finite-volume closure as canonical original HyRec.

## Goal

Expose the source `fplus_from_fminus` and accepted-step radiation update as a
typed, rollback-safe characteristic-history operator with analytic JVP and
exact source parity at `z~1300,1100,900`. Couple it to the rank-one local DAE
from v0.59 without removing any compressed term prematurely.

## B2.1 Typed history schema

Implement immutable schemas for:

```text
CharacteristicHistoryGrid
AcceptedRadiationHistory
CharacteristicQuery
CharacteristicInterpolationStencil
HistoryAppendCandidate
HistoryStepLedger
```

The state must contain, with explicit units and provenance:

```text
accepted eta grid / source indices
Dfminus_hist       [311, n_accepted]
Dfminus_Ly_hist    [3,   n_accepted]
Dfnu_hist          [311, n_accepted]
source energy centres in eV and ordinary frequency in Hz
canonical DLNA and z_start convention
```

A proposed step may create an append candidate, but the durable history mutates
only after the nonlinear step is accepted. Rejected steps and event rollback
must restore the exact prior bytes.

## B2.2 Source-identical characteristic queries

Reproduce every source path in `hydrogen.c::fplus_from_fminus`:

- sub-Ly-alpha virtual-to-virtual feedback;
- Ly-alpha line-to-virtual and virtual-to-line feedback;
- Ly-alpha-to-Ly-beta virtual feedback;
- Ly-beta line feedback;
- Ly-beta-to-Ly-gamma feedback;
- Ly-gamma line feedback.

For each query, lock:

```text
source energy and target energy
eta_query = -ln[(1+z) E_source/E_target]
left/right accepted history indices
interpolation fraction
direction and line/virtual channel
```

The exact source-order two-neighbour linear interpolation is primary. Future
endpoints, out-of-range reads, permuted energies and non-monotone accepted grids
must fail closed.

## B2.3 Analytic JVP and adjoint-safe ownership

The interpolation JVP with respect to the two history endpoints is exact:

```text
d y_query = (1-fraction) d y_left + fraction d y_right.
```

Add derivatives with respect to the query coordinate and frozen background
parameters only when those dependencies are source-identifiable. Do not add a
derivative through a discrete stencil-index switch; localize such switches as
events and restart the step.

The history operator owns only free redshift/characteristic propagation and the
accepted-step append. Atomic, diffusion, escape, COM collision and interface
terms retain their existing single owners.

## B2.4 Coupled accepted-step reference

At each of the three source-conditioned snapshots:

1. read the accepted causal history;
2. construct `Dfplus` and `Dfplus_Ly` from source-identical stencils;
3. assemble and solve the 313 algebraic real/virtual block;
4. evaluate the differential `dx_e/deta` row;
5. compute outgoing `Dfminus`, line histories and average `Dfnu`;
6. create, but do not yet commit, an append candidate;
7. accept or reject the candidate through an explicit transaction;
8. verify exact restart and rollback.

This remains a bounded accepted-step operator test. Adaptive multistep trajectory
integration and event continuation remain PR-05C.

## B2.5 Compressed-term replacement firewall

PR-05B2 may complete the typed replacement of scalar `Dfplus` history feedback
only if all of the following exist in the same stage:

```text
source-equivalent residual contribution
analytic JVP
accepted-step append and rollback
photon-number and exact face-energy ledger
restart state
source C/Python parity
```

Sobolev Ly-alpha escape, native `A1s` diffusion and completed/Schur `Tvv` remain
owned by the canonical algebraic operator unless their complete replacement
contracts are independently closed.

## Hard gates

At each of `z~1300,1100,900`, require:

- exact source stencil/channel classification;
- C/Python `Dfplus` and `Dfplus_Ly` parity;
- no future history endpoint;
- exact accepted-step append and rejected-step rollback;
- analytic history JVP `<1e-10`;
- source real/virtual algebraic residual `<3e-13`;
- electron-rate parity `<4e-13`;
- strict physical positivity where the source variable is an absolute state;
- signed-departure semantics preserved without clipping;
- componentwise photon-number and exact face-energy ledger;
- zero atom source for pure representation crossing;
- exact restart;
- fixed-local-state Bianchi II, class-B `VI_h`, and exceptional `VI_-1/9`
  firewall;
- interface-off v0.59 parity;
- no compressed term removed without a complete owner swap.

## Exit states

- `PASS_PR05B2_CAUSAL_HISTORY_BLOCK`: source-identical characteristic history,
  append/rollback and JVP close at all three snapshots.
- `PASS_BOUNDED_NO_GO`: a required history datum or characteristic measure is
  absent from canonical evidence; publish the obstruction without fitting it.
- `FAIL`: an existing source/parity/conservation gate regresses.

The next stage after a PASS is **PR-05B3 atomic ownership swap and coupled
accepted-step residual**, followed by **PR-05C adaptive short trajectory**.
