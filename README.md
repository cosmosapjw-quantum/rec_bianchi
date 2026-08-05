# rec_bianchi — Full Bianchi–HyRec durable research backup

This repository is the durable backup and active reconstruction workspace for the scalar Full Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3 formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics, and angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-03 / v0.50**.
- Status: the provisional unresolved scalar `2p` pole+crossed lane has been replaced in production by a scalar elastic `1s -> 1s` COM–KHW construction containing the seagull, both time orderings, the hydrogen bound spectrum, the positive continuum measure, and all scalar interference terms in the locked Ly-alpha window. The complete 35-state network was regenerated through `ell=24`; PR-01 frame adaptation and the PR-02 nonlinear/JVP/implicit APIs remain unchanged. **PR-01 through PR-03 are complete.**
- Next stage: **PR-04 HYREC common-measure moment projection**.
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
- `state/`: machine-readable current state, inventory, provenance, receipts, and supersessions.
- `docs/`: handoff, setup, roadmap, GitHub access, backup, and recovery instructions.
- `scripts/`: scientific-stage generation, verification, status, patch, bundle, and safe-push helpers.

## Remote sync status

The owner reports that v0.47 was expanded and merged into the private GitHub `main`. This runtime has no exposed writable GitHub connector and no working Git SSH/HTTPS route, so the exact remote ref/tree remains unverified. v0.50 is therefore delivered with a cumulative v0.47-to-v0.50 patch, an incremental v0.49-to-v0.50 patch, and a standalone full bundle. Fetch remote `main`, apply on a feature branch, and open a PR; never rewrite shared history. See [`docs/GITHUB_PRIVATE_REPO_ACCESS.md`](docs/GITHUB_PRIVATE_REPO_ACCESS.md).

## Publication and license

This repository contains unpublished research and a user-supplied primitive code archive. No public license is asserted here. Keep the repository private unless the owner explicitly changes that policy.

## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full scientific regression: `python scripts/verify_repo.py --scientific`.
- PR-03 production regeneration: `python scripts/run_pr03_full_scalar_khw_stage.py`.
- PR-03 audit-only reuse of the stored network: `python scripts/run_pr03_full_scalar_khw_stage.py --reuse-network` (still performs the expensive selected-pair and runtime audits).
- Original stage bundles retain per-stage full-test receipts.

## Repository checks and patches

Each bounded stage runs `python scripts/check_remote_state.py` and exports binary-safe patches with `python scripts/export_patch_series.py`. See [`docs/REPO_CHECK_PATCH_POLICY.md`](docs/REPO_CHECK_PATCH_POLICY.md).
