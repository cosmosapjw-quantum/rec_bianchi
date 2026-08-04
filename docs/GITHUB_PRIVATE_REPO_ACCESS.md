# GitHub private-repository access and fallbacks

Repository: `cosmosapjw-quantum/rec_bianchi`

## ChatGPT GitHub app — read access

1. In ChatGPT open **Settings → Apps → GitHub**.
2. Select **Connect** or open the gear menu, then choose **Configure repositories on GitHub**.
3. Under repository access, select `cosmosapjw-quantum/rec_bianchi` and save.
4. Private or newly authorized repositories may take several minutes to appear.
5. In GitHub's own search box, run:

   ```text
   repo:cosmosapjw-quantum/rec_bianchi import
   ```

   This requests indexing for connector search. Allow another several minutes.
6. App availability can differ among standard Chat, Deep Research, Agent and Codex runtimes.

The ChatGPT GitHub app may be exposed only as a read/search connector. Do not assume it supplies a Git credential or permits pushes from the current shell.

## Codex — preferred write path

Create or open a Codex GitHub environment for this repository, authorize the repository, and ask Codex to import the delivered v0.49 bundle or apply the appropriate patch on a feature branch. Before merge, require:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py --require-access
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Never force-push shared `main`.

## HTTPS with a fine-grained personal access token

Use a repository-scoped fine-grained PAT in the local shell only. Do not paste it into chat, commit it, or put it in a remote URL.

Minimum practical permissions:

- **Contents: read** for clone/fetch;
- **Contents: write** for feature-branch pushes;
- **Pull requests: write** only when automation must create or update PRs;
- **Workflows: write** only when changing `.github/workflows/**`.

The repository check script supports an ephemeral `GIT_ASKPASS` helper:

```bash
export GITHUB_REC_BIANCHI_TOKEN='REPOSITORY_SCOPED_TOKEN'
python scripts/check_remote_state.py --require-access
./scripts/push_backup.sh
unset GITHUB_REC_BIANCHI_TOKEN
```

## GitHub App installation token — preferred automation credential

For repeatable automation, install a dedicated GitHub App only on this repository and grant the smallest permissions needed. HTTP Git access requires **Contents** permission; workflow-file changes additionally require **Workflows** permission. Prefer short-lived installation tokens over a long-lived personal token.

## SSH or deploy key

A normal user SSH key works when `ssh` and outbound access are available. A deploy key is repository-specific and may be read-only or read/write. For finer permission control and auditable automation, prefer a GitHub App over a write-enabled deploy key.

## Offline full-bundle fallback

When the runtime has no connector, DNS, SSH executable, or token:

```bash
git clone rec_bianchi_v049_full.bundle rec_bianchi
cd rec_bianchi
git switch work/pr02-nonlinear-bose-production-v049
./scripts/bootstrap_sandbox.sh --offline
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

## Patch selection

Two binary-safe patch lanes are exported:

- **cumulative v0.47 → v0.49** for a checkout containing the exact local v0.47 base commit `ced72558437c8d24dce0cb855259b5216549604d`;
- **incremental v0.48 → v0.49** for a checkout containing the exact local v0.48 commit `91f772c3275d318af9cc4f2cacb9a71b0c227f48`.

Apply only after fetching remote `main` and creating a feature branch:

```bash
git switch -c apply/v049-pr02
git am --3way rec_bianchi_<base>_to_<head>.mbox
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

If the remote used squash merges and contains neither exact base commit, use the standalone full bundle as the comparison source or try the binary patch with `git apply --3way --index` on a feature branch. Resolve conflicts explicitly and open a PR. Do not rewrite remote history merely to match local commit IDs.

## Diagnostic interpretation

`python scripts/check_remote_state.py` distinguishes successful remote access and exact `main` SHA from missing `ssh`, HTTPS/DNS failure, absent token, and local dirty state. A user report that v0.47 was merged establishes only a scientific-content base; it does not establish the remote merge commit SHA or ancestry. Patch receipts therefore retain exact local bases and the remote-verification uncertainty.
