# Original-history response to a controlled diagonal shear

## Scope and reused structure

The new object is a geometry-to-native-history response for the actual313
queries of the original z≈1100 snapshot. HISTORY02R supplies characteristic
and native-reference laws; PB01 supplies the original fixed cells/slopes;
KS01 supplies the same stable frozen scalar incoming operator. This unit
connects them for a named controlled geometry and an isotropic source history
held fixed. It is not a new general null-geodesic theorem or full coupled
anisotropic recombination solution.

Use metric(-,+,+,+), eta=ln a, directional scale factors proportional to
exp[(1+lambda v_i)eta], sum_i v_i=0, and target orthonormal propagation n.
All quantities used in the crossing are energy ratios. Native target thermal
energy TR is k_B T_R expressed in eV; E=hbar omega uses the same eV unit.
c,hbar,k_B have not been set to1 in the physical interpretation. W(x)=exp(-x)
is the source's native Wien departure reference, not a newly selected Planck
occupation. Target solid angle is normalized by4pi, distinct from flux/volume
weights and from a source-sphere solid-angle measure.

Conserved spatial covariant momenta give the Bianchi I redshift law. Primary
source: Fleury, Pitrou and Uzan, Phys.Rev.D91,043511(2015), arXiv1410.8473v3,
https://arxiv.org/abs/1410.8473 . The paper's eta is conformal time, whereas
REC eta here is ln a; its observed-source direction convention may have the
opposite sign to our propagation n. Squared direction weights are unchanged.
Marcori et al., Phys.Rev.D98,023517(2018), arXiv1805.12121,
https://arxiv.org/abs/1805.12121 gives related drift multipole structure.
Our finite stored-history coefficients and second monopole expression below
are derived for the present controlled map, not claimed as measurements in
those papers. SciSpace's repository year2022 is corrected to primary2015/2018.

## Crossing and a baseline-preserving chart

For one query define Lambda=log(E_source/E_target)>0 and w_i=n_i^2.
The positive crossing distance Delta solves

    Delta + (1/2)log(sum_i w_i exp(2 lambda v_i Delta)) = Lambda.

At lambda0, Delta0=Lambda. The implemented chart preserves the actual stored
native query by q(lambda)=q_native+Lambda-Delta(lambda). Record the arithmetic
difference q_native-(eta_target-Lambda) separately. This anchoring is an
explicit represented convention, not proof that these two floating clocks
are exactly equal as real-energy expressions.

Let delta=q-q_native=Lambda-Delta. Solve stably

    delta = (1/2)log1p(sum_i w_i expm1(2 lambda v_i (Lambda-delta))).

For V=max|v_i| and t=|lambda|V<1,

    |delta| <= Lambda*t/(1-t).

This follows from Lambda/(1+t)<=Delta<=Lambda/(1-t). If r is the conservative
fixed-cell intersection margin, |lambda|<r/[V(Lambda+r)] keeps every direction
in the same cell. The contract chooses one-quarter of the smallest margin,
and additionally limits |lambda|V. No new timestep trajectory is needed.

## Native reference and first/second partials

Within a fixed source cell the baseline-preserving history change is g*delta,
where g is the actual stored interpolation slope. Hold target TR fixed and
use the native source reference law TR_source proportional to exp(-q).
Relative to the represented baseline x=E_target/TR, the incoming increment is

    Delta u = g*delta + exp(-x exp(delta)) - exp(-x)
            = g*delta + W(x)*expm1(-x*expm1(delta)).

At delta0 this increment is exactly0. Source reference and propagation thus
change together; merely retiming a stored departure would omit the second
term. Incoming target energies are Ebin for0..310, E21 for311 and E31 for312;
the outgoing source-column index is a different routing object.

Write A=sum_i w_i v_i, C=sum_i w_i v_i^2, h=g-x W, k=(x^2-x)W. Expanding
K(t)=(1/2)log(sum w_i exp(2t v_i)) gives K'(0)=A,
K''(0)=2(C-A^2). Implicit differentiation yields

    q' = Lambda*A,
    q'' = -2 Lambda*A^2 + 2 Lambda^2*(C-A^2),
    u' = h*Lambda*A,
    u'' = h*q'' + k*Lambda^2*A^2.

The source direction tangent at isotropy is

    n_source,i' = Lambda*n_i*(v_i-A),

and n dot n'=0. The first trace susceptibility is B=Lambda*h. These
derivatives hold source history/endpoints and target thermodynamic primitives
fixed. Actual DY,Dtheta, thermal evolution, retiming of endpoints and other
geometry dependencies still need their owners for a total H7 derivative.

## Target angular moments

For dOmega/(4pi), <n_i n_j>=delta_ij/3 and
<n_i n_j n_k n_l>=(delta_ij delta_kl+delta_ik delta_jl+delta_il delta_jk)/15.
Let S2=sum_i v_i^2 and trace(v)=0. Then

    <A>=0, <A^2>=2*S2/15, <C>=S2/3.

Consequently the first monopole vanishes, while the first tracefree
quadrupole Q_ij=< (n_i n_j-delta_ij/3) Delta u > is

    <u'>=0,
    Q_ij'=(2/15)*B*diag(v)_ij.

The second monopole is generally nonzero:

    m2 = <u''>
       = S2*[ h*(-4*Lambda/15+2*Lambda^2/5)
              + k*(2*Lambda^2/15) ].

The six-axis/eight-corner rule in the contract integrates the needed degree4
polynomials exactly. It does not integrate arbitrary finite-shear exponentials
exactly. Finite14ray averages validate the chosen discrete angular model;
their derivatives at zero agree with the continuum moments shown above.
No angular-resolution convergence or finite-lambda continuum error is inferred.

Wolfram's independent symbolic evaluation returned {0,0,0,0} for the crossing
series residual, the two Wien derivatives and the second-mean substitution.
This confirms four algebraic identities only. Numerical and physical validity
are assessed separately using actual source arrays and independent review.

## Scalar frozen-source response and one event ledger

For the stable source held fixed, outgoing dependence on scalar incoming is
affine: o=K_s u+c. It therefore consistently consumes the angular mean, giving

    o_bar'=0,
    o_bar''=K_s*m2.

This is a frozen scalar closure fed by the controlled propagated angular mean.
It is not a direction-resolved anisotropic collision solution. The first
quadrupole is exported as an incoming propagation supplier, not forced through
the scalar source as if angular collisions had already been modeled.

For the same single Ly-alpha event,

    R_gamma''=G_N H*((K_s m2)[311]-m2[311]), G_N=3e6*LYA,
    energy_rad''=+E21_J*R_gamma'', energy_atomic''=-energy_rad''.

The direct incoming term is retained. Units are occupation per lambda^2 for
o'', m^-3 s^-1 per lambda^2 for number and J m^-3 s^-1 per lambda^2 for energy;
lambda is dimensionless. No second event is introduced by outgoing storage.

An existing entrywise interval [Klo,Khi] enclosing the represented K_s can be
applied by exact rational dot to the newly stored binary64 m2 vector. The
result rigorously encloses that represented-vector image. It does not include
errors in Lambda/exp evaluation or certify the complete physical derivative.
Decimal finite checks provide numerical evidence for these new coefficients.

## Physical admission boundary and constructive next step

This supplier makes the geometry/reference contribution explicit for actual
history coordinates, with a controllable causal chart and angular owner.
H5 still lacks same-source continuous defect/stability/tube/reference and
whole-cell curvature evidence; its physical epsilon and outgoing bound stay
null. H6 still requires an admitted target-matched incident trace/geometry,
frame/clock/measure and physical-source closure. H7 still needs the actual
source/endpoints/thermodynamic derivatives to add to this propagation partial.
Global convergence and production are separate. A failed control is recorded
at its actual scope; no strong no-go statement is asserted.
