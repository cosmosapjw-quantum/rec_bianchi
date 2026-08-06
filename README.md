# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05B2 / v0.60**.
- The canonical October-2012 original-HyRec accepted radiation history is now
  source-locked as an immutable `eta=ln(a)` state with 7,489 accepted slices.
- Exactly 313 characteristic queries per snapshot reproduce
  `hydrogen.c::fplus_from_fminus` at `z~1300,1100,900`.
- Append/reject/rollback/restart are transaction-safe; future endpoints and
  discrete stencil switches fail closed.
- Analytic history JVP, source algebraic/electron/outgoing parity, photon-number
  and redshift-energy-work ledgers, and the Bianchi local-state firewall pass.
- The scalar history replacement contract is complete, but no owner has yet
  been swapped and Sobolev/`A1s`/`Tvv` terms remain canonical. PR-05 remains in
  progress.
- Next stage: **PR-05B3 scalar history ownership swap and coupled accepted-step
  residual**.

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
[`docs/PR05B3_ATOMIC_OWNERSHIP_SWAP_PLAN.md`](docs/PR05B3_ATOMIC_OWNERSHIP_SWAP_PLAN.md).

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

GitHub `main` contains merged PR #18 at
`27a4e097baf83fbca2b1befd5b780edbf460f020`, tree
`5ee5af26f21f25a7878d308acf4934f4f99598a1`; PR-head CI run 57 completed
successfully. v0.60 is developed on the exact author v0.59 lineage, so exact
remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed v0.60 commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.60 regeneration: `python scripts/run_pr05b2_causal_history_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
