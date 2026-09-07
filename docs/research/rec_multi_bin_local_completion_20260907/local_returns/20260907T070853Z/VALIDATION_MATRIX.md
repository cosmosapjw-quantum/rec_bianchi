# Bounded scientific validation

| Cell | Status | Evidence and claim limit |
|---|---|---|
| Exact source/input and protected paths | PASS | IDENTITY_CHECK.json; exact execution tree, clean detached worktree, original source/tests/archive/workflows unchanged. |
| Six-file syntax/environment | PASS | syntax_environment.log and SYNTAX_EXIT_CODE.txt; not numerical acceptance. |
| Four left invariants, energy dependence, exact rank | PASS | New test_01; rational rank L=4 and V=3, witnesses base [0,1,16], hires [0,1,34]. Floating residuals are separate. |
| Count density chain | PASS | New test_02; beta derivative included, omission detector exceeds frozen 1e-6 threshold. |
| Right kernel and stationary tangents | PASS | New test_03 at one manufactured positive nonthermal state, two tables. No universal physical uniqueness or dynamics claim. |
| Remaining photon axes | PASS | New test_04; 16 comparisons, fixed binary64 tolerance plus 80/120 precision and step checks. |
| Saved CSV rendering and visual inspection | PASS | RENDER_RECEIPT.json plus VISUAL_REVIEW.json; both original generated PNGs opened, no source/test rerun. |
| Original seven groups | REUSED | Fixed PR79 structured Git readback only; no numerical reexecution in this work. |
| Historical original artifact and PNG audit | NOT_TESTED | Raw byte intake, full member manifest and original PNG visual review remain incomplete. |
| Physical source, provider, full repository, grid refinement | NOT_TESTED | Out of scope; physical flags remain false. |

Raw PROCESS/RESULT/RENDER_RECEIPT visual_audit fields remain their original
NOT_PERFORMED values. The later human-visible image inspection is a separate
VISUAL_REVIEW.json; no historical record has been rewritten.

Independent read-only scientific/source review: PASS; INDEPENDENT_REVIEW.md. No additional numerical replay.
