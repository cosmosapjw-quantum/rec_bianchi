# REC-H5 defect-to-tube independent bridge (conditional)

2026-10-28. Source anchor 27d20e3d4ef908d4ac5e9b6d8e1d98045a7294d6, packet b093331bba137ec5949514fb24fb2b4927083fe9ffe58c17f7d61e9746aae9eb. This is a noncanonical independent supporting construction, NOT a physical H5 certificate. Existing native-path owner branch research/rec-h5-native-path-20261028 already has R1-R10 completed, C1-C4 recorded; do not duplicate its native acquisition.

Given actual continuous f'=F(t,f), reconstructed piecewise-C1 z(t), residual d=z'-F(t,z), and initial error e0, choose a declared norm and verify a logarithmic-norm bound mu(DF)<=lambda(t) over an enclosing tube. Then, conditional on existence/continuation in this tube:
||f(t)-z(t)|| <= e0 exp(int_a^t lambda) + int_a^t exp(int_s^t lambda) ||d(s)||ds.
For constants lambda,D, h=t-a, radius r=e0 exp(lambda h)+D expm1(lambda h)/lambda (limit lambda=0: e0+D*h).
For weighted infinity norm with w_i>0, mu(A)=max_i(A_ii+sum_{j!=i}|A_ij|w_j/w_i); apply bound over whole state and tube, not at one face. A sufficient componentwise positivity check, provided every component should be positive, is min_i,t z_i(t)>sup_t r(t). Upper physical constraints require upper margins as well. Prove tube self-consistency and actual continuous model existence; a discrete native recurrence residual is NOT physical ODE defect.

Under exact translation y=f-w and F_y(t,y)=F_f(t,y+w)-w', residual, state norm error, D_yF_y and its logarithmic norm are unchanged. Positivity applies to f, not y. Curvature on smooth segments: y_j''=partial_t F_j+(D_fF_j)F-w_j''. For invertible smooth closure Mv=s: v'=M^-1(s'-M'v); v''=M^-1(s''-M''v-2M'v'). Do not cross unqualified phase switches with a C2 formula.

CAS scalar quotient identities first and second derivative returned {0,0}; initial unspecialized symbolic matrix Inverse derivative was unevaluated, not a proof. Local Python 7 synthetic controls PASS. Actual native F, full-state physical defect, tube, stability, e0, physical M2/epsilon/outgoing bound remain NOT_RUN/null. Reference 313/313 stays prior PASS_SCOPED; physical 0/313. H6/H7 OPEN; L4_ready=false; REI_activation=false. Repository-wide CI prior FAIL is not changed.

Shared canonical DAG remains 28/88 at inherited verified anchor, this independent unit +0. Separate PR240 working 33/88 is not added. Prior unit 20/20 remains closed. Owner existing 600CPU allocation is not reset or spent by this support note. New independent synthetic execution is not charged as owner's native experiment. No production admission, merge or new research node automatically follows.

Review required before applying: actual source-indexed continuous F; piecewise smoothness/QSS invertibility; whole-tube derivative bounds; trajectory source parity; strict physical positivity; 313 geometric cells and rational alpha; model discrepancy and initial error. No native acquisition replay.
