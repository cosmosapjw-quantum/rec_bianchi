# Sandbox and fresh-machine setup

## Online setup with SSH

```bash
git clone git@github.com:cosmosapjw-quantum/rec_bianchi.git
cd rec_bianchi
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py --quick
pytest -q
```

The user's established GitHub convention is SSH authentication as `cosmosapjw-quantum`. Do not place a token in the remote URL.

## Offline setup from the Git bundle

```bash
git clone rec_bianchi_backup_2026-08-04.bundle rec_bianchi
cd rec_bianchi
./scripts/bootstrap_sandbox.sh --offline
python scripts/verify_repo.py --quick
pytest -q
```

## Environment

The bootstrap creates `.venv` when possible. For an offline sandbox, NumPy, SciPy, and pytest must already be installed in the base image. The reference runtime is recorded in `environment/current-runtime.txt`.

Useful environment variables:

```bash
export REC_BIANCHI_ROOT="$PWD"
export BIANCHI_PRIMITIVE_SOURCE="$PWD/archive/inputs/bianchibianchic2"
export JAX_ENABLE_X64=True
```

## Scientific tools

- Wolfram: run the `verify_*.wl` files in stage artifacts for symbolic identities.
- Precise Special Functions: use as an independent high-precision real-axis Gamma/Bessel/2F1 reference, particularly in PR-03.
- Web/SciSpace: re-check current and niche primary literature when the next stage depends on it.

## Recovery check

```bash
python scripts/status.py
python scripts/verify_repo.py --all
```

The first files to read in a new thread are `HANDOFF_PROMPT.md`, `state/PROJECT_STATE.json`, and `docs/CURRENT_STATE.md`.


## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full scientific regression: `python scripts/verify_repo.py --scientific` (can require many tens of minutes).
- Original stage bundles retain the per-stage full-test receipts.


## GitHub authentication fallback

The preferred transport is the user's existing SSH setup. A sandbox without an `ssh` binary may use an exact-repository fine-grained token via `GITHUB_REC_BIANCHI_TOKEN`; `scripts/push_backup.sh` passes it through a temporary `GIT_ASKPASS` helper and never stores it in Git configuration or a URL.
