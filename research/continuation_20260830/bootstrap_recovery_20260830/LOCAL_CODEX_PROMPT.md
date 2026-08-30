# Local Codex continuation prompt

Continue `cosmosapjw-quantum/rec_bianchi` from the stacked recovery branch
`agent/fix/rec-local01-bootstrap-rebind-20260830-r1`.

The original worktree
`/home/cosmosapjw/worktrees/rec-local01-canonical-context-20260830` is preserved
evidence. Do not clean, reset, restore, checkout over, stash, rebase, amend,
squash, force-push, delete or otherwise normalize it. Read it before creating
any new worktree. Inventory all dirty tracked paths and the six reported
evidence/receipt files with path, size, mtime and SHA-256.

Fetch the recovery branch and
`agent/plans/rec-split-domain-bootstrap-20260829-r1` by exact ref. Read
`REMOTE_PUBLICATION.json` on the recovery branch and create a new isolated
worktree at its immutable payload commit. Confirm its tree and package manifest
before continuing. Never substitute `main`, PR #34, PR #36 or PR #39 HEAD.

Run:

```bash
bash research/continuation_20260830/bootstrap_recovery_20260830/FETCH_AND_VALIDATE.sh \
  --repo "$PWD"
```

This must establish only package intake and the exact-preimage R2 sidecar
rebind. It must not upgrade the science claim.

Next, copy the `REC_LOCAL_01_CANONICAL_CONTEXT_INTEGRATION.json` receipt and its
five sibling mutation-evidence files into a new evidence directory. Verify
pre-copy and post-copy SHA-256 equality. Inspect the receipt itself, fill every
field in `REC_LOCAL_01_ADMISSION_TEMPLATE.json`, bind the receipt and worktree
hashes, and add a validator/test for that concrete schema. Stop if any count,
version, path, HEAD/tree, mutation failure mode or pre-restore rejection differs
from the receipt. Do not inherit the user report as evidence.

Validate the completed record with:

```bash
python3 research/continuation_20260830/bootstrap_recovery_20260830/validate_local01_admission.py \
  --admission /absolute/path/to/REC_LOCAL_01_ADMISSION.json \
  --receipt /absolute/path/to/REC_LOCAL_01_CANONICAL_CONTEXT_INTEGRATION.json \
  --evidence-root /absolute/path/to/copied/evidence \
  --inventory /absolute/path/to/preservation_inventory.txt \
  --source-worktree /home/cosmosapjw/worktrees/rec-local01-canonical-context-20260830
```

This is administrative admission of the already executed local run, not a
request to rerun it.

Only after admission, execute
`REC-LOCAL-02_SOURCE_BOUND_PHYSICAL_DEPOSITION_AND_FULL_JVP` exactly as bounded
in `IMPLEMENTATION_PLAN.md` and the parent `CODEX_HANDOFF.md`. Use the actual
source-defined 35x26 physical COM representation, prove positive feasibility,
and include every moving-map derivative. Freeze the eight tracked input hashes
listed in the plan. Reconcile the two Doppler-width definitions explicitly and
stop on the absent source-defined 26-direction face reconstruction rather than
promoting an isotropic or barycentric surrogate. Preserve
`NO_PASS_REC_PHYSICAL_SPLIT` unless all original physical split requirements
close; bounded success may be only
`PASS_REC_ISOTROPIC_PHYSICAL_REFERENCE_ONLY`.

After actual execution, run one PHYS-MATH and one PHYS-MATH-CODE review. Use at
most one reproduced P0/P1 repair and one focused rereview. Commit ordinary,
push one new stacked draft PR against the recovery branch, read back exact
head/tree/paths/evidence and stop. Do not merge or mark ready.
