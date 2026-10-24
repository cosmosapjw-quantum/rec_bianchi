# Exact discrepancy of nested stored histories

## Result and variables

For any two finite scalar tables on a nested2:1 grid, the difference between their continuous piecewise-affine interpolants has an exact cellwise decomposition into a linear common-node discrepancy and a triangular midpoint detail. Its absolute maximum on each coarse cell is attained at one of the three fine knots. The statement applies channel by channel to the314 selected outgoing occupation departures. The coarse/fine numerical trajectories need not solve the same discrete initial-value problem for this represented-function statement; source equality is separately required for the physical interpretation of their difference.

Let coarse nodes be eta_m=eta0+mH and fine nodes eta_(m,j)=eta_m+jH/2, j=0,1,2. Set C0=C_m,C1=C_(m+1), F0=F_2m,Fh=F_(2m+1),F1=F_(2m+2), and u=(eta-eta_m)/H. Define

    E0=C0-F0, E1=C1-F1, delta=(F0+F1)/2-Fh.
    phi(u)=2u for 0<=u<=1/2, and 2(1-u) for 1/2<=u<=1.

Then, for all u in[0,1],

    I_C(u)-I_F(u)=(1-u)E0+u E1+phi(u)delta.                 (1)

The exact cell supremum is

    B=max(|E0|, |(E0+E1)/2+delta|, |E1|).                (2)

## Constructive proof

The coarse interpolant is C0+u(C1-C0). On the left half-cell the fine interpolant is F0+2u(Fh-F0). Subtracting and substituting delta gives (1-u)(C0-F0)+u(C1-F1)+2u[(F0+F1)/2-Fh], which simplifies to the same expression. On the right half-cell I_F=(2-2u)Fh+(2u-1)F1, and substitution with2(1-u)delta proves the second branch. At u=1/2 both expressions equal(C0+C1)/2-Fh; the difference is continuous.

On either half-cell, D=I_C-I_F is affine. For t in[0,1], |(1-t)a+tb|<=max(|a|,|b|) by the triangle inequality. Applying this on the two half-cells bounds |D| by the three knot magnitudes. Each knot is part of the closed interval, so the bound is attained and proves (2). On a half-open operational cell/domain, the same number is the supremum by continuity and the one-sided endpoint limit, though an excluded endpoint is not itself an admitted query. The proof does not sample unknown behavior between stored interpolation knots.

If P_F is the linear interpolant through only F0,F1, then P_F-I_F=phi delta; consequently sup|P_F-I_F|=|delta|. The triangle bound

    B <= max(|E0|,|E1|)+|delta|                           (3)

is useful for identifying cancellation but is generally less sharp than(2). Neither E nor delta alone determines B: choosing E0=E1=-delta cancels the midpoint while preserving endpoint discrepancy; choosing E0=E1=0 leaves only the fine midpoint detail. A direct midpoint calculation protects the implementation from conflating the latter two contributions.

## Continuous-solution relation and open numerical input

For a twice differentiable physical function f, linear interpolation at two exact endpoints has remainder f(eta)-I_f(eta)=f''(xi)(eta-eta_m)(eta-eta_(m+1))/2 for some interior xi. If a justified bound |f''|<=M2 is available on the whole cell, then sup|f-I_f|<=M2 H^2/8. This is the n=1 case of NIST DLMF3.3.5, under its differentiability assumptions. For an exact quadratic, delta=f''H^2/8 exactly. Actual sampled second differences identify a detail of the sampled table; they supply no whole-cell M2 without additional regularity information and a validated bound.

Suppose a same-frame, same-domain fine-reference certificate eps_ref(eta)>=0 establishes |I_F(eta)-f(eta)|<=eps_ref(eta). Triangle and reverse-triangle inequalities give

    max(0,|D(eta)|-eps_ref(eta)) <= |I_C(eta)-f(eta)|
                                  <= |D(eta)|+eps_ref(eta).       (4)

If eps_ref_cell bounds that uncertainty across the cell, B+eps_ref_cell is a valid coarse physical-error upper bound. Thus the discrepancy calculation supplies a concrete term in a future error budget. Currently eps_ref, endpoint uncertainties and physical M2 are null. Different startup memories, different zero-feedback durations, differing step error, event timing and roundoff all enter the measured E. Two runs alone do not identify a convergence order or isolate those mechanisms. This unit measures their combined nodal effect and the separate represented fine detail.

## Floating-point enclosure

Interpret each finite stored binary64 datum as its exact real value. Under correctly rounded binary64 arithmetic without overflow, an operation result widened by nextafter in both directions contains its exact result, including an underflowed operation. The half multiplication is widened for the subnormal case. Interval addition/subtraction is monotone in the relevant endpoints; composing those widened operations therefore encloses C0-F0, C1-F1 and(C0/2+C1/2)-Fh. The absolute-value map of an interval has minimum0 if it crosses0 and otherwise the smaller endpoint magnitude, and maximum the larger endpoint magnitude. Taking maxima over the three resulting absolute intervals yields B_lower<=B<=B_upper.

This is an enclosure of the represented-table quantity(2) under the stated arithmetic model. Floating operations in the decomposition are also checked against a separately constructed exact rational oracle and a local-scale rounding allowance. Arrays and endpoint witnesses are retained so a reviewer can distinguish arithmetic effects from the much larger or smaller measured table discrepancy.

## Connection to existing REC boundary and Bianchi work

The histories store the source-defined signed Wien departure. At a common source eta and common normalization, adding the same Wien reference cancels in I_C-I_F. The H01 event has d_out=T d_in+(1-T)S, where T=exp(-tau/q) and S=xr_p/(3x1s). With frozen geometry, rate and thermodynamic coefficients, a difference delta d_in transfers as delta d_out=T delta d_in and delta R=-G_N Hq(1-T)delta d_in. Those equations and the single-event number/energy ledger are reused from H01; no second source is generated from outgoing storage.

The completed02R characteristic adapter supplies a conditional map of directional retarded queries when its Bianchi frame, geodesic and direction inputs are chosen. This unit is on the actual candidates' scalar FLRW table domain. It introduces no unprovided angular field or thermodynamic Jacobian. A future source-owned query can apply(1) at its admitted common coordinate, then use the already established boundary transfer with an independently allocated input uncertainty.

## Sources and contribution

- NIST DLMF section3.3, equation3.3.5: https://dlmf.nist.gov/3.3. Primary interpolation remainder and differentiability assumptions.
- Peck, Criscuoli and Rast, 2017, ApJ850,9; arXiv:1708.09362, revised2018: https://arxiv.org/abs/1708.09362. Contextual radiative-transfer interpolation-error discussion. Its numerical diffusion results do not certify this REC history.
- Lee and Ali-Haimoud, HyRec-2 (2020 preprint), https://arxiv.org/abs/2007.14114. Recombination context, not a provider of uncertainty for the stored candidate arrays.
- Actual producer/source/clock provenance: provenance/survey/rec_sources/SOURCE_INTAKE_KO.md and PRODUCER_IDENTITY_BINDING.json. Native interpolation guard is documented in the source intake addendum.

Equations(1)-(4) are elementary constructive derivations using standard interpolation and interval arithmetic. The new research contribution in this unit is their source-aligned application to the actual retained h2/h4 histories, with startup/event ownership, raw channel-cell measurements and a usable conditional error interface. No new strong no-go or literature-novel general theorem is claimed. SciSpace discovery metadata is retained with the primary-source date correction; the single bounded Wolfram identity check is preserved separately.
