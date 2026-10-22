# THERM02: current-state RR / Compton compact thermal pilot

This independent cohort extends the recovered THERM01 compact34 conditional
21-population atomic model. The physical contract is fixed in
`FROZEN_CONTRACT.md` before new IVPs. The derivation is in `THEORY.md`; primary
source mapping and exact reuse identities are under `provenance/`.

The thermal state remains w = epsilon_th / k_B. The added Compton term is
affine in w at fixed current density and geometry, so no extra ion or radiation
coordinates are introduced. Six Mao2017 RR factors are mapped to the existing
isotopes. The retained donor number rates make this a named Mao-factor hybrid.
The actual grey-photon hot component and an independently specified Planck
reference are different model choices. Bath debits are passive energy ledgers.

## Execution contract

Exactly five nominal compact34, two tighter compact34, and one full63 oracle
are complete, with 193 saved nodes from z20 to z2. The eight new IVPs and
all three frozen comparison gates passed. Cumulative science/diagnostic/storage
time was 92.951497908 s in this sandbox. No completed REC126, REI129, warm729,
THERM01, PR121, PR124 or other old campaign was rerun. PR124's completed
5–200 eV, 109-node restart cohort is separate from this 5–60 eV cohort.

`REPORT_KO.md` develops the physics and measured results. `HANDOFF_KO.md`,
`DAG.json`, and `NEXT_DAG.json` record the closed local scientific unit and
the next source-bound obligations. `delivery/` records actual publication
and backup receipts; their acknowledgement and byte-verification scopes
are distinguished.

## Measured results

At z=2, the split-seed Mao/off, actual-hot and Planck-reference temperatures
are 6573.376838, 5609.584328 and 5610.699960 K. Planck minus hot reaches
7.194733 K over the saved trajectory. Temperature, electron abundance,
ionic fractions, optical depth, photon/radiation/total signed stress exceed
both observed branch refinement changes. Shear, matter and neutrino signed
stress differences do not; the report preserves that distinction.

The maximum normalized energy residual is 3.7671763e-7 against the frozen
3e-6 limit. One independent retained-array audit reproduced the ledgers and
finite comparisons without scientific imports, RHS calls or new ODEs.
Its scoped review is `evidence/independent_review/REVIEW.md`.

The three PNG/PDF figures in `figures/` are bound to raw data through eleven
CSV files and `results/PLOT_DATA_MANIFEST.json`. Initial display defects
were repaired and confirmed visually; original figures and code are retained.
Completed science does not require another `--run` invocation.

## Scope and retained status

This remains a conditional atomic/thermal test-fluid calculation. Li resonance
final yields, CI/CE and a spectral radiation/Einstein energy backreaction
closure are open inputs or separate research units. It is not a complete
nuclear network or a complete thermodynamic closure.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
The original REI failed raw remains historically local-only.
