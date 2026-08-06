# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05B1 / v0.59**.
- The canonical original-HyRec local system is now source-locked as a rank-one
  semi-explicit DAE in `eta=ln(a)`: `x_e` is differential and the 2s/2p plus
  311 virtual departures are algebraic.
- Radiation time dependence is carried by causal accepted-step
  `Dfminus`/Lyman/average-radiation histories, not by an invented local mass for
  every virtual spike.
- A constructive no-go shows that finite virtual-spike masses inferred from
  centre spacing are non-unique: two admissible support choices differ by a
  factor of two and share the zero-width algebraic limit.
- Source residual, shifted IJacobian, positive bounded backward Euler, restart,
  causality and Bianchi firewall gates pass at `z~1300,1100,900`.
- No compressed native term has been removed. PR-05 remains in progress.
- Next stage: **PR-05B2 source-identical causal characteristic-history block**.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR05B2_CAUSAL_HISTORY_BLOCK_PLAN.md`](docs/PR05B2_CAUSAL_HISTORY_BLOCK_PLAN.md).

## Canonical source

`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, is
the owner-attested unique official-site October-2012 release. Internal
May/October metadata variations are intrinsic to that archive.

## Layout

- `src/`, `tests/`, `data/`: active implementation and regression data.
- `archive/bundles/`: immutable stage ZIPs.
- `archive/expanded/`: browsable stage artifacts and verifiers.
- `archive/inputs/`: canonical sources, host code and validated harnesses.
- `state/`: machine-readable state, provenance, recovery and receipts.
- `docs/`: current state, roadmap, research plans and handoff material.
- `scripts/`: stage generation, C instrumentation, verification and Git-bundle delivery tools.

## Remote and delivery policy

GitHub `main` contains merged PR #17 at
`29e4e8e22a5bf5efaf5d8e43c490ae16bf057440`, tree
`4a409c18f57c25c744722d70f46a26225ecfac4a`; PR-head CI run 55 completed
successfully. v0.59 is developed on the exact author v0.58 lineage, so exact
remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed feature commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.59 regeneration: `python scripts/run_pr05b1_source_identifiable_dae_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
