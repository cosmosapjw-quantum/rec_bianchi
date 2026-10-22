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

Science publication: `d562d03415e37488cd4b5444488c77555260e0fb`.
Recovery publication: `b94314be1be12664f1dec8100d29bdb5f9135adf`.
The final documentary HEAD is the commit containing
`delivery/FINAL_PUBLICATION_BACKUP.json`, pinned in the PR120 completion comment.
All 20 current R1–R10/C1–C10 nodes are COMPLETE_SCOPED. N1 is READY_TO_SELECT;
N2/N3 are INPUT_DEPENDENT; N4/N5 are NOT_RUN.

Final archive: `REC_REI_THERM01_FINAL_RECOVERED_20261022_5445e15edb1d.zip`.
Size: 12,639,251 bytes; 157 payload files plus one manifest.
SHA256: `5445e15edb1d580af8b819e8d6a1b73fc2b9958d76bae92967c38ee0763bf0e0`.
Dropbox file `id:BSpOijBcT10AAAAAAD_h4A`: actual single full GET matches whole-byte
SHA256, ZIP CRC, manifest and all 157 payload SHA256 values.
Google Drive file `1vplg47vr0im-aTm0K6XLMYzvLEY5SJNs`: successful upload and exact
metadata size; whole-byte readback NOT_RUN. Stages A/B have their own preserved
ACK/size receipts; do not promote them to a whole-byte readback claim.

The archive is a fixed payload snapshot made before upload ACK. This receipt,
final DAG and handoff updates form a documentary Git supplement. Do not rewrite
the already verified ZIP to make an impossible self-containing publication receipt.

Original Stage C remote ZIP was incomplete (12,257,739 bytes, no central directory).
All 147 expected payloads were recovered exactly: 85 complete local members and
62 from fixed science Git, with two CSV line endings restored only after original
SHA256/GitSHA agreement. Recovery commit verified all 155 published unit blobs.
The incomplete ZIP remains failure evidence; its cause is undetermined.
Recovery ODE count is 0. Use the final recovered ZIP, not the incomplete object.
