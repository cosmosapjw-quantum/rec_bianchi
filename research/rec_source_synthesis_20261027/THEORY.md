# R5 — joint thermal compatibility and broken-smooth history

## 1. Fixed-column thermal identity

Under `CLAIMS_AND_ASSUMPTIONS.md`, write x_E=DeltaE/(k_B T), x_nu=h nu/(k_B T), delta=x_E-x_nu and n_gamma=(exp(x_nu)-1)^(-1). The mean-intensity Einstein relations give

    B_ul=A_ul c^2/(2 h nu^3),  B_lu=(g_u/g_l) B_ul.
    R_up=n_l(g_u/g_l) A_ul n_gamma,
    R_down=n_u A_ul(1+n_gamma).

Substitute n_u/n_l=(g_u/g_l)exp(-x_E) and 1+n_gamma=exp(x_nu)n_gamma. All positive common factors cancel, giving

    R_down/R_up=exp(-delta),
    I=(R_up-R_down)/(R_up+R_down)=tanh(delta/2).                 (1)

Thus I has the sign of DeltaE-h nu, tends to zero continuously when the two energies agree, and satisfies |I|<=|delta|/2. This is a normalized paired flux diagnostic at the specified common temperature. Its scale is not an experimental uncertainty estimate.

For j_nu=(h nu/4pi)n_u A_ul phi_nu and alpha_nu=(h nu/4pi)(n_l B_lu-n_u B_ul)phi_nu, DeltaE>0 implies positive absorption. Cancellation yields

    S_nu=j_nu/alpha_nu=(2 h nu^3/c^2)/(exp(x_E)-1),
    S_nu/B_nu(T)=expm1(x_nu)/expm1(x_E),
    D=S_nu/B_nu(T)-1=expm1(-delta)/[-expm1(-x_E)].              (2)

The last equality follows by factoring exp(x_E) out of the numerator and denominator of [exp(x_nu)-exp(x_E)]/[exp(x_E)-1]. It avoids subtraction of nearby large exponentials. I and D have opposite signs for nonzero delta. For small delta, I=delta/2+O(delta^3), and D=-delta/[1-exp(-x_E)]+O(delta^2). No collision-rate averaging is involved: collider identity cancels only after a common Boltzmann ratio is specified.

Implementation forms delta from exact source decimal energies/frequencies and exact SI constants before binary64 conversion. It must not subtract separately rounded x_E and x_nu. The independent reference computes the positive fluxes and the original exponential ratio with 80-digit Decimal arithmetic. Existing 128*epsilon64 residual tolerance is retained for nonzero relative diagnostic error; analytic zero is handled explicitly. The old source-frequency gate is read from existing evidence and remains unchanged.

## 2. Distributional curvature and chord remainder

Let f be continuous on [a,b], C2 on each open piece of a finite partition, with first derivative of bounded variation and finite one-sided limits. Write its signed derivative measure as

    d f'=f''_ac(t)dt+sum_(a<t_k<b) J_k delta_(t_k),
    J_k=f'(t_k+)-f'(t_k-).

The linear chord at x in[a,b] is Lf(x)=[(b-x)f(a)+(x-a)f(b)]/(b-a). Define the nonnegative kernel

    G_x(t)=(t-a)(b-x)/(b-a), a<=t<=x;
           (x-a)(b-t)/(b-a), x<=t<=b.

On each smooth interval, integrate G_x f'' twice by parts. The first integration produces internal boundary contributions G_x(t_k)[f'(t_k-)-f'(t_k+)]=-G_x(t_k)J_k. The jump of G'_x at x is -1 and the endpoint contributions give the chord. Consequently

    f(x)-Lf(x)=-integral_a^b G_x(t) f''_ac(t)dt
                -sum_k G_x(t_k)J_k.                           (3)

Taking absolute values and using G_x>=0 gives

    |f(x)-Lf(x)|<=integral G_x |f''_ac|dt+sum_k G_x(t_k)|J_k|.  (4)

For an actual C2 cell with |f''|<=M2, integral G_x dt=(x-a)(b-x)/2, recovering the existing H5 curvature coefficient. If f is piecewise linear, f''_ac=0, so (3) is an exact finite sum and (4) is an exact-arithmetic upper bound. Endpoints have kernel zero. The identity also holds at x equal to a knot by continuity.

An independent finite construction proves the piecewise-linear specialization directly: P(t)=A+Bt+sum_k J_k(t-t_k)_+. Affine terms have zero chord remainder, and the chord remainder of each hinge is exactly -G_x(t_k). This proof does not depend on distribution notation or floating point sampling.

## 3. Finite retiming and one-sided derivatives

Let q and q+d lie in the represented domain. For d>0 use the right derivative m_+(q); for d<0 use the left derivative m_-(q). Integrate the derivative measure between the two endpoints to obtain

    P(q+d)-P(q)-d m_+(q)
      =sum_(q<t_k<q+d)(q+d-t_k)J_k,                 d>0,      (5)
    P(q+d)-P(q)-d m_-(q)
      =sum_(q+d<t_k<q)(t_k-q-d)J_k,                 d<0.      (6)

The starting knot is excluded because its directional slope has already been chosen. A target-knot atom has weight zero and may be omitted. Replacing every J_k by |J_k| yields nonnegative bounds B_+ and B_-. For d=0 the value difference and remainder are zero. Within a single cell, the sum is empty and the first-order response is exact.

The signs in both formulas can be checked on a single hinge. For P(t)=|t|, q=-1/4,d=1/2, the direct remainder is1/2, J=2 and positive-path weight1/4. For q=1/4,d=-1/2, the direct remainder is again1/2 with the negative-path weight1/4. From the knot q=0 toward either side the directional derivative already equals that side's slope, so the remainder is zero.

## 4. Actual native representation and its boundary

Native `hydrogen.c` lines633–652 selects floor((eta-eta0)/h) and performs a two-point linear interpolation; lines641–645 exclude eta>=eta0+h*(iz-1). Define its real-arithmetic counterpart on the exact binary64 source eta0 and h as t_k=eta0+k h. Values are the exact binary64 stored samples. The new code checks the fixed313 source-index/cell witnesses against this exact grid and halts on a mismatch. It records the difference between stored eta-array knots and t_k, and between the saved nominal incoming value and P(q).

The prior H5 consumer instead names a geometric interpolant through stored eta-array coordinates. Its existing anchor radius is preserved. The two reconstructions have explicitly different coordinate identities; the new result is not silently substituted into that consumer. Both use the same original sample bytes and native source ordering.

For every original query, construct two within-cell target midpoints and, where causally available, the midpoints of adjacent cells on either side. Evaluate (5)/(6) by direct piecewise interpolation and by the finite jump sum. Construct a chord through the two adjacent-cell midpoints and check(3)/(4) at the original query. If an adjacent cell is unavailable, use the midpoint between the original query and that side's current-cell endpoint for the chord on that side; mark the unavailable cross-cell retiming case explicitly skipped. In particular incoming_index311/cell5125 is the final legal cell of prefix5127 and has no right-adjacent cell. The fallback remains strictly inside the causal domain. All data arithmetic is rational. No native source, RHS, IVP, old Ks construction or GEO01 root/matvec is rerun.

## 5. Physical error composition and next producer obligation

If independent physical source evidence establishes |y(t)-P(t)|<=epsilon(t), then

    |[y(q+d)-y(q)]-[P(q+d)-P(q)]|
       <=epsilon(q+d)+epsilon(q).                            (7)

Combining (5)/(6) with(7) bounds the physical finite difference relative to the represented directional slope by B_±+epsilon(q+d)+epsilon(q). This uses a value enclosure; a claim about the physical derivative additionally requires derivative control. No such epsilon input was found, so(7) remains a conditional composition rule and the physical outputs stay null.

The new reconstruction formulas make the stored-history part explicit. They do not supply e0, the source-matched continuous F/G closure, whole-tube defect/stability, certified positive tube-radius lower bound or physical curvature. The prior strict E_upper<rho_lower rule remains in force. A proof of an exact represented remainder and a physical history admission have distinct premises.

## Scope and novelty

Equations(1)–(7) are constructive derivations for this adapter/history task. The Peano/BV identity and residual-bound methodology are standard mathematical tools; no novelty or strong no-go theorem is claimed. The new contribution is their explicit source-preserving computational binding and the previously missing joint thermal and knot-crossing diagnostics. NG1–NG7 are not invoked to label an unresolved input as impossibility.
