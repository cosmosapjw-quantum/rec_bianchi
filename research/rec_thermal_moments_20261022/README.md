# REC thermal moments — 2026-10-22 continuation

This unit continues REC PR119 (`ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`) by closing the **retained** gas thermal processes. It reuses the completed 125 main trajectories and one opacity control, adds RR/DR kinetic energy losses, and evolves temperature in eight distinct full63 restart configurations. Read `REPORT_KO.md` for results and `THEORY_KO.md` for the derivation and source assumptions.

The old 126 IVPs are inputs, never new jobs. The eight new configurations start at the exact saved node84, z=7.963732801243163, and end at z=2. The inherited prefix z20→restart is a prescribed-temperature history. The initial native neutron and tritium inventories are zero. The temperature, ions and optical-depth response after restart are coupled; baryon thermal energy remains a test-fluid contribution to the inherited geometry.

## Source and scientific contract

`FROZEN_CONTRACT.md` fixes the four primary cases, two tolerance refinements, two alternative RR energy moments, coefficient domain, finite gates and execution budget before integration. `provenance/PARENT_SOURCE_LOCK.json` pins the donor code/data/vendor inputs; every reused trajectory is checked against its committed receipt. `provenance/MAO_SOURCE_LOCK.json` pins the original CDS tables and selected six rows.

The primary RR loss is a Mao2017 energy-factor **hybrid** with the unchanged parent number rate. The alternative differentiates that same number-rate fit. Their difference is a source sensitivity, not an uncertainty interval. DR retains the signed resonance-fit components. Li-I core energy is assigned to prompt radiative escape in the inherited single-charge-step model. Unmodeled processes and energy owners remain explicit in the theory and report.

Physical HOLD; production NOT_APPROVED; global convergence NOT_RUN; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; historical allocation CLOSED_HOLD_NOT_RESET; REI_activation=false.

## Layout

- `code/recombination_moments.py`: analytic RR/DR rate and kinetic energy moments, including temperature derivatives.
- `code/thermal_sources.py`: source-bound Mao factors, energy ownership and temperature RHS.
- `code/thermal_system.py`: full63 RHS, analytic Jacobian and dynamic-temperature diagnostics.
- `code/run_thermal.py`: immutable eight-configuration runner, hash reuse and finite gates.
- `code/postprocess_saved.py`: the existing126 thermal budget; no ODE calls.
- `code/analyze_and_plot.py`: saved comparisons, numerical refinement checks and figures; no ODE calls.
- `results/saved126`: all193-node histories, input hashes, representative CSV and per-case endpoint table.
- `results/thermal8`: actual new trajectories and STARTED/RESULT receipts, plus campaign receipt.
- `results/analysis`, `figures`: exact plot data, comparisons and PNG/PDF exports.
- `evidence`: distinct test receipts, independent reviews, stage checkpoints and delivery status.

Keep this directory beside `research/rec_rei_hheli_sandbox_20261021`. The final source/results archive includes both units so that the pinned imports and saved donor inputs remain available.

## Environment and reproduction

The actual run used Python3.12.14, NumPy2.3.5, SciPy1.17.0 and Matplotlib3.10.8 on Linux. The runner sets BLAS/OMP threads to1 before importing NumPy. The host had an8-CPU quota and8GiB RAM; this finite campaign is serial with cooperative240s per-case and1200s total wall caps. The cap is scoped to the first frozen invocation. Any continuation after a failed/partial invocation must account for wall already consumed; changing output directories does not reset the allocation.

Commands from the repository root:

```bash
python research/rec_thermal_moments_20261022/code/test_recombination_moments.py
python research/rec_thermal_moments_20261022/code/test_thermal_system.py
python research/rec_thermal_moments_20261022/code/run_thermal.py
```

The last command only displays the frozen plan. The historical executed command was:

```bash
python research/rec_thermal_moments_20261022/code/run_thermal.py --execute
```

Completed trajectories are reused only when the four execution modules, source tables/locks, donor receipt and donor NPZ identities match. The runner refuses to overwrite partial or mismatched results. Hashing is restricted to execution dependencies; adding a report or plot does not invalidate a trajectory. A genuine scientific change needs a new identity and explicit new execution allocation, not deletion of the existing receipt.

The first boundary-column finite-difference checker failure is retained in `thermal_system_tests.json`: its central stencil crossed the inherited u=0 domain boundary. Only that checker stencil was corrected to a fourth-order forward difference. No physical source or acceptance tolerance was changed. The actual test method counts are9 and10; multiple temperatures, directions and mutations are subchecks rather than additional methods.

## Interpretation and delivery

Signed stresses, signed external thermal forcing and tiny isotope populations are retained in saved data. Plot axes use elapsed time since the donor z20 origin, with redshift mapped to an explicitly named reference case. This time is neither the cosmic age nor time since restart.

Local commits and hash-verified archives are concrete checkpoints. GitHub push was rejected by automatic approval review because publication authorization for this new branch was not established in the current user message. No new remote branch, draft PR or remote backup is claimed. `DELIVERY_STATUS.json` and `HANDOFF_KO.md` distinguish local completion from the external publication action awaiting explicit authorization.
