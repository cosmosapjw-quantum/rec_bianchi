# REC-LOCAL-01 bootstrap recovery

`REC-LOCAL-01` reached its context/restart/component assertions, but its
required bootstrap intake stopped on three stale R2 manifest entries. The same
forensic pass found one stale manifest entry in the PR #39 followthrough
payload. Neither mismatch is a continuation-identity or scientific-integrity
failure; both are deterministic packaging failures and remain fail-closed.

This package repairs provenance without rewriting either source preimage:

1. the PR #39 followthrough manifest is rebound on the new stacked branch to
   the bytes already tracked in Git;
2. the historical R2 package at commit `47e19df...` is checked through an
   exact-preimage sidecar manifest;
3. the user-local receipt must be hashed and admitted from the preserved
   worktree before `REC-LOCAL-02` starts.

The sidecar is not a scientific promotion. Current claim remains
`NO_PASS_REC_PHYSICAL_SPLIT`.

Run the package-only intake from a clean checkout of this recovery branch:

```bash
bash research/continuation_20260830/bootstrap_recovery_20260830/FETCH_AND_VALIDATE.sh \
  --repo /absolute/path/to/clean/rec_bianchi
```

Then follow `LOCAL_CODEX_PROMPT.md`. Do not clean, reset, stash or otherwise
mutate the preserved `REC-LOCAL-01` worktree.

Receipt admission is an administrative provenance gate, not a rerun of
`REC-LOCAL-01` and not a physical-result promotion. Use
`validate_local01_admission.py` only after copying and hashing the actual local
receipt and its five sibling evidence files.
