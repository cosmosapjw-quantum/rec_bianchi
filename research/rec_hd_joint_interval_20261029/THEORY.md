# REC-HD-JOINT-INTERVAL01

Owner rec_bianchi; isolated child of PR153, source HEAD 67d8baa092f18b7c1bbf8dfe9e255f8b43b45998. Date 2026-10-29 KST. This finite source-admission calculation uses the assumptions in CONTRACT.json. Central DAG remains 28/88; original physical 0/313.

## R1 — Research contract

The inherited print-only row condition is necessary. A common set of level energies must satisfy adjacent rows simultaneously. The task is to construct a necessary-and-sufficient enclosure test, produce explicit certificates, recover the actual byte-pinned source, and repair the two independently reproduced input/output defects. Source replacement requires its original field-level lineage, which remains an input dependency.

The metric convention is (-,+,+,+), although the present local spectroscopic algebra has no metric-dependent step. Keep c,h,k_B explicit; h=2 pi hbar. A frequency in this document is an ordinary frequency. No IVP, native solve, historical stationary calculation, heat correction or physical rate change is required.

## R2 — Reused and newly recovered evidence

The current raw official LAMDA response is 2289 bytes and reproduces SHA256 0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb. All 17 extracted term/frequency literals equal the PR153 public transcription. Raw source bytes remain in the private backup capsule. Seven CDMS official HTTP requests returned 503; this is SERVICE_ERROR for these requests. Version-authentic CDMS2011v2 bytes and field-level conversion remain unresolved. Official webpage prose does not establish an additional vibrational manifold.

PR152/153 finite algebra was independently reviewed; the reviewer reproduced an absent-output-directory failure and accepted Infinity inputs in the SPCAT header parser. Those are implementation errors, distinct from the input-service failure and from the preserved physical source discrepancy. The exact central 88-node/17-edge object is identified in provenance/CENTRAL_DAG_IDENTITY.json.

## R3 — Variables, domain, and claims

Let L_j=100 c w_j (Hz), F_j=10^9 nu_j (Hz), j=0,...,n for terms and j=1,...,n for adjacent lines. Here n=8, w is the printed cm^-1 literal and nu the printed GHz literal. Define delta_j=L_j-L_(j-1)-F_j. The printed half-quantum radii are r_j=100 c q_w,j/2 and s_j=10^9 q_nu,j/2 in Hz. Let x_j=L_j^true-L_j and y_j=F_j^true-F_j. A common energy model in the closed rounding enclosure exists exactly when

    |x_j| <= lambda r_j,
    |y_j| <= lambda s_j,
    delta_j+x_j-x_(j-1)=y_j.

The physical printed-precision question fixes lambda=1. A computed lambda_min is a diagnostic distance from that enclosure; it is never applied to the original 35Hz acceptance gate. lambda is dimensionless. All radii are finite and nonnegative; quantization is derived from the exact decimal token, preserving trailing zeros. Closed endpoint sufficiency means sufficiency for the stated enclosure; exact tie-to-even printing would require its endpoint rule as an additional condition.

The immutable printed coefficient alpha_print,j=h delta_j/(k_B T) is exact for its fixed literals. The underlying defect before enforcing common-energy equality has the enclosure alpha_print,j +/- h lambda(r_(j-1)+r_j+s_j)/(k_B T). These are different objects. Under a compatible common-energy realization, alpha_true,j=0. T>0 is required; no physical entropy-production interpretation follows from a failed enclosure.

## R4 — Chosen constructive representation

A. Independent row bounds retain PR153's necessary test but miss shared-level constraints. B. Exact interval reachability on this path gives an O(n) decision and constructive witness. C. A general LP solver handles arbitrary graphs but adds floating tolerance and an unnecessary dependency here. Use B for the primary checker and an independently implemented all-contiguous-segment criterion for verification. A general difference-constraint graph formulation proves sufficiency of the segment criterion and supplies dual obstruction certificates.

A discriminating control is n=2, delta_1=delta_2=1Hz, r_0=r_1=r_2=1/2Hz, s_1=s_2=0. Both single-row bounds pass at equality, but delta_1+delta_2=2Hz exceeds r_0+r_2=1Hz; the joint enclosure is empty. Its minimum common scale is exactly 2. A control with deltas (1,-1) has a joint witness at scale1.

## R5 — Constructive proof and tight scale

**Reachable-interval lemma.** At scale lambda>=0 set I_0=[-lambda r_0,lambda r_0]. Given the exact reachable interval I_(j-1)=[l,u], set

    I_j = [-lambda r_j,lambda r_j]
          intersect [l-delta_j-lambda s_j, u-delta_j+lambda s_j].

This follows by eliminating y_j from its closed interval and taking the Minkowski sum of intervals. It is exact, not an interval overestimate: the image of a connected interval under addition of another interval is the entire summed interval. Inductively I_j is exactly the set of reachable x_j. An empty I_j proves infeasibility. Otherwise choose x_n in I_n; backward choose

    x_(j-1) in I_(j-1) intersect
               [x_j+delta_j-lambda s_j, x_j+delta_j+lambda s_j].

The intersection is nonempty by reachability. Set y_j=delta_j+x_j-x_(j-1); this constructs all equalities and bounds. Decision is O(n); storing intervals plus backward witness is O(n).

**Independent segment criterion.** For p<q let D_pq=sum_(j=p+1)^q delta_j, S_pq=sum_(j=p+1)^q s_j. Joint feasibility is equivalent to all n(n+1)/2 inequalities

    |D_pq| <= lambda(r_p+r_q+S_pq).

Necessity follows by summing the equalities and bounding x_p,x_q and all y_j. For sufficiency introduce an auxiliary zero node z and encode x_j-x_z<=lambda r_j, x_z-x_j<=lambda r_j, x_j-x_(j-1)<=-delta_j+lambda s_j, x_(j-1)-x_j<=delta_j+lambda s_j. A finite system x_v-x_u<=w_uv is feasible iff its directed graph has no negative cycle: feasible potentials imply nonnegative cycle sums; conversely shortest-path distances from a super-source give potentials when no negative cycle exists. In the path plus z, each simple cycle either uses one path edge twice (weight 2lambda s_j>=0), one z spoke twice (2lambda r_j>=0), or uses two z spokes and the unique monotone path from p to q. The latter two orientations have weights lambda(r_p+r_q+S_pq) +/- D_pq. Every closed walk decomposes into simple cycles. The displayed segment inequalities therefore exclude every negative cycle, which proves sufficiency. No arbitrary cycle basis or floating tolerance is needed.

**Tight common scale.** If every denominator d_pq=r_p+r_q+S_pq is positive, the minimum is

    lambda_min = max_(p<q) |D_pq|/d_pq.

For d_pq=0 and D_pq!=0 the minimum is infinite; zero/zero imposes no constraint. With n=0 the constraints are feasible and lambda_min=0. At a finite lambda_min all inequalities hold, hence reachability constructs a witness; below it a maximizing segment is a strict obstruction certificate. This is a scale of printing enclosures, not spectroscopic measurement uncertainty and not a revised gate.

The original lambda=1 source calculation may stop at its first empty reachable interval. The independent segment method still checks all36 segments. The two methods share only exact source literals and the physical conversion factor; their algorithms are different.

## R6 — Independent theory review and endpoint correction

Reviewer /root/independent_hd_review read R3-R5 independently and checked exact path difference constraints with a separately coded Bellman-Ford negative-cycle test. All1152 discriminating cases agreed. The review identified one empty-maximum specification gap: the all-zero radii/defects case. The complete formula is lambda_min=max({0} union {|D_pq|/d_pq : d_pq>0}), with infinity if any d_pq=0 and D_pq!=0. Thus n=0 and all-zero finite systems both return0; a finite maximizing value is attained. This clarification preserves the original proof and physical claim. The independent method and actual targeted run are recorded in review/JOINT_THEORY_REVIEW.

Complexity qualifier: O(n) and O(n²) count exact rational arithmetic operations, not bit complexity. Rational numerator/denominator growth depends on input bit length. The9-state fixed input is finite.

## R7 — Independent exact symbolic evaluation

The stateless Wolfram evaluator received the17 literal decimal integers as rational numbers, c exact, and the closed half-quanta. It enumerated all36 segments and returned

    lambda_min = 9137862803786/174896229
               = 52247.34035738414920312547...,
    maximizing segment (p,q) = (5,6),
    row enclosure = 174896229/5000000 Hz = 34.9792458 Hz.

For this particular source the tight global scale equals the most restrictive single row. The all-pass/global-fail synthetic control distinguishes the general joint criterion from row checks. These are exact finite rational checks; the decimal is display only. Input code and raw Wolfram output are retained. The original lambda=1 result and original35Hz FAIL7/8 remain unchanged. The computed scale is not applied to any physical or source acceptance tolerance.
