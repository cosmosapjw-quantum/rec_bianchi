# LINE02: exclusive native Lyα replacement and a scalar rank-one solve

Date: 2026-10-23 Asia/Seoul. Constructive R4/R5/R7/C3 work, not the independent
review. Skill context actually read: physmath-research-loop 1.3.0, SKILL.md,
POLICY_INTEGRATION.md, THEORY_LOOP.md and CODING_LOOP.md in the owner workspace; exact skill context is included in the final archive.
Source inspection: pinned REC114 May-2012 hydrogen.c, preserved physical-flux
adapter, complete z≈1100 CSV, LINE01 THEORY.md and FROZEN_CONTRACT.md.
Two Wolfram evaluator calls check the identities below; full context response and
actual requests/results are in provenance/WOLFRAM_RECEIPTS.json. The context search returned
several irrelevant/no-result items; those are preserved and not used as evidence.

## 1. Chosen object and owner boundary

Use the native two-real plus 311-virtual algebraic system. Real variables are
departures x_r=(δx_2s,δx_2p), dimensionless per hydrogen nucleus. Virtual variables
are the native radiation departure coordinates, not 311 physical atomic species.
Write z for the virtual vector and e=(0,1)^T. All coefficients and incoming history
are frozen at the one preserved snapshot. This is a local algebraic source adapter,
with no proper-time or cosmological integration.

The actual source code (hydrogen.c populateTS_2photon) adds exactly

    r0 = LYA_FACT(fsR,meR) H / (nH_cm3 x1s),
    Trr[1,1] += r0,      sr[1] += r0 b0,
    b0 = 3 x1s Dfplus_Lya.

Here r0 is s^-1 and b0 is dimensionless. At the preserved fsR=meR=1 state,
r0=1.08321818155567779 s^-1. Preserve LYA_FACT=4.662899067555897e15 cm^-3.
Recomputing it from modern exact SI hc changes the coefficient by about
−2.6616535e−7 relative; source parity uses the literal native coefficient.
The emitted photon energy uses the explicitly selected native E21 and SI eV/J
conversion; it does not silently replace the native escape normalization.

The 2p diagonal additionally owns Beta1, R2p2s, two-photon/Raman terms and
A2p_up+A2p_dn diffusion. These, Trv/Tvr/Tvv, sv, other sr components, and the
incoming history owner stay fixed. Removing the entire 2p diagonal would remove
unrelated physics. The local direct-line signed emission per H is

    h0(x_r) = r0 (e^T x_r − b0).

Replace this affine operator exclusively by h*(x_r)=r*(e^T x_r−b*), with
r*≥0. This changes the original owner pair once; it is not an additive extra
LINE01 source. The boundary b* is a declared parameter perturbation of this core
interface, not a change to the simultaneously frozen virtual incoming spectrum.
Its physical interpretation remains this local partial derivative.

## 2. Schur reduction and exact rank-one update

The full frozen equations are

    Trr x_r + Trv z = sr,
    Tvr^T x_r + V z = sv.

V is reconstructed from the native three diagonals; the source's stored Tvr has
shape (2,311), which explains the transpose. Assuming V invertible, define

    W = V^(-1) Tvr^T,  u = V^(-1) sv,
    K = Trr − Trv W,  j = sr − Trv u.

Then K x0=j and z0=u−W x0. Let v=K^(-1)e and a=e^T v. For
Δr=r*−r0 and Δs=r*b*−r0*b0,

    K* = K + Δr e e^T,  j* = j + Δs e,
    η = 1 + Δr a.

Provided K is invertible and η≠0,

    x* = x0 + v (Δs − Δr x0_p)/η,
    z* = z0 − W (x*−x0),
    det K* = det K × η.

Proof: substitute x*=x0+v α into K*x*=j*. Since Kv=e, the residual is
e[α+Δr(x0_p+aα)−Δs], which vanishes for the stated α. The virtual equation
vanishes by construction. The determinant identity follows directly for this
two-by-two K (or from multilinearity of determinant). This also proves uniqueness
under the stated conditions. No large matrix inverse or repeated virtual solve is
required after the frozen preparation.

For the complete 313-vector X, define w=(v,−Wv) and let E select its 2p entry.
Then X*=X0+w α and E^T w=a. This supplies full-state error and tangent maps with
one scalar update. A prior approximate X0 with residual q=M X0−s must not be
called an exact solution: the same update preserves q unless the baseline is
first solved/corrected. Record source-snapshot roundoff separately from the new
algebraic solve residual.

## 3. Numerically useful form and conditioning

Avoid subtracting two similar r*b products unnecessarily. Set Δb=b*−b0 and use

    n = Δr (b0−x0_p) + r* Δb,
    α = n/η.

This is algebraically identical to Δs−Δr x0_p. Use a compensated two-term sum
where practical, retain signed drives, and normalize cancellation tests by gross
loss+incoming scales rather than a small net flux. Exact unchanged parameters
can return the stored/prepared baseline without a new solve.

η is a source-dependent rank-one condition monitor, not the entire condition
number of K*. Require finite parameters and a declared denominator margin, e.g.
η>64 ε_machine(1+|Δr a|), in the physical continuous branch η>0. Report
||K*|| ||K*^-1|| or a residual-based conditioning diagnostic separately if used.
Negative η is algebraically possible but is not admitted by the selected physical
branch. A failed guard is an explicit input-domain rejection, not zero response.

If deleting the native line leaves K_host=K−r0 e e^T nonsingular with positive
inverse in the relevant entries, then γ=r0 a lies in [0,1). This can be checked
for the actual frozen state; do not assume it merely from a source comment.
For all r*≥0, η=1−γ+r*a then stays positive. If this extra property is not
established, retain the explicit η guard; the rank-one identity itself is unchanged.

### 3.1 Stable solved event drive

At a large synthetic r*, subtracting rounded x*_p and b* can lose the small
net event drive. With D0=x0_p-b0, gamma0=r0*a and Delta_b=b*-b0, the same
rank-one identity gives exactly

    D* = x*_p-b* = [D0-(1-gamma0)*Delta_b]/eta,
    h* = r* D*,
    1-gamma_base = (1-gamma0)/eta_base.

To prove the first identity, insert the stable alpha expression and collect
D0(eta-a*Delta_r)/eta and Delta_b(a*r*-eta)/eta; their coefficients are
1/eta and -(1-gamma0)/eta. This is a computational form of the same affine
source, not a new approximation. Retain the direct rounded-state subtraction
as a conditioning diagnostic, but use the rational drive for small flux and
its tangent/bound comparisons. Arithmetic resolution and analytic truncation
bounds are reported separately. The implementation was reconstructed after
the scratch incident; current code and primary output have new identities.

## 4. Residual JVP and solved-state JVP

For an arbitrary full state X and the original full matrix M, source s,

    F*(X,r*,b*) = M X−s + E[Δr X_p−Δs].

At fixed frozen coefficients, for a state direction Vx and parameter directions
dr,db,

    δF* = (M+Δr EE^T)Vx + E[(X_p−b*)dr−r*db].

The reduced expression replaces M by K. At the solved point,

    δx* = (v/η)[(b*−x*_p)dr+r*db],
    δz* = −W δx*.

Proof: differentiate K*x*=j*; the right side is
e[(b*−x*_p)dr+r*db]. The rank-one inverse on e is v/η, verified by direct
multiplication. These derivatives include the solved real/virtual response but
freeze TR, TM, x1s, nH, H, the other line sources, all virtual blocks and history.
They are not the full thermodynamic/cosmological Jacobian. In particular an x1s
direction would also differentiate the departure coordinate, r0, b0, recombination
and virtual opacity coefficients and is outside this JVP contract.

The signed line-rate tangent is

    δh* = (x*_p−b*)dr + r*(δx*_p−db).

For a prescribed state (rather than a solved one), replace δx*_p by Vx_p.

## 5. Source-compatible angular extension

For a declared effective A>0, use τ=A/r0, preserving the native ground-opacity
normalization. Native Wien source and ground-state opacity are retained. This
is the controlled native-compatible extension; it is not the full stimulated
population opacity of LINE01. For tracefree S=σ/H and q(n)=1+S:nn>0, reuse
the existing angular moments B=<β(τ/q)> and Q=<PSTF(nn)β(τ/q)>.
Define

    ρ=τ B=<q(1−exp(−τ/q))>,
    ζ=τ Q=<PSTF(nn) q(1−exp(−τ/q))>.

The replacement is r*=r0 ρ, b*=b0. Both loss and blue feedback carry the same
ρ. Varying only the loss coefficient fails the prescribed equilibrium condition.
The signed photon scalar and PSTF injection are

    Rγ = nH_SI r0 ρ (x*_p−b0),
    Πdotγ = E21_J nH_SI r0 (x*_p−b0) ζ.

In the uniformly thick limit, <q>=1 and <PSTF(nn)q>=2S/15 give
ρ→1 and ζ→2S/15. Thus isotropic incoming radiation and tracefree shear preserve
the scalar native rate in this thick approximation, while a nonzero quadrupole
injection remains. For a tracefree dS tangent within this same approximation,
δr*=0 and δΠdotγ=E21_J nH_SI h0 (2 dS/15) at fixed scalar solution. These are
injection rates, not the value of an evolved radiation stress tensor.

The finite-depth outgoing distortion diagnostic is

    d_out(n)=d_in+[x*_p/(3x1s)−d_in](1−exp(−τ/q(n))).

Its isotropic thick limit is the actual native history formula
Dfminus_Lya=xr[1]/(3x1s). Finite replacement coefficients with the old thick
history output are not a complete coupled runtime replacement. This unit freezes
incoming history and may return the diagnostic; the future history owner must
install the consistent outgoing boundary before a coupled history run.

## 6. Finite-opacity error bound propagated through the source solve

Let ε=1−ρ=<q exp(−τ/q)> and δ=exp(−τ/qmax), so 0≤ε≤δ because q>0 and
<q>=1. Let x0 denote the thick/native algebraic solution, D0=x0_p−b0,
γ=r0 a≥0 and assume γδ<1. Then the exact finite-depth solved-state difference is

    Xfinite−X0 = w r0 ε D0/(1−γ ε).

Consequently, for any chosen vector norm,

    ||Xfinite−X0|| ≤ ||w|| r0 δ |D0|/(1−γδ).

This is a frozen-source state error bound, not a global time-integration bound.
The line flux obeys the exact identity

    hfinite/h0 = (1−ε)/(1−γ ε)   when h0≠0,

and hence

    |hfinite−h0| ≤ |h0| |1−γ| δ/(1−γδ).

At D0=0 both source solutions coincide and the absolute bound is zero; avoid a
0/0 relative statement. For K_S=2S/15, the angular tensor bound
||ζ−K_S||_F≤sqrt(2/3) ε follows from the Frobenius norm of PSTF(nn).
Thus

    ||Πdot_finite−Πdot_thick||_F
      ≤ E21_J nH_SI |h0| δ [sqrt(2/3)+γ||K_S||_F]/(1−γδ).

This separately accounts for the population response and angular-shape error.
It cannot be inferred solely from a scalar escape-factor relative error.
For the actual huge τ, retain logδ=−τ/qmax; an underflowed floating zero is not
a claim that the finite-depth correction is mathematically zero. Log bounds can
be reported without evaluating exp(logδ) in binary64.

For two general coefficient/boundary choices (r_a,b_a),(r_b,b_b), let
w_a=M_a^-1 E and a_a=E^T w_a. The exact finite difference is

    X_b−X_a = w_a { (r_b−r_a)(b_a−X_a,p)+r_b(b_b−b_a) }
                       /{1+(r_b−r_a)a_a}.

Its norm gives a direct source-uncertainty/perturbation envelope when the
denominator is bounded away from zero. Do not reinterpret it as quantified
atomic-data uncertainty without actual source uncertainty inputs.

## 7. Number, energy and ionic-yield ledger

For signed direct-core Rγ (m^-3 s^-1), the local reaction ledger is

    dn_2p/dt=−Rγ, dn_1s/dt=+Rγ, dn_gamma/dt=+Rγ,
    du_atomic_internal/dt=−E21_J Rγ,
    du_gamma/dt=+E21_J Rγ, du_kinetic/dt=0.

Atomic-number and combined internal+radiation energy sums vanish identically.
Free electron and ionic yields for this bound–bound source are zero. It remains
a channel ledger attached to a quasi-stationary algebraic source, not a solved
thermal equation or a license to sum virtual coordinates as atomic populations.
Use proper time seconds in the comoving orthonormal frame, signature (−,+,+,+),
E21=2πℏν, and retain c,ℏ,k_B in physical conversions. No recoil heating, unresolved
line overlap/polarization or matter anisotropic-stress state is supplied.

## 8. Why LINE01 full Planck/stimulated physics remains separate

Let c0=3x1s, w_B=exp(−E21/TR), y=xr[1] and d=Dfplus_Lya. Physical x2p=y+c0w_B.
Native core action is hN=r0(y−c0d). The full Planck incident occupation is
fP+d=w_B/(1−w_B)+d, and a stimulated-opacity thick source normalized with the
same r0 would instead have

    hP=c0r0[(y+c0w_B)/(c0−y−c0w_B)−w_B/(1−w_B)−d]
      =r0[y/{(1−w_B)(1−w_B−y/c0)}−c0d].

Therefore hP−hN=r0 y[1/{(1−w_B)(1−w_B−y/c0)}−1], and
dhP/dy=r0/(1−w_B−y/c0)^2. At y=d=0 both are LTE, but they are different
off-equilibrium operators. The source-constant conversion is another separate
difference. No native equivalence is claimed from small numerical differences.
The selected LINE02 affine path preserves the exact native operator convention;
the nonlinear full-stimulated path remains a documented alternative.

## 9. Acceptance mapping (exact counts and tolerances in FROZEN_CONTRACT.md)

1. Reconstruct full313 and Schur2 from the one preserved input; compare the new
   rank-one update with fresh direct algebraic reference solves for a bounded
   coefficient/boundary set. This is new source-adapter validation, not history replay.
2. Check full residual with component gross scales |M| |X|+|s|, not net residual
   self-normalization. Check reduced and reconstructed virtual states separately.
3. Check state and (dr,db) JVPs against analytic direct-matrix expressions and
   selected independent finite/complex directions, retaining scale and conditioning.
4. Verify exclusive owner removal/replacement, unchanged virtual blocks, matching
   modification of loss and feedback, energy/number signs, and duplicate-owner
   rejection. Include wrong-sign/wrong-normalization mutations as falsifiers.
5. Use a few finite-depth manufactured probes to test bounds that underflow at
   the actual native τ. Label them controlled source-interface fixtures, not
   additional saved cosmological states. Reuse ANGULAR01 kernel evidence.
6. Plot source-driven real/virtual response and ledger, local derivative residual,
   and scalar/PSTF angular response. Read actual figures in the single review pass.

No IVP or original native runtime is required by these derivations. The independent
review and production numerical evaluation belong to the parent unit, not this
constructor. Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false remain.
