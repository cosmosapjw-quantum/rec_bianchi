# rec_bianchi — Full Bianchi–HyRec durable research backup

This repository is the durable backup and active reconstruction workspace for the scalar Full Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3 formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics, and angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-01B1-B3B3B0 / v0.46**.
- Status: interior and near-exterior red/blue interface blocks pass through ell=24; direct far jumps beyond |x|=10.25 and nonlinear adaptive exterior action are open.
- Next stage: **PR-01B1-B3B3B1**.
- Completion target: verified scalar solver through the 12-PR roadmap.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/verify_repo.py --quick
pytest -q
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md), [`state/PROJECT_STATE.json`](state/PROJECT_STATE.json), and [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

## Layout

- `src/`, `tests/`, `data/`: reconstructed active PR-01 workspace.
- `archive/bundles/`: exact immutable stage ZIPs.
- `archive/expanded/`: browseable expanded stage artifacts.
- `archive/inputs/`: user-supplied primitive Bianchi host code.
- `state/`: machine-readable current state, inventory, provenance, and supersessions.
- `docs/`: handoff, setup, roadmap, backup, and recovery instructions.
- `scripts/`: verification, status, bundle, and safe push helpers.

## Remote sync status

The local repository is configured for `git@github.com:cosmosapjw-quantum/rec_bianchi.git`. The current execution sandbox had no outbound GitHub route and no writable GitHub connector, so the remote ref/tree could not be verified here. A verified Git bundle and safe push script are provided; do not claim remote sync until `scripts/push_backup.sh` completes and records the remote tree.

## Publication and license

This repository contains unpublished research and a user-supplied primitive code archive. No public license is asserted here. Keep the repository private unless the owner explicitly changes that policy.


## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full scientific regression: `python scripts/verify_repo.py --scientific` (can require many tens of minutes).
- Original stage bundles retain the per-stage full-test receipts.

## Repository checks and patches

Each bounded stage runs `python scripts/check_remote_state.py` and exports binary-safe patches with `python scripts/export_patch_series.py`. See [`docs/REPO_CHECK_PATCH_POLICY.md`](docs/REPO_CHECK_PATCH_POLICY.md).
