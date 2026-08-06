# GitHub private-repository access and Git-bundle fallbacks

Repository: `cosmosapjw-quantum/rec_bianchi`

## Managed ChatGPT GitHub connector

The managed connector can inspect private repository state when the repository
is authorized in ChatGPT Settings. Connector visibility does not imply that the
current shell has a reusable Git credential. Treat connector read/write actions
and shell Git authentication as separate capabilities.

Current durable remote receipt:

```text
main: 47106fec89c176c3f3b91ed7e4ff198dea323968
tree: b1cc9c0959bd89418a4f24a51959c44bb163fe88
PR:   #14 merged
```

See `state/PR14_REMOTE_BASE_RECEIPT.json`.

## Preferred local integration path

Use the self-contained feature Git bundle on a branch created from freshly
fetched remote main:

```bash
git fetch origin --prune
git switch -c apply/v056-pr04c1b-c2 origin/main
git bundle verify /path/to/rec_bianchi_v056_feature.bundle
git fetch /path/to/rec_bianchi_v056_feature.bundle \
  refs/heads/delivery/v056:refs/remotes/v056/delivery
```

Read the ordered `feature_commits` list from
`rec_bianchi_v056_bundle_receipt.json` and cherry-pick it oldest to newest.
This preserves GitHub-side CI/toolchain overlays while applying only the v0.56
feature work.

Then require:

```bash
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_imports.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
python scripts/verify_repo.py --scientific
```

The local exact-author lineage does not have the same tree as the GitHub merge
tree. Do not reset or force-push remote main merely to match an author-tree hash.

## Full offline recovery

The full bundle is a disaster-recovery copy of the exact author repository and
all its refs:

```bash
git clone /path/to/rec_bianchi_v056_full.bundle rec_bianchi_v056_recovery
cd rec_bianchi_v056_recovery
git branch -a
git switch work/pr04c1b-c2-v056
python scripts/check_hyrec_binary_hash_policy.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

A full-bundle clone is not proof that the feature cherry-picks conflict-free
onto current remote main; the remote-based integration branch must still be
tested independently.

## Codex or another GitHub-authorized coding environment

Open the repository, create a branch from `origin/main`, fetch the delivered
feature bundle, cherry-pick the receipt's ordered commits, run every gate, and
open a PR. Never bypass the shared compiler-dependent binary-hash fixture and
never force-push shared `main`.

## HTTPS with a fine-grained personal access token

Use a repository-scoped fine-grained PAT only in the local shell. Do not paste
it into chat, commit it, or put it in a remote URL.

Minimum practical permissions:

- **Contents: read** for clone/fetch;
- **Contents: write** for feature-branch pushes;
- **Pull requests: write** only when automation creates or updates PRs;
- **Workflows: write** only when changing `.github/workflows/**`.

The repository scripts support an ephemeral `GIT_ASKPASS` helper:

```bash
export GITHUB_REC_BIANCHI_TOKEN='REPOSITORY_SCOPED_TOKEN'
python scripts/check_remote_state.py --require-access
./scripts/push_backup.sh
unset GITHUB_REC_BIANCHI_TOKEN
```

The token is never written to Git configuration or a remote URL.

## SSH, GitHub CLI, and GitHub App alternatives

A normal user SSH key is preferred when the shell can complete the actual
GitHub handshake. `gh auth login` is a practical interactive alternative. For
repeatable automation, a repository-scoped GitHub App installation token is
preferable to a long-lived personal token or a write-enabled deploy key.

## Backup branch naming

`scripts/push_backup.sh` no longer contains a historical v0.45 branch name. On
divergence it uses a UTC timestamped branch unless `BACKUP_BRANCH` is explicitly
set, and the PR title refers to the current durable stage.

## Diagnostic interpretation

`python scripts/check_remote_state.py` distinguishes successful remote access,
missing SSH/HTTPS authentication, DNS/network failure and local dirty state.
Remote inaccessibility is not evidence of synchronization. `git bundle verify`
checks bundle format and object connectivity; it does not replace scientific
regression after integration.
