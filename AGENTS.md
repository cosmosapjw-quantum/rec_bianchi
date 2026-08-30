# Repository agent map

This file is a map, not a complete process manual.

1. Read `docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md` before changing a
   scientific gate, receipt, manifest, fixture, or claim.
2. Use the current root `HANDOFF_PROMPT.md` as the continuation locator and
   scientific stop boundary.
3. Preserve immutable evidence and every unrelated dirty/untracked checkout.
   Work from an exact commit in an isolated worktree.
4. Compile each observed P0/P1 into one focused test, invariant, or explicit
   blocker. Do not add overlapping gates or recursive reviews.
5. Run the smallest dependency cone that can falsify the changed behavior,
   followed by at most one independent read-only review. Merge and ready
   transitions require separate authorization.

Current terminal claim:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

`NO_PASS_REC_PHYSICAL_SPLIT`
