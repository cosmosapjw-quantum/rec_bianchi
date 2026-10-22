# THERM02 runner implementation return

## Status and ownership

The sandbox runner is implemented and its no-ODE preflight passed. This worker
executed **0 cosmological IVPs, 0 RHS calls, and 0 old suites**. Root owns the
actual eight-case science run, independent review, figures, publication and
backup. No trajectory acceptance is claimed here.

Changed deliverables:

- `code/run.py`
- `evidence/RUNNER_STATIC_CHECKS.json`
- This implementation return.

`coupled_thermal.py`, `checks.py`, `plot.py`, the frozen contract and all reused
payloads remain unchanged. The existing adapter PASS receipt was matched by
source SHA-256; its suite was not rerun.

## Actual executable checks

Working directory: `research/rec_rei_thermal_compton_20261022`.

1. `python -m py_compile code/run.py` — process exit **0**, no output.
2. `python code/run.py --preflight` — process exit **0**, decisive output:

```text
RUNNER_PREFLIGHT: PASS; 8 configurations; 0 RHS calls; 0 cosmological IVPs; 0 old suites
```

The final preflight body took 0.44343780399503885 s. This is a wiring-check
measurement, not a cosmological solver performance claim. An earlier preflight
also passed; after exclusive creation of `ATTEMPT.json` was added, the identical
preflight command was rerun against the final runner identity.

Final runner SHA-256:
`a7fd5f599b05dcec3f0c1b1a78a3de144f7d40ebf9a1db25a60b4c5b13402e4d`.

Final preflight receipt SHA-256:
`ec0271023e4f5cdd54a85b43b6d78a3b8b3b1f87ac07f87ce7e47f255e43f1e2`.

The final read-only inventory found zero `data/*/RESULT.json` files.

## Implemented execution and preservation contract

`python code/run.py --run` executes the frozen five nominal compact34 cases,
two tighter compact34 cases and one nominal full63 oracle in order. No arguments
print help. `--plot` only dispatches the existing data-only plotting module.
`--preflight` checks configuration, tolerance projection, initial compact
admission, JSON identities, an independently specified signed-source fixture
and a closed NPZ round trip. It does not evaluate an RHS.

BDF uses `t_eval=None` and dense output. `solver_return.npz` initially saves
every returned accepted solver node before checking solver success. It is later
augmented with full63 reconstructions, diagnostics and the signed six-vector.
The 193 comparison nodes are evaluated separately through `solution.sol`.
Saved193, accepted BDF nodes, GL8 and GL16 states each receive their own physical
scope/gate report. Each diagnostic point evaluates the current state once and
shares it between diagnostics and the ledger integrand.

The five signed ledger integrands and their instantaneous absolute values are
integrated separately. The normalization is
`max(abs(epsilon0), abs(epsilon), sum(integrated_abs_sources))`.
The CMB/reference and UV Compton entries enter the residual with negative signs
when moved to its left side. GL8/GL16 arrays retain their actual x, states,
five integrands and two exchange ratios. Their signed and absolute cumulative
ledgers and the exchange-ratio integrals are stored in `trajectory.npz`.
The absolute-throughput GL8/GL16 difference is recorded and checked at the same
3e-6 scale, in addition to the signed-ledger difference.

Actual-grey exchange is normalized by the current actual photon energy density;
the external-reference ratio is separately named and zero while inactive.
These measurements are not backreaction error bounds. The three numerical
comparisons report relative T, absolute charge fractions, tau, and all six
signed observables, including separate matter and radiation components.

An exclusive `ATTEMPT.json` creation blocks simultaneous duplicate starts.
An existing PASS case is reused only if source/config identity and every
recorded artifact byte count/SHA-256 agree. A failed result, changed identity,
or interrupted directory stops the campaign. There is no automatic retry.
Closed atomic `trajectory_partial.npz` checkpoints preserve sample arrays and
completed GL stages. Exceptions preserve the last RHS trial. If `solve_ivp`
raises before returning, its internal accepted steps are unavailable; this
specific case preserves the last RHS trial and the thrown error without
claiming an accepted-step return.

The 180 s case limit covers solver work, diagnostic/quadrature evaluation and
output preservation. A cumulative 1200 s budget includes all existing case
receipt wall times, with failed receipts blocking restart. Limits are explicitly
cooperative. Process termination without a result leaves a nonempty attempt
directory that requires diagnosis before further execution.

## Remaining root work

1. Preserve/publish the implementation checkpoint and its exact preflight.
2. Run `python code/run.py --run` once within the frozen contract.
3. Read every admission and comparison result before plotting.
4. Run `python code/run.py --plot`, inspect plots, and commission fresh review.
5. Complete the source-bound physical interpretation and delivery receipts.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
