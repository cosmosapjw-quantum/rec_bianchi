# Constructive theory — native path, recurrence and closure

## 1. Fixed source and finite state

Let h be the represented native DLNA and let n be its global integer index.
Let i=n-izH0 denote a radiation-local index. The source maintains electron and
matter-temperature arrays, local H/He variables, two derivative memories per
integrated component, phase flags and a causal radiation history. The augmented
state S_n includes all of these quantities; it is not the vector of virtual
photon spikes alone. The original archive/input/closure and call sequencing
in the compiled execution determine a finite transition S_(n+1)=Phi_n(S_n).
Every observation hook records arguments already evaluated by that transition.
It does not reevaluate a physical source or replace the transition.

For the pure-H differential branch, with F_n the actual returned dxHII/deta,

  x_(n+1)=x_n+h*(5*F_n/4-F_(n-2)/4),
  previous2_next=previous, previous_next=F_n.                 (1)

The same operation applies to actual thermal ODE steps. In the H/He branch the
neutral-H variable is updated with the opposite sign of the ionized-H RHS.
The identity between these statements is xHII=1-xH1s. Post-Saha and algebraic
thermal updates have their own source-defined maps; equation(1) is only used
where its branch was actually taken. Memory initialization by stored secants
must be recorded as initialization, rather than attributed to earlier source
calls. This finite augmented construction is closed because the source code
specifies every branch, interpolation and memory shift from its prior inputs.

## 2. Actual calls and slot ownership

Label successive actual hydrogen calls by m, retaining (phase,callsite,i,z,
xe,xHII,nH,H,TM,TR,F_return). FULL calls also solve the2+311 real/virtual
algebraic populations and write photon history at slot i. Define W_i to be
the last observed FULL call that writes that slot before the captured prefix
is finalized. W_i is computable by one forward traversal of the trace: replace
writer[i] with m whenever an actual write event is recorded. Induction on the
ordered event list proves that the recorded last writer is exactly the native
slot's owner. Unwritten zero-initialized slots are separately marked.

Some post-Saha expressions contain two mutating source calls as operands.
Their textual order is not used to choose W_i. Hooks observe actual execution
order. The final committed thermodynamic node Theta_n and the final writer's
input Theta^W_i are two distinct records. Their equality, where present, is an
observed finite-source property; a mismatched trial writer is not relabelled
as a committed node. Capturing final radiation arrays supplies a direct join
check against each stored writer's outgoing values and the retained old data.

## 3. Discrete arithmetic and consistency

Treat captured finite binary64 values as exact reals. For an actual integrated
component let sigma=-1 for neutral-H xH1s, whose logged native return is the
ionized-H derivative, and sigma=+1 for the other integrated components. Define
F_current and F_previous2 as sigma times their logged native derivative values;
these are the signed derivatives of the component X. The represented residual is

  rho_n = X_out-X_in-h*(5*F_current/4-F_previous2/4).          (2)

This can be evaluated exactly with rational arithmetic. It measures evaluation
rounding of this discrete update and the correctness of logged operands. It
is neither the local truncation error nor the continuous ODE defect. A
componentwise operation scale is

  G_n=|X_out|+|X_in|+|h|*(5|F_current|/4+|F_previous2|/4).

The frozen finite-source check uses |rho_n|<=64*eps64*G_n, with zero G requiring
zero residual. Different C parenthesization of the update remains visible in
the exact residual and is not removed by rounded recomputation.

For a smooth exact trajectory with F(eta)=X'(eta), expanding F(eta-2h) gives

  X(eta+h)-X(eta)-h*(5F(eta)/4-F(eta-2h)/4)
    = (2/3)h^3*X'''(eta) -(7/24)h^4*X''''(eta)+O(h^5).      (3)

Constant and linear F are integrated exactly; the leading local consistency
order is3, hence the source's second-order terminology. This Taylor result
requires a smooth exact differential branch. It supplies no bound across a
phase switch or on the unknown physical X''' of the actual capture.

## 4. Exact represented reconstruction on existing H5 cells

For each original query j, keep its exact represented geometric endpoints
(a_j,b_j), q_j, route and source-column index from SOURCE_CONTEXT. Let U_L,U_R
be the newly captured committed row values at the corresponding radiation
indices; keep writer-input endpoints as a separate U^W variant. Set

  alpha_j(t)=(t-a_j)/(b_j-a_j), alpha_j=alpha_j(q_j),
  Uhat_j(t)=(1-alpha_j(t))*U_L+alpha_j(t)*U_R,
  slope_j=(U_R-U_L)/(b_j-a_j).                              (4)

The identities Uhat(a)=U_L and Uhat(b)=U_R follow by substitution. Strict
t in(a,b) implies0<alpha_j(t)<1; consequently min(U_L,U_R)<=Uhat<=max(U_L,U_R)
componentwise. Positive endpoint fields remain positive along this declared
affine segment. All operations in(4) are exact rational operations on source
binary64 values and existing stored clock endpoints. A norm requires an
explicit compatible weighting; no full-state norm is inferred from a scalar.

The derivative is the exact slope on each open segment. At a common knot the
derivative jump is slope_right-slope_left; the distributional second derivative
contains this jump times the knot delta. Thus a segment's zero classical second
derivative is a fact about the chosen affine representation. It is not a bound
on the unknown physical curvature. This explicit represented path is useful
input to later defect evaluation because both its value and its derivative
are now specified on the same cells as the existing H5 queries.

There are distinct clock maps: native global index, native local index,
-log(1+rounded native z), and the stored H5 geometric endpoint. All are labelled.
The new data join uses the original integer mapping and stored endpoints. It
does not use a fresh logarithm to redefine the previous context or alpha.

## 5. Algebraic closure differentiation

The source forms a block linear system for2real and311virtual native departures
from equilibrium with1s (the source comment states xi-xi[eq with1s]):

  M(eta)v(eta)=s(eta),                                     (5)

Here v is the solved departure vector, not an absolute population vector.
Its virtual components satisfy xv_b=x1s*Dfnu_b and the native Lyalpha output
is xr_2p/(3*x1s). Signed departures are allowed. The coefficients depend on
thermodynamic inputs and the causal incoming
radiation. On an interval where M,s are C2 and M is invertible, differentiate
(5). Product rule and left multiplication by M^-1 give

  v'=M^-1*(s'-M'v),
  v''=M^-1*(s''-M''v-2M'v').                              (6)

This is a constructive implicit derivative formula. For any compatible induced
norm, if uniform bounds A>=||M^-1||, Bk>=||M^(k)|| and Sk>=||s^(k)|| exist,

  V0=A*S0,
  V1=A*(S1+B1*V0),
  V2=A*(S2+B2*V0+2*B1*V1)                                (7)

bound ||v||,||v'||,||v''|| respectively. These statements follow from triangle
inequality and submultiplicativity; invertibility and uniformity are explicit
premises. A saved solve residual at one state does not provide A or Bk/Sk.

For an output y=Q(z), z=(eta,theta,u,v), with Q C2,

  y'=DQ(z) z',
  y''=DQ(z) z'' + D2Q(z)[z',z'].                           (8)

The first coordinate eta has eta'=1,eta''=0. Incoming u can be differentiated
on a fixed causal interpolation stencil using its original pullback map;
stencil crossings need the previously retained jump/boundary terms. Equations
(6)-(8) specify the actual coefficient/input derivatives a physical M2 supplier
must enclose. They do not assign dynamics to algebraic virtual spikes.

## 6. Connection to the retained H5 conditional bound

Given a specified continuous coupled F, a fixed norm, an absolutely continuous
reconstruction Xhat and actual initial error e0, let delta bound
||Xhat'-F(eta,Xhat)|| throughout an admissible tube. If F is uniformly L-Lipschitz
there, the usual integral comparison yields

  e(eta)<=e0 exp(integral L)+integral delta(s)exp(integral_s^eta L)ds.  (9)

A tube must contain this comparison bound and remain in the domain on the
whole interval. Model/closure discrepancy belongs in delta or an explicitly
separate forcing bound. The preceding capture supplies Xhat and its segment
slopes; it does not assign values to missing F/norm/e0/delta/L/tube inputs.
The previously proved exact native Wien translation and reference curvature
bounds remain valid with unchanged inputs and are reused, without rerunning.

## 7. Actual contribution and scope

The theoretical output is a finite native-source/call/slot construction,
exact represented reconstruction, correct skipped-history multistep identity,
and explicit implicit-closure curvature supplier equations. Numerical
acquisition/joins/controls implement these statements next. Physical uniform
H5 coverage remains0/313 until its independent operands are supplied.
No new no-go or universal exclusion is asserted (NG1-NG7 not invoked).

