# rec_bianchi — Full Bianchi–HyRec durable research backup

This repository is the durable backup and active reconstruction workspace for the scalar Full Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3 formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics, and angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-04B1 / v0.52**.
- Status: the owner-supplied `HyRec_Oct2012.zip` is byte-locked and safety-audited; the original source builds without source edits under GNU C, reproduces a complete baseline history, and agrees with the prior pinned native sparse-block registry. The original C diffusion rates, full 313-state real/virtual solve, dense solve, and structured Schur solve pass independent parity checks.
- Scientific boundary: the native reversible variable is a **dimensionless virtual-level proxy**, not yet the physical photon finite-volume measure of PR-04A. Direct substitution of native `Aup/Adn` or a completed `Tvv` block is therefore forbidden. **PR-01 through PR-03 are complete; PR-04 remains in progress.**
- Provenance boundary: the archive bytes are durable owner-supplied input whose filename and package metadata correspond to the October-2012 release, but independent byte equality with a fresh official-server download was not verified in this runtime.
- Next bounded stage: **PR-04B2 physical native-measure and full-trajectory FLRW closure**.
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
- `archive/inputs/`: byte-locked user-supplied primitive sources and host code.
- `state/`: machine-readable current state, inventory, provenance, receipts, and supersessions.
- `docs/`: handoff, setup, roadmap, GitHub access, backup, and recovery instructions.
- `scripts/`: scientific-stage generation, C harnesses, verification, status, patch, bundle, and safe-push helpers.

## Remote sync policy

The owner performs GitHub fetch/push/PR operations from the local Ubuntu workstation. This execution environment does not claim a remote push. Every stage therefore exports an exact Git bundle and binary-safe incremental/cumulative patches. Fetch remote `main`, create a feature branch, apply the appropriate patch or import the bundle, rerun tests, then push and open a PR. Never rewrite shared history. See [`docs/GITHUB_PRIVATE_REPO_ACCESS.md`](docs/GITHUB_PRIVATE_REPO_ACCESS.md).

## Publication and license

This repository contains unpublished research and a user-supplied primitive code archive. No public license is asserted here. Keep the repository private unless the owner explicitly changes that policy.

## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full repository verifier with fast tests: `python scripts/verify_repo.py --all`.
- Full scientific regression: `python scripts/verify_repo.py --scientific`.
- PR-04B1 regeneration: `python scripts/run_pr04b_original_hyrec_native_stage.py`.
- Original stage bundles retain per-stage scientific receipts.

## Repository checks and patches

Each bounded stage runs `python scripts/check_remote_state.py` and exports binary-safe patches. See [`docs/REPO_CHECK_PATCH_POLICY.md`](docs/REPO_CHECK_PATCH_POLICY.md).
