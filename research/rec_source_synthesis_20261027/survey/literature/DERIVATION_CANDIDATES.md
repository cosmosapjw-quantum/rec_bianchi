# Constructive derivation candidates from the current source survey

Status: direct analytic candidates for the parent R3–R5 contract. No new numerical
cases or production tests were executed in this survey. The original HD source
and H5 physical-admission obligations remain separate.

## A. HD: joint thermal imbalance from the two fixed source columns

Assume one isolated transition with positive A_ul and frequency nu>0, positive
degeneracies g_u,g_l, positive lower population, and a common positive radiation
and collision temperature T. Use the original tabulated level gap
DeltaE=E_u-E_l>0. Let

    x_E = DeltaE/(k_B T),
    x_nu = h nu/(k_B T),
    delta = x_E-x_nu = (DeltaE-h nu)/(k_B T).

No natural units are used. The scalar signature convention is irrelevant here.
For the mean-intensity Einstein-B convention,

    B_ul = A_ul c^2/(2 h nu^3),
    g_l B_lu = g_u B_ul,
    n_gamma = 1/(exp(x_nu)-1).

The Boltzmann population supplied by a collision detailed-balance construction is

    n_u/n_l = (g_u/g_l) exp(-x_E).

Absorption and total radiative de-excitation fluxes therefore satisfy

    R_up   = n_l (g_u/g_l) A_ul n_gamma,
    R_down = n_u A_ul (1+n_gamma),
    R_down/R_up = exp(-x_E) exp(x_nu) = exp(-delta).

Consequently,

    (R_up-R_down)/(R_up+R_down) = tanh(delta/2).            (A1)

This exact identity quantifies the joint compatibility of the two original
columns. The separate collision and radiation algebraic tests do not force
delta=0. The sign of delta fixes the direction of the spurious net radiative
flow at that prescribed common temperature. The original absolute source
mismatch can bound its magnitude via

    |A1| <= tanh(h |nu_E-nu|/(2 k_B T)),
    nu_E = DeltaE/h.

Equality holds in the displayed magnitude expression for exact inputs, because
tanh is odd and monotone. The inequality form permits an outward-enclosed
frequency difference.

For a shared line profile with the usual spontaneous emissivity and stimulated
absorption coefficients, the source function is

    S_nu = (2 h nu^3/c^2)/(exp(x_E)-1),

whereas the Planck function is

    B_nu(T) = (2 h nu^3/c^2)/(exp(x_nu)-1).

Thus

    S_nu/B_nu(T) = expm1(x_nu)/expm1(x_E),                 (A2)
    S_nu/B_nu(T)-1 =
        expm1(-delta)/[-expm1(-x_E)].                    (A3)

Equation A3 avoids subtracting two near-equal large positive exponentials and
is suitable for implementation when the source discrepancy is small. A1 can
use tanh directly. These are two independent presentations of the same
joint-thermal inconsistency; neither alters the source or enforces equality.

### Bounded coding candidate

Use exactly 8 original radiative lines and the existing source nodes
T=50,100,200 K: 24 cases. Consume the already established exact source identity
and preserve old 35 Hz pass/fail. Compute signed delta, paired-flux imbalance,
and source-function/Planck ratio with a stable elementary-function formulation;
an independent high-precision evaluation can audit only these new 24 cases.
Do not rerun the unchanged54 collision-value ingestion checks.

The collider label does not enter A1–A3: it cancels after imposing the same
Boltzmann ratio. This algebraic cancellation does not license p/o-H2 mixing.
Keep the original two collider blocks separate in all state/rate data, and
keep their actual availability mask. Values outside the source temperature
nodes or range are not required for this candidate.

Do not apply this 50–200 K collision source to the earlier H5 high-redshift
temperature by extrapolation. A dimensionless imbalance diagnostic is not an
admission of a complete cosmological molecular model, nor a correction of the
fixed seven source-gap failures.

### Three choices distinguished

1. Keep both columns and report A1–A3. This is an honest diagnostic.
2. Set all photon frequencies to level gaps or construct cumulative energies
   from the line frequencies. Either gives delta=0 by construction but changes
   the source. Neither is an accepted repair.
3. Adopt a separately identified, same-fit precision-qualified successor deck
   after source/state/uncertainty qualification. This could define a new input
   identity; it cannot retroactively pass the original bytes.

## B. H5: direct Peano identity for broken-smooth histories

Let f be continuous on [a,b], absolutely continuous, and piecewise C^2 with
f' of bounded variation. Let its interior derivative jumps be

    J_k = f'(t_k+)-f'(t_k-).

The distributional second derivative is the signed measure

    d f' = f''_ac(t) dt + sum_k J_k delta_(t_k).

For a<x<b define the nonnegative Green/Peano kernel

    G_x(t) = ((t-a)(b-x))/(b-a),  a<=t<=x,
           = ((x-a)(b-t))/(b-a),  x<=t<=b.

Writing Lf(x)=[(b-x)f(a)+(x-a)f(b)]/(b-a), integration by parts
on each smooth subinterval and cancellation of internal boundary terms gives

    f(x)-Lf(x) = - integral_[a,b] G_x(t) d f'(t)
               = - integral_a^b G_x(t) f''_ac(t) dt
                 - sum_k G_x(t_k) J_k.                 (B1)

This is the first constructive map from a saved piecewise representation to an
interpolation remainder that includes its actual corners. Its absolute bound is

    |f(x)-Lf(x)| <= integral G_x |f''_ac| dt
                   + sum_k G_x(t_k)|J_k|.              (B2)

For a single smooth cell with |f''|<=M2, integral G_x dt
=(x-a)(b-x)/2, recovering the classical curvature term

    |f(x)-Lf(x)| <= M2 (x-a)(b-x)/2.                    (B3)

For a continuous piecewise-linear reconstructed history, f''_ac=0 and B1 is
the exact finite slope-jump sum. It need not vanish when the interpolation
interval crosses a saved knot. Reading a piecewise-linear function as globally
C^2 and setting M2=0 across its knots would miss the second term of B2.

At a knot x, B1 still holds by continuity. All endpoints and knot equality
conventions must be fixed before implementing a right/left derivative API.

### Finite retiming of the represented history

For h>0, with f'_+(t) as the right derivative,

    f(t+h)-f(t)-h f'_+(t)
       = integral_(t,t+h) (t+h-u) d f'(u).              (B4)

For h<0, with f'_-(t) as the left derivative,

    f(t+h)-f(t)-h f'_-(t)
       = integral_(t+h,t) (u-t-h) d f'(u).              (B5)

Endpoint atoms do not contribute at t+h because their kernel is zero;
the starting derivative is the directional one, so the atom at t is
excluded. For a piecewise-linear history, these integrals are exact finite
sums of stored slope jumps with nonnegative weights. A convenient enclosure
replaces J_k by |J_k|. The path must remain inside the represented domain and
crossed knots must be enumerated; no extrapolation is implied.

This certificate concerns the represented numerical history f. If the desired
physical history f_* satisfies |f_*-f|<=epsilon_h on the relevant domain, then
a physical value discrepancy additionally needs that independent history
enclosure. A physical derivative or physical retiming remainder requires
corresponding derivative/model control. The finite jump sum alone supplies
none of H5's missing continuous physical defect/tube/stability/curvature
constants.

Parent integration should bind B1–B5 to the actual native interpolation
coordinate, interpolation branch, source arrays, valid domain, and knot
direction convention. A uniform-eta knot model cannot silently stand in for
a different interpolation coordinate. Actual source readback decides that
mapping.

## C. H5 logarithmic-norm refinement retained as reference only

For y'=F(s,y), a continuously differentiable approximation p(s), a fixed
positive scale matrix S, and residual

    r(s)=p'(s)-F(s,p(s)),

suppose ||S^-1 r(s)||_infinity<=d over the whole interval and

    mu_infinity(S^-1 D_yF(s,z) S)<=mu

over the whole convex tube needed by the mean-value argument.
Here mu may be negative. For real matrices,

    mu_infinity(A)=max_i[A_ii+sum_(j!=i)|A_ij|].

Then the Dini derivative of the scaled error obeys
D^+ e<=mu e+d. With initial bound e0,

    e(s)<=exp(mu s)e0+d (exp(mu s)-1)/mu,  mu!=0,
    e(s)<=e0+d s,                         mu=0.

A certified safe radius lower bound rho_lower closes the local tube argument
only when this upper envelope remains strictly below rho_lower throughout
the interval. For negative mu, checking the endpoint alone is insufficient
unless monotonicity has been established; use the actual maximum or a valid
whole-interval enclosure. In the constant-mu/constant-d case the envelope is
monotone toward d/(-mu), so its maximum on a finite interval is attained at
one of its endpoints.

This construction follows the method in Neumaier's Theorem4.1/Proposition4.3
and reduces to his Corollary4.5 for a global Jacobian bound. It is included to
identify a future tightening route, not to replace the previous nonnegative-L
consumer or certify actual REC values in this survey. No new signed-mu
calculation was run.

## Evidence scope

The mathematical identities A1–A3 and B1–B5 are direct derivations offered
for the parent's selected R5 scope and independent review. They are not new
strong no-go results. Neumaier provides an existing a posteriori method;
its novelty is not claimed. HD source provenance and original gate status
remain those in SURVEY_FINDINGS_KO.md and SOURCE_REFERENCES.json.

