# rec_bianchi — Full Bianchi–HyRec durable research backup

This public repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C2C1B2B1B / v0.71**.
- The v0.70 generic pseudo-transient backward-error unit floor is superseded:
  it falsely accepted `O(1e-18)` occupations under harmless variable rescaling.
- The z~1100 Bianchi-II physical residual, analytic JVP, problem-specific gross
  and photon-number hard gates, and shifted matrix-free operator are connected.
- The canonical parent is correctly rejected; no physical macro convergence is
  claimed.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain available.
- Next: **one safeguarded matrix-free z~1100 Bianchi-II macro**, then measured
  preconditioner selection and only afterwards the 9x4 lane expansion.

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

GitHub `main` contains merged PR #25 at `3d429b70715c3a16bd7d27f0d78accef2c249843`, tree
`9ef976724fe20ae9e8bc855ccc76d74f1b09c598`; PR-head CI run 84 completed successfully.

The preferred v0.68 delivery is based on the exact author-v0.66 endpoint and includes an integration compatibility commit. Create a branch from fresh `origin/main`, cherry-pick only the receipt-listed v0.68-from-v0.66 commits, rerun all gates, and never rewrite shared history. The older cumulative v0.65 route is retained only for disaster recovery and must not be replayed onto remote main.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.68 regeneration: `python scripts/run_pr05c2c1b2a_two_photon_raman_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
