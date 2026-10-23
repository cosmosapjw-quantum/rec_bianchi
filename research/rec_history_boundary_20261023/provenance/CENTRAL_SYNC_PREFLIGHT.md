# Central REC status synchronization proposal

This subtask performed read-only GitHub intake and prepared local proposed files.
No central GitHub mutation, scientific execution, new review, probe, or node was
performed. Parent controller owns final publication and review outcome binding.

## Exact observed central identity

- Repository: cosmosapjw-quantum/rei_bianchi.
- Branch: research/orchestration-sandbox-20261022.
- Actual HEAD: 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17.
- Actual tree: f4bb481007415b7ae2c07250c25c3cb1aa4481f6.
- PR222: open, draft, unmerged; base research/rei-coupled-isotope-contract-20261022.
- Root AGENTS blob: 429a5a13ee75b1222bc50627f8d5973d01dd21c4.
- No applicable nested AGENTS in research/ or orchestration_longterm_20261023/
  or assembly/ was present in the inspected direct trees.
- assembly/DAG.json blob: 38a901d0a92d14d3821471bf9f170828a770cae4.
- thermal/rec_bianchi_LONGTERM_CONTRACTS.json blob:
  60d63277bb5274993d520e9c9b14cce4d354ea23.
  SHA256 c116f64c33d966fa81a74e13657735044a6f20a2365b00a3ee79338c0297e44f;
  no trailing newline in the original authority file, preserved in baseline/.
- Fixed assembly/HANDOFF_rec_bianchi_KO.md blob:
  1ad650f3593a49e755eca45e5037b64849635610.
- README.md blob: 08a2b3829d4a415f56cea01b59603006fe2bb02f.

The exact baseline copies and proposed files are under baseline/ and proposed/.
Only three paths are proposed in the central task subtree:

1. assembly/DAG.json — change REC-LINE02 plan_status and add observed_completion;
   change REC-HISTORY plan_status to PARTIAL and add observed_completion with
   REC-HISTORY-01 primary PASS608/608 and independent review pending.
2. assembly/REC_HISTORY_STATUS_UPDATE.json — add separate delivery/science/budget/
   claim-gate observations with actual local evidence SHA256, root source-binding
   fields and historical provider verification levels.
3. README.md — add one short current-observation pointer.

Original authority files, embedded documents and node contracts remain unchanged.
The handoff at the user-fixed SHA is immutable; the same historical handoff file
need not be rewritten in the new branch. No new top-level DAG node is introduced:
REC-HISTORY-01 is the named bounded child in the parent's observation. Thus the
40 source-plan nodes and17 conditional integration edges remain unchanged.

## Why use the existing observed_completion pattern

DAG already uses it for HE-X1. Its author contract says current_unit_selected,
while plan_status and observed_completion contain COMPLETE_SCOPED and the actual
science commit. Keeping contract versus later observation distinct preserves
both the fixed source and current progress.

The current assemble.py computes plan_status mostly from historical selection
statuses and drops existing observed_completion fields. Blind regeneration
would regress HE-X1 to OWNER_IN_PROGRESS and erase its observed result. The
current render_handoffs.py rewrites every repository handoff. Neither needs to
run for this targeted observation update. Existing schema permits the additive
wrapper; existing validation checks immutable author equality and graph
structure, not the new scientific result. No validator success is claimed by
this preparation.

## Publication binding still owned by root

The sidecar intentionally has publication_source.commit/branch/pr=null and a
pending-source status: REC-HISTORY primary results were read locally, not from
an invented remote commit. Before central publication, root must bind the actual
REC source/results/delivery commit and PR. If independent review has completed,
update only the subunit's observed review/admission fields to the actual receipt;
keep parent PARTIAL, actual-history calibration INPUT_DEPENDENT_UNCALIBRATED,
and Bianchi directional propagation OPEN. Include the final cumulative budget,
not only the observed primary charge. Original old allocations remain untouched.

All names ending pending here are snapshots of the preparation time, not claims
about what the controller may complete subsequently.

## Parallel changes and lease

Central HEAD had no movement from the fixed pin. However PR222 received a new
VigilODE PR80 observation comment at2026-10-23T15:16:48Z:
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222#issuecomment-6368220382 .
It reports a separate additive overlay and says no central files were overwritten.
Do not integrate or overwrite that distinct owner observation in the REC patch.
Immediately before publication reread the central branch and target path blobs.
A branch shift requires reading/preserving the delta before selecting a new
expected SHA. The root plan is a separate branch from this observed base and a
Draft PR; no merge or activation is part of this proposal.

The initial encoded branches API URL returned400; git/ref/heads/... succeeded.
A whole-repository recursive tree call returned Transport closed; smaller direct
root/research/unit trees succeeded. These are lookup failures, not science/runtime
blockers and do not justify any execution restriction.
