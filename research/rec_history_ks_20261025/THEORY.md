# Stable source incoming operator and certified local coupling

## R1-R4: question, source and choice
THERMO01 established a numerically checked six-primitive derivative J_s for a
stable evaluation of the native piecewise equations. RESP01 certified a
different represented native matrix K_0. No equality or transfer certificate
between those representations was established. This unit constructs K_s
directly on the stored stable matrices, making the local incoming/primitive
pair usable without importing K_0's norm. The same physical source and
arithmetic representation are thus bound by actual inputs, not a naming claim.
The incoming field remains an independent local variable. H5/H6 supply its
history, frame and physical uncertainty in later work.

## R5: constructive derivation
At a fixed permitted primitive point theta and fixed source table/branch,
write M X=c+B u and o=T X+P u. The source is affine in u. The only nonzero
entries of B are precisely the three families in FROZEN_CONTRACT.md, obtained
by differentiating sr and sv with respect to their owned incoming component.
Since M,T,P do not depend on u, differentiation gives M V=B and
K = T M^{-1} B+P, dimensions V313x313 and K314x313.
For a simultaneous variation, delta o=J_s delta theta+K_s delta u to first
order. J_s already includes derivatives of M,T,P,c,Bu at fixed u; therefore
adding K_s delta u neither omits nor double-counts the local chain rule.
The derivative of u with respect to trajectory/geometry is still an external
pullback. No bound on that pullback is supplied by this formula.

Let Z and Vhat be floating candidates, regarded as exact binary64 numbers.
Outward arithmetic encloses Q=I-ZM and R=B-M Vhat. Let rho bound ||Q||inf
strictly below1. ZM=I-Q is invertible by its Neumann series, hence square M
and Z are invertible. The exact response error satisfies
V-Vhat=(I-Q)^{-1} Z R.
For every column j, define sigma_j >= max_i (|Z| |R|)ij and
e_j=up(sigma_j/down(1-rho)). Then |Vij-Vhatij|<=e_j.
Let t_i bound sum_k|Tik| and enclose C=T Vhat+P by elementary outward dots.
Then Kij lies in [down(Clo_ij-t_i e_j),up(Chi_ij+t_i e_j)].
Take exact interval absolute-value minima/maxima and outward row sums.
max_i sum_j min|Kij| <= ||K||inf <= max_i sum_j max|Kij|.
The lower bound remains valid although different entries may attain their
minima at different underlying solutions, since it is only a lower bound.
All floating products used to construct rho,sigma,t and widening must be
widened; a BLAS residual is diagnostic and is not used as an enclosure.

If componentwise |delta u_j|<=epsilon_j, epsilon_j>=0, then
|delta o_i|<=sum_j max|Kij| epsilon_j for the fixed-theta affine map.
The map is exactly affine in real arithmetic for the represented coefficients,
so there is no local-incoming Taylor remainder. A physical prediction still
needs a justified physical epsilon and coefficient/model/trajectory error.
The bound API returns null rather than manufacturing physical epsilon.
The six-column Js is numerically checked, not a certified interval; the
combined matrix must retain that distinct evidence type.

For the same Ly-alpha event, N=C_N(o311-u311), C_N=3e6 LYA H.
dN/du_j=C_N(K311j-delta311j), and dE_rad=E21 eV_J dN,
dE_atom=-dE_rad. The Kronecker term is essential: response of incident photons
cannot be counted as emitted photons. The sign-paired energy channels are
one event represented twice; they do not prove total physical energy closure.
The ionization source has F=-(C-beta0 X0-beta1 X1)/H, hence
dF/du=beta^T V_first2/H, with proper-time derivative H*dF/du at fixed theta.

## Actual history admission
The original producer stores accepted outgoing histories at eta_j=eta0+jh.
At iz5127 the causal prefix has5127 knots indexed0..5126. For each owned
source/target energy link, eta_emit=-log((1+z_face)E_source/E_target).
For eta0<=eta_emit<eta5126, k=floor((eta_emit-eta0)/h) and
lambda=(eta_emit-eta_k)/h; incoming=(1-lambda)y_k+lambda y_{k+1}.
Use outgoing channel ownership from the immutable query map.
At exact upper endpoint the native contract refuses; earlier-than-start
queries use the explicit thermal boundary, not an extrapolated fitted tail.
Agreement with stored incoming binds the actual payload and query convention.
It does not determine deviation between this discrete curve and a physical
solution. If a validated whole-cell second derivative bound M_j existed,
linear interpolation would contribute at most M_j h^2/8 plus weighted
endpoint uncertainties. Those inputs are currently null, so this expression
remains a conditional future interface, not a computed physical error.

## Evidence and limitations
Direct proof above is the authority for this implementation. Rump,
Verification methods, Acta Numerica19(2010),287-449,
https://www.tuhh.de/ti3/paper/rump/Ru10.pdf, supplies broader interval-verification
context; no unexamined theorem is treated as an extra premise.
The underlying source is the retained HyRec implementation and its source
mapping; Ali-Haimoud and Hirata, Phys.Rev.D83,043513(2011),
https://arxiv.org/abs/1011.3758, provides model context. Literature searches
via Exa and SciSpace identify context, not physical uncertainty for this run.
Wolfram generic matrix identities and exact Fraction controls independently
check algebra; neither replaces source binding or interval implementation.

