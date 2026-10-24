# REC-HISTORY-REFINE01 — twenty-stage evidence map

These ten theory stages and ten coding stages reference one primary comparison and one saved-data figure run. They are not twenty experiments. The root decision is COMPLETE_SCOPED_STORED_HISTORY_ENVELOPE, limited to the stored interpolants; physical admission ceilings remain.

## Checkpoints and provider acknowledgement

| Checkpoint | Local observed state | Actual provider ACK status | Evidence |
|---|---|---|---|
| S0 | ORIGINAL_FROZEN_ARCHIVE_RETAINED_VERIFIED | GIT_PUBLISHED_DRAFT_BRANCH_AND_DROPBOX_COMPLETED_ACK; DRIVE_FINAL_S3_ONLY_NOT_ATTEMPTED | delivery/PUBLICATION_STATE.json; delivery/S0_DROPBOX_ACK.json |
| S1 | ORIGINAL_FROZEN_ARCHIVE_RETAINED_VERIFIED | GIT_PUBLISHED_DRAFT_BRANCH_AND_DROPBOX_COMPLETED_ACK; DRIVE_FINAL_S3_ONLY_NOT_ATTEMPTED | delivery/PUBLICATION_STATE.json; delivery/S1_DROPBOX_ACK.json |
| S2 | ORIGINAL_FROZEN_ARCHIVE_RETAINED_VERIFIED | GIT_PUBLISHED_DRAFT_BRANCH_AND_DROPBOX_COMPLETED_ACK; DRIVE_FINAL_S3_ONLY_NOT_ATTEMPTED | delivery/PUBLICATION_STATE.json; delivery/S2_DROPBOX_ACK.json |
| S3 | ORIGINAL_IMMUTABLE_S3_ARCHIVE_RETAINED_18OF20_SNAPSHOT | GIT_PUBLISHED_DRAFT_BRANCH_AND_DROPBOX_COMPLETED_ACK; ADDITIONAL_DRIVE_EXPLICIT_UNKNOWN | delivery/S3_PROVIDER_COMPACT_RECEIPT.json; delivery/S3_GITHUB_COMPACT_RECEIPT.json; delivery/S3_DRIVE_STATUS.json |

All S0/S1/S2/S3 checkpoints have actual Git publication/readback and completed Dropbox acknowledgements. PR133 and centralPR225 remain open drafts. The additional S3 Drive upload has no completed ACK; server creation/cancellation remain UNKNOWN and no dual-provider completion is claimed. The original S1 code/input is unchanged; two packaging metadata additions were published at S2.

## Theory and coding stages

| Stage | Work | Observed state | Last checkpoint | Evidence |
|---|---|---|---|---|
| R1 | Contract and source identity | EVIDENCE_RETAINED | S0 | `FROZEN_CONTRACT.md`; `inputs/CASE_PLAN.json`; `provenance/survey/rec_sources/CANDIDATE_SOURCE_MANIFEST.json` |
| R2 | Repository backup and literature survey | EVIDENCE_RETAINED | S2 | `SURVEY_SYNTHESIS_KO.md`; `provenance/LITERATURE_INTAKE.json`; `provenance/survey/cross_repo/INTAKE_CLOSED_AT_566f242b_KO.md`; `provenance/survey/backups/FINDINGS.md` |
| R3 | Frozen claim boundary | EVIDENCE_RETAINED | S0 | `FROZEN_CONTRACT.md`; `inputs/CASE_PLAN.json` |
| R4 | Nodal and midpoint-detail decomposition choice | EVIDENCE_RETAINED | S0 | `THEORY.md`; `FROZEN_CONTRACT.md` |
| R5 | Constructive derivation and exact supremum | EVIDENCE_RETAINED | S0 | `THEORY.md` |
| R6 | Symbolic identities and fresh independent review | COMPLETE_SCOPED_INDEPENDENT_REVIEW_PASS | S2 | `provenance/WOLFRAM_SYMBOLIC_CHECK.json`; `evidence/independent_review/FINAL_REVIEW.md`; `evidence/independent_review/FINAL_REVIEW.json` |
| R7 | Single actual retained-history comparison | EXECUTED_ONCE_ARITHMETIC_CHECKS_PASS | S2 | `results/primary001/SUMMARY.json`; `results/primary001/RAW_COMPARISON.npz`; `execution/primary001/RESOURCE_RECEIPT.json` |
| R8 | Astra scientific decision | COMPLETE_ROOT_DECISION_SCOPED_STORED_ENVELOPE | S2 | `CLAIM_GATES.json` |
| R9 | Reusable conditional theory and API | IMPLEMENTED_SCOPED_REFERENCE_UNAVAILABLE | S2 | `THEORY.md`; `code/envelope.py`; `results/primary001/SUMMARY.json` |
| R10 | Final report handoff and delivery | COMPLETE_FINAL_REPORT_HANDOFF_GIT_AND_DROPBOX_DELIVERY | S3 | `REPORT_KO.md`; `NEXT_THREAD_HANDOFF_KO.md`; `delivery/PUBLICATION_STATE.json`; `delivery/S3_GITHUB_COMPACT_RECEIPT.json` |
| C1 | Frozen baseline and implementation scope | EVIDENCE_RETAINED | S0 | `FROZEN_CONTRACT.md`; `inputs/CASE_PLAN.json` |
| C2 | Source mapping and query API | IMPLEMENTED | S1 | `provenance/survey/rec_sources/SOURCE_GUARD_CLARIFICATION.md`; `code/envelope.py`; `code/analyze_pair.py` |
| C3 | Exact decomposition and interval algorithm | IMPLEMENTED | S1 | `THEORY.md`; `code/envelope.py` |
| C4 | Limits case plan environment and commands | FROZEN_BEFORE_PRIMARY | S1 | `inputs/CASE_PLAN.json`; `ENVIRONMENT.json`; `evidence/setup/S1_SYNTAX_ENVIRONMENT_COMMANDS.json` |
| C5 | Implementation | AST_PARSE_PASS_AND_SINGLE_RUN_RETAINED | S1 | `code/envelope.py`; `code/analyze_pair.py`; `code/run_bounded.py`; `code/render_results.py`; `evidence/pre_repair_s1/REPAIR_NOTE.md` |
| C6 | Meaningful synthetic controls | OBSERVED_ALL_PASS | S2 | `results/primary001/SYNTHETIC_CONTROLS.json` |
| C7 | Source masks direct/decomposed and Fraction checks | OBSERVED_ALL_PASS | S2 | `results/primary001/FRACTION_ORACLE.json`; `results/primary001/PER_CHANNEL.csv`; `evidence/report_facts.json` |
| C8 | Raw results resource ledger and reproduction | RETAINED_AND_FIRST_PNGS_ACTUALLY_INSPECTED | S2 | `results/primary001/RAW_COMPARISON.npz`; `BUDGET_LEDGER.json`; `execution/primary001/COMMAND.json`; `execution/primary001/SOURCE_INPUT_SNAPSHOT.json`; `execution/figures001/RESOURCE_RECEIPT.json`; `results/figures/VISUAL_INSPECTION.json` |
| C9 | Fresh independent code/numerical review | COMPLETE_SCOPED_INDEPENDENT_REVIEW_PASS | S2 | `evidence/independent_review/FINAL_REVIEW.md`; `evidence/independent_review/FINAL_REVIEW.json` |
| C10 | Final reproducible delivery and handoff | COMPLETE_FINAL_REPORT_HANDOFF_GIT_AND_DROPBOX_DELIVERY | S3 | `REPORT_KO.md`; `NEXT_THREAD_HANDOFF_KO.md`; `delivery/PUBLICATION_STATE.json`; `delivery/S3_GITHUB_COMPACT_RECEIPT.json` |

**Workflow completion:20/20.** R10/C10 close against the actual S3 Git and Dropbox acknowledgements plus the final report and handoff. The immutable S3 archive retains its truthful18/20 freeze-time snapshot; this D1 supplement records the subsequent closure.

## Admission and pending delivery

R6/C9 have the actual fresh independent review files; R8 has the actual root CLAIM_GATES.json decision. R10/C10 are complete with the actual report, handoff, S3 Git readback and Dropbox completed ACK. Additional Drive remains explicitly unresolved. Final physical-reference uncertainty/bounds, curvature, order and goal-percent remain null. Original-target coverage remains0/313, parentREC-HISTORY remainsPARTIAL, H5 remainsINPUT_DEPENDENT_UNCALIBRATED, and physical HOLD/productionNOT_APPROVED/REI_activation=false remain.

Late central566f and current Library-delta intake are retained under provenance/survey/cross_repo with prior pinned files unchanged. Both first PNGs were actually viewed by executor and root, with root layout/readability PASS; no presentation repair was needed.
