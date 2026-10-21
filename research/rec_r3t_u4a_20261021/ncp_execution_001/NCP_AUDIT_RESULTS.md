# R3T-U4A independent audit and result adjudication

## Scope and decision

Fresh read-only PHYS-MATH/CODE review: **`PASS_SCOPED` for the executed
32-step interval 74411 → 74443**. No material numerical or physics defect was
found in this interval. This review admits only the bounded restart result.

The raw supervisor terminal status remains **`CAP_HOLD`** with its SHA
unchanged. An additive review of the exact systemd terminal journal records
**`PASS_SCOPED_OBSERVED_RESOURCE_BOUNDS`**: 5.346 scope CPU seconds, 5.425340
seconds supervisor wall time, 321.3M reported scope memory peak, successful
unit deactivation. The worker's 4.212451 CPU-second and 4.218228 wall-second
snapshot ends before final manifest/RESULT writes and excludes imports,
bootstrap and teardown; it is not the complete job measurement. The terminal
`infinity` properties were read after transient scope unload and are not used
to infer earlier active settings.

## Independent evidence checks

- All 49 worker manifest entries match the returned files.
- Checkpoint SHA matches the frozen R3Q accepted checkpoint at global index
  74411. The checkpoint has H_ONLY/post-Saha state, predictor RHS tail from
  indices 74409 and 74410, and 1,519 accepted causal columns owned by indices
  72892..74410. New accepted photon columns are 1519..1550, with no prefix
  mutation.
- 33 states and 32 accepted rows are contiguous through global index 74443.
  All per-step checkpoint receipts and the final checkpoint agree with the
  accepted history and predictor.
- Native output has 20,064 ordered records: 32 STEP, 32 RHS, 9,952 V, 9,952 A,
  and 96 L. The accepted binary stream columns equal the corresponding final
  checkpoint columns.
- Maximum native/Python xe absolute difference is `1.11e-16`; Tm absolute
  difference is `0`; H RHS scaled difference is `1.61422542e-11`; photon lane
  tolerance ratios remain below 1. Maximum accepted Schur residual is
  `5.860e-16`.
- Python common-input checks cover 128 FULL inputs: maximum scaled RHS
  difference `2.75968137e-12`; maximum V/A/L tolerance ratios are
  `2.60257e-5 / 3.18139e-4 / 5.78427e-6`.
- 16+16 restart output has exact floating-value equality with the one-shot 32
  output. This is value equality, not a byte-level assertion.
- Targeted local tests cover checkpoint ownership, missing/duplicate or
  uncommitted history rejection, source-before-stage guards, post-Saha-off
  AB predictor, event transition logic, canonical callback table, and
  cumulative 32-step cap (17 passed, exit 0).

## Exact scope and limits

The primary Python trajectory used 128 FULL evaluations. The split Python
audit used another 128; common-input C comparisons used 128 calls; the native
restart used 32 FULL evaluations. These are separate work counts, not a
single-run count. This was correctness/restart verification, not a performance
benchmark: lanes/s, records/s and I/O bytes were not measured. Raw native output
and binary lane streams are retained.

The interval ends `post_saha=true` with `NO_EVENT_WITHIN_BOUND`. It does not
demonstrate post-Saha exit, U4 boundary crossing, U5/U6 completion, global
convergence, physical validity, or production readiness. Preserve U5 `h`
`HOLD_9_FAIL`, U5 `h/2` `HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, REI activation
false, global convergence `NOT_RUN`, physical `HOLD`, and production
`NOT_APPROVED`.

The independently observed supervisor terminal-accounting defect remains open
for future invocations. The consumed allocation was not relaunched or reused.
