# rec_bianchi — Full Bianchi–HyRec durable research backup

This repository is the durable backup and active reconstruction workspace for the scalar Full Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3 formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics, and angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-02 / v0.49**.
- Status: the nonlinear stimulated Bose collision network is connected to runtime `BackgroundSnapshot` states on the locked positive-weight `L=12/20/24` angular lanes. Exact JVP, log-variable implicit positivity, BE, photon-number, free-energy and same-event four-force gates pass. **PR-01 and PR-02 are complete.**
- Next stage: **PR-03 full scalar COM–KHW amplitude**.
- Completion target: verified scalar solver through the 12-PR roadmap.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md), [`state/PROJECT_STATE.json`](state/PROJECT_STATE.json), and [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

## Layout

- `src/`, `tests/`, `data/`: active implementation and regression data.
- `archive/bundles/`: exact immutable stage ZIPs.
- `archive/expanded/`: browseable expanded stage artifacts.
- `archive/inputs/`: user-supplied primitive Bianchi host code.
- `state/`: machine-readable current state, inventory, provenance, and supersessions.
- `docs/`: handoff, setup, roadmap, GitHub access, backup, and recovery instructions.
- `scripts/`: scientific-stage generation, verification, status, patch, bundle, and safe-push helpers.

## Remote sync status

The owner reports that v0.47 was expanded and merged into the private GitHub `main`. This runtime has no exposed GitHub connector function and no working Git SSH/HTTPS route, so the exact remote ref/tree could not be re-read. v0.49 is therefore delivered with cumulative v0.47-to-v0.49 and incremental v0.48-to-v0.49 binary-safe patches plus a standalone full bundle. Fetch remote `main`, apply on a feature branch, and open a PR; do not rewrite shared history. See [`docs/GITHUB_PRIVATE_REPO_ACCESS.md`](docs/GITHUB_PRIVATE_REPO_ACCESS.md).

## Publication and license

This repository contains unpublished research and a user-supplied primitive code archive. No public license is asserted here. Keep the repository private unless the owner explicitly changes that policy.

## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full scientific regression: `python scripts/verify_repo.py --scientific`.
- PR-02 production receipt: `python scripts/run_pr02_nonlinear_bose_runtime_stage.py`.
- Original stage bundles retain per-stage full-test receipts.

## Repository checks and patches

Each bounded stage runs `python scripts/check_remote_state.py` and exports binary-safe patches with `python scripts/export_patch_series.py`. See [`docs/REPO_CHECK_PATCH_POLICY.md`](docs/REPO_CHECK_PATCH_POLICY.md).
