# Codex continuation — THERM01 completed finite science

Repository: `cosmosapjw-quantum/rec_bianchi`.
Branch: `research/rec-rei-thermal-yield-20261022`.
Draft PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/120 .
Unit: `research/rec_rei_thermal_yield_20261022`.
Execution-source checkpoint: `f68f6e8391f115f36da2766bc8eb20724d1c673f`.
Read the latest PR/branch and delivery receipts before interpreting a later document-only HEAD.

## Completed work to reuse

Read `HANDOFF.json`, `DAG.json`, `RESULTS_KO.md`, `FROZEN_CONTRACT.md`,
`SOURCE_SCOPE_CLARIFICATION.md`, `NEXT_SOURCE_INPUTS.md`, and
`evidence/INDEPENDENT_REVIEW.md`. The frozen contract is an execution-identity file;
the separate scope clarification corrects its overly broad core-excitation sentence.

Exactly eight new THERM01 histories are complete: six nominal, one tight34, one
full63 oracle. All have 193 saved epochs and 21 reconstructed populations, z20→2.
The new nominal state is compact34, with dynamic w=epsilon_th/kB. All finite gates
and the bounded independent review passed. The maximum normalized energy residual
is 2.935629461677083e-6 against 3e-6: only 2.1457% headroom. Preserve that qualification.
Three PNG/PDF figure pairs and ten CSV sources are complete and checked.

Do not rerun REC126, REI129, warm729, any other completed historical campaign, or
the completed THERM01 histories merely to recover or republish artifacts. Their
counts are separate. REI's historical first failed raw remains local-only in its
original preservation scope; it is not retroactively covered by later archives.
All eight new THERM01 trajectory and solver-return NPZ files are preserved here.

## Reuse and recovery commands

Python 3.12.14, NumPy2.3.5, SciPy1.17.0, Matplotlib3.10.8 were actually used.
`requirements-runtime.txt` records those versions. This unit is self-contained
with the 57 immutable donor files and PR220 compact module in vendor/.

For lost figures only, read the existing raw; this command performs no ODE:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLCONFIGDIR=/tmp/therm01-mpl python code/run.py --plot
```

Do not invoke a full campaign as an automatic recovery step. The default runner
has source/config/raw-hash cache guards, but even cached revalidation is unnecessary
unless it resolves a concrete missing result. Never delete an output directory or
change a scientific identity merely to bypass its cache/failure guard.

## Positive next work

Follow N1–N5 in `NEXT_SOURCE_INPUTS.md`: resolve actual charge/level/energy data for
in-band Li resonances and 60–200 eV correlated channels; select an independent H/He
partial recombination-cooling witness; freeze source tables, units, exclusive
channels, energy ledger and finite criteria before code. Recheck the compact
invariant subspace if new processes break electronic isotope equality or introduce
nuclear transmutation. Allocate a new source identity/cohort for genuinely new IVPs.

The retained direct Li I1s photoionization channel is zero below its edge. Physical
50–60 eV resonant core excitations are excluded, not nonexistent. Source-fit
derivative cooling accuracy remains unmeasured. UV remains prescribed. Do not
claim full nuclear or thermodynamic closure or complete 5–200 eV ionic yields.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.

## Delivery interpretation

Stages A/B freeze and implementation archives were uploaded to both configured
backup providers. Stage C carries all raw/science/review outputs; final delivery
receipts record the actual later ACKs and publication pins. Local payload/CRC
verification and Git object SHA matches are distinct from remote ZIP whole-byte
readback. For new archives the latter remains NOT_RUN unless a later explicit
receipt demonstrates otherwise. Never inherit the historical REC recovery's
whole-byte PASS as a claim about a new archive.
