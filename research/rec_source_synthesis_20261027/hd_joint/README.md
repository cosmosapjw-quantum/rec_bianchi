# HD joint thermal diagnostic — prepared C5–C8 implementation

Scientific authority and acceptance belong to the parent under `../CODING_CONTRACT.md` (SHA256 `7dd2e930cad8bf919a9dbbf90a0426f76ea00eaf6eabf16f3d677b8726d1364e`). This subtree adds a callable diagnostic and one bounded source/reference/control/figure pass. It does not qualify a production line, change the source gate, mix colliders, extrapolate temperatures, or execute historical suites.

## Equation to code

| Frozen object | Implementation |
|---|---|
| Exact SI constants and decimal source gap | `joint_diagnostic.py::joint_thermal` uses `Fraction` before binary64 conversion |
| I = tanh(delta/2) | `joint_thermal`, `paired_flux_imbalance_I` |
| D = expm1(-delta)/[-expm1(-x_E)] | `joint_thermal`, `source_planck_deviation_D` |
| Ratio = 1+D, independently checked as ratio | `joint_thermal`, `source_planck_ratio` |
| Independent positive fluxes b/(1-b), r/(1-b) | `decimal_reference.py::decimal_reference`, 80 digits |
| Original exponential source ratio | `decimal_reference`, without transformed production formulas |
| Actual eight source lines at three original nodes | `run_diagnostic.py::main`, 24 rows |
| Original 35 Hz gate | Read pinned historical evidence and require exact rational source-gap agreement |
| Coherence, sign, invalid/domain controls | `targeted_controls.py::run_controls`; runner adds source/collider preservation checks |
| PNG/PDF from saved outputs | `plot_saved.py::plot_saved`, two signed diagnostic panels plus distinct old-gate panel |
| Limits, command, raw output, code/input identity, cumulative debit | `run_bounded.py::main` |

## Frozen command, pending parent C4 GO

Run exactly once after parent C4 GO, from `/workspace/scratch/6104ad84b826/rec_bianchi`:

```bash
python research/rec_source_synthesis_20261027/hd_joint/run_bounded.py --attempt primary001 --go C4_GO
```

Primary child allocation is 60 CPU seconds, 180 wall seconds, one thread, 2 GiB address space. The child includes the actual diagnostics, independent reference, targeted controls and saved-output plot; all debit the HD unit. The unit cumulative ceiling is 360 CPU seconds. A new attempt name preserves failed outputs and reads previous observed debits; there is no automatic retry. Final receipt serialization has an unmeasured metadata tail recorded as `UNKNOWN_NOT_ZERO`.

Expected output directory is `raw/primary001/`, containing `PREEXEC.json`, `EXECUTION.json`, `DIAGNOSTICS.json`, `DIAGNOSTICS.csv`, `TARGETED_CONTROLS.json`, `SUMMARY.json`, `SUMMARY.md`, `targeted_run.stdout.txt`, `targeted_run.stderr.txt`, `joint_thermal_diagnostics.png` and `.pdf`. A failed child retains whatever it actually produced. No result file is claimed until execution and readback occur.

The figure is generated only from `DIAGNOSTICS.json`. Its signed I/D panels use a symmetric logarithmic scale; the separate logarithmic Hz panel retains the original gate classification. The parent/fresh reviewer must inspect the actual saved PNG.

## Status and context

**PREPARED_ONLY. SCIENTIFIC_EXECUTION_NOT_RUN. TESTS_NOT_RUN. PLOT_NOT_RUN.**

The source input, parser and coding contract were checked by metadata SHA256 readback during preparation and matched the frozen identities. Requested executor role is lower-tier mechanical implementation; the runtime model identity is `UNKNOWN_NOT_EXPOSED`.

Skill context used: PhysMath Research Loop 1.3.0 `SKILL.md`; `references/CODING_LOOP.md` selected C5–C8; `references/POLICY_INTEGRATION.md`; parent-selected delegation scope. No recursive delegation or review. One production verification and one fresh parent-controlled review remain authorized. Source/contract byte identity is exact; numerical diagnostics use the frozen `128*epsilon64` criterion. Historical scientific results, failed attempts and costs are reused without replay.
