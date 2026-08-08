# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C2C1B1 / v0.67**.
- The scalar theory contract remains complete under the explicit
  hydrogen-frame isotropic-source axiom.
- Complete direct thermodynamic network nodes are locked at z~900,1100,1300,
  with the exact v0.50 3000 K anchor and fixed-topology inverse-temperature log
  interpolation.
- The original-HyRec virtual-spike source is source-identical; the paired
  one-photon line source is a positive theory-contract adapter and is not
  relabelled canonical source decomposition.
- Actual Bianchi characteristics supply directional face transport.  Full
  withheld-node validation now covers every pair and same-cell block.
- Next: **PR-05C2C1B2 canonical two-photon/Raman source census, measured
  preconditioner and multi-macro closure**, then PR-06 FLRW history parity.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_commit_range_whitespace.py
PYTHONPATH=src python scripts/check_imports.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR05C2C1B2_PRECONDITIONER_MULTI_MACRO_PLAN.md`](docs/PR05C2C1B2_PRECONDITIONER_MULTI_MACRO_PLAN.md).

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

GitHub `main` contains merged PR #24 at `2d777b1c7e56dcdf1e17feb1f728410ea0792df8`, tree
`0d2914566a3f211c2c3f324952b851a50da3a946`; PR-head CI run 81 completed successfully.  v0.67 is
reconstructed on the exact author v0.65 lineage, so exact remote-tree identity
is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a thin incremental and full recovery Git bundle. Create a
branch from fresh `origin/main`, cherry-pick only the receipt-listed v0.67
commits, rerun all gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.67 regeneration: `python scripts/run_pr05c2c1b1_source_adapter_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
