# Independent theory review — REC source synthesis

## Decision and execution scope

**PASS for the stated represented-history and fixed-column identities after two minimal scope clarifications, both now closed.** Equations (1)–(7) are mathematically correct under the repaired assumptions. The coding contract may freeze these formulas and source-preserving conventions. This decision does not certify an implementation or admit either an HD source repair or a physical H5 error bound.

This was one independent R6 pass, followed only by readback of the two repairs. The reviewer changed only this review and its JSON decision. No recursive reviewer, numerical science script, symbolic service, historical test, native interpolation execution, IVP, or matrix reconstruction ran. Source reads, metadata parsing and hashing were performed. Controlled scientific-process CPU debit is 0 because no such process ran; metadata/I/O costs were not measured and are `UNKNOWN_NOT_ZERO`.

Requested identity: fresh independent Astra theory reviewer. Actual runtime model identity is `UNKNOWN_NOT_EXPOSED`; the role request and model labels are not an independently observed runtime receipt. Requested workflow remains the parent's user-locked canonical 1.0.0 task. A discoverable 1.3.0 skill and an archived 1.3.0 review guide were read as supplementary instructions; neither replaced the locked task or its scientific criteria.

Reviewed inputs: `RESEARCH_CONTRACT.md`, `EXECUTION_FREEZE.json`, `CLAIMS_AND_ASSUMPTIONS.md`, `EXPLORATION_AND_SELECTION.md`, `THEORY.md`; native `research/rec_history_thermo_20261024/vendor/hydrogen.c` around `interp_Dfnu` and its callers; original `research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json`; and the preserved original HD data header and transition rows. Exact reviewed hashes are recorded in `THEORY_DECISION.json`.

## 1. Independent direct-flux derivation

Put `r = exp(-x_E)`, `b = exp(-x_nu)` and `C = n_l (g_u/g_l) A_ul`. The stated positive temperature, gap, frequency, degeneracies, population and A coefficient imply `0 < r,b < 1` and `C > 0`. Using a Planck occupation gives, directly,

    R_up   = C b/(1-b),
    R_down = C r/(1-b).

Therefore `R_down/R_up = r/b = exp(-delta)` and

    (R_up-R_down)/(R_up+R_down)
      = (b-r)/(b+r)
      = (1-exp(-delta))/(1+exp(-delta))
      = tanh(delta/2).

This independently fixes the sign: a larger level gap suppresses the downward population relative to the photons, so the defined upward-minus-downward imbalance is positive. A smaller gap gives the reverse sign. For a zero mismatch the two fluxes coincide. Since `|tanh z| <= |z|`, the bound in the draft follows without a small-mismatch approximation.

The same substitution gives `S_nu = (2 h nu^3/c^2) r/(1-r)` and `B_nu = (2 h nu^3/c^2) b/(1-b)`. Thus

    S_nu/B_nu - 1
      = [r(1-b)-b(1-r)]/[b(1-r)]
      = [exp(-delta)-1]/[1-exp(-x_E)].

This verifies the `expm1` form, its denominator sign, and its opposite sign to the paired-flux imbalance. It also supplies an additional algebraic consistency relation, with `I` as defined in the draft:

    D [1-exp(-x_E)] = -2 I/(1+I).

The source function is understood on the nonzero line-profile support, or as the line-coefficient ratio extended through a profile zero. The population factor in the absorption coefficient is positive; a normalized physical line profile is nonnegative. No population inversion or absorption-sign reversal is introduced by a small mismatch while `DeltaE > 0`.

The mean-intensity Einstein convention is internally consistent: `A_ul/B_ul = 2 h nu^3/c^2`, with upward/downward stimulated rates defined using `J_nu`. The `4 pi` factors in emission and absorption cancel. The scalar identities do not depend on a spacetime metric convention.

The original source labels level values in `cm^-1` and frequencies in `GHz`. Its correct direct construction is

    DeltaE = h c 100 (Etilde_u-Etilde_l),
    nu = 10^9 nu_GHz,
    delta = h [100 c (Etilde_u-Etilde_l)-10^9 nu_GHz]/(k_B T).

This expression is dimensionless and retains exact decimal source values and exact SI conversion factors until the final conversion. It avoids subtracting independently rounded dimensionless energies. The tabulated rounded `E_u/k(K)` column is not a replacement for the declared level column. `h = 2 pi hbar` is the frequency rather than angular-frequency convention; no natural-units substitution is implied.

Eight lines at the three existing nodes give 24 intended diagnostic cases. These radiative identities make no use of collision-rate averaging and do not qualify the source. The old 35 Hz rule and its seven failures, separate para-/ortho-H2 data, and prohibition of temperature extrapolation remain intact. The 24 numerical outputs and their 80-digit references are prospective implementation evidence, not results of this review.

## 2. Independent hinge proof of both retiming directions

For one hinge `H_tau(t) = max(t-tau,0)`, the right derivative at `q` is `1_{q >= tau}` and the left derivative is `1_{q > tau}`. The difference at a starting knot is essential.

For `d > 0`, direct evaluation of the hinge yields

    H_tau(q+d)-H_tau(q)-d H_tau'(q+)
      = q+d-tau,  if q < tau < q+d,
      = 0,        otherwise.

For `d < 0`, the same case split gives

    H_tau(q+d)-H_tau(q)-d H_tau'(q-)
      = tau-q-d,  if q+d < tau < q,
      = 0,        otherwise.

In both directions the crossing weight is nonnegative. The sign of a crossing contribution is the sign of the slope jump. Summing these identities with coefficients `J_k`, while the affine term has zero remainder, proves (5) and (6). In particular, the negative-direction formula has a plus sign in front of `J_k`; reversing the travel direction does not negate this remainder.

At the starting knot the directional derivative has already absorbed the relevant slope, so the starting atom is correctly omitted. A target-knot atom has zero weight. For `d = 0` the value difference and remainder are zero. At the left boundary only admissible positive motion is needed; a left derivative outside the represented domain is not requested. Strictly admissible endpoints in the interval imply the entire retiming segment stays in the domain.

The `P(t)=|t|` examples in the draft check both directions: from `-1/4` to `1/4`, and conversely, the direct remainder is `1/2 = 2(1/4)`. Starting at zero gives zero directional remainder on either side. Signed sums can cancel for several knots; replacing jumps by their absolute values produces a valid upper bound, not generally equality.

## 3. Independent chord calculation and regularity

For a hinge with `a < tau < b`, its endpoint chord is `(x-a)(b-tau)/(b-a)`. Direct subtraction gives

    H_tau(x)-L H_tau(x)
      = -(tau-a)(b-x)/(b-a),  tau <= x,
      = -(x-a)(b-tau)/(b-a),  x <= tau.

This is exactly `-G_x(tau)`. Hinges outside the chord interval are affine or zero on the interval and contribute nothing. Summing over jumps proves the piecewise-linear version of (3), including its minus sign. The kernel is nonnegative, vanishes at both chord endpoints, and is continuous at `x`. Consequently the absolute-jump sum in (4) bounds the magnitude of the signed chord remainder.

For a finite piecewise-C2 partition with a BV first derivative and finite one-sided limits, the derivative measure has the stated integrable density plus the finitely many jump atoms. Integrating the hinge representation against that measure extends the result to (3). Direct integration gives

    integral_a^b G_x(t) dt = (x-a)(b-x)/2,

which verifies the smooth-cell curvature coefficient and its units. Since eta and occupation departure are dimensionless, derivatives are consistently per eta or per eta squared; the kernel and integration measure supply the two powers of eta in the smooth remainder, and the single kernel supplies the power required by a slope jump.

**Finding TR-02, CLOSED:** the original wider regularity statement did not explicitly say that the partition was finite. A general BV derivative can have a singular-continuous part, which must be included in the measure identity if that wider class is intended. The parent added the finite-partition qualification to both the assumptions and theorem. The actual finite sampled interpolant was already unaffected. No new implementation or physical condition is required.

## 4. Native grid, causal boundary, and actual query witnesses

The inspected C routine uses `floor((lna-lna_start)/dlna)`, the corresponding linear fraction, and rejects `lna >= lna_start + dlna*(iz-1)`. It returns thermal prehistory before the left endpoint, but the new module expressly restricts its domain and provides no such extension. The exact-rational grid `t_k = eta0 + k h` is therefore the stated real-arithmetic reconstruction of the in-domain formula.

It is not the rounded native C execution, and it is not the geometric interpolant through stored eta-array coordinates. The draft correctly keeps these identities separate, preserves the prior consumer's anchor radius, and requires recording coordinate and nominal-value differences. This review does not certify the yet-to-run 313 exact-grid cell comparisons or any interpolation-rounding bound.

Metadata readback observes 313 queries, prefix 5127, and cells ranging from 4770 through 5125. The final legal cell is 5125, because its right knot is the excluded domain endpoint `t_5126`. Twelve query witnesses lie in that cell:

| incoming_index | source_index | cell |
|---:|---:|---:|
| 134 | 135 | 5125 |
| 135 | 136 | 5125 |
| 136 | 137 | 5125 |
| 137 | 138 | 5125 |
| 138 | 139 | 5125 |
| 139 | 311 | 5125 |
| 140 | 141 | 5125 |
| 141 | 142 | 5125 |
| 142 | 143 | 5125 |
| 143 | 144 | 5125 |
| 144 | 145 | 5125 |
| 311 | 140 | 5125 |

**Finding TR-01, CLOSED:** a two-adjacent-cell chord cannot be constructed for these queries while retaining the fixed prefix. The parent added a generic rule: an unavailable adjacent-cell retiming is explicitly skipped, and the chord endpoint on that side becomes the midpoint between `q` and the current-cell endpoint. On the right, `(q+t_5126)/2` is strictly below `t_5126`, so it remains admissible and still lies above `q`. The available left-adjacent midpoint supplies the other endpoint. Thus every query retains a chord test without using future samples or the excluded endpoint. The printed incoming-index 311 is an example, not the full set.

If the pending exact-grid checks retain all source cell witnesses and the two within-cell targets are valid, the metadata implies 626 within-cell cases, 313 left crossings, 301 right crossings, and 12 unavailable right-crossing skips: 1240 executed retimings, plus 313 chords. These are conditional expected counts, not executed results or a tolerance. The runner must derive counts from the actual admitted data.

## 5. Physical composition and scientific admission

Let `e(t) = y(t)-P(t)`. Then the difference between the physical and represented finite differences is exactly `e(q+d)-e(q)`. The triangle inequality proves (7) when an independently justified nonnegative enclosure `|e(t)| <= epsilon(t)` is available at both endpoints. Adding this inequality to the represented retiming remainder proves the stated bound relative to `d m_+(q)` or `d m_-(q)`.

The argument does not bound `y'`, prove physical smoothness, or produce epsilon from interpolation identities. Dividing the value enclosure by a shrinking step would generally enlarge the error. The draft correctly leaves derivative control and physical proof inputs separate. Actual physical epsilon remains null, physical proof coverage remains 0/313, and the strict rule `E_upper < certified_positive_rho_lower` is unchanged.

The new results establish exact finite identities for the declared reconstruction and a conditional route for composing independently supplied physical bounds. Original programme completion remains 32/88 in the scoped working return and 27/88 in shared central authority, with a new canonical increment of zero. No strong no-go claim is proposed or established.

## Closed review result

Both reported findings are closed by targeted text changes. No critical theoretical finding remains open. Implementation, exact-source bindings, reference-value checks, resource receipts and physical source qualifications retain their original evidentiary obligations. This completed one-pass review should not be restarted merely because those later stages are pending.
