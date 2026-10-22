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
are planned, with 193 saved nodes from z20 to z2. No completed REC126, REI129,
warm729, THERM01, PR121, or other old campaign is rerun. The PR122 proposed
5–200 eV, 109-node restart cohort is not this cohort.

Implementation and measured results will be committed after the physical
checkpoint. `DAG.json` records the current stage and next unmet dependency.

## Scope and retained status

This remains a conditional atomic/thermal test-fluid calculation. Li resonance
final yields, CI/CE and a spectral radiation/Einstein energy backreaction
closure are open inputs or separate research units. It is not a complete
nuclear network or a complete thermodynamic closure.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
The original REI failed raw remains historically local-only.
