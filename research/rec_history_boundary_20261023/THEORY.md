# REC-HISTORY: independent native boundary/source derivation

Prepared for the REC-HISTORY owner, 2026-10-23 request. This is a source-bound
theory review. No scientific code, old LINE02 cases, review probes, native solver,
or IVP was executed. File materialization and hashes are provenance operations.

## 1. Source identity and scope

Authoritative repository pin: `cosmosapjw-quantum/rec_bianchi@a7c46fd8338971e2cefa776f5dd7b25a46974990`.
The fixed orchestration handoff is
`rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17/research/orchestration_longterm_20261023/assembly/HANDOFF_rec_bianchi_KO.md`.
Read the pinned LINE02 FROZEN_CONTRACT, THEORY, GLOBAL_DAG and native C sources.
REC-LINE02's 194 checks and independent review remain reused evidence; this
document adds no numerical count to that work.

| Source | Git blob | SHA256 / identity status |
|---|---|---|
| `research/rec_line_native_owner_20261023/vendor/hydrogen.c` | `2df4561f1b1ef80991ca3b7645666a630eea19b7` | `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`, 37471 bytes; Git blob matched |
| same directory `hydrogen.h` | `80d612d2c032059f419b701f1376d43513cff2ed` | `e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba`, 7837 bytes; Git blob matched |
| `research/rec_r3s_ncp_campaign_20261021/ncp_execution_001/evidence/campaign_001/jobs/h4_legacy16/run/worker/source_extract/HyRec/hyrec_params.h` | `b2940f20d4e2ff0a46d66101c1c0c5ac13c5e67b` | `46b4cb3f7a463ddbae966c02114e16f8e079615e4838f5dcbcb6cd1c5a67a83f`, 3769 bytes; Git blob matched |
| same source-extract directory `history.c` | upstream `af01782d70a29bb55ed053c37cafff044964ade5` | Connector text has normalized line endings; local text SHA256 `69d208a789423433b53d98d38f3dfeab5503e1a5deb06d0d2fc991d40fa5e5fe`; semantic inspection only, not byte-identity assertion |

The first materialization of hydrogen.c added one trailing newline. That local
SHA256 `1ff1b7e34b9c7c0db301445a3f05b6e5745d37caaaf1d116bb80eedc7739d228`
was withdrawn before use; the table gives the corrected source identity.
AGENTS.md at repository root returned404 at the pinned commit. The complete tree
contains AGENTS files only inside historical surveys of other repositories, not
on the ancestry of the selected REC source directory.

The inspected h4 header has DLNA=8.49e-5/4, NSUBLYA=140, NSUBLYB=271,
NVIRT=311. The boundary contract must nevertheless carry the spacing of its own
history payload. An unrelated saved-history spacing must not be inferred from
this particular campaign header.

## 2. Actual owner graph

`hydrogen.c:633–652` owns interpolation; `667–718` owns incoming history;
`777–799` owns outgoing storage. `populateTS_2photon:441–526` consumes incoming
distortions in the real and virtual source vectors. `rec_HMLA_2photon_dxHIIdlna`
first obtains incoming values, builds and solves the313-state algebraic system,
and only then writes the current history column.

There are314 outgoing history channels:311 virtual-bin red edges plus Lyα,
Lyβ and Lyγ red edges. There are313 consumed incoming channels:311 virtual blue
edges plus Lyα and Lyβ blue edges. Lyγ blue incidence is the prescribed thermal
boundary and is not a fourth history input hidden in the interface.

| Destination | Sole upstream history owner | Energy pair |
|---|---|---|
| virtual b=0..138,140..269,271..309 | virtual b+1 red edge | E[b+1]→E[b] |
| virtual139 | Lyα red edge | E21→E[139] |
| incoming Lyα | virtual140 red edge | E[140]→E21 |
| virtual270 | Lyβ red edge | E31→E[270] |
| incoming Lyβ | virtual271 red edge | E[271]→E31 |
| virtual310 | Lyγ red edge | E41→E[310] |

This routing reads one upstream owner for every destination. The transfer is
occupation transport. It must not be posted as an additional atomic emission
or as an extra photon source on top of the outgoing boundary/event ledger.

## 3. Causal interpolation and its exact differential

Write ell=ln a, h=Δln a>0, ell_j=ell0+jh. For a transfer from E_up>E_down,

    ell_star = ell_now − ln(E_up/E_down),
    u=(ell_star−ell0)/h, j=floor(u), f=u−j,
    I[y]=(1−f)y_j+f y_(j+1).

This follows directly from the scalar native characteristic E a=constant. The
native function returns0 for iz=0 or1 and for ell_star<ell0. Otherwise it
requires ell_star<ell0+h(iz−1), strictly. The latest stored endpoint itself is
rejected because the implementation always reads both j and j+1. If the
current time is exactly ell0+h iz, this condition is the delay constraint
ln(E_up/E_down)>h. A substitute inclusive endpoint rule is a changed algorithm,
not native parity. NaN/invalid geometry checks are an additional API guard and
should be identified as such.

Inside a fixed interpolation cell the exact tangent is

    δI=(1−f)δy_j+f δy_(j+1)+(y_(j+1)−y_j)δu,
    δu=(δell_star−δell0−u δh)/h,
    δell_star=δell_now−δln E_up+δln E_down.

At a knot, the query derivative is one-sided unless adjacent slopes agree.
The array-value derivative remains the well-defined linear interpolation map.
The discrete iz/thermal-start branch has no ordinary derivative across its
switch. An implementation should either select a fixed-cell tangent with a
cell-margin guard or return the active one-sided convention explicitly.

For an underlying twice continuously differentiable scalar history y,

    |I[y]−y(ell_star)| ≤ h² f(1−f) sup_cell|y''|/2
                      ≤ h² sup_cell|y''|/8.

The proof is the standard two-point interpolation remainder, whose product of
distances is h²f(1−f). This is a derived conditional bound. A physical numerical
bound requires a justified curvature bound or an independent same-domain
retained-history witness. Polynomial fixtures only calibrate the manufactured
domain in which their derivatives are known.

Convex interpolation preserves the range of the stored distortions and hence
their positivity when both distortions are nonnegative. Signed distortions
remain admissible. The source comment claiming positive spectrum is not, by
itself, a proof that arbitrary signed physical occupations remain positive:
the thermal baseline must also be restored at the query energy/time. Check
f_thermal(ell_star,E_up)+I[y] explicitly when physical positivity is asserted;
do not clip a negative result or require every distortion to be positive.

## 4. Finite Lyα boundary and the native event ledger

Use the native local non-tilted frame and proper seconds. Let

    x=x1s>0, s=xr_p/(3x), d=d_in,
    q(n)=1+S:nn>0, t=τ/q, A=1−exp(−t),
    d_out(n)=d_in(n)+(s−d_in(n))A.

The stable computation of A is −expm1(−t). For τ→0, d_out→d_in; for
τ/q→∞, d_out→s, reproducing `hydrogen.c:794`. No finite-opacity source can use
the old thick outgoing boundary while claiming source-boundary consistency.
For a fixed ray, the exact differential is

    δd_out=exp(−t)δd_in+A δs+(s−d_in)exp(−t)δt,
    δs=δxr_p/(3x)−s δx/x,
    δt=δτ/q−τ δq/q².

At fixed s,τ,q the incoming-error multiplier is exp(−t), in[0,1]. This local
contraction does not include the solved excited-population response.

Define the native number phase-density normalization

    G_N=3×10^6 LYA_FACT  [m^-3],
    r0=LYA_FACT H/(nH_cm3 x),  nH_SI=10^6 nH_cm3.

The directional lower-frequency boundary flux minus incoming flux is

    R_gamma=G_N H <q(d_out−d_in)>.

For isotropic incoming d and C=<q(1−exp(−τ/q))>,

    R_gamma=G_N H C(s−d)
           =nH_SI r0 C(xr_p−3x d).

This is exactly the LINE02 event ledger with r_star=r0 C and b_star=3x d.
The proof is substitution plus G_N/(3x)=nH_SI r0/H. The appropriate angular
weight is qA, not A alone. In the anisotropic case a scalar unweighted average
of d_out does not carry the correct flux.

For directional incoming d(n), the finite affine source pair instead is

    r_star=r0 C,
    s_star=3x r0 <q A d(n)>.

Retain this source coefficient directly when C→0; computing an effective
b_star=s_star/r_star introduces an avoidable transparent-limit singularity.

The SI phase density for two photon polarizations is
G_SI(E)=E³/(π² hbar³ c³), obtained from2d³p/(2πhbar)³ and E=cp.
G_SI(E21) differs from the literal native G_N by the already documented
approximately2.66e−7 constant-convention offset. Native parity and modern-SI
normalization are separate checks, not conflicting tolerances.

For signed R_gamma, the one local line event gives

    dot n_2p=−R_gamma, dot n_1s=+R_gamma,
    dot n_gamma=+R_gamma,
    dot u_atomic=−E21_J R_gamma, dot u_gamma=+E21_J R_gamma,
    dot u_kinetic=0, dot n_e=0.

Writing outgoing history is the radiation representation of this event. It
does not authorize a second additive photon debit/credit. Retarded transport
between different energies also includes cosmological dilution/redshift work;
that energy difference must not be assigned as gas heating.

For scalar FLRW free transport in a fixed physical-energy bin,

    dot n_bin+3H n_bin=H[G(E)f]_(Elo)^(Ehi)+S_number,
    dot u_bin+4H u_bin=H[E G(E)f]_(Elo)^(Ehi)+S_energy.

These follow by integrating ∂t f−H∂lnE f=C and integrating by parts. They
explain why occupation transfer has no extra a^-3 or a^-4 amplitude factor;
the density measure supplies the dilution.

## 5. Actual frozen-history map versus the LINE02 partial JVP

At a fixed thermodynamic state, native M does not depend on incoming u. Its RHS
is s_base+B u. In the order u=(virtual311, Lyα, Lyβ), B has the following
nonzero entries, read directly from `hydrogen.c:449,464,526`:

    B[real2p,Lyα]=3 r0 x,
    B[real2s,Lyβ]=3 r0 x *1.664786871919931,
    B[virtual_b,virtual_b]=Tvv0[b] x P_b,
    P_b=1−one_minus_Pib[b].

Thus X=M^-1(s_base+B u), and δX=M^-1 B δu when M and the other scalar inputs
are fixed. Every incoming-history channel changes the appropriate RHS. The
old b-only LINE02 JVP is only the Lyα column of this dependency.

The outgoing virtual row is linear in X and u at these fixed coefficients:

    Dfeq_b=−(Tvr0b*xr_s+Tvr1b*xr_p+offdiag_b*xv_neighbors)
           /(x(1−P_b)Tvv0[b]),
    dminus_b=(1−A_b)u_b+A_b Dfeq_b.

For τ_b≤1e−30, native code copies u_b. Native small-depth A_b and1−P_b use
the specified second-order branches at1e−6. Preserve that convention for
parity, while a stable expm1 implementation should be recorded as a separately
tested mathematical form. The solved row also yields
Dfeq_b=(xv_b/x−P_b u_b)/(1−P_b), but the apparent small denominator requires
the matched analytic limit. It must not be evaluated as0/0.

The three Ly rows are

    dminus_alpha=xr_p/(3x),
    dminus_beta=xr_s exp(−E32/TR)/x,
    dminus_gamma=xr_s exp(−E42/TR)/x.

Collect outgoing314=T X+P u. The complete frozen-coefficient source-to-boundary
map and tangent are therefore

    dminus=T M^-1(s_base+B I[history])+P I[history],
    δdminus=(T M^-1 B+P) δu,
    δu=I δhistory + I_query δquery.

For a declared norm, interpolation error then obeys
||δdminus||≤||T M^-1 B+P|| ||δu||. A local line or solved-population acceptance
must allocate its input-history interpolation budget through this actual
response operator, or a declared selected-column restriction. Thermodynamic,
opacity and geometry directions additionally differentiate M,B,T,P and the
departure coordinate. They are outside this frozen-map expression.

## 6. Scalar native propagation and Bianchi characteristic admission

The actual May2012 history owner is scalar and assumes E a=constant.
For a general Bianchi ray,

    d ln E/dt=−H−sigma_ab n^a n^b=−H q(n,t),

and the direction also evolves. The retarded event must satisfy the integrated
direction-dependent energy ratio, together with the direction/frame map.
Installing angular outgoing values in the scalar native history arrays does
not construct that additional characteristic owner. A sound first unit may
admit: (a) exact scalar native boundary/history compatibility, and (b) a local
finite angular boundary adapter with explicit angular data. The subsequent
directional history contract must supply geodesic/frame interpolation before
the two can be combined into a Bianchi-history claim.

## 7. Minimal new finite validation proposal

Freeze the selected actual owner and payload identity before any code/test.
The following categories distinguish implementation verification from physical
history-error calibration; they are proposals, not executed counts.

1. Source-extracted native interpolation oracle: startup0/1, pre-start, exact
   interior knot, fractional cell, signed data, just-below-latest, rejected
   latest endpoint. Record branch and two read indices.
2. Routing oracle: all313 destination rows from the declared311 energies and
   three native line energies; ensure each row has exactly one owner and the
   known thermal Lyγ-blue condition is explicit.
3. Finite line boundary: transparent, moderate, thick depths; q=1 and one
   anisotropic positive-q fixture; compare flux-weighted boundary difference
   to the independent native event formula and retain signed absorption.
4. JVP oracle: a fixed-cell history-amplitude direction and query direction;
   the outgoing local derivative above; optionally the selected Lyα incoming
   column of the frozen source solve, with the old LINE02 checks reused.
5. Independent interpolation bound witness: analytic curved history with known
   y'' verifies the h²/8 formula in a manufactured domain. Actual-history error
   admission additionally requires a same-domain retained finer/reference
   history or justified physical curvature envelope. Leave that obligation
   UNCALIBRATED if those data are not available.
6. Domain/ownership falsifiers: future read, duplicate line source, missing
   energy/frame metadata, wrong photon sign, omitted q flux weight, and
   treating a history transfer as a second physical emission must be rejected
   or fail the independent invariant as appropriate.

The frozen contract should bound fresh finite-case work only. LINE02's primary
budget and six historical review probes remain spent, not reset or replayed.
No native history integration is needed for the bounded interface tests.

## 8. Review findings and decisions

| Finding | Evidence and impact | Minimal treatment |
|---|---|---|
| Latest-endpoint causality is strict | C query guard633–652; generic interpolation may read an unavailable current cell | Preserve branch/indices and explicit rejection |
| Scalar history and angular boundary have different domains | Scalar delay667–718 versus q-dependent energy flow | Separate admitted scalar map and local angular boundary; require characteristic owner for coupling |
| Outgoing boundary and atomic event share one photon owner | Exact flux identity in§4 | Post source once; use outgoing as radiation representation |
| Signed distortion is not a positivity defect | Native departure variables and convex interpolation | Restore thermal baseline for physical positivity; retain signed values |
| Interpolation physical tolerance is uncalibrated from one snapshot | No retained time-neighbor curvature in LINE02 snapshot | Derive propagation/bound and request exact same-domain witness; manufactured tests remain scoped |
| Old partial tangent lacks actual history dependence | All313 incoming channels enter RHS | Use explicit B/I and outgoing O/P derivatives or declare selected-column scope |

No strong no-go is proposed. The unresolved items identify concrete provider
inputs and derivatives, not a general impossibility. Physical HOLD, REC_U5
HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN,
production NOT_APPROVED and REI_activation=false are retained.
