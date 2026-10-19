# R3O low-z implementation handoff to parent

**Implementation and local verification completed; independent dual review and full physical production remain with the parent.** No GitHub, backup, DAG, parent research files, or shared existing source modules were mutated. The source capsule is not a git checkout. The parent-confirmed baseline is PR108 HEAD `23e0a3a6c439a1f015aa8f7380f4eedf0b569df7`.

## Owned new files

All paths below are relative to `/workspace/scratch/afe554957b2e/rec_work`.

| File | SHA256 |
| --- | --- |
| `src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py` | `484d8822b1cf4b607d47c196571f7bdbee7eabfad7bc77489d6befdd8106294b` |
| `scripts/verify_r3o_lowz.py` | `192f6ba070f35d7cede83fc03a96757064844f517f9b6c5910c2d7d305ddb193` |
| `scripts/c_harness/original_hyrec_r3o_lowz_harness.c` | `d179b07d33562557924f763b85a58f5a2cec48ec2a78c4ab39a6702d82e88756` |
| `tests/trajectory/test_r3o_lowz.py` | `1426df45824660bfbfa9f7f57c7cea2fc357baa0edbb80ad7bc6371d21cd4900` |

The smoke receipt's imported-source content identities still match the final implementation. Subsequent changes were confined to the new test file. Frozen h-stage U7/U8 index constants are not used for the refined clock.

## Equations, indices, and input chain

Source `history.c` lines 458–484 retain `rec_get_xe_next2_HTm`, both current/prev2 updates, and both derivative-memory rotations. Lines 578–596 supply the outer EMLA table guards and permanent Peebles continuation. C `.c` files, headers other than the copied clock definition, and the atomic rate tables remain original. Only the new isolated `hyrec_params.h` copy substitutes `DLNA=(8.49e-5/2.)`, producing the existing reviewed h2 header SHA `e83d8031975c0a64cdb45a2b8ba03a4a0a75c85fac5cf2437aadc915e25751bf`.

The Python stage imports the original reviewed Peebles expression and thermal RHS, and calls the existing original-table EMLA source. It imports the refined cosmology, not the original h-grid cosmology. Stage selection preserves the source expression's left-to-right multiplication/division order. There is no photon read, append, interpolation, or RT rerun in this stage.

At the input state `n`, memory is `prev=F[n-1]`, `prev2=F[n-2]`, and the update is

`y[n+1] = y[n] + h2 * (1.25*F[n] - 0.25*prev2)`.

R3M `states_json`/`steps_json` provide the actual Python endpoint at 58389 and its two hydrogen/thermal RHS tails. The C endpoint and its tails are independently parsed from the actual final two native `STEP` records. No Python seed is copied into the independent C trajectory. The same immutable pins as `scripts/compare_r3n_time_grids.py` are enforced for the entire original NPZ, native CSV, verification JSON, and source ZIP; the verification's original U5 checkpoint identity is also required. Inputs are hashed before loading, after loading, and after execution, including failure paths. Spectral arrays remain covered by the NPZ whole-file hash but are not materialized.

- Start input/global index: **58389**.
- Step: **4.245e-5**.
- Source node count: **211717**.
- Last accepted/output node: **211716**.
- Required continuation updates: **153327**.
- Last RHS input remains at positive z; the final output z is `-2.238689928646398e-5`.
- z=0 uses source global stencil `[211713,211714,211715,211716]`, clamped fraction `1.4726230889209546`. The fraction is not clipped, and no RHS is evaluated at the final negative-z output.

**Parent theory input: conditional TR_MIN switch is 144931, not a hardcoded doubled old-h event.** The continuous threshold is `144930.175824884`. With `Tm/Tr > .1`, input 144930 has rescaled Tr `0.00400002985517672` eV (guard true), and input 144931 has `0.003999860057513351` eV (guard false), z `16.030414995085543`. The original h input 72466 corresponds to h2 input 144932, z `16.0296920693132`; the extra h2 half-step crosses TR_MIN earlier. Original C/Python guard comparisons and a controlled two-step transition verify input 144930→output144931 EMLA followed by input144931→output144932 Peebles. This is a clock/guard result, not the unrun physical h2 trajectory's event: an earlier physical `TM_TR_MIN` crossing remains possible and is selected by the production loop.

## New interfaces

```python
LowZCheckpoint(
    iz, xe, Tm_K,
    hydrogen_prev, hydrogen_prev2,
    thermal_prev, thermal_prev2,
    peebles_event_iz=None, peebles_event_reason=None,
)

load_reviewed_u6_boundary(raw: Path, source_zip: Path) -> dict
# Returns distinct "python" / "native" checkpoints plus exact input hashes.

continue_refined_low_z(
    checkpoint, c, emla_source, *, max_steps,
    before_attempt=None, on_accept=None, on_checkpoint=None,
    checkpoint_interval=4096,
) -> dict

source_stage_guard(c, z, Tm_K) -> (bool, reason_or_None)
source_z0_cubic(four_source_end_values) -> dict
```

Native symbols: `rec_r3o_lowz_init`, `rec_r3o_lowz_guard`, `rec_r3o_lowz_rhs`, `rec_r3o_lowz_step`, `rec_r3o_lowz_z0`, `rec_r3o_lowz_dlna`, `rec_r3o_lowz_nz`, `rec_r3o_lowz_z`. The shared-library wrapper is `NativeLowZ` in the verifier. `-DR3O_LOWZ_MAIN` also builds a bounded standalone C CLI; both shared and standalone builds were tested against the original source translation units.

## Actual local results

All new runs below were in this sandbox. R3M full5210 was reused from the owner workstation and was not rerun.

### Actual U6-boundary smoke

Command actually executed:

```sh
python3 scripts/verify_r3o_lowz.py --mode smoke --steps 16 \
  --raw-dir /workspace/scratch/afe554957b2e/rec_raw_verified/full5210_stored \
  --evidence-dir /workspace/scratch/afe554957b2e/rec_recovery/r3o_lowz_smoke_001
```

- Exit 0; `SMOKE_PASS_SAME_H_PENDING_REVIEW`.
- Python and native C each accepted 16 new low-z EMLA steps, through index 58405.
- Native and Python state maxima: xe `7.434376394267938e-14`; Tm `2.49687949887451e-16`.
- Fixed same-h state limits: xe `5e-9`, Tm `5e-10`.
- Four actual common inputs: 58389, 58390, 58391, 58404.
- Common RHS maxima: hydrogen `2.1707559781417694e-14` (limit `3e-10`), thermal `3.621030056849089e-14` (limit `2e-10`).
- Input/source/code before-after identities: MATCH. Native binary hash is also checked after execution.
- Wrapper measured CPU `5.130202` s, wall `5.480337858003622` s. Internal inclusive process-tree CPU `5.048521000000001` s; wall `5.354274590004934` s. Distinction is process startup/report closure overhead.
- Applied limits: 20 CPU s, 60 wall s, 2 GiB address space, with 3 CPU s / 8 wall s recovery reserve. Peak parent RSS `93151232` B.
- Verification SHA256: `3f509eb19c97f95352036034f81f153306d41f813afe41d68ef3cee684ab21bc`.

### Small verification suite

```sh
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -m unittest discover -s tests/trajectory -p test_r3o_lowz.py -v
```

Final result: **20 tests, OK**, exit 0; total wrapper CPU `2.275386` s and wall `2.2769355420023203` s. Tests include real original-C EMLA and Peebles common-input operators and updates, exact guard threshold ordering, input/output event indexing, source z0 interpolation byte agreement, prev2 memory rotation, absorbing Peebles, forbidden final-output RHS, dirty output preservation, tampered raw rejection, checkpoint memory/domain rejection, current allocation and smoke identity gates, compiler process-tree CPU accounting, and partial checkpoint behavior after a work-budget stop or failed comparison.

These controlled operator tests are labeled as controlled inputs; they are not fake sampled physical trajectories. Only the separate actual U6-boundary smoke is a new physical continuation. Numerical time-integration parity uses the frozen tolerances; only the same-input final cubic tests assert byte identity.

Measured aggregate across all test attempts plus the actual smoke: **10.917785 CPU s**, below the assigned approximately 30 CPU s allowance. Source inspection and a small clock-only diagnostic are separate low-cost activity. No full low-z physical production or performance claim was made.

Earlier attempts are retained: `tests_001` found the environment lacked pytest, so the new tests use stdlib unittest; `tests_002` exposed the native wrapper's endpoint error classification; `tests_003` exposed the incorrect doubled-index test expectation. The final wrapper and test corrections passed. These are environment/implementation/test-expectation findings, not physical failures.

## Resource and recovery contract

The runner reserves a new evidence directory atomically and creates outputs exclusively. It writes paired native/Python accepted states to `accepted_pairs.jsonl`, periodically fsyncs them, and writes separate immutable JSON checkpoints at start, first two accepted steps, every4096 steps, the stage event, stop, and exception. Rejected candidates preserve the prior accepted state/memory. Failed comparisons preserve the actual accepted Python state and available native state without admitting them. Partial checkpoint JSON includes all four RHS memory values, stage event, current code/input identities, and the last four Python states. The accepted-pair ledger retains every native/Python accepted pair.

Resource checks include the Python process, reaped children, and live compiler descendants via Linux `/proc` accounting; subprocess process groups are terminated on limits. CPU and address-space rlimits and a wall timer are applied. Recovery reserve is used to seal records and perform after-hash checks. Total cap overruns do not retain a PASS status. The historical budget is always `CLOSED_HOLD_NOT_RESET`; a fresh allocation is a separate record.

The module can continue from a validated `LowZCheckpoint` with its predictor tails; the production CLI currently starts from the pinned R3M raw boundary. **Automatic CLI resume/stitching from a previous partial run is not implemented.** Checkpoints and the complete accepted-pair ledger are available for parent-coordinated recovery. A fresh full invocation must have a new explicit allocation; the runner never silently resets cost or consumes a partial record as a full-history admission.

## NCP production entry point and remaining obligations

This implementation has not consumed a new NCP allocation. Parent independent dual review is still required; the implementer and the C comparisons are not a substitute for that review.

The full runner accepts:

```sh
python3 scripts/verify_r3o_lowz.py --mode full \
  --raw-dir /absolute/path/to/full5210_stored \
  --evidence-dir /absolute/path/to/new/r3o_lowz_full_001 \
  --allocation-json /absolute/path/to/current_allocation.json \
  --smoke-verification /absolute/path/to/r3o_lowz_smoke/verification.json
```

The parent/executor must supply a concrete current allocation with `allocation_id`, `allow_full_lowz=true`, `parent_coordination_confirmed=true`, `dual_review_acknowledged=true`, `historical_budget_status="CLOSED_HOLD_NOT_RESET"`, exact `source_code_sha256` from the same-code smoke/preflight, timezone-aware `issued_at_utc` and `expires_at_utc`, `cpu_s`, `wall_s`, `memory_bytes`, `recovery_cpu_s`, `recovery_wall_s`. The allocated wall interval must fit before expiration. Recovery reserves must be positive and smaller than their totals. Full execution requires a completed, unchanged-input same-code smoke of at least16 steps. This is an execution guard, not a scientific admission or an allocation that this agent has created.

Full production status can only become `FULL_LOWZ_SAME_H_PASS_PENDING_DUAL_REVIEW` after all153327 steps, matching model/event sequence and frozen state/memory tolerances, a Peebles event, final original cubic same-input byte identity, independent C endpoint agreement, and final input/code/source/binary readback. Joining earlier h2 source history for a global convergence descriptor remains with the parent; this new output spans U6 boundary→source end only. `h/h2/h4` physical convergence, speedup, Bianchi/REI/CMB admission remain unapproved, U5 `HOLD_9_FAIL`/`HOLD_8_FAIL` remain, REI activation remains false.

## Parent evidence collection

Under `/workspace/scratch/afe554957b2e/rec_recovery/`:

- `r3o_lowz_implementation.json`: final owned-file hashes, scope, receipts, test/run results, prior-attempt classifications.
- `r3o_lowz_environment.json`: actual Python/NumPy/gcc/platform metadata.
- `r3o_lowz_tests_001..004.log` and paired JSON resource receipts; final is004.
- `r3o_lowz_smoke_001/`: source manifest/copy, native library/build logs, paired accepted ledger, checkpoints, NPZ, verification JSON.
- `r3o_lowz_smoke_001.log`, `r3o_lowz_smoke_001_execution.json`.

Parent owns publication, backup, the research DAG, THEORY, and the original-h adapter/probes. Do not fold this local implementation handoff into a claim that the pending dual review or full153327-step execution was completed.
