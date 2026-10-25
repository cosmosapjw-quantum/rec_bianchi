# REC-HISTORY-KS01 frozen theory-to-code contract
Version 1. Root scientific owner: Astra; requested mechanical executor: gpt-6.1-sol.
Actual model identity is recorded only if execution metadata exposes it.
Workflow: physmath-research-loop built-in 1.0.0 / approved design v0.2.
This finite unit is authorized by the user's current full research-loop request.
Source base: cosmosapjw-quantum/rec_bianchi@52226bb8d3ac99e7de2bd7934ab30e6fb3f257fe.
Owned branch: research/rec-history-ks-20261025.
Owned repo path: research/rec_history_ks_20261025/.
No existing checkout is available; use a selective source projection and Git data API.
No clone or worktree is requested.

## Question and scope
Construct the 314x313 incoming-response operator K_s for exactly the stable
piecewise source representation used by THERMO01's stored 314x6 J_s. Certify
the induced infinity norm of the represented binary64 coefficient operator
by elementary outward residual arithmetic. Export conditional componentwise
box weights and same-event ionization / Lyman-alpha number / opposite energy
response. This is new stable-source work, not a rerun of RESP01's native K_0.
Admit the actual original 35 MB history payload, its prefix, source indices,
scalar FLRW frame, parameters and all 313 query cells. No temporal physical
uncertainty is inferred from same-h reconstruction agreement.
A parallel REC-HISTORY-02 C5 checkpoint owns H6 Bianchi-I retiming; do not
implement or count that checkpoint's work in KS01.

## Exact immutable inputs and reuse
THERMO01 final S3 above; science S2 95d0b62daef5bc0b522c5b5a579b33bef15fc6f2.
S2 restored archive SHA256 f17aa795966c9af1805b9194db42dae99f6daa266205b0293ead3bff4f2090d1.
Reuse source.py, scalar.py, inputs.py and source tables from that archive;
reuse results/primary001/BASE_COEFFICIENTS.npz and ANALYTIC_RESPONSE.npz.
Do not rerun its six-axis derivative, complex-step, native parity or old IVP.
Before execution write exact byte manifests for every source and data file used.
The prior canonical 23-input snapshot is
adddf7381edfb7d670025c651cf813594107a260acce308702f33b1d415fad54.
Original target: z=1099.9986525171403,T0=2.728 K,
nH0=.18745798773143102 m^-3; switches and fsR=meR=1 fixed.
theta=(xe,xHII,ln TR,ln TM,ln nH,ln H); source-unit values use eV,cm^-3,s^-1.
Incoming u has 311 signed Wien-departure virtual bins plus Ly-alpha,Ly-beta.
Outgoing o has the same 311 virtual bins plus Ly-alpha,Ly-beta,Ly-gamma.
Original payload data/pr05b2_source_history_v060.npz, blob
de43b1a2642fa0aa049abbfd1b0a7d775d684b1b,35239470 bytes,
SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1.
Original accepted_count=7489,h=8.49e-5,z_start=1700.4825068138662.
At target iz=5127 only prefix columns 0..5126 are available.
Use stored RESP QUERY_RESPONSE_COEFFICIENTS.csv for source/target mapping only;
do not reuse its numerical K0/event coefficients as Ks.
Original input.dat provenance, producer source and raw-member hashes are
retained in source_intake/SOURCE_HISTORY_PROVENANCE.json and
ORIGINAL_NATIVE_HISTORY_LEAD.json. Preserve the distinction between direct
payload checks and the retained provenance chain for cosmological parameters.

## Equations and representation
THEORY.md supplies the proof. At fixed theta, M_s X=s_const+B_s u and
o=T_s X+P_s u. M_s,T_s,P_s are the stored stable BASE_COEFFICIENTS arrays.
Let x=1-xHII, ly=LYA*H/nH/x. In the source's scalar multiplication order:
B[0,312]=3*ly*x*1.664786871919931; B[1,311]=3*ly*x;
B[b+2,b]=Tvv[0,b]*x*(1-p[b]), b=0..310; all other entries zero.
Use stable p exactly as represented, never substitute literal native p.
Compute Vhat=solve(M_s,B_s), Zhat=solve(M_s,I), Khat=T_s Vhat+P_s.
Reuse stored Js without recalculating its six columns.
The represented-operator certificate encloses exact real algebra on these
binary64 M,B,T,P, not rounding derivatives, libm uncertainty or physical history.
The approximate solves may use one-thread BLAS/LAPACK. Every certificate dot
uses elementary nextafter-widened multiply/add, never a BLAS dot as a proof.
Reuse RESP interval.py with source identity; adapt only its generic certify
method, omitting native-source imports. Return explicit rho>=1 failure.

## Frozen validation criteria
A. Verify source/input hashes and stored coefficient identity. A fresh stable
base build (no solve) must reproduce stored M,s,T,P exactly as binary64 arrays;
if deterministic representation differs, return to root before any scientific
claim. Missing inputs or changed source is not permission to choose replacements.
B. Certify rho=||I-ZM||_infinity upper <1 and finite K lower/upper matrices.
The norm interval must have (upper-lower)/max(upper,1e-280)<=1e-6.
This is certificate sharpness, not a physical error tolerance.
Approximate Khat and Vhat are reported separately; interval containment is
assessed against exact manufactured references, not assumed for rounded Khat.
Primal V backward residual <=2048 eps64 componentwise gross
|M||V|+|B|; zero gross requires exact zero residual.
C. Two fixed incoming directions d1_j=(-1)^j and d2_j=sin(j+1), multiplied
by max(max|u|,1e-30). Using stable source, solve at u+d1,u-d1,u+d2,u-d2.
Check affine outgoing/F/number response against Khat*d and derived coefficients:
normalized max error <=2e-9 using max(response,direct difference,1e-280).
If tiny event cancellation prevents a relative comparison, also report its
absolute error and gross roundoff; do not silently drop a failed criterion.
D. Joint local response with stored Js: theta directions
v1=(.1,-.2,.3,-.1,.2,-.3),v2=(.2,.2,-.1,.1,-.3,.2);
incoming directions above; h=1e-6,5e-7. Eight endpoint solves total.
Check central-difference outgoing,F,R_gamma against Js*v+Ks*d and stored
theta coefficients; at least one step per direction normalized residual<=2e-5.
Rebuild real endpoints and refuse any native branch, arithmetic branch or
source table stencil crossing. Do not infer asymptotic convergence from2steps.
E. Independent exact-Fraction manufactured systems (<=3x3,<=12small RHS):
include nonsymmetric/nontrivial T/P and cancellation. Verify exact K and norm
contained by the interval proof; reject rho>=1,nonfinite,negative epsilon.
One zero epsilon and one supplied manufactured epsilon exercise conditional
box API. A supplied manufactured epsilon is never the physical epsilon.
F. Same-event factors: N=3e6*LYA*H*(o_alpha-u_alpha), radiation=E21*EV_J*N,
atomic=-radiation, with outward factors for interval quantities.
Report ionization derivative beta^T V[:2]/H and proper rate H times this.
Opposite energy arrays sum exactly to zero by shared-event construction;
check stored Js energy rows too. No extra physical process or closure.
G. Actual history admission: validate payload byte identity, all raw-array
hashes where represented layout is specified,finite arrays,strict eta and
source-index ownership,energy identity,accepted_count/prefix/parameter chain.
Use outgoing_virtual and outgoing_lyman, never average_virtual, for queries.
For each stored source/target query, compute the original linear cell and
reconstruct u from only prefix0..5126. Native domain eta0<=q<eta[prefix-1];
earlier times require explicit thermal-prehistory zero; future/latest knot
refuses. Eta grid comparison absolute<=32eps*max(|eta|,1).
Reconstructed u must agree with stored u at normalized max<=5e-9; report
all errors and boundary margins. Strict endpoint tests must cover exact
upper endpoint refusal and valid last-cell interior. Parameter mismatch and
different cosmology finer-history substitution must refuse. This is a new
actual-payload admission, not an old campaign replay.
H. Figures use saved results only: row-gain/norm interval with transparent
certificate width, and joint-response/history-admission residuals. Root and
same independent reviewer inspect actual PNGs and labels; preserve first PNGs.

## Finite execution and stopping
One primary scientific process: cap45 inclusive CPU s/135 wall s,1thread,
RLIMIT_AS1GiB. Reserved one targeted repair:5CPU/15wall,not yet authorized.
Figures/targeted scalar tests:10CPU/30wall. Total local new cap60CPU/180wall.
Large RHS cap639: 313 for V +313 for Z +1 base +4 affine +8 joint =639.
Small RHS cap12 (dimension<=3). New IVP=0,native runtime=0,
old campaign replay=0. No automatic retry. Save raw inputs/code/stdout/stderr,
partial results and resource receipt on any failure, then return to root.
Root may authorize one targeted continuation within remaining budget,
preserving all earlier raw records. If rho fails, report failure rather than
changing norm, precision or tolerances without root decision.
One Wolfram symbolic evaluation <=10s remote timeConstraint is authorized
for generic algebra only. Remote CPU is unknown and tracked separately,
never added as measured zero. No numerical user arrays are sent to CAS.
Prior local known lineage24.120157CPU s (THERMO01+RESP01+REFINE01+H01);
prior THERMO01 execution8.362847CPU/8.336637456wall; older unknown remains
unknown. Parallel HISTORY02 upper-bound charges belong to its own ledger
and do not become KS01's remaining allowance.
Preparation, providerIO,publication and full-turn elapsed are separate.

## Deliverables and completion
One full theory loop R1-R10 and coding loop C1-C10.
S0 freezes R1-R5/C1-C4 (9/20): theory,intake,contract,input identity and scope.
S1 adds R6/C5 (11/20): independent preexec review,exact implementation.
S2 adds R7-R9/C6-C9 (18/20): actual run,results,figures,independent verdict.
S3 closes R10/C10 (20/20) after actual Git,draftPR,Dropbox,Drive and central
additive observation receipts. Each of20stage rows names evidence and actual
checkpoint delivery; shared checkpoints avoid empty duplicate archives.
Do not declare a backup until success; receipts outside the backed snapshot
need not be recursively included in another archive.
All full raw retained inputs/results are backed once; immutable originals are
not regenerated. Public Git projection omits unrelated private-repo metadata;
private backup keeps the source census. Preserve failures and reviewer findings.
Central update starts at latest canonical HEAD; carry prior REC observations
from PR227, append KS01 only to REC nodes/own return records, preserve original
40contracts,17edges,7authorities,other38nodes,AGENTS,fixed handoffs. No assembler/
renderer. Re-read head before writing and use expected_sha ref leases.
No merge,activation,CI rerun or production approval is part of this unit.

## Claim gates
H5 actual-payload/source-domain admission may close locally; physical epsilon,
independent reference uncertainty,endpoint uncertainty,whole-cell curvature,
absolute history bound remain null. H6 actual incident trace/selected Bianchi
geodesic-direction-frame/measure-volume-clock-source-query owner remains OPEN.
H7 gains same-source local pair [Js,Ks] if successful; history pullback,
retiming,geometry and thermal ODE remain OPEN. Global REC-HISTORY=PARTIAL.
Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false;
first failed REI raw HISTORICAL_LOCAL_ONLY. Existing CI red is separate.

