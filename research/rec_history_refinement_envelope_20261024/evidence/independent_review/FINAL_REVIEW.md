# Independent scientific review — REC-HISTORY-REFINE01

## Decision

**PASS_SCOPED_STORED_HISTORY_ENVELOPE.** The single completed primary run supports the discrepancy decomposition and outward enclosure of the exact cell supremum of the selected stored binary64 interpolants. No unresolved material defect blocks this scoped result. No additional numerical probe, primary replay, trajectory solve, or new audit layer is required.

This decision does not admit an absolute physical error, a convergence order, the original target history, production use, or REI activation. Physical HOLD and all inherited claim ceilings remain in force.

Reviewer: fresh independent Astra review role, task `/root/refinement_independent_review`; the reviewer did not author the contract or implementation and did not execute numerical science. Runtime model identity was not independently exposed by the execution tools. This is one review session, including closure of the controller-authorized narrow correction before the first primary run.

## Evidence inspected

The review inspected CENTRAL_AGENTS.md, FROZEN_CONTRACT.md, THEORY.md, inputs/CASE_PLAN.json, the candidate source manifest, producer receipt identity binding, source intake and native guard clarification, and retained producer passages establishing branch/event ownership. It read all four implementation modules and the executed source/input snapshot, primary COMMAND/RESOURCE_RECEIPT, empty stderr, SUMMARY, all synthetic control outcomes, Fraction oracle structure and representative exact rational records, per-channel CSV records, and compressed raw NPY headers and selected stored numerical entries. No scientific array comparison was rerun by the reviewer.

The current source/input files match the primary execution snapshot. Important executed SHA256 values are:

| Object | SHA256 |
| --- | --- |
| code/envelope.py | 4ead3162b2fee2f91255fbd24b78440dc7db436b2d3ee6f74fd1425ef79ef232 |
| code/analyze_pair.py | dbca47c6622bd2b918dcbe6f654feed4fe83aca1d4ca9ebca68fc7692b8cf150 |
| inputs/CASE_PLAN.json | 6711a193e553cf684e74d42d12bc3e76ec6ff72a842a5e72e023cf990976d154 |
| Coarse original | 70274c9631b33e4ed1c4b8761608cd9ce22f82d96b0afbcb36c0e786e2c04c6d |
| Fine original | 7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9 |

Figure rendering and actual PNG visual inspection are recorded separately by the controller. This scientific decision does not claim that the reviewer inspected image pixels.

## Mathematical and numerical assessment

The decomposition D(u)=(1-u)E0+uE1+2min(u,1-u)delta follows by direct subtraction on each half-cell. Because D is affine on each half-cell, convexity of absolute value bounds it by the two endpoint magnitudes on that half-cell; the union gives exactly the three witnesses at u=0, 1/2, 1. The midpoint is calculated directly from coarse endpoints and the fine midpoint, separately from its decomposed expression. The continuous interpolation remainder and conditional reference inequalities are correctly distinguished from what the stored samples themselves establish.

The interval implementation widens each subtraction, addition, and multiplication by 0.5 using nextafter, then applies the correct interval absolute-value map and maximum of three lower/upper bounds. This encloses the exact stored-table supremum under the stated IEEE binary64 arithmetic model, including subnormals. It is not a bound on an unrepresented physical solution. The actual controls include a minimum-normal/2 exact rational witness, which checks gradual underflow, and a minimum-subnormal/2 enclosure witness. Both passed. Overflow and nonfinite rejection are implemented and exercised for the comparison path.

The Fraction oracle constructs the two interpolants directly from Fraction.from_float inputs, independently of the decomposition implementation. It checks both query paths and compares exact rational cell maxima with rational conversions of interval endpoints. The local arithmetic allowance is 64 eps64 times the maximum absolute value of the five local input samples plus eight least subnormals, without a unit-scale floor. This is an implementation check, not a physical tolerance.

The run retained 238,326 channel-cells and 714,978 witnesses, with 314 outgoing channels ordered virtual_out[0..310], then lyman_out[0..2]. The raw arrays have the prescribed shapes, both source tables are retained, and the four masks and field/index mapping are present. The CSV contains 1,256 rows, one per channel and mask. average_virtual is excluded.

## Domain, causality, and source ownership

For the selected validated full tables, the operational domain is 0<=x<759 and the analysis closure is 0<=x<=759. The direct query checks bracketing indices against both face-owned committed prefix lengths; for integer prefix lengths this enforces x<min(Nc-1,(Nf-1)/2,759). It correctly admits x=0 with sufficient committed history and rejects the upper operational endpoint. Native iz>=2 is a prefix-length requirement, not x>=2.

The decomposed query additionally requires the complete fine cell, including its right fine endpoint. A direct left-half query can therefore be available while the decomposition is not. This conservative availability difference prevents future reads and does not invalidate any actual comparison, which uses the complete selected tables. Users of the helper should preserve this documented distinction rather than assume the two APIs have identical availability for partial prefixes.

Startup-origin cells 0..7, post-startup cells 8..758, continuation-before-event cells 8..757, and event cell 758 are consistent with the source ownership. Continuation-only statistics retain propagated startup effects. The final cell has C758/F1516 on H_HE, F1517 as the first H_ONLY input, and C759/F1518 on H_ONLY; event.iz denotes the updated state, not the outgoing input index. The histories share their own source frame/cosmology, but their startup memories, zero-feedback durations, and event histories are not assumed identical. Their discrepancy cannot isolate a time-stepping mechanism or infer an integration order.

## Actual outcomes

All 26 synthetic controls passed. All 350 exact rational point checks and all 70 exact rational enclosure checks passed. The full-array midpoint residual check passed; its largest residual/tolerance ratio was 0.015607467292599894 at channel 138, cell 667, with residual 7.888609052210118e-31 and allowance 5.054381280651739e-29. The largest oracle error/tolerance ratio was 0.017121122007845685, on the direct path at channel 154, cell 1, u=3/4.

| Cell mask | Largest stored discrepancy B |
| --- | ---: |
| Startup origin | 1.8537853650065213e-16 |
| Post-startup | 1.6498272419025407e-15 |
| Continuation before event | 4.601037190915281e-17 |
| Event straddling | 1.6498272419025407e-15 |

The global maximizing recorded witness is lyman_out[0], channel 311, cell 758, u=1. Its enclosure is [1.6498272419025405e-15, 1.649827241902541e-15], with recorded B=1.6498272419025407e-15. This is the excluded operational endpoint x=759, retained legitimately as a closure witness and the one-sided supremum. It must not be presented as an admitted operational query. The recorded normalized discrepancy for that channel is 0.2919868991524095 relative to its full admitted history scale; small absolute occupation-departure units do not establish high physical accuracy. Fine detail and nodal discrepancy can partly cancel: the last-cell detail for channel 311 is -1.6599938418419126e-15, while its midpoint difference is -8.350793367332902e-16.

The primary process exited zero with empty stderr, no timeout, no controller exception, and no source changes during execution. It used 2.242494 inclusive child CPU seconds and 2.271521004004171 execution wall seconds, with peak RSS 97,324 KiB, within the 16 CPU/45 wall/1 GiB primary caps. The receipt accurately describes process-local CPU enforcement and post-exit inclusive accounting; it does not claim a live aggregate monitor.

## Narrow correction closed within this review

Before the first primary run, the controller authorized outward rounding and overflow rejection for the conditional scalar physical_bounds helper, explicit documentation that its supplied binary64 D is treated as exact and that callers must supply any discrepancy arithmetic uncertainty, and the two explicit underflow controls. The primary snapshot contains those corrections and their passing controls. The certified whole-cell interface remains physical_cell_upper(B_upper, eps_ref_cell), conditional on a justified same-domain fine-reference certificate. No completed primary was invalidated or repeated.

All actual reference-error, endpoint-uncertainty, physical-M2, absolute-physical-bound, convergence-order, and physical-goal-completion fields remain null. The original target coverage remains 0/313 and the selected source T0=2.7255 K differs from the original target T0=2.728 K. No physical reference was supplied or inferred.

## Admission and next action

Admit this finite represented-history comparison and its retained arithmetic evidence. Proceed to the already authorized final report, inspected figures, checkpoint and draft delivery without more numerical execution for this unit. Preserve Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false; REC-HISTORY parent PARTIAL; H5 INPUT_DEPENDENT_UNCALIBRATED. No strong no-go conclusion is made.
