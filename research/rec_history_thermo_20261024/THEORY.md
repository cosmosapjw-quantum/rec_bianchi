# REC-HISTORY-THERMO01 — local primitive thermodynamic derivative

## Result being constructed and domain
Construct the complete local derivative of the original October-2012 HyRec FULL
hydrogen source at the retained z=1099.9986525171403 face. The six primitive
coordinates are theta=(xe,xHII,ln TR,ln TM,ln nH,ln H). Logarithms mean changes
relative to the positive baseline values, so their increments are dimensionless.
Temperatures inside the native source are rescaled eV, nH is cm^-3 and H s^-1;
fsR=meR=1, all EFFECT_A/B/C/D and DIFFUSION switches are 1.
Signature (-,+,+,+), c,hbar,kB are retained in physical interpretation.

The 313 incoming signed Wien departures u, 311 energies, source frame, geometry,
frequency grid and characteristic query times are held fixed. xe and xHII are
independent source arguments; the analytic source extends to an open
neighborhood with xe>0 and 0<xHII<1. At the pure-H baseline xe=xHII the physical
tangent is the restriction dxe=dxHII. Ambient coordinate columns are not six
independent cosmological trajectories. No history time interpolation derivative,
Bianchi direction/frame variation, matter-temperature evolution equation or
new initial-value solution is included.

The same-domain history admission remains separate. Actual coarse/finer and
original native history arrays exist. Selected-source evidence presently lacks
the independent endpoint/reference uncertainty or validated full-cell curvature
needed to assign a physical epsilon. This unit advances the independent H7
coefficient-dependence obligation needed by a future coupled defect/Jacobian
analysis; H5 remains INPUT_DEPENDENT_UNCALIBRATED.

## Implicit derivative
Write M(theta) X(theta,u)=s(theta,u), where X=(xr2s,xr2p,xv0,...,xv310).
At any nonsingular source state:
  M X_k = s_k - M_k X.
Outgoing o(theta,u)=T(theta)X+P(theta)u obeys
  o_k = T X_k + T_k X + P_k u,
or equivalently the derivative of the native outgoing evaluation at fixed u.
A full-source differential combines this local coefficient derivative with the
already established incoming derivative K du. The prior frozen K does not
supply the M_k,T_k,P_k terms constructed here.

Differentiate the native ionization source as well. With x=1-xHII,
S=C_S TR^(3/2) exp(-EI/TR), A_l=Alpha_l(TM,TR),
Aeq_l=Alpha_l(TR,TR), and C_l=nH A_l xe xHII-S Aeq_l x,
  F = dxHII/dln a = -(sum_l C_l - sum_l Beta_l xr_l)/H.
This expression is algebraically identical to the native DAlpha/Saha expression;
DAlpha means A-Aeq, not a derivative. For k:
  F_k = -(sum C_l,k - sum(Beta_l,k xr_l + Beta_l xr_l,k))/H
        - F (ln H)_k.
Keep the literal source expression for baseline comparisons and document any
algebraic regrouping. The proper-second ionization derivative is that of H F,
if exported, with the H product rule.

## Temperature rates and source coefficient derivatives
The four-point native Lagrange stencils are frozen by the baseline TR,TM/TR.
Let r=TM/TR. Existing primitive_rates supplies derivatives at fixed r or fixed
ln TR. Then
  dA/dln TM = r A_r,
  dA/dln TR at fixed TM = A_logTR - r A_r.
The same chain rule applies to DAlpha; Beta and R2p2s depend only on TR.
Beta detailed balance contributes 3/2+EI/(4TR) to its logarithmic factor.
S contributes 3/2+EI/TR. At fixed temperatures:
  dC_l/dxe = nH A_l xHII,
  dC_l/dxHII = nH A_l xe + S Aeq_l,
  dC_l/dln nH = nH A_l xe xHII.

For the native line escape R_alpha=C_L H/(nH x):
  dR_alpha/R_alpha=dln H-dln nH+dxHII/x.
For each source virtual bin, Gamma is formed BEFORE the two neighboring
Lyalpha diffusion adjustments, exactly as hydrogen.c. With fixed energies:
  tau=Gamma x (hc/E_b)^3 nH/(8 pi H),
  dtau=tau(dGamma/Gamma-dxHII/x+dln nH-dln H).
Use a direct product derivative where Gamma=0; do not divide by zero.

Diffusion coefficients use D_E^2=2 E21^2 TM/mH. Differentiate every recurrence
in populate_Diffusion, including the detailed-balance factor:
  d exp(DeltaE/TM)/dln TM=-(DeltaE/TM)exp(DeltaE/TM).
No negative-rate clipping may be introduced relative to native source.
Two-photon/Raman rates differentiate their Bose denominators and Boltzmann
factors, retaining each fixed energy-sign branch.

## Native piecewise escape map
Let p(t)=1-P_escape and A(t)=1-exp(-t). The native formulas are:
 t<=1e-6: p=t/2-t^2/6, A=t-t^2/2;
 t>1e-6: p=1-(1-exp(-t))/t, A=1-exp(-t).
Their real-source derivatives on a fixed branch are
 p'=1/2-t/3, A'=1-t (small branch);
 p'=[1-(1+t)exp(-t)]/t^2, A'=exp(-t) (large branch).
Stable evaluation of p' may use its convergent series in the cancellation
regime, with the implemented truncation recorded and independently compared
to high precision. Preserve original p/A value semantics for source snapshot
parity; do not silently switch to a different source model or threshold.

Tvv0=Gamma/p (or the native zero-tau limit) and sv=Tvv0*x*u*(1-p).
For t>1e-30, o_b=u_b+(eq_b-u_b) A_b, so
  do_b=A_b deq_b+(eq_b-u_b) A'_b dt_b
at fixed incoming. The native eq denominator is x*p*Tvv0; all factors vary.
The source transparent branch t<=1e-30 gives o_b=u_b and zero coefficient
derivative while that branch is fixed. At a branch surface, two-sided
derivatives or finite differences crossing the switch are not admitted.
Lyalpha: o_alpha=xr2p/(3x); Lybeta/gamma add exp(-E32/TR),exp(-E42/TR).

## Single-event number and energy
R_gamma=G_N H(o_alpha-u_alpha), G_N=3e6*LYA_FACT in m^-3.
  R_gamma,k=G_N H(o_alpha,k+(o_alpha-u_alpha)(ln H)_k).
At fixed atomic constants the same event yields radiation +E21_J R_gamma,k
and atomic -E21_J R_gamma,k. An outgoing storage update adds no second event.
This is the original scalar opaque line convention. It does not provide an
angular collision law.

## Discriminating identities
1. M_xe=0, while s_xe has only the two real entries nH A_l xHII.
2. With simultaneous dln nH=dln H and other primitives fixed, M is invariant:
   M_lnnH+M_lnH=0. The two real sources change by nH A_l xe xHII;
   virtual and incoming line-source coefficients are unchanged.
3. The pure-H ionization direction is the sum of xe and xHII columns.
4. M X_k+M_k X-s_k=0 is an independent implicit residual.
5. Independent complex-step full-source solves on the frozen analytic branches
   verify the six coefficient and outgoing derivatives; central differences
   on two prescribed mixed directions expose branch/step issues.
6. Reusing algebraic values from the stored face and checking newly rebuilt
   coefficients does not rerun the original native trajectory or RESP01
   certificate.

## Evidence interpretation
This is a local Jacobian of the source's piecewise real arithmetic equations,
numerically evaluated in binary64 and checked by independent derivative
methods. It is not an interval enclosure of transcendental or whole-trajectory
errors. No physical tolerance or input epsilon is invented. Literature supports
the source equations and sparse atom/radiation system; the source-bound six
columns and their observed numerical verification are this unit's contribution.
No new strong no-go theorem is proposed (NG1–NG7: not invoked).

