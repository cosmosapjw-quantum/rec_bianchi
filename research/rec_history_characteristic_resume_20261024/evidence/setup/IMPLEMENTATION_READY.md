# READY_FOR_S1_FREEZE — C5 source and exact case plan

No scientific primary, independent probe, native runtime, IVP, dense RHS or old replay executed. No figure rendered. AST/compile syntax checks only; no numerical dependencies imported for those checks. NPZ zip headers were inspected to select named arrays, without evaluating history. The case-plan serializer performs metadata construction only.

## Files

- code/characteristic_adapter.py: positive-rate crossing, log-domain direction, general JVP (including axis off-axis amplification), native-Wien correction, strict-prefix fixed-cell degree<=2 history and unchanged vendor boundary/JVP/ledger composition, conditional error map.
- code/independent_reference.py: independent mpmath 80dps equations; root bisection 300 iterations, normalized tangent curves and fixed a priori central step 1e-25. No adapter/vendor imports.
- code/verify_primary.py: one predeclared case stream; raw JSONL flush per row, first failure exception/condition/traceback preserved, fail-and-stop without automatic repair, final summary. Actual h4 eight interior queries only; no actual angular spectrum or M2 inference. Deliberate photon-clock defect is detected by photon-clock/fixed-cell identity, rather than assuming tiny scalar amplitudes exceed a unit-scaled threshold.
- code/freeze_case_plan.py and inputs/CASE_PLAN.json: 127 unique case IDs, 48/12/16/12/8/16/12/3 groups. Extreme Wien controls predeclare relative 8e-12 and 5e-324 absolute underflow floor. Root/tangent scales follow frozen contract. Includes exact axes, zero components, Lambda0, near-positive-boundary rates, axis off-axis tangent and Lambda0 tangent.
- code/run_bounded.py: source/input/contract snapshots, command/environment, stdout/stderr, one-child resource limits and process-group wall timeout, postexit inclusive child getrusage CPU, RSS highwater, source unchanged check. No live aggregate monitoring claim.
- code/render_saved_rows.py: two PNG/PDF figures from saved primary rows only; no adapter/oracle/NPZ import or recomputation. Figure folder creation refuses overwrite.

## Immutable copies

INPUT_COPY_RECEIPT.json records exact Stage A NPZ, old frozen contract/progress/budget/Wolfram, three donor provenance modules and ADM01 target CSV. Vendor Git blob remains 1aa7f134c332bc4596372df18c7c47306260ecfc. SURVEY_COPY_RECEIPT.json records all16 explicitly selected nonprivate summaries; the corrected backup JSON filename is BACKUP_LIBRARY_SURVEY.json. Root-owned new Wolfram source/result were not edited.

## Commands prepared, not executed

From unit root after S1 publication/backups and root GO:

```
python code/run_bounded.py --cpu 16 --wall 45 primary001 python code/verify_primary.py --output results/primary001
```

Later saved-row rendering must use the figure/repair reserve, after controller review of primary:

```
python code/run_bounded.py --cpu 4 --wall 15 figures001 python code/render_saved_rows.py
```

New total allocation 30CPU/90wall, primary16/45, review6/15, figure+repair8/30. Historical allocations/spend stay separate. Actual first primary outcome is unknown. First failure stops and returns to root, with no repair absent root decision. Parent REC-HISTORY PARTIAL, actual h4 ADM01 coverage0/313 and INPUT_DEPENDENT_UNCALIBRATED remain.

Executor request: gpt-6.1-sol. Actual independently exposed runtime model metadata: unavailable; no lower-tier model observation is claimed from the requested label.
