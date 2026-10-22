# REC omitted thermal process budget

**Complete:** source-budget postprocessing of eight immutable full63 thermal
trajectories,109 nodes each,872 saved states. **New ODE integrations:0.**
On four primary paths, the identifiable hot-electron Compton component is
−2.576 to−2.592 eV/baryon from z7.9637 to2: about30% of the existing primary
photoelectron heating. This motivates Compton-first coupling in the next
finite unit. The fixed-path forcing integral is not a solved temperature
response or a bound on all omitted physics.

Start with [REPORT_KO.md](REPORT_KO.md), [THEORY_KO.md](THEORY_KO.md),
[HANDOFF_KO.md](HANDOFF_KO.md), and [NEXT_UNIT_CONTRACT.md](NEXT_UNIT_CONTRACT.md).
The exact current runtime identity is
`88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c`.

## Artifacts

- `code`: Compton and collision providers, retained-grid postprocessor,
  focused tests, and plotter.
- `data`: source-bound HG97 H/He coefficients and support definitions.
- `provenance`: actual primary-source and existing-code ownership, input
  bindings, recent REC/REI intake and previous delivery receipts.
- `results/budget_v1`: completed first run; full coefficient, mask, source,
  CI transfer, radiation moment and forcing arrays for all872 saved states.
- `figures/v3`: current3 figures (PNG/PDF), exact plotted arrays and table.
  Earlier versions are retained correction evidence; see figures/README.md.
- `evidence`:16 actual test methods, symbolic fixtures, independent raw-NPZ
  recomputation, implementation/physics/visual reviews and stage backups.

The two sibling units `rec_thermal_moments_20261022` and
`rec_rei_hheli_sandbox_20261021` are immutable runtime/input dependencies.
The final restore archive includes them. Python3.12.14 and the actually used
package versions are recorded in `requirements.txt` and result metadata.

## Scientific scope

Actual-U hot Compton and the separate isotropic Planck reference retain
distinct energy owners. UV exchange uses the inherited71 bins. CI kinetic
loss transfers to binding energy and adds an electron; CE is a prompt-escape
source. Below-range fit continuation, unsupported channels, and numerical
underflow remain distinct. Physical HOLD, production NOT_APPROVED, global
convergence NOT_RUN, REI_activation=false and U5 CLOSED_HOLD_NOT_RESET remain.

Publication authorization was explicitly granted. Local/remote commit
mapping, exact tree equality and create-only Dropbox readback belong to the
actual delivery receipts. Final archive self-identity and its later upload
acknowledgment reside outside the ZIP to avoid self-reference.
