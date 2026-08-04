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
6. If GitHub is available in Deep Research or Agent mode but absent in standard Chat, use the experience where the app is exposed. App availability can differ by ChatGPT experience.

The ChatGPT GitHub app is a **read/search connector**. It does not push commits or pull requests. Use Codex or one of the authenticated Git methods below for writes.

## Codex — preferred write path

Create or open a Codex GitHub environment for this repository, authorize the repository, and ask Codex to apply the exported patch on a feature branch and open a PR. Before merge, require:

```bash
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Never force-push shared `main`.

## HTTPS with a fine-grained personal access token

Use a repository-scoped fine-grained PAT in the local shell only. Do not paste it into chat, commit it, or put it in a remote URL.

Minimum practical permissions:

- **Contents: read** for clone/fetch;
- **Contents: write** for branch pushes;
- **Pull requests: write** only when automation must create/update PRs;
- **Workflows: write** only when changing `.github/workflows/**`.

This repository's scripts use an ephemeral `GIT_ASKPASS` helper:

```bash
export GITHUB_REC_BIANCHI_TOKEN='REPOSITORY_SCOPED_TOKEN'
python scripts/check_remote_state.py --require-access
./scripts/push_backup.sh
unset GITHUB_REC_BIANCHI_TOKEN
```

## GitHub App installation token — preferred automation credential

For repeatable automation, install a dedicated GitHub App only on this repository. Grant the smallest permissions needed. HTTP Git access requires the repository **Contents** permission; workflow-file modification additionally requires **Workflows** permission. Use short-lived installation tokens rather than a long-lived personal token.

## SSH or deploy key

A normal user SSH key works when `ssh` and outbound port access are available. A deploy key is repository-specific and can be read-only or read/write. For finer permission control and auditable automation, prefer a GitHub App over a write-enabled deploy key.

## Offline/bundle fallback

When the runtime has no connector, DNS, SSH executable, or token:

```bash
git clone rec_bianchi_v048_full.bundle rec_bianchi
cd rec_bianchi
git switch work/pr01c-background-frame-adapter-v048
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

For an existing v0.47 checkout, apply the v0.48 mbox on a feature branch:

```bash
git switch -c apply/v048-pr01c
git am --3way rec_bianchi_<base>_to_<head>.mbox
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

If the remote used a squash merge and does not contain the exact local v0.47 commit, use the binary patch with `git apply --3way`, or compare/import the standalone v0.48 bundle on a new branch. Do not rewrite remote history merely to match local commit IDs.

## Diagnostic interpretation

`python scripts/check_remote_state.py` distinguishes:

- successful remote access and exact remote `main` SHA;
- missing `ssh` executable;
- HTTPS/DNS failure;
- absent token;
- local dirty state.

A user report that v0.47 was merged establishes the scientific content base, but it does not establish the remote merge commit SHA. Patch receipts therefore record both the exact local base and the remote-verification uncertainty.
