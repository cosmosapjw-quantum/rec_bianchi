# REC-HISTORY-02R — frozen continuation contract

Date: 2026-10-24 Asia/Seoul. User explicitly requested the next theory and coding
research loop after a latest-branch/conversation/repository/backup survey.
Protocol: user-supplied physmath-research-loop built-in 1.0.0 / design v0.2.
This is an additive implementation and finite validation of the recovered
REC-HISTORY-02 Stage A construction. It does not alter another owner's reservation.

## 1. Identity, reuse and current scope

REC publication parent: c7cdabd871ab2ef6f722594ff063b8ce8550e6b4
on research/rec-history-input-admission-20261024, draft PR131.
New branch: research/rec-history-characteristic-resume-20261024.
Allowed repository writes: research/rec_history_characteristic_resume_20261024/.
Central fixed authority: rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17.
Current orchestration base observed: 8b6e741ceb305cb0a6fde244ee002eb5926559fe.
The separate REC observations branch at44d0a6d8703f50bf3d7548812a1ab13d9b2c3877
contains current ADM01 observations. A later central additive update must preserve
current owners, all40 original node contracts,17edges, authority, HE-X1,
HE-ANG/CR-N4 and all unrelated changes. No assembler/renderer replay or merge.

Recovered HISTORY02 Stage A ZIP SHA256:
ca748e1e9e3ee1c9fe2c82418221f0230998b97223b38d91c558ae3924a077da.
Its14 payloads and CRC15 were verified after one GET. Preserve its original
FROZEN_CONTRACT, STAGE_PROGRESS, BUDGET and WOLFRAM_SYMBOLIC without edits.
R1-R5/C1-C4 were recorded prepared/derived at2026-10-23T21:39:14.733816Z.
Its local spent0 and60CPU/180wall allocation are a historical snapshot.
Later original-owner activity/spend is unobserved. No historical budget reset
or claim of60seconds currently remaining is made. REI-L0 remains reserved.

Reuse HISTORY01 boundary/JVP/interpolation and ledger source exactly:
rec@93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa
research/rec_history_boundary_20261023/code/history_boundary.py
Git blob1aa7f134c332bc4596372df18c7c47306260ecfc.
Reuse608+14 HISTORY01,194 LINE02 and historical6probes; replay0.
ADM01's386primary/3probe observations and its partial evidence preservation
remain unchanged. The h4 smoke data have0/313 coverage at the ADM01 fixed face.

The new leaf implements the previously unimplemented positive-rate,
constant-shear Bianchi I retarded crossing, source direction, native-Wien
reference conversion, fixed-cell tangent, and conditional finite error map.
It supplies a concrete characteristic owner for this subclass. It does not
supply a general-Bianchi characteristic or a new recombination trajectory.

## 2. Mathematical contract

The attached original Stage A equations and conventions are reused.
Metric(-,+,+,+); normal-frame propagation direction n=p/|p|;
eta=ln(a), not conformal time; p_i=a exp(beta_i)(E/c)n_i.
E=hbar omega and x=E/(k_B T); code energy ratios are dimensionless.
beta_i=b_i eta+constant, sum b_i=0, a_i=1+b_i>0, H>0.

For Lambda=ln(E_s/E_t)>=0, Delta=eta_t-eta_s:
g_i=n_ti exp(a_i Delta), D=||g||,
F(Delta)=ln D-Lambda=0, n_s=g/D.
F'=q_s=sum a_i n_si^2 in[a_min,a_max],
Lambda/a_max<=Delta<=Lambda/a_min.
Lambda0 and exact axes/FLRW have their exact closed forms.
The evaluated q at the local boundary is q_t=sum a_i n_ti^2.
This distinguishes source q_s in the root Jacobian from target q_t.

For tangent n_t dot dn_t=0, sum db=0:
dDelta=[dLambda-sum n_si exp(a_i Delta-lnD)dn_ti
        -Delta sum n_si^2 db_i]/q_s.
deta_s=deta_t-dDelta.
v_i=exp(a_i Delta-lnD)dn_ti+n_si(Delta db_i+a_i dDelta);
dn_s=v-n_s(n_s dot v).

Native stored departure is d=f-W with W(x)=exp(-x).
For the declared reference T_s=T_t exp(Delta):
x_s=x_t exp(Lambda-Delta),
d_in=H(eta_s,n_s)+W(x_s)-W(x_t).
This reference temperature is prescribed, with no gas thermal evolution.
dx_s=x_s(dlnx_t+dLambda-dDelta);
doffset=x_t W_t dlnx_t-x_s W_s(dlnx_t+dLambda-dDelta).
The absolute occupation is f_in=H+W_s; preserve signed departures.

Use the original degree<=2 angular field
H=c0+v dot n+n^T Q n with10time-linear coefficient histories.
dH=dH_data+H_eta deta_s+(v+2Qn) dot dn_s.
This is a specified finite represented field; actual angular spectra are not
inferred from scalar stored arrays.

Compose with unchanged HISTORY01 boundary/boundary_jvp/line_ledger:
A=-expm1(-tau/q_t), T=exp(-tau/q_t), s=xr_p/(3x1s);
d_out=T d_in+A s, dq_t=sum n_ti^2 db_i+2sum a_i n_ti dn_ti.
The existing local same-event ledger is the sole atomic/radiation event owner.
Propagation redshift work is distinct and no second source is introduced.

## 3. Guards and finite conditional error

Directions must be finite unit3-vectors within64eps; a tiny normalization within
that roundoff is allowed. Shear trace tolerance64eps*max(1,L1norm(b)).
Reject nonpositive a_min, Lambda<0, nonfinite transforms/tangents, negative
absolute occupations and malformed arrays. Zero direction components are valid.
Use shifted log-sums for lnD/n_s; do not divide by n_ti.
Use log-domain x_s and stable signed Wien differences with expm1.
For x exp(-x), the x->infinity limit is0, without inf*0.

The new history wrapper MUST reject eta_s<eta0, iz<2 and eta_s>=eta0+h(iz-1)
BEFORE invoking the preserved HISTORY01 interpolation, whose legacy thermal
fallback is not this new leaf's admission policy. No clipping/clamping/gap fill.
A time knot with nonzero source-time tangent is NONSMOOTH_QUERY.
Zero query-time tangent may reuse its recorded fixed cell.

Given supplied valid e_H,K_eta,K_n,eps_F and arithmetic allowance:
eps_Delta<=eps_F/a_min,
||dn_s/dDelta||=sqrt(Var_n(a))<=(a_max-a_min)/2,
|dW_s/dDelta|=x_s exp(-x_s)<=1/e,
e_in<=e_H+[K_eta+K_n(a_max-a_min)/2+1/e]eps_Delta+e_arithmetic.
At fixed target coefficients e_out<=T e_in,
e_number<=G_native H_t q_t A e_in and e_energy=E21_J e_number.
All bounds apply over the actual query uncertainty tube; missing inputs stay
unadmitted. A sampled residual plus a chosen floating allowance is not a
rigorous library-wide roundoff certificate. Tests use independent high-precision
references and declared finite allowances. No actual history M2 is inferred.

## 4. Actual input and new finite cases

Copy actual h4 smoke NPZ exactly from Stage A:
SHA256 b2489168155ad1a18a887a880eb0ca90376be5506c3c61d6bf06e9e70007c54c.
Source photon clock g0=72892,h=2.1225e-5,eta0=-ln8001+g0*h.
Outgoing shape314x24 is virtual311 + Lyman3; photon column belongs to input
state g, accepted state is g+1. It remains a scalar FLRW history at its own
early retained domain, with no admitted independent uncertainty.
Use8 declared interior channel/cell interpolation queries. This is new adapter
use of actual bytes, not repetition of the old313-query admission.
Retain the target snapshot identity from ADM01 for source/domain comparison.

Predeclare and save the actual case list before primary:
-48retarded cases: FLRW, axes and zero components, LRS/triaxial shear,
 Lambda0/small/native ratios/large logratio, a_min near the positive boundary.
-12tangent directions: angular, shear, ratio and mixed, independent70+digit
 central differences with an a priori small step and converged root precision.
-16Wien controls: both signs, equality/near equality, x0, underflow and
 transformed x beyond finite direct exp representation.
-12fixed-cell history+boundary composites, including source/time/direction/data
 tangents and the existing single local energy ledger.
-8actual stored h4 interior queries with independent scalar interpolation.
-16invalid domain/shape/nonfinite/negative-absolute/knot/missing-bound cases.
-12analytic finite envelopes, including parameterized root perturbations.
-3deliberate defects: FLRW delay in shear; omit Wien offset; photon clock+1.
Cases may overlap controls but unique rows/conditions and invocation counts
must be reported honestly. No unplanned broad suite or old campaign replay.

Acceptance inherited: root/direction/Killing/norm/value <=5e-12 scaled,
JVP<=5e-9 scaled, scale=max(1,abs(expected),abs(actual)) plus saved absoluteerrors.
Wien extreme controls use max(abs(reference),1e-300) and declared8e-12 relative
gate or underflow-quantum absolute floor; save which regime applies.
Actual linear interpolation<=64eps scaled. Finite analytic envelopes must
contain the independent reference with stated arithmetic terms.
No acceptance threshold changes after execution to create PASS.

## 5. New invocation resource contract

This implementation has its own new source identity and explicit current
allocation. Historical HISTORY01, ADM01 and original HISTORY02 ledgers remain
separate and unchanged. Later spending on the original owner is unobserved.
Local allocation:30CPU seconds /90execution-wall seconds /1thread /1GiB AS.
Primary:16CPU/45wall. One independent changed-source review:at most6small
probes,6CPU/15wall. Figure rendering and diagnosed repair:8CPU/30wall.
Preserve all failed attempts in these cumulative figures.
No IVP, native recombination runtime, old science replay, new coupled history,
production mutation, merge or activation.
One new Wolfram symbolic call with requested5-second kernel limit may check
the composite derivative and variance identity; record external actual tool
result/time availability separately. Do not infer CPU/RSS from the tool limit.

Numerical commands must set threadenv before importing arrays, enforce
RLIMIT_CPU and RLIMIT_AS and a single-child wall timeout. Save source snapshot,
command/cwd/environment, stdout/stderr, raw rows, summary, exitcode and
postexit inclusive getrusage. Do not claim a live aggregate monitor.

## 6. Review, publication, checkpoints and next action

Astra owns framing/admission; lower-tier executor implements/runs under this
contract. One fresh independent Astra review pass covers theory, actual code,
raw outputs and actual2PNG figures, with at most one diagnosed bounded repair.
The reviewer may check pre-code contract then return to the actual diff/results
in the same pass; no recursive independent-review chain.

Each of20R/C stages has science/execution/publication/backup/global-DAG fields.
Completed/reused stages refer to the cumulative checkpoint that contains their
actual evidence. Checkpoints: S0 restored theory+current intake; S1 frozen code
and case plan before primary; S2 original raw primary immediately after exit;
S3 independent review+two saved-row figures+formal report; final provider/Git
companion receipt. Complete stages that share one execution cite that same
actual output and checkpoint, without artificial duplicate runs.

For each checkpoint publish only this additive research unit with expected-SHA,
force=false and a draft PR, and upload its immutable cumulative archive to
Dropbox and Drive. Record ACK/ID/size separately for each provider. Bounded
waits; unknown/noACK remains unknown, not success. A provider interruption
does not invalidate completed math or justify a science replay.
Preserve first raw arrays/rows and first figures; all later corrections additive.

Parent REC-HISTORY remainsPARTIAL; H5 INPUT_DEPENDENT_UNCALIBRATED;
actual matched-parameter history/reference uncertainty, qualified angular
supplier, variable/general Bianchi geometry, and full thermodynamic Jacobian
remain explicit downstream obligations. Full physical completion fraction=null.
Physical HOLD;U5 HOLD_9_FAIL/HOLD_8_FAIL;CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN;production NOT_APPROVED;REI_activation=false;
first_failed_REI_raw HISTORICAL_LOCAL_ONLY.


