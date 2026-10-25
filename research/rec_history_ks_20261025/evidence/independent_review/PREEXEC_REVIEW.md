# KS01 independent pre-execution scientific review

Reviewer role: parent-dispatched independent scientific reviewer; did not implement KS01.
Observed time: 2026-10-24T23:19:16Z (2026-10-25 08:19:16 KST).
Scope: R6 pre-execution theory/contract review. No scientific source executed, no matrix solve, no numerical campaign, no literature re-survey, no recursive review.
Verdict: **PASS_THEORY_PENDING_IMPLEMENTATION**. No current blocking scientific defect was found in the frozen construction. This verdict does not authorize the primary process; the root owns execution authorization and budget.

## Inspected identities

| Object | SHA-256 |
|---|---|
| FROZEN_CONTRACT.md | 389c754f6a025c4f1b1cf36673f2f41efc3e28b148ab0633319362c57a39ac98 |
| THEORY.md | f4ac0608f4e4c61b5c719ffc4c3dd138d788501b418b761a64d658a28630583b |
| retained THERMO source.py | 2f55b2eb0b3744d730f862e8df694f7aeeffe4a21113afb6c024a5353920b272 |
| retained THERMO scalar.py | b4716151af9c67ac0a238a3cd16b0336b6f7909b2b8d4122d180f2a969908e2d |
| retained RESP interval.py | e5b7d9aa94b49234de626672ca1c0e7db694e38885fb40c478880d2f2b904250 |

Also read: retained THERMO inputs.py and OPERATOR_BINDING_CLARIFICATION.md; retained SOURCE_HISTORY_PROVENANCE.json, ORIGINAL_NATIVE_HISTORY_LEAD.json; QUERY_RESPONSE_COEFFICIENTS.csv header/initial mapping rows; prior source-mapper text for clock, scalar frame, outgoing channel ownership and finer-cosmology differences. These retained documents were treated as provenance, not fresh physical calibration.

## Direct source mapping and derivative

At fixed theta the retained build() forms incoming-dependent source terms only in sr[0], sr[1] and sv[b]. The three derivative families in the contract agree with those expressions:

- sr[0]: coefficient of u[312] is 3*ly*x*1.664786871919931.
- sr[1]: coefficient of u[311] is 3*ly*x.
- sv[b]: coefficient of u[b] is Tvv[0,b]*x*(1-p[b]).

The retained scalar order and stable p must be used. Algebraic cancellation of ly*x or substitution of native p would alter the chosen floating representation. M,T,P have no incoming dependence. Thus M V=B and K=T V+P are the correct fixed-theta affine derivative.

The represented-coefficient certificate concerns exact real algebra on frozen binary64 M,B,T,P. The sequential rounded source evaluator is checked numerically by the affine controls; the certificate does not become a derivative of the binary rounding function. The existing contract states this distinction adequately.

The local chain rule delta o=Js delta theta+Ks delta u is correct when Js is reused at the same source/base/incoming identity. Js already includes theta differentiation of the full source with u held fixed. An external history pullback would enter only through delta u. Combining the blocks neither supplies nor bounds that missing pullback.

## Residual enclosure proof

With Q=I-ZM, ZM=I-Q and rho>=||Q||inf<1, the square matrices I-Q,Z,M are nonsingular. For R=B-M Vhat,

  (I-Q)(V-Vhat)=Z R,

so V-Vhat=(I-Q)^(-1) Z R. The nonnegative column estimate sigma_j>=max_i (|Z| |R|)_ij gives

  |V_ij-Vhat_ij| <= sigma_j/(1-rho).

For t_i>=sum_k|T_ik|, outward evaluation of T Vhat+P followed by widening by t_i e_j encloses each exact K_ij. Every product, addition, denominator and final widening must honor the arithmetic enclosure, including the products used to form |Z||R| and t_i e_j.

Entrywise absolute minima sum to a valid row lower bound and entrywise maxima to a valid row upper bound, without requiring simultaneous attainability of the individual interval endpoints. Taking the maximum over rows therefore gives a valid enclosure of ||K||inf. The proof is dimensionally consistent: M and B are rates; Z has time units, Q and V are dimensionless; T,P,K are dimensionless.

At fixed theta the represented map is affine. The componentwise uncertainty formula sum_j max|K_ij| epsilon_j is therefore a finite box bound, with no incoming Taylor remainder. Physical coefficient/model errors and physical epsilon remain separate inputs.

## Same-event signs and units

The retained source outputs use F=-(C-beta0 X0-beta1 X1)/H. Consequently dF/du=beta^T V_first2/H has the positive sign in THEORY.md. F is a derivative with respect to ln a; H F is the proper-time ionization rate at fixed theta.

The source's LYA carries inverse cubic-centimetre normalization; the factor 3e6*LYA*H converts the occupation difference into number per proper cubic metre per second. E21 is in eV and EV_J converts eV to joules. The radiation derivative is therefore in J m^-3 s^-1 per incoming occupation.

For Ly-alpha the incoming subtraction is required:
  dN/du_j=C_N(K_311j-delta_311j).
The delta term is present in the contract and must remain in implementation. Atomic energy is the exact sign-paired representation of this same event. Its cancellation does not supply other-event, transport-work, geometry or thermal-ODE closure.

Js remains a numerically checked six-column block; only Ks receives the proposed represented-coefficient interval certificate. These two evidence types must remain distinct in plots and exported records.

## History admission and exclusions

The original h=8.49e-5 native payload and its retained input.dat lineage match the intended target-source lead. The prefix at iz5127 has 5127 knots indexed0..5126. The specified strict domain eta0<=eta_query<eta5126 admits only cells whose two endpoints lie in that prefix. Earlier queries use the explicit zero thermal departure boundary; the final knot/future does not become an interpolated endpoint.

The redshift map eta_emit=-log((1+z_face) E_source/E_target) has the correct sign for a higher-energy source photon propagating to a lower-energy target in scalar FLRW. Virtual/Lyman outgoing ownership must be checked for every313 query, including line gaps, and average_virtual must not be substituted.

Actual-payload byte/member/clock/energy/parameter admission is a useful new result. Same-h reconstruction agreement is only discrete consistency. The stated null physical epsilon/reference/endpoint/curvature fields and exclusion of different-cosmology finer trajectories preserve the correct claim boundary. H5 can gain a local input admission; its physical calibration remains open. The other HISTORY02 owner retains H6 retiming.

## Pre-execution controls and budget

The frozen 639 large RHS count is consistent:
313(V)+313(Z)+1(base)+4(affine)+8(joint)=639.
Exact Fraction manufactured systems are separately limited to <=12small RHS. No native/IVP/old campaign is required by this plan. One primary process with 45CPU/135wall, one thread and1GiB, plus the separately reserved repair/scalar/figure allocations, respects the stated finite unit cap. Unobserved earlier HISTORY02 charges remain in that owner's ledger.

No tolerance was changed in this review. In particular, small event-response cancellation must retain the frozen relative failure as an observed failure even if gross-roundoff evidence explains it. A future repair must be root-owned and retain the original failing evidence.

## Concrete implementation checks to close in the same review

1. Arithmetic platform: retained interval.py explicitly assumes correctly rounded basic arithmetic and gradual underflow. Record this assumption and include a finite subnormal/no-FTZ scalar control within the already allocated small arithmetic controls. A BLAS residual is never a certificate.
2. Box API labeling: interval.py's returned lower field is a lower bound on the row's worst-case box gain, not a positive lower bound on every realized |delta o_i|. Document that meaning if exported; epsilon=0 needs a zero-response interpretation even if outward endpoints include a tiny positive bound.
3. Provenance paths: source_intake/... in the frozen prose currently resolves under retained THERMO provenance/source_intake, not the new unit's root. Resolve the actual files in the execution manifest before launch. This is a locator issue, not a source or physics mismatch.
4. Evidence type: retain Js as numerically checked, Ks as represented-operator certified only after successful implementation/runtime results. Finite differences do not upgrade Js to an interval certificate.

These are targeted implementation/metadata obligations, not new research stages or a request to replay any completed work. The same reviewer should inspect the actual lower-tier code, results and plotted images once after the primary run. Code and result verdicts remain PENDING.

## Skill context

Applied physmath-research-loop built-in1.0.0/v0.2 RESEARCH_POLICY.md and EVIDENCE_AND_HANDOFF.md read earlier in this child session, and the parent-selected R6 scope. Reused prior provider/source survey. Claims are separated as derived theory, retained provenance, numerical checks pending and implementation checks pending. No new strong no-go claim is made.

