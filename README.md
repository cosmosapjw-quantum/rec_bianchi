# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C1 / v0.62**.
- Original-HyRec accepted radiation history remains on its exact canonical
  `DLNA=8.49e-5` macro grid.
- Adaptive backward-Euler full and both half-step trials, rejection and event restart occur only
  inside one canonical macro interval; every trial passes the hard residual/positivity gates and a successful macro endpoint commits exactly one history slice.
- Source-conditioned rank-one DAE lanes near `z~1300,1100,900` pass positivity,
  backward-error, algebraic and restart gates.
- Deterministic Bianchi-shaped event inputs test rollback/restart semantics only;
  full COM-KHW/interface coupling and source-derived boundary speeds remain PR-05C2.
- v0.62 was resealed from durable v0.61 bytes after an attachment-registration interruption; transcript-only v0.62 claims are superseded by the committed recovery receipts.
- The recovery verifier now checks committed feature-range whitespace as well as staged and unstaged source changes; only verbatim `state/*.log` evidence is excluded.
- Next stage: **PR-05C2 full coupled adaptive trajectory**.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_commit_range_whitespace.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR05C2_FULL_COUPLED_ADAPTIVE_PLAN.md`](docs/PR05C2_FULL_COUPLED_ADAPTIVE_PLAN.md).

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

GitHub `main` contains merged PR #20 at
`796eabf6339b9a13355ccc61907a5314b9cd9196`, tree
`f6f7ef5f36917d6722e741aed705a6b4c7273955`; PR-head CI run 65 completed
successfully. v0.62 is reconstructed on the exact author v0.61 lineage, so exact
remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed v0.62 commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.62 regeneration: `python scripts/run_pr05c1_adaptive_macro_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
