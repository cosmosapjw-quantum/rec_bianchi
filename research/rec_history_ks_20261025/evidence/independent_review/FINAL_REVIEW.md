# REC-HISTORY-KS01 — independent final scientific review

Reviewed at: 2026-10-25T02:20:48Z  
Reviewer: `/root/receipt_metadata`, the same independent reviewer used for theory and pre-execution code review. The reviewer did not implement the primary code or execute the scientific run.

## Verdict

**PASS_SCOPED_SAME_SOURCE_KS_AND_ACTUAL_HISTORY_ADMISSION**

Frozen criteria A–H are satisfied by the one recorded PRIMARY001 execution and the saved-data figures after one preserved layout correction. There is no remaining blocking defect within this finite scope. This closes this review episode for the actual result, its scientific interpretation, and its figures; it does not authorize another scientific execution or establish publication completion.

The new result is an interval enclosure of the stable, represented binary64-coefficient incoming operator `K_s`, together with actual original-history payload admission and local numerical consistency checks of `[J_s, K_s]`. The reused `J_s` remains numerically checked. No interval certificate for `J_s`, physical history interpolation error, full history pullback, or global evolution follows from this verdict.

## Review method and evidence identity

This postrun review read the actual JSON and NPZ files in `results/primary001/`, the execution receipts in `evidence/execution/primary001/`, the retained pre-execution evidence, and both first PNGs and the corrected PNG. The data-only readback is recorded in `POSTRUN_EVIDENCE_READBACK.json`. It performed no source import, new solve, certificate rerun, finite-difference rerun, IVP, native runtime, or old campaign replay.

The 38-file execution manifest agrees with `HASHES_BEFORE.json`, `HASHES_AFTER.json`, and `VERIFIED_IDENTITIES.json`. The implementation has the same fingerprints accepted in `PREEXEC_CODE_VERDICT.json`:

| File | SHA256 |
| --- | --- |
| `code/primary.py` | `4f70551253935117da5dbbc18f52c4db56293d16bd51bb4c137ab4eed4c6ac33` |
| `tests/manufactured.py` | `e8cf49487937466c6de4f79d930bdb44bd7f774ddb190ff59660e22c9a1c37ad` |
| `inputs/EXACT_IDENTITIES.json` | `77522e3a93cf75dac9f364071c567a51b4d2b11e6abb769a66a64b2020a206e8` |

The retained 23-input THERMO binding is reused through canonical snapshot `adddf7381edfb7d670025c651cf813594107a260acce308702f33b1d415fad54`. The fresh stable coefficient comparison records exact array agreement for `M`, `s`, `T`, `P`, `Beta`, `Tvv`, and `p`. This is evidence for the specified source and arithmetic representation, not a transfer of the previous native `K0` certificate.

## Frozen acceptance A–H

| Criterion | Observed evidence | Review result |
| --- | --- | --- |
| A — exact identity and stable representation | Retained input checks, current 38-file manifest, unchanged before/after hashes, and all seven stored/fresh coefficient comparisons pass. | PASS |
| B — inverse-residual certificate and residual | `rho = 3.458800151575591e-12 < 1`; finite, ordered `314 x 313` K endpoints; relative norm width `1.1067031540253658e-11 <= 1e-6`; componentwise backward residual `2.1996442957690597e-15 <= 4.547473508864641e-13`; zero-gross residual exact. | PASS |
| C — incoming affine controls | Both frozen incoming directions, four endpoints, and all outgoing/F/number comparisons pass. Maximum normalized error is `1.8555728462562315e-13`, below `2e-9`. | PASS |
| D — joint local controls | Both frozen directions at both steps pass all three metrics, stronger than the required one passing step per direction. Maximum normalized error is `6.684273687479512e-8`, below `2e-5`; branch/stencil ownership stays fixed. | PASS |
| E — manufactured and refusal controls | Exact Fraction 2x2 and 3x3 comparisons pass, including nonsymmetric/cancellation cases; `rho >= 1`, nonfinite, and negative epsilon refuse. Five numeric plus five Fraction RHS are recorded. Arithmetic assumptions have the recorded checks. | PASS |
| F — ionization and the same Ly-alpha event | The reviewed formulas retain the direct incident subtraction, time conversion, volume conversion, and opposite energy signs. Actual saved event arrays are finite and ordered; atomic interval endpoints are exact negatives of reversed radiation endpoints. | PASS |
| G — actual original history admission | The 35,239,470-byte payload has the required SHA256; raw members, eta, source routing, prefix, parameters, and all 313 query records are bound. Reconstruction normalized error is `3.219042386314642e-15 <= 5e-9`; last-cell interior accepted, exact upper endpoint and different cosmology refused. | PASS |
| H — actual saved-data figure inspection | First row-gain figure accepted; first joint/history figure's zero-floor distortion preserved and corrected once. The corrected actual PNG passes inspection. | PASS AFTER PRESERVED LAYOUT CORRECTION |

### Certificate interpretation

The reviewed construction is `M X = c + B u`, `o = T X + P u`, `V = M^-1 B`, and `K_s = T V + P`, with the already-reviewed source-specific `B` mapping. The inverse candidate is only a numerical candidate. The proof uses outward enclosures of `Q = I - Z M` and `R = B - M Vhat`, then the identity `(I - Q)(V - Vhat) = Z R` and the positive denominator lower bound `0.9999999999965411`. It does not substitute a BLAS residual for the outward residual proof.

The actual result is:

`1.17562722922718 <= ||K_s||_infinity <= 1.1756272292401908`.

Both maximizing row indices are 0. The per-column state error bounds range from `2.302074236660525e-15` to `5.691070685639611e-14`. Saved row gains have shape 314; K intervals and box weights have shape `314 x 313`. The actual box weights equal the entrywise maximum of the absolute interval endpoints and are nonnegative.

This enclosure concerns the exact real linear algebra defined by the frozen binary64 coefficient values, under the explicitly checked arithmetic assumptions. It does not enclose coefficient generation, transcendental functions, cosmological model uncertainty, or the derivative of a floating-point program. The norm exceeds 1, so this is a gain enclosure and provides no contraction claim. A lower box-gain bound concerns the worst-case attainable gain over a supplied box; it is not a positive lower bound on every realized output perturbation.

### Event signs, units, and raw preservation

The Ly-alpha number event derivative contains `3e6 * LYA * H * (K_s[311,j] - delta[311,j])`. The direct incident term is essential. The `1e6` factor converts the source volume convention to `m^-3`; number rate is `m^-3 s^-1`. Radiation energy uses `E21 * EV_J` and has units `J m^-3 s^-1`; atomic energy is the opposite of that same event. Ionization uses `Beta^T V[:2] / H`, and its proper-time rate uses the additional H factor. These are frozen-source coefficients, with no unassigned physical uncertainty silently absorbed into their intervals.

All 15 saved event arrays have length 313 and are finite. Number, F, proper-time, and radiation interval endpoints are ordered. The saved atomic low/high endpoints equal exactly the negatives of radiation high/low, and the point estimates have the exact opposite sign relation. The original Js opposite-energy evidence remains preserved and reused.

All 13 base/affine/joint endpoint NPZ files exist, have finite saved arrays, and retain `X[313]`, `incoming[313]`, and `outgoing[314]`. The pre-execution fixes for small-RHS accounting and immediate candidate/endpoint preservation remain closed; the preserved original code and diffs remain in `evidence/preexec_before_fix/`.

### Actual history admission and remaining physical uncertainty

The admitted original payload SHA256 is `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`. Its raw outgoing virtual, outgoing Lyman, average virtual, and energy members have individually recorded identities; incoming reconstruction uses the outgoing owners rather than the stored average virtual values. The payload does not encode cosmology. Parameter binding therefore explicitly uses the retained `input.dat` producer chain: `T0 = 2.728 K`, `nH0 = 0.18745798773143102 m^-3`, and `fsR = meR = 1`.

The causal prefix has 5,127 entries ending at index 5,126. All actual queries use `PREFIX_LINEAR_CELL` with retained cell indices 4,770 through 5,125 and source indices 1 through 313. The minimum margin to the unavailable upper domain endpoint is `5.278877512893132e-8`. The exact eta construction agrees, and no actual query uses the prehistory-zero fallback. The explicit last-cell interior check accepts, while the exact unavailable upper endpoint refuses.

The maximum absolute reconstruction difference is `2.9030081312133234e-28`; the fixed global incoming normalization is `9.018235185579106e-14`. Their recorded normalized discrepancy verifies this representation/routing reconstruction. It does not measure the physical time interpolation error of the underlying trajectory. The existence of other finer histories, same-h parity, or storage equivalence does not supply that missing uncertainty.

`CONDITIONAL_BOX.json` therefore correctly remains `INPUT_DEPENDENT_UNCALIBRATED`, with `epsilon = null` and `bound = null`. Physical reference uncertainty, endpoint uncertainty, whole-cell curvature/defect bound, and absolute history bound remain null.

## Figure review and preserved correction

The reviewer directly viewed:

1. `results/figures001/row_gain_norm.png`: accepted. Row bounds, norm enclosure, and separately displayed interval widths are legible. The plot explicitly states that no physical uncertainty is assigned.
2. `results/figures001/joint_history_residuals.png`: the unlabelled replacement of exact zeros by `1e-300` stretched the right axis over roughly 300 decades and hid nonzero residual structure. This was a concrete presentation defect, with no change to the saved scientific results.
3. `results/figures002/joint_history_residuals.png`: accepted. It retains all eight exact-zero queries at zero, labels the symlog linear region `1e-20`, shows nonzero errors and the `5e-9` criterion clearly, and identifies the four joint checks as fixed local checks rather than convergence evidence.

The first PNGs and original plotting code are preserved. The final figure receipt records no source evaluations or RHS and unchanged source hashes. The accepted row-gain PNG identity in the first-asset receipt is `be59984a9694122c4f02ced23ebc9a1929db405bfad469d4888fa4849e68c549`; the corrected joint/history PNG identity is `5e6deec3ea005609c00a6f883b36f25d3ed3370f414b1b8ee2f698a8de80e86c`.

## Actual resource accounting

PRIMARY001 is one execution, exits 0, has no timeout and empty stderr, and uses exactly 639 large RHS plus 10 small RHS. Primary child CPU is `3.58383 s`, wall is `3.6257994920015335 s`, and maximum RSS is `115188 KiB`. Its recorded limits are 45 CPU seconds, 135 wall seconds, 1 GiB address space, and one thread.

The first saved-data figures use `2.128907 CPU s / 2.173025782991317 wall s`. The single layout correction uses `1.8178819999999998 CPU s / 1.8211946119990898 wall s`. The figure subtotal is `3.946789 CPU s / 3.994220394990407 wall s`, within the total `10/30 s` figure allocation. The recorded child subtotal for the unit is `7.530619 CPU s / 7.62001988699194 wall s`, within the `60/180 s` cap. The reserved scientific repair has zero attempts. A prelaunch layout wrapper refusal is recorded separately and is not an additional primary run.

The independent saved-evidence readback separately measured its inspection section at `0.518211486 CPU s / 0.06553812300262507 wall s`, with `31000 KiB` maximum RSS. This is read-only inspection overhead, not an additional scientific solve; it is not a measurement of the entire review turn or its imports. Provider I/O, preparation, publication, and full-turn elapsed time are outside the recorded child execution subtotal. The known inherited CPU value is `24.120157 s`; older unmeasured work remains unknown. Requested execution model and observed execution model remain distinct, with observed model null.

## Claims that remain held

- H5: actual payload admission is completed in this scope; physical interpolation calibration remains `INPUT_DEPENDENT_UNCALIBRATED` with the physical quantities above null.
- H6: actual incident trace and selected Bianchi geodesic/direction/frame, measure/volume/clock, source and query owner linkage remain OPEN.
- H7: the same-source local pair `[J_s, K_s]` is supported at fixed incoming/grid/frame/query ownership. History pullback, retiming, geometry, and thermal-ODE closure remain OPEN. Js is numerically checked, not interval certified.
- Physical HOLD; `REC_U5 HOLD_9_FAIL/HOLD_8_FAIL`; `CLOSED_HOLD_NOT_RESET`; `global_convergence NOT_RUN`; `production NOT_APPROVED`; `REI_activation=false`; first failed REI raw `HISTORICAL_LOCAL_ONLY` remain unchanged.

No merge, activation, additional run, production approval, unrelated CI conclusion, or delivery completion is implied by this independent scientific verdict. The parent owns actual publication and its receipts.

## Skill context used

Parent-supplied active workflow: physmath-research-loop built-in 1.0.0 / approved v0.2. The reviewer read the provided `references/RESEARCH_POLICY.md` and `references/EVIDENCE_AND_HANDOFF.md`, reused unchanged evidence, retained failures and initial figures, distinguished identity/admission/scientific validity, and performed one finite review with the targeted corrections above. There was no subdelegation, review-of-review, provider resurvey, new literature search, or optional scientific rerun.
