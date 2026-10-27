# R9 / C1–C4 — frozen coding contract

The scientific authority is the parent. Theory is `THEORY.md`, SHA256 `6b1952f382164c760479f5c3b8bef09803bcddc86343433225f052840c6ea5f1`; R6 decision is `review/THEORY_DECISION.json`, SHA256 `431fe1e98557b6521154d6eb4e0728d3445d639adddf0941126e3daa8d776753`. R7 independently checked the two thermal identities and Peano kernel mass in Wolfram. Preserve `EXECUTION_FREEZE.json` and all historical costs/results.

## Shared boundaries

- Write only this unit's `hd_joint/` or `history_remainder/` assigned subtree. Do not modify earlier HD/H5, PB01, KS01, THERMO01 or GEO01 code/results. The root owns stage records, integration and publication.
- Original REC checkout base is `4a8e541030ee2cbd02e26ba671083b705d309d49`. The API-published continuation is `research/rec-source-synthesis-20261027`; exact remote preflight/head and source hashes accompany the new run. The temporary local index still names the original base; do not reset/rebase/commit other work.
- New scientific execution uses one thread, at most2GiB/process, under the unit caps HD360CPU s and history360CPU s. Freeze each child command before running; HD primary max60CPU/180wall, history primary max120CPU/240wall. Plotting, diagnostics and targeted repairs debit their own unit. Parent independent review/integration cap180CPU remains separate. Stop on exhausted cap, source mismatch, an ambiguous scientific criterion or a required model change.
- Record real command, exit code, start/end, code/input identity, CPU/wall/RSS and environment. Preserve failed attempts. For unknown tails use UNKNOWN_NOT_ZERO. No IVP, native/RHS replay, old matrix rebuild, historical suite replay, temperature extrapolation, collider mixing or physical-admission promotion.
- One fresh code/raw-result/figure review follows implementation. A specific finding permits one targeted repair and affected checks, preserving the original failure. Do not run unchanged successful suites again.

## HD implementation

Input: `/workspace/scratch/6104ad84b826/survey_literature/lamda_hd_live.dat`, exact2289bytes/SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`. Reuse `research/program_expansion_20261025/hd_adapter/lamda_hd.py` SHA256 `ef10b34e1891755334083340b84ff1e298151df720c13f008b3762505813e275` and the existing original source-gate evidence. Locate the parser's real file path if needed and verify its hash. Public Git receives code and derived results, not a new raw LAMDA mirror.

Implement a small callable diagnostic and runner in `hd_joint/`. Use the original eight lines and T=50,100,200K only. Construct exact rational delta = h_SI[100c(Etilde_u-Etilde_l)-10^9nu_GHz]/(k_B T), then convert for `tanh(delta/2)` and `expm1(-delta)/[-expm1(-x_E)]`. Preserve signs, analytic zeros and original level/frequency identity. Export per-case delta, paired-flux imbalance I, source/Planck deviation D and ratio1+D, exact source-gap linkage, old gate classification and source provenance.

Reference: independent 80-digit Decimal evaluation of positive fluxes `b/(1-b)` and `r/(1-b)` with b=exp(-x_nu), r=exp(-x_E), and the original exponential source ratio. Do not import/call the production formula for the reference. Compare each nonzero I,D by absolute relative error against `128*epsilon64 = 2.842170943040401e-14`; require analytic zero exactly when the constructed control has equal energies. A ratio near1 is compared as the ratio itself, while the small deviation receives its own relative check. Do not derive delta by subtracting rounded x-values.

Controls: exact-coherence synthetic input labelled as such; opposite-sign mismatch with positive gaps; invalid/nonfinite/nonpositive inputs; unsupported temperature nodes; collider blocks unchanged; no call to a qualified production line consumer that would bypass its original energy-frequency bridge gate. New numerical functions are diagnostics and cannot qualify the seven failing lines.

Produce saved JSON/CSV, a concise summary, targeted-test raw output, one bounded execution receipt and one scientific PNG/PDF from saved outputs. The figure should show signed I and D over the three source temperatures with line identities; keep the old 35Hz comparison visibly distinct. The parent/reviewer will actually inspect the PNG. No new54-rate DB suite or old parser test suite is requested.

## History implementation

Inputs: original `research/rec_history_geometry_response_20261026/inputs/history.npz`,35239470bytes/SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`; original `research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json` SHA256 `5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8`. Use original outgoing_virtual then outgoing_lyman source ordering, eta[0], dlna, prefix5127 and the313 fixed query/source/cell witnesses. Native source: `research/rec_history_thermo_20261024/vendor/hydrogen.c::interp_Dfnu`, lines633–652.

Implement exact-rational piecewise-linear value, directional slope, signed jump sum, absolute-jump bound and chord Peano remainder in `history_remainder/`. Grid is the source-native real-arithmetic t_k=Fraction(eta0)+k Fraction(dlna), with binary64 source values converted exactly. The causal domain is [t0,t5126), so reject its right endpoint and anything outside. Starting-knot derivatives must depend on travel direction; d=0 returns zero without requesting an invalid exterior derivative. Do not apply a positive curvature-only smooth bound across a corner.

Actual binding must verify every313 exact-grid cell against the frozen witness, all source indices and the original metadata. On mismatch stop for authority; do not shift a cell or invent rounding slack. Preserve original source/native reference. Record exact clock differences versus stored eta-array knots and the nominal-value anchor difference for the new native-real reconstruction, separately from the previous stored-geometric anchor.

For each actual query:

1. Two within-cell targets are midpoints from q to the native left/right knots.
2. Left/right crossing targets are neighboring-cell midpoints when available under the fixed prefix. Derive counts from data. Twelve frozen final-cell witnesses currently imply unavailable right crossings; report these as `SKIP_CAUSAL_PREFIX`, not failures or extrapolated runs.
3. Compute direct `P(target)-P(q)-d*slope_directional` and the signed finite jump sum independently; require exact rational equality. Require absolute remainder <= absolute-jump bound exactly. Show that a dropped-jump/zero-curvature mutation fails when actual remainder is nonzero; do not require a nonzero result from an identically flat source.
4. Construct a chord between adjacent-cell midpoints. On a side lacking an adjacent cell, use midpoint(q,current-cell-endpoint) for that side. Require a<q<b and strict causal validity. Compare direct chord error and negative Peano jump sum exactly, with exact bound inclusion.

Small controls use independently constructed affine functions, one hinge/absolute value in both directions, multi-jump cancellation, a starting knot, a target knot, zero step, nonuniform grids if generic support is offered, reversed/duplicate knots, final causal endpoint and out-of-domain requests. A mutation changing the negative-path sign or including the starting atom must be caught.

Output exact identities and display values, actual executed/skipped counts, maximum represented remainders and bounds, conditioning/cancellation where meaningful, source mapping and clock-difference diagnostics. Save an actual-data figure distinguishing zero within-cell remainder from crossed-knot cases and the absolute-jump envelope. PNG and PDF are generated from saved results. This is a representation result: `physical_epsilon=null`, `physical_bound_coverage=0/313`; do not edit or feed invented constants into the earlier H5 bound consumer. Ks and all GEO roots/matvecs are reused only as historical context, not executed.

## Positive transition after acceptance

After exact/source/numerical checks and independent review pass, publish the diagnostics and represented-history module with scoped claims. Apply additive observations to existing HD/H5/REC-HISTORY wrappers, preserve latest BASS/REI owner returns and the original88 contracts, then deliver source/input ZIPs and dual-provider receipts. The original programme numerator stays32 unless its original full node obligations have actually been met; this unit alone supplies no such promotion.
