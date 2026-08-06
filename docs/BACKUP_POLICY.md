# GitHub backup and durability policy

- `origin`: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`.
- Exact historical ZIPs are canonical immutable scientific releases under
  `archive/bundles/`.
- Expanded copies under `archive/expanded/` are for browsing and search.
- The root `src/`, `tests/`, and `data/` are the reconstructed active workspace;
  provenance is in `state/ACTIVE_WORKSPACE_PROVENANCE.json`.
- This repository contains unpublished research artifacts and remains private
  unless the owner explicitly changes the publication policy.

## Per-stage durable protocol

After every bounded scientific stage:

1. add the immutable artifact directory, ZIP and runtime data;
2. update `state/PROJECT_STATE.json`, `state/BUNDLE_INDEX.json`, the
   supersession ledger, roadmap and handoff;
3. run the policy scanner, quick verifier, fast tests, targeted stage tests and
   full scientific regression;
4. commit without rewriting shared history;
5. run `python scripts/check_remote_state.py` or record an equivalent managed
   connector receipt; remote inaccessibility is never synchronization evidence;
6. create and verify both Git-bundle deliveries with
   `scripts/export_git_bundle_delivery.py`;
7. push only when fast-forward-safe, otherwise use a feature branch and PR;
8. seal SHA-256, bundle-head and test receipts.

Never treat transcript-only statements as completion. Never commit credentials,
tokens, private keys or generated credential helpers.

## Git-bundle delivery policy

The canonical patch delivery is no longer an `.mbox` or raw binary diff.
Each stage supplies:

- a **self-contained feature bundle** containing a dedicated delivery ref at
  the target commit and all reachable objects;
- an ordered feature-commit list in the receipt for cherry-picking onto freshly
  fetched `origin/main`;
- a **full recovery bundle** containing all local refs;
- `git bundle verify` output, SHA-256 and file size for both bundles.

The self-contained feature bundle is intentionally conservative: the remote
main tree can contain GitHub-side CI/toolchain overlays that are absent from the
exact author lineage. Consumers fetch the bundle, inspect the ordered commits
and cherry-pick them onto a remote-based integration branch rather than force
remote history to equal the author tree.

## Test tiers

- Fast recovery/CI: `pytest -q -m "not slow"`.
- Repository verification: `python scripts/verify_repo.py --all`.
- Full scientific regression: `python scripts/verify_repo.py --scientific`.
- Current-stage regeneration:
  `python scripts/run_pr04c1b_c2_coupled_interface_stage.py`.

## GitHub authentication fallback

The preferred transport is the owner's existing SSH setup. A sandbox without
an authorized SSH transport may use an exact-repository fine-grained token via
`GITHUB_REC_BIANCHI_TOKEN`; `scripts/push_backup.sh` passes it through a
temporary `GIT_ASKPASS` helper and never stores it in Git configuration or a
remote URL.
