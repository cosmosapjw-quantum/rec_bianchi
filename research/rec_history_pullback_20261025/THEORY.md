# REC-HISTORY-PB01: source-bound endpoint/query pullback

## 1. Defined object and retained source

The receiver is the frozen THERMO01/KS01 target:
z=1099.9986525171403, T0=2.728 K,
nH0=0.18745798773143102 m^-3, fsR=meR=1.
The independent variables here are signed, dimensionless native Wien-departure
history samples and the dimensionless emission coordinate eta=ln(a). Geometry,
reference temperature, source coefficients, prefix length and channel owners are
held fixed. A physical retiming provider must subsequently supply their coupled
variation. The metric convention is (-,+,+,+); no new natural-unit convention is
introduced. Existing number and energy response units are retained.

The native source interp_Dfnu/fplus_from_fminus interpolates outgoing departures
directly, using alpha=(q-eta0)/h-k and k=floor((q-eta0)/h). Its TR argument is unused.
Ly-beta/gamma exponential factors belong to the outgoing producer already.
The retained history_boundary.interpolation and interpolation_jvp are reused.
The 313 source indices form a permutation of 1..313, hence their two samples
(source,k),(source,k+1) are 626 distinct active history coordinates. Their actual
input census is a primary acceptance condition.

KS01 supplies an interval [Klo,Khi] for the real linear algebra of frozen
binary64 coefficients M,B,T,P:
K_s=T M^-1 B+P, shape314x313. At fixed thermodynamic coefficients this response is
independent of incoming u. Its existing inverse-residual proof and numerical
controls are reused; no solve, inverse, source coefficient generation or
THERMO six-column derivative is part of PB01.

## 2. Anchored chart and arithmetic bridge

For each admitted query q_j, retain the actual native-order binary64 fraction
a_j, the nominal binary64 h>0 and the two binary64 history samples y_Lj,y_Rj.
These stored values are treated as exact real constants in the new chart.
The base input for local source composition remains the stored KS01 incoming u0.
Define the connected history perturbation by the increment of this chart:
u_connected=u0+H(dy,xi)-H(0,0). This preserves the local source/Js anchor exactly.

H_j(dy,xi)=(1-a_j-xi_j/h)(y_Lj+dy_Lj)
           +(a_j+xi_j/h)(y_Rj+dy_Rj).

This definition separates the local coordinate map from evaluation rounding.
The fraction in KS01 admission used (q-eta[k])/h; it was a numerically checked
reconstruction, not a bitwise identity with the native order. Record both
fractions and both base reconstructions in PB01. Neither discrepancy is a
physical history uncertainty.

For a finite native query evaluation q'_j, define
xi_actual=q'_j-q_j using the exact difference of the two represented coordinates,
a'_j=the retained native interpolation fraction at q'_j, and
e_a,j=a'_j-a_j-xi_actual/h.
Then the exact real interpolation with native fractions differs from the
anchored chart by e_a,j*(y'_Rj-y'_Lj). This is an arithmetic bridge, before the
floating-point endpoint and interpolation evaluation errors. Independent
Fraction controls evaluate the identity on the actual binary64 constants.
The implementation records actual rounded endpoint increments and query shifts
for native finite controls, so requested perturbations are not silently treated
as exactly representable.

## 3. Domain and fixed-stencil responsibility

The chart is convex in its endpoint samples for
-h*a_j < xi_j < h*(1-a_j).
The query must also remain in the same source cell and strict available prefix
when checked through the retained interpolation function. Preserve the stored
eta-knot margins, native-order/chart margins and global strict-prefix margin as
distinct quantities. The implementation takes the conservative intersection,
uses an interior safety factor for probes, and confirms the same k/prefix.

A nonzero query tangent at an exact representable knot is refused by the
retained scalar JVP. Endpoint-only variation at a fixed selected knot follows
the retained scalar contract. Cell crossings require a new branch/one-sided
contract. A supplied query law xi=DQ*dp is an external input, not generated here.

## 4. Tangent, adjoint and exact finite remainder

Let P be the313x626 sparse interpolation matrix with disjoint row supports:
P[j,2j]=1-a_j, P[j,2j+1]=a_j.
Let g_j=(y_Rj-y_Lj)/h and G=diag(g).
Differentiating H at dy=xi=0 gives
dH=P*dy+G*xi.
The connected outgoing first variation is
do=A*dy+C*xi, A=K_s P, C=K_s G.

For the declared Euclidean coordinate pairing, write v=K_s^T*w.
Then A^T*w=P^T*v and C^T*w=G*v. P^T is a scatter-add operation.
These are coordinate cotangents. A physical integral inner product requires its
own measure/Riesz map; no angular/volume measure is chosen by PB01.

Direct expansion gives the exact finite remainder:
H(dy,xi)-H(0,0)-P*dy-G*xi = r,
r_j=(xi_j/h)*(dy_Rj-dy_Lj).
Consequently the fixed-coefficient source increment is exactly
Delta o=K_s*(P*dy+G*xi+r).
For dy=t*d and xi=t*x the remainder is t^2*x_j*(d_Rj-d_Lj)/h.
No third-order term occurs in this fixed chart. Separate theta variation remains
the existing numerically checked Js term, with its own local remainder.

## 5. Endpoint norm preservation

Assume 0<=a_j<=1 and distinct active endpoint columns for different j.
For every output row i, disjoint columns imply
sum_p |(K_s P)[i,p]|
 =sum_j (|K_s[i,j]|*(1-a_j)+|K_s[i,j]|*a_j)
 =sum_j |K_s[i,j]|.
Taking the maximum gives ||K_s P||_inf=||K_s||_inf.

This is a conditional algebraic identity, applied after the actual source-slot
census. Therefore KS01's certified interval
[1.17562722922718,1.1756272292401908] is inherited by the endpoint pullback norm.
The constructive equality follows from positive partition and disjoint support.
For shared supports the triangle inequality still gives <=; equality can fail
by cancellation. A small shared-support example checks this condition.
This standard linear-algebra observation is not claimed as a new no-go theorem.

## 6. Query block and conditional finite boxes

Each exact rational g_j is computed from the stored binary64 endpoint values
and h. Its enclosing float endpoints and the existing K interval give C
element intervals by outward elementary multiplication. Outward sums of
absolute endpoint envelopes give lower/upper row gains and a norm enclosure.
The common-clock column C*1 and optional per-row radius-scaled query gains are
reported separately from independent query-coordinate gains.

For supplied nonnegative endpoint radii e_Lj,e_Rj and query radii tau_j inside
the fixed-cell domain, define
b_j=(1-a_j)e_Lj+a_j e_Rj+|g_j|tau_j
    +(tau_j/h)(e_Lj+e_Rj).
The expansion above and triangle inequality imply
|Delta o_i| <= sum_j W_ij*b_j,
W_ij=max(|Klo_ij|,|Khi_ij|).
All arithmetic forming a claimed enclosure is outward.
The first three terms bound the tangent, and the final term bounds the mixed
finite remainder. Manufactured boxes validate implementation only.
Physical endpoint/query/reference/curvature uncertainty remains unassigned.

For a continuous physical history, its independently justified interpolation
error must additionally be supplied, e.g. endpoint uncertainty plus
M_cell*h^2*a*(1-a)/2 at the corresponding query. The cellwise linear stored
representation's zero curvature does not assign the physical M_cell.
Current physical epsilon and physical outgoing bound stay null.

## 7. Event composition and next physical connection

KS01's stored ionization, proper-time, Ly-alpha number, radiation energy and
opposite atomic energy response rows are composed with the same P and G.
Their source H, energy and volume normalization are retained; no H=2e-13
constant from a different checkpoint is imported. Atomic/radiation opposite
signs are preserved by paired interval endpoints of the same event.

For an eventual named physical parameter p, the missing source map is
dy=DY*dp, xi=DQ*dp with any needed reference-offset derivative. Only after those
owners are admitted may the physical chain
Js*Dtheta + A*DY + C*DQ + reference contributions
be assembled. H5 calibration, H6 actual trace/frame and H7 geometry/thermal
evolution remain distinct obligations.

## Evidence and novelty status

The native source and scalar adapter supply the variable and clock convention.
The chain rule, adjoint and bilinear formula above are directly derived.
Wolfram checked the generic tangent, exact remainder and transpose identity:
three True results, timeConstraint10s; remote CPU unmeasured.
Polavarapu et al., Tellus A48(1996),74-95,
DOI10.3402/tellusa.v48i1.11633, was found through SciSpace and its abstract read
through Exa: interpolation regularity affects tangent validity. The full theorem
is not imported as a premise. Official dolfin-adjoint verification documentation
was read for Taylor remainder testing. Four sample steps will be diagnostic
implementation evidence; the exact chart identity supplies the algebraic result.
NG1-NG7 are not applicable to a new strong no-go claim because none is proposed.
