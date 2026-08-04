# GitHub backup and durability policy

- `origin`: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`.
- Exact historical ZIPs are canonical immutable releases under `archive/bundles/`.
- Expanded copies under `archive/expanded/` are for browsing and search.
- The root `src/`, `tests/`, and `data/` are the reconstructed active workspace; provenance is in `state/ACTIVE_WORKSPACE_PROVENANCE.json`.
- After every bounded scientific stage:
  1. add the new artifact directory and ZIP;
  2. update `state/PROJECT_STATE.json` and supersession ledger;
  3. run `python scripts/verify_repo.py --all` and `pytest -q`;
  4. commit without rewriting shared history;
  5. push to `main` only when fast-forward safe, otherwise to a dated feature/backup branch and open a PR;
  6. create a fresh Git bundle and SHA-256 receipt.
- Never treat a transcript-only statement as completion.
- Never commit credentials, tokens, private keys, or generated credential helpers.
- This repository contains unpublished research artifacts and should remain private unless the owner explicitly changes the publication policy.


## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Full scientific regression: `python scripts/verify_repo.py --scientific` (can require many tens of minutes).
- Original stage bundles retain the per-stage full-test receipts.


## GitHub authentication fallback

The preferred transport is the user's existing SSH setup. A sandbox without an `ssh` binary may use an exact-repository fine-grained token via `GITHUB_REC_BIANCHI_TOKEN`; `scripts/push_backup.sh` passes it through a temporary `GIT_ASKPASS` helper and never stores it in Git configuration or a URL.


## Repository check and patch export

At the start and end of every bounded user-invoked stage run `python scripts/check_remote_state.py`. Remote inaccessibility must be recorded, not interpreted as synchronization. After committing, run `python scripts/export_patch_series.py` and deliver the mbox, binary diff and receipt. This is an explicit per-stage protocol, not an unattended background job.
