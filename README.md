# rec_bianchi — Full Bianchi–HyRec durable research backup

This repository is the durable backup and active reconstruction workspace for
the scalar Full Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds,
tetrad and 1+3 formalism, finite tilt, nonlinear large shear, HYREC-grade atomic
physics, and angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-04B2B / v0.54**.
- Status: a direct positive original-HyRec-to-17-cell equality is rejected by a sharp support bound and an exact identifiability audit. The full and diffusion native measures cannot preserve `M0,M2` on `|x|<=4.25`; after support restriction, five moments leave a 12-dimensional null space for seventeen target masses.
- Scientific boundary: this is an informative no-go, not a solver failure. The native transport and COM–KHW collision representations remain distinct. **PR-01 through PR-03 are complete; PR-04 remains in progress.**
- Provenance: `HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, is the owner-attested unique official-site October-2012 archive. Internal May/October metadata variations are intrinsic to that canonical release.
- Next bounded stage: **PR-04C split-domain conservative number/energy exchange and multi-snapshot closure**.
- Completion target: verified scalar solver through the 12-PR roadmap.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json), and
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

## Layout

- `src/`, `tests/`, `data/`: active implementation and regression data.
- `archive/bundles/`: exact immutable stage ZIPs.
- `archive/expanded/`: browseable expanded stage artifacts.
- `archive/inputs/`: byte-locked canonical sources, host code, and validated research/coding harnesses.
- `state/`: machine-readable current state, inventory, provenance, receipts, and supersessions.
- `docs/`: handoff, current state, roadmap, bounded research plans, GitHub access, backup, and recovery instructions.
- `scripts/`: scientific-stage generation, C instrumentation, verification, status, patch, bundle, and safe-push helpers.

## Remote sync policy

The owner performs live GitHub fetch/push/PR operations from the local Ubuntu
workstation. This execution environment does not claim a remote push. Every
stage exports an exact Git bundle and binary-safe incremental/remote-milestone/
cumulative patches. Fetch remote `main`, create a feature branch, apply the
appropriate route, rerun tests, then push and open a PR. Never rewrite shared
history. See
[`docs/GITHUB_PRIVATE_REPO_ACCESS.md`](docs/GITHUB_PRIVATE_REPO_ACCESS.md).

## Publication and license

This repository contains unpublished research and canonical third-party source
input. No public license is asserted here. Keep the repository private unless
the owner explicitly changes that policy.

## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full repository verifier with fast tests: `python scripts/verify_repo.py --all`.
- Full scientific regression: `python scripts/verify_repo.py --scientific`.
- PR-04B2B regeneration: `python scripts/run_pr04b2b_partition_nogo_stage.py`.
- Original stage bundles retain per-stage scientific receipts.

## Repository checks and patches

Each bounded stage runs `python scripts/check_remote_state.py` when available
and exports binary-safe patches. See
[`docs/REPO_CHECK_PATCH_POLICY.md`](docs/REPO_CHECK_PATCH_POLICY.md).
