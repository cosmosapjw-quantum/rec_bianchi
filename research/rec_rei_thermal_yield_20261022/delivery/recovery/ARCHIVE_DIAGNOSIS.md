# THERM01 Stage C archive diagnosis

**Result: all 22 binary science files are complete and byte-identical to the expected identities. The downloaded top-level ZIP is incomplete.**

This bounded recovery review parsed the existing remote bytes without extracting or modifying the scientific unit. It performed no ODE or historical campaign rerun.

## Input and byte boundary

- Downloaded archive: `/workspace/scratch/a6dfe82cc85f/recovery/REMOTE_STAGE_C.zip`
- Bytes: **12,257,739**; original recorded archive length: **12,583,886**; difference: **326,147 bytes**.
- SHA256: `c1b672434d6259d2079362e1ee5484e7a9b45bc8e8514230ca38da3c0ff21489` (unchanged after review).
- Expected recovery plan: **147 payloads**, SHA256 `d4b4b5ea46c8af3ec72c0790dfc21031de0f01178f5f06c0fc1f364ee0ccbab5`.
- Exact EOF: byte offset **12,257,739**, immediately after complete member `results/thermal_split60_tight34_plot_source.csv`.
- Last member local header: **12,178,105**; compressed data span: **[12,178,213, 12,257,739)**; compressed length: **79,526**; uncompressed length: **202,245**.
- No top-level central directory or EOCD was encountered in the sequential parse. Embedded `PK` signatures occur inside member data and are not a top-level archive footer.
- Standard ZIP reader result: `{'opened': False, 'exception': 'BadZipFile', 'message': 'File is not a zip file'}`.

## Payload verification

| Check | Result |
|---|---:|
| Complete local members | 85 |
| Decompression / CRC32 / local and expected lengths / expected SHA256 / Git blob SHA1 all pass | 85 |
| Identity failures | 0 |
| Expected binary science files present and matching | 22 / 22 |
| NPZ / PNG / PDF present and matching | 16 / 3 / 3 |
| Expected recovery-plan paths absent | 62 |

The complete binary set includes `solver_return.npz` and `trajectory.npz` for all eight THERM01 cases, plus all three PNG/PDF figure pairs. This is byte preservation evidence; it is not a new scientific execution or a new physics acceptance decision.

## Interpretation and recovery limits

The observed file is a structurally incomplete ZIP ending at a complete local-member boundary. These bytes do not identify whether an upload captured an unfinalized archive, a later process truncated bytes, or another delivery failure occurred. The review does not infer an upload cause. No separately available finalized original ZIP was compared, so whole-original-archive identity is not asserted.

The absent set is measured against the parent-provided 147-payload recovery plan: 2 plot-source CSVs, 59 vendor files, and 1 delivery metadata file. A recovery-plan metadata file need not have belonged to the original finalized archive. Present payload hashes independently match that plan.

The optional helper extracts only after every present payload verifies and the destination passes a preflight. Existing regular files must be byte-identical; differing files or symlinks abort. Missing payloads remain missing and must be restored from the independently pinned source. Extraction was **not** run by this review.

```bash
python3 recovery/salvage_stage_c.py --extract-to /absolute/path/to/restored/unit
```

## Missing relative paths

- `results/thermal_uv_off_plot_source.csv`
- `results/thermal_warm60_plot_source.csv`
- `vendor/rei_pr220/code/compact_system.py`
- `vendor/rei_pr220/provenance/DONOR_IDENTITY.json`
- `vendor/rei_pr220/vendor/rec_hheli/DAG.json`
- `vendor/rei_pr220/vendor/rec_hheli/README_KO.md`
- `vendor/rei_pr220/vendor/rec_hheli/THEORY_KO.md`
- `vendor/rei_pr220/vendor/rec_hheli/code/atomic_network.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/coupled.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/geometry.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/run_pilot.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/verify_atomic.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/verify_coupled.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/verify_optimization.py`
- `vendor/rei_pr220/vendor/rec_hheli/code/verify_runner.py`
- `vendor/rei_pr220/vendor/rec_hheli/data/CAMPAIGN.json`
- `vendor/rei_pr220/vendor/rec_hheli/data/atomic_coefficients.json`
- `vendor/rei_pr220/vendor/rec_hheli/data/atomic_model.json`
- `vendor/rei_pr220/vendor/rec_hheli/data/atomic_reference_rates.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/COUPLED_VERIFICATION.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/INDEPENDENT_CODE_REVIEW_STAGE_B.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/INDEPENDENT_CODE_REVIEW_STAGE_B.md`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/INDEPENDENT_CONTRACT_REVIEW_STAGE_A.md`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/INDEPENDENT_PHOTO_SCOPE_REVIEW.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/INDEPENDENT_PHOTO_SCOPE_REVIEW.md`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/OPTIMIZATION_VERIFICATION.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/RESOURCE_INTAKE.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/RUNNER_DEVELOPMENT_FINDINGS.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/RUNNER_VERIFICATION.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/RUNNER_VERIFICATION_PRE_LEASE_AUDIT.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/RUNNER_VERIFICATION_PRE_PARENT_REUSE.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/RUNNER_VERIFICATION_PRE_RESOURCE_SHAPE.json`
- `vendor/rei_pr220/vendor/rec_hheli/evidence/WOLFRAM_IDENTITIES.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/BASELINE_SOURCES.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/INPUT_SURVEY.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/INPUT_SURVEY_KO.md`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/REUSE.md`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/UPSTREAM_SOURCE_INTAKE.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/UPSTREAM_SURVEY.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/atomic_development.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/atomic_literature_retrieval.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/atomic_scope_KO.md`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/atomic_sources.json`
- `vendor/rei_pr220/vendor/rec_hheli/provenance/atomic_verification.json`
- `vendor/rei_pr220/vendor/rec_hheli/stages/LOOP_STATUS_STAGE_B.json`
- `vendor/rei_pr220/vendor/rec_hheli/stages/STAGE_A_RECEIPT.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_primary/selected_HHe_RR_DR_rows.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_primary/selected_photo_rows.txt`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_reused/LI_PHOTO_CONTRACT.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_reused/SOURCE_MANIFEST.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_reused/badnell_lithium_dr_rows.txt`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_reused/badnell_lithium_rr_rows.txt`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_reused/lithium_coefficients.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/atomic_reused/provider_reconstruction.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/baseline/LICENSE`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/baseline/REI_BACKGROUND_FAMILY_LOCK.json`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/baseline/canonical_fv.py`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/baseline/lrs_boltzmann.py`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/baseline/species_hierarchy.py`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/he31/prepared_moments.py`
- `vendor/rei_pr220/vendor/rec_hheli/vendor/tangent/tangent_core.py`
- `delivery/STAGE_C_LOCAL.json`

## Scope and gates

REC126, REI129, warm729 and previous completed calculations were not rerun. The REI first-failure raw remains within its original local-only preservation scope. Physical/REC U5 HOLD, global convergence NOT_RUN, production NOT_APPROVED and REI_activation=false are unchanged. The prior THERM01 finite acceptance and its source/process limitations are neither broadened nor recomputed by this delivery diagnosis.

Per-member offsets, CRC32 results, byte counts, SHA256 values, Git blob SHA1 values, and all 62 missing expected records are in `ARCHIVE_DIAGNOSIS.json`.
