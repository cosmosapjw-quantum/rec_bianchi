# Native reference theorem and H5 composition
Unit REC-H5-NATIVE-REFERENCE01; R5 adopted derivation under FROZEN_CONTRACT.md.

## Theorem 1: exact native observable map
Let E,kN,T0 be positive exact real interpretations of the frozen source scalars, eta in a finite real interval, x=E exp(eta)/(kN T0), and w=exp(-x). Then w is smooth and
w'=-x exp(-x),
w''=(x^2-x)exp(-x),
w'''=(-x^3+3x^2-x)exp(-x).
For G(eta,f)=f-w(eta), G_f=1, G_ff=G_eta_f=0,
G_eta=x exp(-x), G_etaeta=-(x^2-x)exp(-x).

Proof. x'=x. Apply product and chain rules successively. The f derivative is the identity in the scalar occupation coordinate. In norm abs(delta_f) its factor is one; in norm abs(delta_f)/s_f it is s_f. This scalar fact makes no assertion about an unspecified full coupled-state norm.

## Theorem 2: whole-cell derivative envelopes
On any finite cell [a,b], x is positive and increasing. The exact supremum of abs(w') is the largest endpoint value and the value at x=1 when in [x(a),x(b)]. The exact supremum of abs(w'') is the largest endpoint value and the values at r_minus=(3-sqrt(5))/2 and r_plus=(3+sqrt(5))/2 whenever contained.

Proof. abs(w')=x exp(-x), whose x derivative is (1-x)exp(-x). On either side of x=1, abs(w'') is smooth; its interior nonzero extrema require w'''=0. Since x>0, the only such roots solve x^2-3x+1=0. The remaining nonsmooth point x=1 is a zero and cannot increase the maximum. Compactness gives attainment, including singleton cells. On x>r_plus both envelopes decrease, so the left endpoint suffices only after proving the whole-cell regime. An interval enclosing either critical point that overlaps the cell is conservatively included in the implementation.

## Theorem 3: exact reference translation preserves a posteriori operands
Suppose f'=Ff(eta,f), with the regularity used by the conditional H5 theorem. Set y=f-w and Fy(eta,y)=Ff(eta,y+w)-w'. For any differentiable approximate path fhat, define yhat=fhat-w. Then
yhat'-Fy(eta,yhat)=fhat'-Ff(eta,fhat).
For any two states at the same time, their differences and any fixed norm of those differences are unchanged by the translation. Hence initial error, defect, state Lipschitz bounds and corresponding translated tube radii are preserved.

Proof. Substitute the definitions and cancel w'. The state difference identity follows by cancelling w in both states. At fixed eta, the difference of Fy at two states is exactly that of Ff at translated states; the translation maps the two tubes bijectively. The result applies componentwise when only photon coordinates are translated. A different or approximate reference would introduce additional value/derivative terms and is outside this lemma.

This theorem does not supply the currently absent coupled trajectory or Ff, defect, stability, positive uniform tube or initial error.

## Theorem 4: distinct characteristic and native-temperature bridges
For positive target/source energies Et,Es and 1+z>0 define
qstar=-ln((1+z)Es/Et), xt=Et/(kN T0(1+z)), delta=qhat-qstar.
Then xs(qstar)=xt and
Bchar=ws(qhat)-exp(-xt)
     =exp(-xt)*expm1(-xt*expm1(delta)).
For the separate represented native temperature TRhat>0,
BTR=exp(-xt)-exp(-Et/TRhat),
Btotal=Bchar+BTR=ws(qhat)-exp(-Et/TRhat).

Proof. Exponentiating qstar gives Et/((1+z)Es), which cancels Es. Also xs(qhat)=xt exp(delta). Factor exp(-xt) and subtract one; the displayed nested expm1 identity follows. Adding BTR telescopes. Each identity concerns the prescribed reference. It does not bound physical occupation retiming.

## Theorem 5: exact native-to-absolute-interpolant bridge
For a<qhat<b let alpha=(qhat-a)/(b-a), I the endpoint affine interpolation functional, yL,yR the frozen departure samples and uhat the frozen incoming value. Put
Jref=I[ws]-ws(qhat), ra=uhat-I[y].
Then
(uhat+w_native)-I[y+ws]=ra-Jref-Btotal,
abs(Jref)<=M2_ref*(qhat-a)*(b-qhat)/2,
abs(DirectBridge)<=abs(ra)+upper_abs(Jref)+upper_abs(Btotal).

Proof. Expand I linearly and insert ws(qhat), giving the signed identity. The scalar linear interpolation remainder for C2 reference functions is
ws(qhat)-I[ws]=ws''(xi)*(qhat-a)*(qhat-b)/2
for some xi in (a,b); taking absolute values proves the bound. For q at an endpoint the residual is zero by definition. If x(a)>1 then ws''>0 throughout, so the chord residual Jref is nonnegative. The final bound is the triangle inequality. The old exact anchor radius is abs(ra) and is preserved, even when the native alpha differs from geometric alpha.

## Corollary: the known term in physical H5 curvature
For physical occupation coordinate fj with fj'=Fj(eta,f),
y_j''=partial_eta Fj + (D_f Fj)F - ws''.
Thus a separately supplied whole-tube bound A_j on
abs(partial_eta Fj+(D_f Fj)F)
yields physical departure curvature <= A_j+M2_ref.
The current producer determines M2_ref. It does not determine A_j.

More generally, for G(eta,u) along u'=F,
d2G/deta2=G_etaeta+2G_eta_u F+G_uu[F,F]
          +G_u(partial_eta F+D_u F F).
The source-specific G derivatives now have explicit operands. To apply the conditional H5 tube theorem, the actual F/path/norm/defect/stability/tube and physical endpoint error operands are still needed. The single target native face does not stand in for an all-time coupled trajectory.

## Evidence and scope
The constructive source analysis and routing details are in CONSTRUCTION_CANDIDATES.md, SHA256 dd7401ab7c189d7ce435047f99048ef5cc68b1db6f589a25d3ad255bc1603a9b. R3 fixes the stored-cell convention; no candidate formula changes are introduced here. The independent R6 derivation checks these same identities and the exact 313 metadata bindings. Numerical enclosures are a separate C-loop obligation.

These theorems establish the reference/representation producer under the frozen source model. Full physical epsilon and outgoing bound remain null, coverage0/313, H6/H7 OPEN and L4/REI activation false. No no-go or broad novelty claim is made.
