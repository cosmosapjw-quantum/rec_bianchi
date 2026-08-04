# Repository check and patch policy

This project cannot perform unattended background polling.  Instead, every
user-invoked bounded stage begins and ends with an explicit repository check.

## Stage-start protocol

```bash
python scripts/check_remote_state.py
cat state/REMOTE_CHECK_LATEST.json
```

When the remote is accessible, fetch it before scientific edits and compare
`origin/main` with the local base.  When it is inaccessible, do not infer that
it is empty or synchronized; use the last durable base in
`state/PATCH_BASE.json` and state that limitation.

## Stage-end protocol

1. Run fast and stage-specific tests.
2. Update the scientific ledger, project state and supersession ledger.
3. Run `python scripts/check_remote_state.py` and include its receipt in the stage commit.
4. Commit the bounded stage.
5. Export binary-safe patches:

   ```bash
   python scripts/export_patch_series.py
   ```

6. Provide the `.mbox`, binary `.patch`, receipt, and updated artifact ZIP.
7. Push only when fast-forward-safe. Otherwise use a feature branch and PR.

## Applying a delivered patch

Preferred:

```bash
git switch -c apply-rec-bianchi-patch
git am --3way rec_bianchi_<base>_to_<head>.mbox
pytest -q -m "not slow"
```

Fallback for a raw binary diff:

```bash
git switch -c apply-rec-bianchi-patch
git apply --3way --index rec_bianchi_<base>_to_<head>.patch
git commit
pytest -q -m "not slow"
```

Never apply a patch blindly if the receipt's base commit is absent or the
remote has diverged. Fetch first and retain the patch on a dedicated branch.
