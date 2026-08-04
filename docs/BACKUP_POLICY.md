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
