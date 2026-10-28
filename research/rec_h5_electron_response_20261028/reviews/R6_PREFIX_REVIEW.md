# Additive R6 review — reconstructed binary64-prefix response model

Reviewer: `/root/incoming_theory_review`. Unit: REC-H5-ELECTRON-RESPONSE01.

## Decision

**PASS_SCOPED for the additional mathematical model and its reviewed source-prefix mapping.** The original real-coefficient model, its original acceptance criteria, the seven reported source-bridge failures, and the original R6 records are preserved. This review authorizes no relabeling of those failures. It does not independently accept the new execution results: the all-record source parity, new model's declared gates, and final implementation/result review remain numerical and C9 obligations.

The reviewed model contract is `MODEL_COMPARISON_CONTRACT.md`, 3715 bytes, SHA-256 `f6d2c83291af1449cdb90f0603ce31920812d98a3fecf8d5146b1aa95801c995`. The whole code file at the reviewed snapshot is `code/incoming_response.py`, 22861 bytes, SHA-256 `ce47a2bc204c58c29cc0962aa78c2130e7381279953a78198d6de3fb693649ac`. The code examination here is limited to the three source-prefix functions, their constants and input meaning; it is not a full C9 implementation review. Function-specific hashes are recorded in the receipt.

## Separate status of the two models

The original G_real uses the defined real exponential/polynomial with saved represented M. The controller's preserved C8 record reports that its source-forcing bridge passed 2 of 9 controls and failed 7 at the fixed 512 eps64 criterion. The adjoint theorem remains valid for that declared real model. Failure to pass a bridge to a separate floating-point source is not a contradiction of the linear-algebra theorem.

The new G_prefix is a separately named exact-real coefficient model made from reconstructed host binary64 prefixes. It does not replace G_real, widen its tolerances or erase its failed run. Comparing these two coefficient choices is a diagnosed model comparison within the same unit and cumulative resource ledger. Any claim of source agreement for G_prefix must use its own declared checks and actual evidence.

## Verification of the specified prefixes

For each virtual bin the source C expression is left-associated:

    sv_b = fl(fl(fl(Vbb*x1)*u_b)*fl(1-omega_b)).

The function `native_prefix_data` reconstructs a_b64=fl(Vbb*x1) and pi_b64=fl(1-omega_replay). It uses the source's comparison to the binary64 literal 1e-6, large-tau `1-(1-exp(-tau))/tau`, and small-tau `tau/2-(tau*tau)/6` grouping. `prefix_coefficients` lifts these two binary64 prefixes and multiplies them in Decimal at the requested precision. This is a numerical approximation to the specified exact-real product L(a_b64)*L(pi_b64); no extra binary64 multiplication of the two prefixes is inserted into the model definition.

The Lyman prefix code follows the original sequence

    RLya64 = fl(fl(fl(kL64*H64)/nH64)/x164),
    g_alpha64 = fl(fl(3*RLya64)*x164),
    g_beta64 = fl(g_alpha64*kBeta64).

The returned order is Ly0 then Ly1. `reconstructed_source64` places Ly0 in real row 1 and Ly1 in real row 0 and uses the original c_i grouping from the saved s, x1, DAlpha, Alpha and Delta. Its virtual row operation is `(a*u)*pi`, matching the source grouping. The fixed fsR=meR=1 assumption is essential to the simplified source constant kL.

Here exp64 denotes the binary64 result returned by this host's `math.exp`; no correctly-rounded-exp guarantee or original-libm identity is inferred. Source/output bitwise agreement on the stored records can support this host's reconstruction, but does not identify unrecorded intermediate bits uniquely and does not establish cross-platform behavior. The model contract correctly keeps those distinctions.

## Reuse of the adjoint and discrepancy formulas

M and q are unchanged. Consequently the previously computed adjoint can be reused and

    J_prefix = G_prefix^T lambda,
    J_prefix-J_real = (G_prefix-G_real)^T lambda

holds in the real models. Reusing lambda entails no repeated 132-point solve or new native point call. The original conditional M/V/pivot requirements and full-state-provider limitations from R6 still apply.

The source-to-saved identity remains valid with G_prefix replacing G_real, provided the source mismatch is recomputed for that model. As before, closure of this identity is algebraic consistency, not by itself evidence that the new G is the correct source coefficient. The separately declared bitwise source reconstruction, source-forcing bridge and scalar-response checks must all remain visible.

The contract requires bitwise equality of every source entry for 132 saved primary records and all nine controls. It then applies the unchanged source/scalar/decomposition tolerances to the new model and uses its G in the independent directional checks. The old nine controls still span one direction at each of three points; this additional model does not change that rank.

## Numerical diagnosis boundaries

Both subtractions in the source expression can matter. For small positive tau in the exponential branch, error in exp64 can be amplified in `(1-exp64(-tau))/tau`, with a scale proportional to eps64/tau. For large tau, computing omega close to one and then `1-omega` can produce a relative error proportional to eps64*tau. These are analytic mechanisms to distinguish using the actual saved worst-row tau and the prescribed expm1 comparison; this review performs no such numerical evaluation and does not select one mechanism from the reported failure magnitude alone.

The frozen native M itself was assembled using the native arithmetic. G_real deliberately combines that saved M with a real reconstruction of Pi, whereas G_prefix uses reconstructed arithmetic prefixes. Neither choice becomes a physical coefficient uncertainty enclosure merely by passing source comparisons. The production HyRec source is unchanged and QSS03 coefficient-box/inverse-gain work remains separate.

## Findings and evidence status

Blocking findings in the additional model specification or the three reviewed source-prefix mappings: **0**. The interpretation of exp64 as the observed host operation, exact-real final prefix product, retained failed model, native-controls rank, and missing full-P derivatives are essential to this scoped decision.

This reviewer did not author the three functions, execute them, import the numerical module, run a source/adjoint calculation, or inspect the new model's numerical output. Only static source/document reads and metadata hashing were performed. No original R6 file was modified. The accompanying receipt identifies the preserved original R6 hashes. Actual reviewer independence is separate-agent source derivation and static review; model-family diversity is not observed or claimed.
