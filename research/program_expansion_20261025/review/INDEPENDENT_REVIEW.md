# Independent decision: HD parser and H5 source binding

Date: 2026-10-25 client date. Reviewer: `/root/independent_review`, separate from both implementation agents. This is one source/code review pass with verification of its bounded repairs. The reviewer did not edit either implementation, run prior compiler fixtures, rebuild the old response matrix, evaluate an RHS or integrate a trajectory.

## Decision and exact scope

**Accept the pinned HD literal parser and the actual-source H5 binding/conditional evaluator within their implemented scope.** Two scientific input gates remain open:

| Object | Independent decision | Remaining obligation |
|---|---|---|
| HD source/level/line/collider parser | `PASS_IMPLEMENTATION_REVIEW` | Retain the original input identity and unsupported domains. |
| Complete original HD adapter contract | `HOLD_SOURCE_DISCREPANCY_UNQUALIFIED` | Resolve the supplied level/frequency discrepancy in lines 2–8 against the original source. |
| HD internal-energy/photon bridge | Line 1 meets the fixed catalog-rounding gate; lines 2–8 are refused | Catalog-rounding compatibility does not supply experimental uncertainty. |
| H5 actual 313-query/626-endpoint/operator binding | `PASS_ACTUAL_SOURCE_BINDING_REVIEW` | Supply the actual source-matched continuous bound evidence. |
| H5 conditional bound evaluator | `PASS_CONDITIONAL_IMPLEMENTATION_REVIEW` | An external proof artifact's bytes are not its mathematical approval. |
| H5 physical epsilon and outgoing bound | `INPUT_DEPENDENT_UNCALIBRATED`, both `null` | Actual bound coverage is **0/313**. |

Production approval, REI activation and global physical completion remain unchanged. The requested implementation work has produced usable code, actual source bindings and a source discrepancy; these results do not close the full physical programme.

Final reviewed code identities:

- `hd_adapter/lamda_hd.py`: `ef10b34e1891755334083340b84ff1e298151df720c13f008b3762505813e275`.
- `h5_input_binding/code/h5_bounds.py`: `a797c75ad987cdaadd3c7ffc08888c3ae09ab4b02700c4b028291c938e4225b2`.
- Actual H5 context: `5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8`.

`HD_INDEPENDENT_REFERENCE.json` records the earlier HD snapshot tested in full. `H5_INDEPENDENT_CHECK.json` records the final HD hash, direct review of its changed Decimal-context path, and the selective precision-4/precision-80 closure checks. The unchanged source/data evidence is reused. The subsequent root finding H5-R3 was reproduced and closed within this same review pass; `evidence/h5_tube_radius/CLOSURE.json` records the final H5 hash and six targeted independent controls. The preceding H5 full check remains valid for unchanged source/arithmetic paths and is not relabelled as a run against the final hash.

## HD: original rows and independent arithmetic

The reviewer read the actual 2,289-byte source with SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`, the canonical WU `Species` constructor and the fixed central HD contract. A separate header/row reader supplied the reference tokens. Exact `Fraction` arithmetic checked the nine level energies, eight line frequencies and 54 collision-rate unit conversions, independently of the adapter's Decimal operations. The canonical WU implementation mapped the nine J-labelled levels to neutral 1H–2H species, preserving `v=UNSPECIFIED` and the distinct p-/o-H2 collider identities.

The exact source calculation is

\[
\Delta\nu_{ul}=\left|299792458\times100\,(E_u-E_l)_{\mathrm{cm}^{-1}}
                  -10^9\nu_{ul,\mathrm{GHz}}\right|.
\]

The source's first line has `8.2410162 Hz` discrepancy and meets the fixed 35 Hz gate. Lines 2–8 exceed it; line 2 gives `947678.840324 Hz`, and the maximum is `1827572.5607572 Hz` for line 6. All exact values are in `HD_INDEPENDENT_REFERENCE.json` and `../hd_adapter/SOURCE_DISCREPANCY.md`. The original full test failure remains in `../hd_adapter/raw/attempt1/`; no source value or tolerance was changed. The new bridge refusal follows this actual source result.

The independent high-precision checks gave:

- 54 upward rates: maximum normalized difference from independently evaluated 80-digit Decimal detailed balance `2.0746076942048495e-15`.
- 24 thermal line cases: independent high-precision Planck/Kirchhoff comparison passed the original `128 * binary64 epsilon = 2.842170943040401e-14` criterion.
- Explicit refusals for 75 K, temperatures outside support, a combined/unspecified collider and an absent collision pair passed. Positive values lost to binary64 underflow are distinguished from analytic zero. A population inversion retains negative net absorption.

Detailed balance uses the tabulated level-energy gap; the LTE algebra check uses the identical catalog photon energy in the population ratio, Planck function and Einstein relations. Those are separate checked constructions. Their algebraic consistency does not repair the seven incompatible level/frequency pairs. Einstein B multiplies mean specific intensity J_nu, and the line-profile normalization remains the caller's declared input.

## H5: source binding, derivation and computation

The corrected central conditional derivation and its prior independent review were read directly. The Gronwall bound, orientation change for backward eta, fixed dimensional state scales, strict tube bootstrap and pointwise interpolation coefficient `a(1-a)/2` remain valid under their stated assumptions. The evaluator preserves the distinction between continuous-domain bounds and sampled residuals/second differences.

The original history identity was read back as 35,239,470 bytes, SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`. The actual context binds 313 fixed represented queries, 626 distinct endpoints and the existing 314-by-313 entrywise K_s intervals. The independent readback checked incoming indices 0, 14, 156 and 312 directly against the original NPZ and stored chart; index 14 contains the largest representation term. The owner implementation checked all 313 rows. The same source, causal prefix, eta clock and native reference remain explicit.

For a fixed represented query, the new exact source term is

\[
b_{\mathrm{repr},j}=
\left|u_{j,\mathrm{stored}}-
\left[(1-a_j)y_{L,j,\mathrm{stored}}+a_jy_{R,j,\mathrm{stored}}\right]\right|.
\]

It is nonzero for all 313 queries and has maximum
`2125323597749/7573333069425850157122243222373270552576`, approximately
`2.806325270875912e-28`. This term measures the actual difference between the stored incoming value and exact geometric interpolation of the represented endpoints. It is an additive representation contribution, distinct from endpoint errors, model discrepancy, physical curvature and query retiming.

The implemented conditional expression is

\[
\epsilon_j=(1-a_j)e_{L,j}+a_je_{R,j}
 +\frac12 M_{2,j}(q_j-\eta_{L,j})(\eta_{R,j}-q_j)
 +b_{\mathrm{repr},j}.
\]

The actual input packet supplies no `e0`, differential defect, stability L, tube radius, native-channel Lipschitz/reference bound or whole-cell curvature proof. Its consumer correctly returns `BLOCKED_ACTUAL_BOUND_INPUTS`, coverage 0/313 and null physical bounds. The inverse-certificate rho is labelled as a matrix quantity and is not used as an ODE defect or physical tube radius.

The positive-series exponential enclosure is mathematically constructive: after scaling to `0 <= z <= 1`, the N=48 tail is bounded by `t_49/(1-z/50)`, since every later term ratio is at most `z/50`. Repeated squaring preserves the upper direction. For L=0 the Gronwall evaluator uses the exact limit `e0+d*s`. With nonnegative e0, L and d, its state-radius upper bound is nondecreasing in oriented path length, so the strict terminal comparison `E_upper < rho_lower` is sufficient for the stated scalar bootstrap condition. Here `rho_lower > 0` must be a certified lower bound on a safe tube radius. Its proof must cover the entire open tube of at least that radius about the same reconstruction, in the same fixed weighted norm and over the same eta domain. An upper bound on the safe radius cannot establish this inclusion. The proof content remains conditional pending independent scientific review.

Sharp quadratic interpolation, zero-L, endpoint and positive-exponential controls passed. Six independent exponential cases, including the initially failing 63.5 serialization case, retained containment after outward decimal serialization. The preceding 36 implementation tests passed. After H5-R3, the owner ran only 10 affected/new controls successfully, and this reviewer independently checked six radius-direction cases; the full suite was not rerun. Their manufactured proofs remain explicitly labelled and do not populate the actual physical packet. The old K_s certificate and completed PB01 work were not replayed.

## Findings and closure

| ID | Observed issue | Smallest correction and result |
|---|---|---|
| HD-R1 | Positive Decimal population/profile could become zero during conversion or coefficient arithmetic, producing a false analytic-zero label; tiny temperature could underflow the k_B T denominator | Explicit conversion/output underflow checks and stable exponent order; affected regression and independent refusal cases passed. **Closed.** |
| HD-R2 | Seven literal energy/frequency pairs fail the original 35 Hz criterion | Preserve source columns and first failure, expose per-line qualification and refuse their common energy bridge. **Source obligation remains open; implementation disposition accepted.** |
| HD-R3 | Ambient Decimal precision could affect the floating upward-rate construction | Fixed local precision for the energy gap and explicit binary64 degeneracy ratio; final precision-4/80 controls agree. **Closed.** |
| H5-R1 | `str(exp_upper(63.5))` exceeds Python's 4,300-digit integer-string limit inside the declared implementation range | Exact integer floor/ceil onto a 64-significant-digit decimal grid for output bounds; internal rational arithmetic and exact source representation terms retained. Upper quantities round upward and the tube margin rounds downward. Original failure is preserved in `H5_SERIALIZATION_FIRST_FAILURE.json`; full candidate regression and independent containment checks passed. **Closed.** |
| H5-R2 | Missing-input report used `continuous_reconstruction` while the evaluator required `reconstruction` | Match the executable input key and reconsume the actual missing-input packet. **Closed.** |
| H5-R3 (P1, `scientific_input_semantics`) | Root found that `tube_radius.upper` was consumed as a guaranteed safe radius. Independent reproduction with `E_upper=1/2` and radius upper `1` returned a candidate and claimed margin `1/2`, although a safe radius `1/10` is compatible with that upper. | Require a positive, proof-referenced `tube_radius.lower`; reject upper-only, compare strict `E_upper < rho_lower`, and serialize `rho_lower-E_upper` downward. Same-tube proof coverage is explicit. Six independent controls passed: upper-only refusal, equality refusal, misleading-upper refusal, zero refusal, missing-proof refusal, and valid lower `3/4` giving exact margin `1/4`. **Closed within the same review pass.** Original code/finding/reproduction remain in `evidence/h5_tube_radius/`. |

No unresolved implementation finding prevents the scoped adoption above. The two open scientific input obligations are the actual HD source discrepancy and missing H5 continuous-bound evidence; neither is a no-go result.

## Evidence and measured review cost

Reproducible reviewer scripts: `check_hd_independently.py`, `check_h5_independently.py` and `check_h5_tube_radius_direction.py`. Their actual results are `HD_INDEPENDENT_REFERENCE.json`, `H5_INDEPENDENT_CHECK.json` and the two runtime receipts in `evidence/h5_tube_radius/`. The bounded serialization failure is separately preserved. The original three measured processes used **0.348280 CPU seconds**. The H5-R3 reproduction and targeted closure added **0.063903 CPU seconds** and approximately **0.007086 inner-wall seconds**, under their frozen aggregate cap of CPU 10 seconds / wall 60 seconds / 1 GiB / one thread, within the shared review/integration budget. These five measured processes therefore total **0.412183 CPU seconds**, with maximum observed RSS **57,916 KiB** and approximately **0.278770 inner-wall seconds**. These are reviewer-process costs; separately measured owner controls/plots must not be merged or counted twice. One earlier scalar J1→0 reference probe, file reads, tool/network/model time and final receipt writes were not measured as complete process cost and are `UNKNOWN_NOT_ZERO`. No whole-turn cost claim is made.

The current final code and saved results are sufficient for root integration/publication of this limited decision. The two physical input gates above must remain visible in the DAG and next handoff.
