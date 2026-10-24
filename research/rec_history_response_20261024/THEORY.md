# REC-HISTORY-RESP01 — source-owned history-error response

## Question and scope

At the original native scalar-FLRW face near z=1100, how does an error in each
of the 313 incoming history samples affect the 314 stored outgoing departures
and the single Lyalpha atomic/radiation event? The earlier H01 work established
the map, tested three directions, and supplied a positive comparison witness
and two manufactured conditional envelopes. This unit constructs its entire response,
encloses the exact response of the represented frozen matrices, and supplies
query-indexed weights for the outstanding independent history uncertainties.

The original target remains T0=2.728 K, nH0=0.18745798773143102 m^-3,
z_face=1099.9986525171403. The saved scalar snapshot supplies its own nH,H,x1s,
TR, and matrices. Metric signature (-,+,+,+), non-tilted local frame, proper
seconds, signed dimensionless occupation departures; c,hbar,k_B retain their
usual dimensional meanings. No new trajectory or thermal closure is introduced.

## 1. Native source map

Use the unchanged native ordering X=(xr_2s,xr_2p,xv_0,...,xv_310),
u=(virtual_0,...,virtual_310,Lyalpha,Lybeta). At fixed thermodynamic state,

    M X = b0 + B u,        o = T X + P u,
    K = T M^(-1) B + P,    delta o = K delta u.

The outgoing order is virtual311,Lyalpha,Lybeta,Lygamma. Incoming perturbations
are around the stored face and do not change M,T,P or source coefficients.
M and the base solution are retained PREPARED_BLOCKS input bytes; no original
preparer or old campaign is rerun. Native source entries are

    B[0,312] = 3 r0 x1s * 1.664786871919931,
    B[1,311] = 3 r0 x1s,
    B[b+2,b] = Tvv[0,b] x1s (1-one_minus_P[b]),
    r0 = LYA_FACT H/(nH_cm3 x1s).

For a virtual bin with tau>1e-30, let A be the unchanged native branch
1-exp(-tau) for tau>1e-6, otherwise tau-tau^2/2. Its T row follows

    eq_b = -(Tvr[0,b] xr_2s + Tvr[1,b] xr_2p
             + offdiag_b*xv_neighbors)
            /(x1s one_minus_P[b] Tvv[0,b]),
    o_b = A_b eq_b + (1-A_b) u_b.

For tau<=1e-30 the native row is o_b=u_b. The line rows are

    o_alpha=xr_2p/(3 x1s),
    o_beta=xr_2s exp(-E32/TR)/x1s,
    o_gamma=xr_2s exp(-E42/TR)/x1s.

This is the native opaque Lyalpha source case. Finite tau alternatives and
thermodynamic derivatives of these coefficients are outside this computation.
The numerical certificate concerns the exact real operator represented by
the saved binary64 M,B,T,P arrays. Constructing those coefficient arrays and
comparing them with the unchanged H01 native map are separately recorded.
This avoids assigning an unproved transcendental-error bound to system libm.

## 2. Rigorous enclosure for the represented linear system

Let Vhat approximate M^(-1)B and Z approximate M^(-1). They may be obtained
in a single multiple-right-hand-side solve. Use outward elementary interval
arithmetic, not an unqualified floating residual, for the following quantities:

    Q = I-Z M,    rho >= ||Q||_infinity.

If rho<1, ZM=I-Q is nonsingular; the square matrix M is therefore nonsingular.
For R=B-M Vhat,

    V-Vhat = (I-Q)^(-1) Z R.

Enclose R, form a componentwise upper bound P_res >= |Z| |R|, and set

    sigma_j >= max_i P_res[i,j],
    e_j >= sigma_j/(1-rho).

The Neumann series yields |V[i,j]-Vhat[i,j]|<=e_j. If an outward evaluation
of T Vhat+P gives [L0,U0], let t_i>=sum_k |T[i,k]|. Then

    K[i,j] in [L0[i,j]-t_i e_j, U0[i,j]+t_i e_j].

All upper/lower sums, products and the positive denominator are rounded in
the appropriate direction. Reject nonfinite values, overflow, or rho>=1;
these are certificate failures for this computation and are not physical
no-go results. Binary64 round-to-nearest, correctly rounded basic operations,
and gradual underflow are explicit arithmetic assumptions. Each multiply and
add is widened with nextafter; a full matrix dot is built from these elementary
steps, so no unspecified BLAS reduction-order assumption enters the enclosure.
The preliminary floating solve only supplies candidates Vhat,Z.

## 3. Sharp box propagation and its interval certificate

For a supplied incoming error box |delta u_j|<=epsilon_j with epsilon_j>=0,

    sup |delta o_i| = sum_j |K[i,j]| epsilon_j.

Triangle inequality gives the upper bound. Choosing
delta u_j=epsilon_j sign(K[i,j]) attains it for that selected row. Different
rows may have different extremizers; a single vector is not asserted to attain
every row's maximum simultaneously. A zero coefficient has arbitrary sign.
The global induced infinity norm is max_i sum_j |K[i,j]|.

For each interval [Lij,Uij], upper absolute weight is max(|Lij|,|Uij|).
The lower absolute weight is zero if the interval contains zero and otherwise
min(|Lij|,|Uij|). Outward row sums give enclosures of each row norm and of
the induced infinity norm. Weighted sums give a valid error allocation for
any independently justified epsilon vector. The current physical epsilon
vector is absent and remains null. Unit-amplitude weights describe sensitivity;
they are not a physical error estimate or a newly chosen scientific tolerance.

The local frozen-population multiplier exp(-tau/q)<=1 from H01 is a different
derivative: K also contains the solved population response. Actual computed
norms will determine amplification for this snapshot; no numerical outcome
or positivity/contraction claim is assumed before execution.

## 4. Event number and energy response

In the native scalar opaque case, o_alpha is outgoing314 row311 and u_alpha
is incoming313 column311. The single event number rate is

    R_gamma = G_N H (o_alpha-u_alpha),
    c_j = G_N H (K[311,j]-delta[j,311]),
    delta R_gamma = sum_j c_j delta u_j,
    G_N = 3e6 LYA_FACT [m^-3].

The same event carries atomic internal energy -E21_J delta R_gamma and
radiation energy +E21_J delta R_gamma. Their exact sum is zero because both
are defined from the same event scalar. No additional photon source is added
when storing outgoing occupation. Keep native E21 and LYA_FACT; modern SI
G(E)=E^3/(pi^2 hbar^3 c^3) is a distinct normalization previously documented.
Number-response coefficients have units m^-3 s^-1 per occupation; energy
coefficients have units J m^-3 s^-1 per occupation.

## 5. Connection to the required history input

For each actual source-owned link, eta_emit=eta_face-ln(E_source/E_target).
Keep the original 313 source indices, energies, query times and redshifts.
No unrelated finer candidate changes this target. A future same-domain error
provider supplies epsilon_j, including its trajectory/endpoints, interpolation,
startup/events, parameter/frame and arithmetic contributions as applicable.
These weights then propagate that box through the solved source and event.

When a causal interpolation operator I maps endpoint errors to incoming
errors, K I is the corresponding response. This unit exports query-indexed
weights without inventing an endpoint grid or changing prefix ownership.
The prior H01/02R strict-past guards and characteristic conventions are reused.

## 6. Literature position and interpretation

The sparse effective atom/radiation source is supported by the original HyRec
paper (Ali-Haimoud and Hirata, Phys.Rev.D83,043513,2011; arXiv1011.3758).
HyRec-2 (Lee and Ali-Haimoud, Phys.Rev.D102,083517,2020; arXiv2007.14114)
tabulates radiative-transfer corrections and cosmological derivatives; its
published accuracy does not supply this stored history's independent epsilon.
SciSpace/Exa discovery and direct author-paper reads are retained separately;
SciSpace arXiv year2022 entries are corrected against the original papers.
Rump (Acta Numerica19,287-449,2010,Theorem1.1) provides the approximate-left-
inverse nonsingularity criterion used here; the author manuscript is
https://www.tuhh.de/ti3/paper/rump/Ru10.pdf. The linear resolvent, Neumann
series and box-support argument above are directly derived here. The
contribution is their source-bound full operator, enclosure,
and per-query allocation at the actual retained target, not a new general
linear-algebra theorem. NG1-NG7 strong-no-go admission is not invoked.

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
REC-HISTORY remains PARTIAL while its absolute physical history input and
full angular/thermodynamic dependencies remain open.
