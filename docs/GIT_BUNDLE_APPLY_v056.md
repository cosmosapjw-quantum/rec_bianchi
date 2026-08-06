# Applying the v0.56 Git-bundle delivery

## Files

```text
rec_bianchi_v056_feature.bundle
rec_bianchi_v056_full.bundle
rec_bianchi_v056_bundle_receipt.json
```

The feature bundle is self-contained and exposes
`refs/heads/delivery/v056`. The JSON receipt records the exact target, the
exclusive local feature base, SHA-256 values and the ordered feature commits.
The full bundle carries all author-repository refs for disaster recovery.

## Integrate onto GitHub main

The verified remote base at stage start is:

```text
commit 47106fec89c176c3f3b91ed7e4ff198dea323968
tree   b1cc9c0959bd89418a4f24a51959c44bb163fe88
PR     #14
```

Create a branch from fresh remote main:

```bash
git fetch origin --prune
git switch -c apply/v056-pr04c1b-c2 origin/main
```

Verify and fetch the feature bundle:

```bash
git bundle verify /path/to/rec_bianchi_v056_feature.bundle
git ls-remote /path/to/rec_bianchi_v056_feature.bundle
git fetch /path/to/rec_bianchi_v056_feature.bundle \
  refs/heads/delivery/v056:refs/remotes/v056/delivery
```

Inspect the exact author result:

```bash
git log --oneline --decorate refs/remotes/v056/delivery
```

Read `feature_commits` from the JSON receipt and cherry-pick those commits in
the listed oldest-to-newest order. Do not cherry-pick the local v0.55 shared
gate commit: PR #14 already contains the equivalent remote fix.

```bash
git cherry-pick <feature-commit-1> <feature-commit-2> ... <feature-commit-N>
```

Resolve any conflict in favour of preserving the remote CI/toolchain overlay
unless the v0.56 commit intentionally changes the same scientific behavior.

## Verification after cherry-pick

```bash
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_imports.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
python scripts/verify_repo.py --scientific

git diff --check origin/main...HEAD
git fsck --full
git status --short
```

The final working tree must be clean before push. The compiler-dependent HyRec
executable hash may be asserted only when
`binary_hash_is_meaningful` is true. The numerical-output hash remains
unconditional.

## Push and PR

```bash
git push -u origin apply/v056-pr04c1b-c2
```

Open a PR into `main`. Do not force-push shared history.

## Full recovery clone

```bash
git bundle verify /path/to/rec_bianchi_v056_full.bundle
git clone /path/to/rec_bianchi_v056_full.bundle rec_bianchi_v056_recovery
cd rec_bianchi_v056_recovery
git branch -a
git switch work/pr04c1b-c2-v056
python scripts/check_hyrec_binary_hash_policy.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

The full author bundle is not the GitHub merge tree. It is a recovery source and
comparison oracle. The remote-based cherry-pick branch is the integration
result that must pass CI.
