# REC-H5-DEFECT-BOUND01 — conditional analytic research unit

Date:2026-10-25. Status: DERIVED_CONDITIONAL_AUTHOR_ANALYSIS; independent admission PENDING; implementation/execution NOT_RUN; actual H5 physical bound remains null. This unit supplies a constructive route from source-matched differential-equation evidence to existing history error propagation. It does not claim a new general theorem or strong no-go. Candidate application is distinct from completed PB01 coordinate pullback, KS01 represented-matrix certificate and REFINE01 stored-history differences. Active-owner duplication must be checked before implementation.

## R1 scope and completion criterion
Given the identical original REC cosmology, clock eta, native departure reference, source model, causal prefix and query cells, derive sufficient input bounds that convert an approximate history into a physical H5 uncertainty vector. Complete this analytic unit by exhibiting the exact inequality, its assumptions, source/domain obligations, unit convention and executable finite next gate. Do not generate a new trajectory or choose a physical tolerance.

## R2–R3 evidence and assumptions
Actual source is REC137 ea89c97abeb7a663a813f00e9aadddaf0b32a6a9, history SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1, z1099.9986525171403,T0=2.728K,nH0=.18745798773143102m^-3,prefix5127,313queries.
NEXT_INPUT_CONTRACT explicitly requires an independent reference plus uncertainty, endpoint uncertainty, or justified whole-cell curvature/defect bound.
NIST DLMF3.3(i), https://dlmf.nist.gov/3.3#i, gives the polynomial interpolation remainder used below. This is a standard reused result. Official dolfin-adjoint verification documentation https://dolfin-adjoint.github.io/dolfin-adjoint/documentation/verification.html distinguishes a discrete Taylor consistency test from a source-model uncertainty certificate.
Assume exact target x(eta) solves x'=F(eta,x) on a declared tube. Fix positive, dimensionally declared state scales S=diag(s_i), independent of eta and the state, and use the dimensionless norm ||v||_S=||S^-1 v||. The continuous approximate reconstruction xh is absolutely continuous on each interval of a finite partition. Require ||F(eta,u)-F(eta,v)||_S<=L(eta)||u-v||_S in the tube, with L>=0 locally integrable, initial scaled error<=e0, and actual defect r=xh'-F(eta,xh) bounded almost everywhere by an integrable d(eta)>=0 in the same scaled norm. If the target includes unresolved model/source error b, its bound must be added to d; omitting b certifies only the chosen equations.
History channel y_j=G_j(eta,x(eta)) must be twice continuously differentiable on the query cell or have an appropriate weak-derivative remainder bound. At source discontinuities, partition the cell or use a separately proved jump-aware bound.

## R4–R5 construction and derivation
For forward eta>=eta0, let e=xh-x. Absolute continuity and the stated bounds give
d||e||_S/deta <= L(eta)||e||_S+d(eta) almost everywhere.
This almost-everywhere inequality, or its integral form, is sufficient; no pointwise upper-right Dini derivative assertion is needed with merely integrable bounds.
Multiply by exp(-integral L). Integration gives
E(eta)=exp(integral_eta0^eta L)e0
 + integral_eta0^eta exp(integral_s^eta L)d(s) ds,
and ||e(eta)||_S<=E(eta), provided the enclosure remains inside the tube. Tube membership is a bootstrap obligation, not an assumed numerical observation.

For a backward history interval, choose orientation sigma=-1 (forward: sigma=+1) and parameterize s=sigma*(eta-eta0)>=0, eta(s)=eta0+sigma*s. The transformed equation is dx/ds=sigma*F(eta(s),x). Apply the same forward bound in s with L_s(s)=L(eta(s)) and d_s(s)=||sigma*r(eta(s))||_S bounded by d(eta(s)). All integration limits run from0 to s>=0. Inserting a negative eta interval into the forward formula without this orientation change is not justified.

If G_j is state-Lipschitz in the declared scaled norm with constant K_j and has source/reference mismatch bounded by b_Gj, endpoint error is <=K_j E+b_Gj plus explicit representation error. This transfers a state defect to the actual native departure variable; merely bounding an unrelated temperature trajectory does not suffice.

For a fixed query q in [eta_L,eta_R], h=eta_R-eta_L>0 and a=(q-eta_L)/h, let eL,eR be nonnegative absolute endpoint radii, |yh_L-y_L|<=eL and |yh_R-y_R|<=eR, in the native history-channel units. They are not signed errors or relative error fractions. The linear interpolation operator I is a positive partition:
I(yh)-I(y)=(1-a)(yh_L-y_L)+a(yh_R-y_R).
The scalar linear remainder is
y(q)-I(y)(q)=y''(xi)(q-eta_L)(q-eta_R)/2.
Thus with a nonnegative absolute curvature bound M2>=sup_cell|y''|, choose
epsilon_j(q)=(1-a)eL+a eR + M2 h^2 a(1-a)/2.
Then |I(yh)(q)-y(q)|<=epsilon_j(q)
 <= (1-a)eL+a eR + M2 h^2/8.
The pointwise coefficient is preferable to the coarser1/8 bound when actual query positions are known.
When the actual native departure map G_j and F are sufficiently smooth, its curvature follows from
y_j''=G_etaeta+2 G_etax F+G_xx[F,F]+G_x(F_eta+F_x F),
with all derivatives evaluated on the same exact source trajectory. Any temperature-dependent reference in G_j is included in these derivatives. This formula identifies a required bound; it does not supply M2 from sampled data alone.

For vector/componentwise histories, use a separate bound per channel. With same-source stable K_s and interval enclosure W_ij=max(|Klo_ij|,|Khi_ij|), the already admitted frozen response satisfies
|delta o_i| <= sum_j W_ij epsilon_j.
This deterministic box enclosure does not require statistical independence of endpoint or channel errors. Correlations can make it conservative; a narrower correlated enclosure needs separate justified information.
For physical nonlinear outgoing dynamics, this frozen-linear bound needs its own nonlinear remainder allocation; it is not silently promoted to a full evolving-system enclosure.

Eta is dimensionless ln(a). The vector e has componentwise state units, while ||e||_S,E,e0 are dimensionless under the declared scales; d has scaled-error units per eta and L has inverse-eta dimension. K_j converts the dimensionless state-error norm to native history-channel units. Endpoint radii, b_Gj and epsilon are absolute native-history errors, and M2 has native-history units per eta^2. W converts each channel error to the corresponding outgoing-output units. Converting from proper t requires F_eta=F_t/H and the actual H/source dependence. It is not valid to insert proper-time derivatives into the eta formula unchanged.

## R6 adversarial checks and limits
The argument fails as a physical certificate if any of: different cosmology/reference; unbounded actual source-model discrepancy; residual sampled only at nodes with no between-node bound; tube escape; discontinuous history hidden inside one cell; extrapolated provider support; unverified absolute endpoint radii.
Each identifies a specific missing input or scope correction. None proves the physical goal impossible.
A same-h equality or h/2–h/4 stored-history difference supplies neither d nor M2 without a further justified relation. Existing REFINE01 observations therefore remain valid in their stored-history scope.
Fixed-query H5 epsilon is distinct from PB01 query-coordinate uncertainty tau and exact mixed endpoint/query remainder. If query/geometry vary, declare their joint domain and use PB01 once; do not add a second copy of the same endpoint error.
The new statement is a conditional bound, not a probabilistic confidence interval.

## R7 validation design (not executed)
The exact equality cases y(eta)=constant or linear give zero curvature remainder. Quadratic y=M2 eta^2/2 at the midpoint reaches M2 h^2/8. For a scalar scaled state in forward path-length parameter s>=0, x'=Lx with constant defect has exact bound E=exp(Ls)e0+d*expm1(Ls)/L, with L=0 limit e0+ds. These are independent analytic controls for a future implementation.
Actual acceptance additionally requires interval/enclosure input files for all313queries with the exact source identity, verified tube/support, and a predeclared observable tolerance. No numerical cap or physical tolerance is invented here. A source bound may be large yet valid; acceptance against an observable tolerance is a second decision.

## R8 decision
Adopt the conditional analytic construction as the next source-input contract. H5 remains INPUT_DEPENDENT_UNCALIBRATED and epsilon=null until actual d/L/K/M2/endpoint/reference bounds are supplied and assessed. No new RHS/native/IVP/operator/certificate evaluation was performed.

## R9 implementation contract
Inputs: source identity, eta cells/query positions and forward/backward orientation, fixed dimensionally declared state scales/norm, native-reference map G, defect bound and tube certificate or externally justified endpoint bounds, per-cell curvature, Ks interval identity, observational tolerance supplied by owner.
Outputs: componentwise epsilon, frozen outgoing enclosure, provenance of each bound, and separate nonlinear/model residual obligations.
Reject unsupported domain, negative/nonfinite bounds, mismatched source/reference/clock, absent between-node bound, or tube violation. Keep mathematical bound validity separate from whether it meets the science tolerance.
PASS actual bounds→feed existing KS01/PB01 uncertainty propagation only. FAIL source identity→repair matching metadata only if same physical source; otherwise obtain correct source. No replay of completed matrices/trajectories.

## R10 resume
The author derivation is complete within the stated conditional scope; independent scientific admission has not been performed for this new note. The implementation and physical-input admission are pending. No claim of all20research/coding stages is made. Root may choose a different ready research unit with actual inputs rather than allocating a numerical run to absent H5 data.
Requested authority:Astra-tier. Observed runtime identity:NOT_OBSERVABLE. Scientific computation count0; external retrieval costs not measured and not zero. No cumulative budget reset.


## Targeted independent-review correction

The independent theoretical reviewer requested explicit forward/backward orientation, almost-everywhere Gronwall assumptions for integrable L/d, and nonnegative absolute endpoint radii with a fixed dimensional norm. These analytic precisions were added without changing frozen inputs, scientific code, numerical outputs, tolerances or budgets. The actual-source curvature chain rule and the absence of any statistical-independence requirement are now explicit. Independent final readback is pending; no numerical or plotting run was made.
