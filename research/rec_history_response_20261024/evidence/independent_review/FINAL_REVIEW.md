# REC-HISTORY-RESP01 independent scientific review

## Decision

**PASS_SCOPED_REPRESENTED_OPERATOR_AFTER_DIAGNOSED_CHECK_REPAIR.** No unresolved material scientific blocker remains for this finite unit. The accepted result is the full fixed-source response and its enclosure for the exact real matrices represented by saved binary64 M, B, T and P, together with query-indexed conditional weights and the one-event number/energy response. It is not an absolute history-error certificate, thermodynamic Jacobian, full angular calculation, or physical completion decision.

This is the conclusion of the same independent review session that produced PREEXEC_REVIEW.md. The reviewer inspected source, derivation, implementation, saved observations, diagnosed repair and first figures. Reviewer scientific numerical probes, old-test replays, native evaluations, solves and provider mutations were all zero. Saved JSON/CSV inspection and NPZ-header inspection did not recompute scientific arrays. Requested review role was Astra; an independent runtime model identifier was unavailable.

## Retained primary findings

The original primary ended with **exit 2 / FINDING_RETURN_TO_ASTRA**. That history is retained unchanged, not replaced by an invented primary PASS. Its interval certificate and planned exact controls already passed:

| Quantity | Saved observation |
|---|---:|
| rho upper bound for norm of I-ZM | 3.5019104723714056e-12 |
| outward denominator lower bound | 0.999999999996498 |
| induced infinity norm lower bound | 1.175627229227178 |
| induced infinity norm upper bound | 1.1756272292401924 |
| selected nominal maximum row | 0 |
| exact point-dot probes | 32 each for ZM, MV, ABSZ_ABSR, TV; 128 total, all pass |
| exact manufactured inverse systems | 4, all pass |
| dense algebraic RHS columns | 627 |

Zero/identity, cancellation, signed interval products, min-normal/2 and min-subnormal/2 controls passed. Nonfinite, overflow and invalid epsilon controls refused as intended. A deliberately unverified inverse produced rho=1.0000000000000007 and certificate refusal as intended.

The row-0 independent witness was already inside the signed response interval and between its certified row-gain bounds. No coefficient sign was uncertain for that row. The genuine primary failures were two native floating-arithmetic comparisons at virtual row 310; neither was a failure of the interval certificate.

## Diagnosed failure and bounded repair

Native virtual output is evaluated as u+(eq-u)*A. The original diagnostic gross scale used the algebraically combined coefficients, |T||x|+|P||u|. When A is close to one, P=1-A is small while the imperative evaluation still subtracts and re-adds an order-|u| quantity. Thus the original scale omitted real intermediate-operation magnitudes. The original row-310 CSV tau is 19.211816766711749, consistent with this cancellation mechanism.

For direction 3, the saved native outgoing residual was 9.44475617506435e-17, while the defective allowance was 5.795686339313739e-18. For the existing all-channel witness, the row-310 residual was 3.417777942171102e-17 versus 2.6927198692885805e-18. All other original comparison components passed.

The reviewer returned this material test-scaling defect to the controller. The controller authorized one lower-tier saved-data repair. For virtual rows only, the diagnostic now includes an additional 2|u| in the gross scale, which conservatively covers the native |u| and |A u| intermediates for 0<=A<=1. Source diagnostics and line rows are unchanged. The multiplier stays 512*eps64. This is an operation-magnitude correction, not a physical tolerance or arbitrary small-net floor.

Inspected code/recheck_saved_diagnostics.py reads the existing residuals/scales, reconstructs only the frozen elementary direction vectors, applies that scale correction and records before/after identities. It does not call the source map, form matrix products, solve a system, repeat exact tests or recompute a certificate. Its observed outcome is **PASS_SAVED_DIAGNOSTICS**, all nine groups and 2,822 componentwise comparisons pass, with the original primary outputs unchanged. The revised allowances at the two formerly failing components are 2.0511081385796724e-13 and 2.2737636816310133e-13 respectively. The code change in checks.py/run_primary.py makes that same corrected diagnostic reproducible; it was not used to rerun the primary.

The original failure is therefore resolved as a false-FAIL comparison criterion. This resolution admits the existing finite scientific result without silently altering its arrays or rerunning completed science.

## Proof, representation and source interpretation

The pre-execution assessment of the resolvent and outward arithmetic stands. rho<1 proves nonsingularity of represented M. Each outward residual product and the downward-rounded positive denominator propagate to a valid column error bound, then to componentwise K intervals. Finite checks and outward elementary multiplication/addition account for the declared gradual-underflow model. The preliminary numerical inverse and solve remain candidates only; they do not supply the enclosure proof by themselves.

The represented operator is K=T M^-1 B+P. Native evaluation order and coefficient construction are separately compared; the report must not turn gross-scale parity into exact equality with the native imperative floating program. Similarly, no libm transcendental enclosure is inferred. This distinction is particularly material because it explains the diagnosed comparison defect.

The certified induced infinity norm is strictly greater than one. This establishes worst-case amplification for a unit incoming occupation-error box at this frozen snapshot; it does not say that every error vector is amplified, that the history trajectory is unstable, or that an actual physical error has that size. The per-row sharp-box proof is valid, with distinct rows potentially requiring distinct sign vectors. The local frozen-population exp(-tau/q) multiplier from H01 is a different derivative and does not contradict this solved-population result.

Number-response coefficients use m^-3 s^-1 per occupation, with outward native normalization products. Energy-response coefficients use J m^-3 s^-1 per occupation. Atomic and radiation energy are opposite signs of the same event scalar, not two independently added sources. The exact paired energy sum is zero by definition. Query indices/energies/redshift metadata retain the original source-owned routing.

H01 already supplied three dense history directions, a positive-comparison witness and two manufactured conditional envelopes. RESP01 advances the full 314-by-313 response, its componentwise enclosure, and per-query conditional error allocation. No new general matrix theorem or first rigorous bound is claimed.

## Artifacts, figures and resource observations

RAW_RESPONSE.npz headers contain the full 313-by-313 M/B/Vhat/Z, 314-by-313 T/P/Khat/Klo/Khi, residual bounds, column bounds, row gains, witness arrays and all 313 number/radiation/atomic coefficients and intervals. The exported CSVs contain 314 row gains, 313 query records and 313 ranked contributors. The physical epsilon field remains absent/null; no physical epsilon is silently set to a unit vector.

The reviewer actually viewed both original first PNGs: absolute_response.png and query_event_contributions.png. They are readable and unclipped. The heatmap displays log10 absolute nominal response; the contribution curves display coefficient magnitudes. The event plot therefore does not convey coefficient signs; signed CSV coefficients are authoritative, and the controller's figure notes explicitly state that convention. Original PNG/PDF artifacts remain retained with no rerender required.

Saved local receipts report primary CPU 3.203344 s / wall 3.2247228199994424 s, repair CPU 0.107592 s / wall 0.11499967400050082 s, figures CPU 2.765718 s / wall 2.772379770000043 s. Total local measured CPU is 6.0766539999999996 s and execution wall 6.1121022639999865 s, within the frozen 45 CPU / 90 wall caps. Dense RHS columns remain 627; additional repair RHS columns, source actions and certificate recomputations are zero. New IVP, native runtime and old campaign replay remain zero. Provider I/O and full-turn elapsed time are separate; external symbolic CPU is not invented.

## Admission ceiling and stopping decision

The complete finite source-operator unit may be reported as scoped PASS after the documented diagnostic repair. The actual physical history epsilon/reference, full angular supplier and full thermodynamic Jacobian remain open. Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED and REI_activation=false remain in force. A finite 20/20 workflow and actual provider publication/backup states must be reported separately from those scientific dependencies.

No further numerical verification is requested. The single-session review is complete; proceed to scoped reporting and the already authorized publication/backup closure.
