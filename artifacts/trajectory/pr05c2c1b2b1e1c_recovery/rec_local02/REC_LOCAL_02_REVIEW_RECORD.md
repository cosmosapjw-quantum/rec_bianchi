# REC-LOCAL-02 post-execution review record

## Binding

- Source preimage: commit `754692d1644a092b149d99990e939e725b28c004`,
  tree `ec05c7f3d247d3804d58d43863589d43793ae0dc`.
- Diagnostic module SHA-256:
  `a8982d7a2e87f420459474528762aa638567d7621dfa494f0638bde0e66aad9a`.
- Runner SHA-256:
  `b381925a3056b5669b70b7ece69739a14278494e82da3310fa8406d49b34099f`.
- Focused test SHA-256:
  `81135445f7727cb099031316bf24653b2af6b5d19af24110ec95778d112d752c`.
- Execution record SHA-256:
  `1198df57ededc3c40f5e9ccb9ee94974ac11076915eafe00cfe8cfe49d4e6b76`.
- Final focused command before review termination:
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p
  no:cacheprovider -q tests/trajectory/test_physical_split_reference.py`.
  Result: `8 passed in 1.18s`.

The eight tracked scientific inputs are bound inside the execution record.
The final remote commit and tree are bound by the post-push readback, not by
this pre-commit execution record.

## PHYS-MATH-CODE review

The post-execution code review reproduced one P1: feasibility was initially
evaluated with the deposition orientation reversed.  The required component
orientation is `B[target_com_cell, source_native_index]`, so every source
column, rather than every target row, must conserve number and energy.

The one allowed P0/P1 repair corrected the orientation, retained an explicitly
`EXPLORATORY_NONAUTHORITATIVE` sparse witness, selected no physical map, and
left only `SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT` as the
terminal blocker.  Its focused rereview closed that declared dependency cone:
all eight source columns were inside the tested target hull, number residual
was zero, no physical map was emitted, and all eight downstream physical
operations remained exactly `NOT_RUN`.

The code review also noted two nonblocking receipt limitations: the execution
record does not hash its generator/test or bind a final commit, and a failed
future generation could leave an older file.  The hashes above and final
remote readback provide the bounded publication binding for this run.

## PHYS-MATH review

The final PHYS-MATH review found no P0 and one additional P1 in the final bytes.
The candidate recomputes a finite-volume centroid from the modern line and
interval faces.  The tracked network's locked physical photon moment owner is
instead `momentum_scale`; its cell energy is
`momentum_scale * c / electron_volt`.  The two target-energy arrays differ by
as much as `5.5440192880951145e-08 eV`.  Consequently, the recorded sparse
witness does not establish the execution record's claimed exact physical
number-energy certificate, even though its self-consistent focused tests pass.

All eight native source energies remain strictly inside the locked
`momentum_scale` target-energy hull, so existence of a nonnegative adjacent
feasibility witness survives.  The present witness weights, residuals, and
hash are not admitted as that locked physical certificate.  The repair and
focused-rereview budget was already exhausted, so this P1 is preserved without
a second repair or review loop.

The same review independently confirmed:

- Original-HyRec Doppler width `57907148285.825386 Hz` and direct-node width
  `57907834835.931496 Hz`, relative difference
  `1.1856051047806029e-05` using the CSV width as denominator.
- Direct-node measure residual `1.0878134039731587e-08` and incompatible
  default-3000 K residual `5.827123144338342e-04`.
- The two positive angular fields have equal monopole and distinct first
  moments, so scalar history does not identify a 26-direction face field.
- The red/blue residuals prove scalar source-boundary packet reconstruction
  consistency only.  They are not total directional COM interface-crossing
  flux or independent four-force balance.
- Metric `(-,+,+,+)`, hydrogen-frame and SI entries are declared conventions;
  four-force, full moving-map JVP, response, and restart work were not run.

## Claim disposition

| Claim | Status | Scope |
| --- | --- | --- |
| Eight Gate-3 tracked input hashes match | `VALIDATED` | Exact files listed in the implementation plan. |
| Actual source occupation/measure is 35x26 | `VALIDATED` | Positive isotropic bootstrap occupation and tensor-product measure; not a coupled endpoint. |
| A nonnegative number-energy witness exists | `VALIDATED` | Hull existence only; exploratory and not selected as physical deposition authority. |
| Current receipt is an exact locked physical moment certificate | `FAILED_P1` | It bypasses the tracked `momentum_scale` owner. |
| Source-defined 26-direction face reconstruction exists | `FAILED_ABSENT_AUTHORITY` | Scalar history plus isotropic/P0/MUSCL alternatives do not supply it. |
| Full moving-map JVP and physical ledgers pass | `NOT_RUN` | Stopped before deposition selection and coupled execution. |
| `PASS_REC_ISOTROPIC_PHYSICAL_REFERENCE_ONLY` | `FORBIDDEN` | Exact physical certificate and face authority are not closed. |
| `NO_PASS_REC_PHYSICAL_SPLIT` | `VALIDATED_CLAIM_CEILING` | Repository-wide physical split claim remains unpromoted. |

Terminal review disposition:
`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / STOP_BUDGET_P1_UNRESOLVED`.
