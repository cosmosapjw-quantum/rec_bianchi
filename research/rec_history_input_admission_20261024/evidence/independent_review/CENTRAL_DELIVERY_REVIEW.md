# Central delivery-preservation appendix

## Disposition

**PASS_SCOPED_DELIVERY; material findings 0.** The prepared central patch preserves the scientific authority/contract graph and accurately records the bounded REC-HISTORY-ADM01 result. The existing `FINAL_REVIEW.md` and `REVIEW.json` remain unchanged. This appendix is the delivery part of the same finite review, with **additional scientific probes 0, numerical reruns 0, and external mutations 0**.

The reviewed scope may proceed to publication under the root's existing authorization: the isolated REC admission evidence and the two central paths listed below. The actual new REC commit and PR must replace the preparation placeholders once, and the root may confirm those concrete IDs and the two changed paths by readback. That mechanical substitution does not need another scientific review or probe. This disposition does not admit an error bound, reset prior HOLDs, merge a PR, activate REI, or authorize further integration work.

## Distinct identities

| Role | Exact identity |
|---|---|
| Prepared central patch base | `rei_bianchi@68420637a9ab54ada92afd786c5733bc0764b8c9` |
| Fixed user handoff authority | `rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17` |
| Before DAG Git blob from the frozen patch contract | `87deeb6c65497b8dd5cdf6dbef397293f7d0c492` |
| Before DAG observed SHA256 | `10d1b731e594d2875025ef0a0d2068bd30a319adad93fc2478e34ec11d1b53df` |
| Prepared after DAG observed SHA256 | `690501be7475a57b8a9b568742c350a1310a26f09d19513ba3c9e57b9955c9ed` |
| Prepared combined diff observed SHA256 | `6972fa2badd7b1d0aceaf5b4b6b5ab2b68834990ae4eff33d5451c6078f32ea4` |

These hashes identify the reviewed local preparation. Actual publication and live remote HEAD were not observed by this read-only appendix. The intended publication uses the stated current-base identity; the historical handoff is neither overwritten nor represented as that current base.

## Exact central mutation surface

Only the following repository paths occur in the prepared patch:

1. `research/orchestration_longterm_20261023/assembly/DAG.json`
2. `research/orchestration_longterm_20261023/assembly/returns/REC_HISTORY_ADM01_20261024.json`

In the DAG, only wrapper keys `plan_status` and newly added `observations` change on `REC-LINE02` and `REC-HISTORY`.

`REC-LINE02` becomes wrapper `COMPLETE_SCOPED`, with recovered final-receipt identity and explicit reuse of 194 primary checks, 202 rank queries and six historical review probes. Its source-owned original contract, including its historical status wording and source pin, is unchanged.

`REC-HISTORY` becomes wrapper `PARTIAL`. Its observations distinguish the reused HISTORY01 boundary completion, the newly completed finite input-admission determination, and the separate reserved HISTORY02 owner. Its original contract remains unchanged.

Direct read-only comparison of the actual before/after JSON files returned:

| Preservation property | Observed result |
|---|---|
| Node count | 40 → 40 |
| Node IDs and order | Identical |
| Integration edges | 17 → 17 |
| Entire integration object | Identical |
| All top-level values except the node list | Identical |
| All 40 embedded original contracts | Identical |
| Changed nodes | Exactly `REC-LINE02`, `REC-HISTORY` |
| Changed keys on either selected node | Exactly `plan_status`, `observations` |
| Other 38 complete node objects | Identical |
| Authority pointers and all local/external/conditional dependencies | Preserved |
| HE-X1 wrapper and `observed_completion` | Preserved |

The standalone authority files and historical `COMPLETION_EQUIVALENCE.json` are absent from the mutation surface. The supplied `PRESERVATION_CHECK.json` agrees with the actual diff and the direct JSON inspection. No assembler or central renderer was run.

## Scientific summary and accounting consistency

I read the complete `REPORT_KO.md`, `CLAIM_GATES.json` and `BUDGET_LEDGER.json` and compared their summarized claims with the already completed scientific review. They consistently state:

- One primary invocation, 386 assertions and 1,252 candidate-query rows; one independent review with three probes.
- Fixed target z=1099.9986525171403; required source z=1100.092189396162 through 1133.87330719964.
- U5 retained-cell coverage 313/313 with 10,277 face-causal columns; the other three candidates each cover 0/313.
- Source and energy-grid identity are separate from physical equivalence. Actual caller/capsule binding and the independent U5 event-state T0 reconstruction are both recorded.
- Target T0=2.728 K versus actual candidate T0=2.7255 K; target nH0=0.18745798773143102 m^-3 versus candidate nH0=0.18971712352134673 m^-3.
- Physical reference remains unadmitted; endpoint/reference/curvature bounds remain null; H5 remains INPUT_DEPENDENT_UNCALIBRATED and REC-HISTORY remains PARTIAL.
- Physical HOLD, U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED, REI_activation=false, and first_failed_REI_raw HISTORICAL_LOCAL_ONLY remain intact.
- HISTORY02 ownership remains reserved. No universal absence/no-go, new IVP, native runtime, dense solve, old campaign replay or old boundary replay is asserted.

The four recorded execution entries sum to CPU **4.239657598 s** and execution wall **4.371854306999012 s**, under the frozen 20 s / 60 s allocation. Peak recorded RSS is 107,564 KiB; numerical threads are one. The old HISTORY01 allocation remains closed and separate. Source reads, documentation, provider work and this delivery inspection are explicitly outside the scientific-execution sum. No live aggregate monitor is claimed.

`material_blockers: 0` and `PASS_SCOPED` refer to correctness of this finite admission determination. Nearby explicit physical HOLD and null uncertainty fields prevent this from being represented as calibrated physical-reference admission.

## Publication placeholders and finite closeout

Both the prepared ADM01 wrapper observation and the new return sidecar contain `evidence_commit: null`, `evidence_pr: null`, and `publication: PENDING`. This is an accurate preparation state and does not fabricate publication. The next permitted mechanical change is to replace these with the actual isolated REC publication identities and observed publication state, preserving all reviewed scientific content and graph structure. Root readback suffices for that substitution.

No material defect was found. There is no request for another review cycle. This appendix does not itself perform or claim external publication.

## Actual inspection record

- Read `CENTRAL_PATCH_CONTRACT.md`, `CENTRAL_PATCH.diff`, `PRESERVATION_CHECK.json`, the before/after DAG, the actual return sidecar, copied central `AGENTS.md`, authority list, and historical completion-equivalence record.
- Read the three new REC summary/accounting files above.
- Ran read-only `diff -u before/.../DAG.json after/.../DAG.json`: exit 1, the normal status indicating the expected two changed wrapper regions. This is not a failure.
- Ran read-only inline Python JSON inspection: exit 0, returning the exact preservation properties listed above. This was metadata/delivery inspection, not a new scientific probe.
- Read-only `cat`, `sed`, `rg`, and `sha256sum` calls exited 0. No central file was modified by the reviewer. Only this appendix and its JSON companion were written.

The unchanged skill context is PhysMath Research Loop 1.3.0, selected-stage and finite-review rules, typed identity, separation of result/provenance/packaging validity, and concrete scope preservation. The copied central AGENTS policy was also read; no additional speculative security or governance gate was introduced.
