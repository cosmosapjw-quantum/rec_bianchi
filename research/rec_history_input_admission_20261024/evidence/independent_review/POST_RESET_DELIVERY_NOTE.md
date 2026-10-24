# Post-reset delivery note — partial preservation disclosed

## Disposition and scope

**PASS_RECOVERY_AWARE_DELIVERY.** The new summary-derived coverage display and central preservation fields represent the recovered evidence without claiming that the original detailed raw files or original figures were fully preserved. Publication may proceed within the previously reviewed isolated REC evidence and two central-path scope, with this preservation limitation explicit and actual publication IDs read back by the root.

This is a delivery note appended to the already completed single scientific review. It does not reopen that review, repeat its probes, or replace the original review documents. Additional scientific review passes 0; scientific probes 0; IVPs 0; native runtime 0; primary/query/campaign/boundary reruns 0; external mutations by this reviewer 0. The original Physical HOLD, H5 INPUT_DEPENDENT_UNCALIBRATED, and REC-HISTORY PARTIAL remain unchanged.

## What is currently preserved, and what is not

The current `results/primary001/SUMMARY.json` has observed SHA256:

```text
6b21a45bb6c3ba2b2460c284e87ac224872226a0bb2aaa46ee4c948d05f8f84e
```

This equals the original identity supplied by the root and recorded in the recovery-aware report. Checking this file hash was a mechanical identity check, not a scientific recomputation.

The root's recovery report records restoration of 45 Stage A source/contract files with the original archive SHA256 and CRC checks. This note does not repeat those archive checks. The review texts and recorded three-probe output were reconstructed from the surviving conversation record, with the distinctions already recorded in `RECOVERY_RECORD.md` and `RECOVERY_RECORD.json`: `tiny_review.py` matches its original recorded SHA256; the other five restored review files do not have independently available original file hashes.

The following original detailed artifacts are **not recovered**:

- The 1,252 primary candidate-query rows.
- The original 313-query table.
- Original checks files and controller receipt files.
- The original and corrected two-panel PNG/PDF figures.

The already observed scientific results and old resource measurements remain historical recorded evidence. They must not be described as a newly rerun verification or as proof that the original detailed artifacts are currently available. This note does not reconstruct missing rows from a summary, infer per-query values, or reproduce a query-delay panel.

`REPORT_KO.md` explicitly states `PARTIAL_AFTER_WORKSPACE_RESET`, lists these missing artifacts, identifies the exact-recovered summary and context-restored review, and distinguishes the newly generated display from an original PNG byte recovery. `NEXT_INPUT_CONTRACT.md` repeats the missing rows/query/controller/figure limitation and preserves the no-replay boundary. These statements match the present delivery scope.

## New coverage display inspected

I directly opened and visually inspected:

`results/figures/history_input_coverage_recovered.png`

Observed PNG SHA256:

```text
c7d4063101e1339b302999ae6434864e39b7a004184aad6c3adebb37ffa96bfc
```

The title identifies it as a **recovered-summary display**. Its footer explicitly says that it is a new display from the recovered exact SUMMARY, that original figures and detailed query rows were not recovered, and that neither a scientific rerun nor query-delay reconstruction was performed.

The displayed h/2 U4, h/4 R3Q and h/4 smoke counts are 0/313; h/2 U5 is 313/313. Total retained column counts are 2,006, 1,519, 24 and 16,733 respectively. The solid eligible past prefix is visually separated from the muted dashed future archive, with a last-causal-knot tick and full-archive strict-endpoint marker distinguished. The target face and required retarded-source band remain displayed. This agrees with the prior reviewed 10,277-column U5 causal prefix and preserves the meaning of coverage as retained-cell availability only.

The title does not overlap the U4 bar. The caption keeps the physical-domain mismatch, prior HOLDs and open error calibration explicit, including target T0=2.728 K and candidate T0=2.7255 K. There is no claim that this single-panel figure is a restoration of the old two-panel image or a substitute for the unrecovered detailed query evidence.

## Current rendering receipt and historical totals

The actual current `execution/figure003/RESOURCE_RECEIPT.json` records:

| Field | Recorded value |
|---|---:|
| Command | `python render_coverage_recovered.py` |
| Return code | 0 |
| Timeout | false |
| Inclusive CPU | 1.688871296 s |
| Wall | 1.7208976399997482 s |
| Peak child RSS | 78,800 KiB |
| Numerical threads | 1 |
| CPU / wall caps | 4 s / 8 s |
| Address-space cap | 1 GiB |

The receipt identifies single-child CPU/address-space rlimits and wall timeout, and does not claim a live aggregate monitor. This is a new rendering of saved summary values, with new scientific cases 0.

The current `BUDGET_LEDGER.json` separately records historical pre-reset entries and the current figure003 receipt. It reports cumulative CPU **5.928528894 s** and execution wall **6.09275194699876 s**, within the original 20 s / 60 s allocation. The earlier central `execution` values of CPU 4.239657598 s and wall 4.371854306999012 s are the **historical pre-reset subtotal**, not the updated cumulative total including figure003. The root confirmed that the lower-tier final assembly will update central `execution` to the actual cumulative total together with the Git-ID substitution, preserving the pre-reset subtotal in a separate historical field. This is within the authorized mechanical assembly scope and does not need a new scientific review.

## Central preservation fields

I read the new `evidence_preservation` object in both the actual prepared DAG's ADM01 observation and the actual return sidecar, and read the updated combined diff. Both explicitly contain:

```json
{
  "status": "PARTIAL_AFTER_WORKSPACE_RESET",
  "primary_summary": "EXACT_SHA256_RECOVERY",
  "primary_detail_rows": "NOT_RECOVERED",
  "original_figures": "NOT_RECOVERED",
  "review": "CONTEXT_TEXT_RECOVERY",
  "no_scientific_rerun": true
}
```

This is a correct concise central representation of partial preservation. The more detailed report and this note identify the additional missing original query table, checks and controller files. The prior `PASS_SCOPED` and `material_blockers: 0` fields describe the already completed bounded admission determination; they are not a statement of complete post-reset raw preservation.

The updated diff keeps the changes within the previously reviewed REC-LINE02 / REC-HISTORY wrappers and return sidecar; it does not change scientific contracts, physical HOLDs, dependency policy, or the separately reserved HISTORY02 owner. The current-base identity and fixed handoff authority remain distinct. This note does not rerun the earlier 40-node / 17-edge comparison or revalidate unrelated source history.

## Final assembly boundary

The first read of `delivery/RECOVERY_STATUS.json` returned a missing-file status while the root was writing it concurrently. The root subsequently confirmed that this file and the current budget ledger had been completed. This is recorded as the root's assembly confirmation; no additional read or probe was performed. Updating the central cumulative total while retaining its historical subtotal, inserting actual commit/PR identifiers, and the root's final readback remain the agreed final mechanical assembly actions. They do not require another scientific probe or a new scientific review cycle.

Recovery-aware scoped publication is permitted with the limitations above retained. **A claim of complete preservation of the original detailed raw outputs, controller files, or old figures is not supported.** The root will supply and read back actual new Git/publication identities; this note does not fabricate or claim them.

All prior review documents are left untouched. This note records the current display/preservation inspection only.
