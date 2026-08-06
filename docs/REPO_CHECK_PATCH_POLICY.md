# Repository check and Git-bundle delivery policy

This project cannot perform unattended background polling. Every user-invoked
bounded stage begins and ends with an explicit repository check.

## Stage-start protocol

```bash
python scripts/check_remote_state.py
cat state/REMOTE_CHECK_LATEST.json
```

When the remote is accessible, fetch it before scientific edits and compare
`origin/main` with the exact local author base. When it is inaccessible, do not
infer that it is empty or synchronized; use the last durable connector/base
receipt and state that limitation.

## Stage-end protocol

1. Run policy, fast, stage-specific and scientific tests.
2. Update the scientific ledger, project state, bundle index, roadmap and
   supersession ledger.
3. Record the exact remote commit/tree observed at the end of the stage.
4. Commit the bounded stage and receipt seal without force-push.
5. Export verified Git bundles:

   ```bash
   python scripts/export_git_bundle_delivery.py \
     --repo . \
     --base <exclusive-feature-base> \
     --ref HEAD \
     --version v056 \
     --output-dir /path/to/delivery
   ```

6. Deliver the feature bundle, full bundle, JSON receipt, SHA-256 list and
   immutable scientific artifact ZIP.
7. Rehearse a fresh clone from the full bundle and a fetch from the feature
   bundle before making any completion claim.

## Applying the self-contained feature bundle

Start from current remote main:

```bash
git fetch origin --prune
git switch -c apply/v056-pr04c1b-c2 origin/main
git bundle verify /path/to/rec_bianchi_v056_feature.bundle
git fetch /path/to/rec_bianchi_v056_feature.bundle \
  refs/heads/delivery/v056:refs/remotes/v056/delivery
```

Read `feature_commits` from the bundle receipt. Cherry-pick them in the listed
oldest-to-newest order:

```bash
git cherry-pick <commit-1> <commit-2> ... <commit-N>
```

Then run:

```bash
python scripts/check_hyrec_binary_hash_policy.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
python scripts/verify_repo.py --scientific
```

The delivery ref includes the exact author tree for inspection and recovery,
but the target integration tree is the result of applying the ordered feature
commits to freshly fetched remote main. Do not reset remote main to the author
tree merely to obtain an exact tree hash.

## Full recovery bundle

A new independent clone can be made from the full bundle:

```bash
git clone /path/to/rec_bianchi_v056_full.bundle rec_bianchi_v056_recovery
```

After cloning, select the recorded feature branch/tag and run all verification
commands. `git bundle verify` proves bundle format/object connectivity; it does
not substitute for scientific tests after integration.

Never apply a delivery blindly when the receipt, SHA-256 or ordered commit list
is missing. Never force-push shared history.
