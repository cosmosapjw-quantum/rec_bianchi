# rec_bianchi — Full Bianchi–HyRec durable research backup

This repository is the durable backup and active reconstruction workspace for the scalar Full Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3 formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics, and angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-04A / v0.51**.
- Status: the exact durable HYREC-2 FULL source/convention registry is locked, and the v0.50 scalar elastic COM–KHW event measure has been projected onto a positive 17-cell ordinary-frequency common measure through `Gamma,M1,...,M4`. The scalar Bose, BE-null, number, free-energy, same-event energy, analytic-JVP, implicit-positivity, and geometry-firewall gates pass. **PR-01 through PR-03 are complete; PR-04 is in progress.**
- Open source gate: the official October-2012 original-HyRec archive bytes and SHA-256 were not available in this runtime. Native original-HyRec primitive/stencil parity is therefore not claimed.
- Next bounded stage: **PR-04B original-HyRec archive and native primitive common-measure parity**.
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

## Remote sync policy

The owner performs GitHub fetch/push/PR operations from the local Ubuntu workstation. This execution environment does not claim a remote push. Every stage therefore exports an exact Git bundle and binary-safe incremental/cumulative patches. Fetch remote `main`, create a feature branch, apply the appropriate patch or import the bundle, rerun tests, then push and open a PR. Never rewrite shared history. See [`docs/GITHUB_PRIVATE_REPO_ACCESS.md`](docs/GITHUB_PRIVATE_REPO_ACCESS.md).

## Publication and license

This repository contains unpublished research and a user-supplied primitive code archive. No public license is asserted here. Keep the repository private unless the owner explicitly changes that policy.

## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full repository verifier with fast tests: `python scripts/verify_repo.py --all`.
- Full scientific regression: `python scripts/verify_repo.py --scientific`.
- PR-04A production regeneration: `python scripts/run_pr04a_hyrec_common_measure_stage.py --workers 12`.
- Original stage bundles retain per-stage scientific receipts.

## Repository checks and patches

Each bounded stage runs `python scripts/check_remote_state.py` and exports binary-safe patches with `python scripts/export_patch_series.py`. See [`docs/REPO_CHECK_PATCH_POLICY.md`](docs/REPO_CHECK_PATCH_POLICY.md).
