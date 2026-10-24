# REC-HISTORY-THERMO01 frozen theory-to-code contract
Version1; author/acceptance owner root Astra; workflow physmath-research-loop
built-in1.0.0/designv0.2. Source parent rec_bianchi@
ccf2bd088972e952fbe8e7e6eb21ccc8a7275447, source tree
cddef023e1b581d52a7537912e4cf92de7335fa0.
New branch research/rec-history-thermo-20261024.
Owned repo path research/rec_history_thermo_20261024/.
No existing clone/worktree is available; Git connector publication is used.

## Scope and exact inputs
THEORY.md is the implementation equation contract.
Original target T0=2.728K,nH0=.18745798773143102m^-3,
z=1099.9986525171403. Scalar FLRW and native source constants.
Six coordinates xe,xHII,logTR,logTM,lognH,logH as defined in THEORY.
Input CSV blob6399b59ca3c97d6c5b1162f83f50a6677fad06ff,
SHA2563a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7.
Prepared NPZ blobe96d15dfc0432429f2fcb680159f4820c02ce591,
SHA256014ce6c467639b28086cfc1d6a70a09818544896b5d21e88508523bec111b9de.
Original hydrogen.c blob2df4561f1b1ef80991ca3b7645666a630eea19b7,
SHA256421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b.
hydrogen.h blob80d612d2c032059f419b701f1376d43513cff2ed.
Alpha_inf.dat blob3fae8b09181cdf04716491acfe60fa21bd2a55e3,
SHA256c543c755d99ba8e999450dd5cb486a3ad88d26378da0ccc8363b10418e4832bd.
R_inf.dat blob220d432db0bc763157202db8001819460d5638c3,
SHA256ce914f4b552ba55ba00f7916f36b0986f19adfdb638e5aefae91f7b2d05a8112.
two_photon_tables.dat blobdf04635e8fd5ed03481547a7967a14030d90a79b,
SHA25693d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9.
Existing primitive_rates.py blob3ae7cda8c91456025a019f81ca13f638f717079b,
full_2012_atomic_source.py blobffeda51ddbde4d631088fd4787822e3a94e49785,
and original_hyrec_native.py blob069a1671e18229f27882549a0cd38071e6d9a661
are source-only references for existing value/derivative methods. Record all
actual bytes in inputs/INPUT_IDENTITIES.json before execution.

## Implementation and permitted work
Lower-tier requested gpt-6.1-sol/high implements and executes only after root
gives RUN_READY. Actual runtime model remains unobserved unless metadata
identifies it. Root authors theory, contract, decisions and repairs; fresh
Astra reviewer independently reviews equations, source mapping, code and raw
results. Same reviewer may close one diagnosed finding without new review loop.

Implement standalone source-owned coefficient construction and forward
derivative (explicit analytic tangent or six-component dual arithmetic).
Reusing existing local polynomial derivative code is preferred. Keep native
coefficient order and branch masks; do not execute/compile native C.
Base and tangent linear solves are algebraic313x313 solves, not IVPs.
Independent oracle: complex-step evaluation of full source with branch masks
and polynomial stencils fixed by real baseline, using complex arithmetic,
without calling analytic tangent propagation. Document shared value formulas
so independence is derivative-method independence, not independent physics.
Incoming313 is held fixed. Export base blocks, derivatives, source solution,
all314x6 outgoing columns,313x6 algebraic-state columns, ionization derivative,
number/energy columns and the physical pure-H combined direction.

## Frozen verification and stopping
One primary process planned; no automatic retries. Preserve original outputs,
stdout/stderr and exact source/input snapshot before any diagnosis.
(A) New reconstructed values compare with stored original source blocks,
tau/rates/sources/outgoing and dxHIIdlna. Each named block uses
maxabs(error)/max(maxabs(reference),1e-280)<=5e-9. Structural zeros are checked
separately. Report every block residual, not only a global maximum.
This is a new-reconstruction criterion, not an edit of old source tests.
(B) Analytic six-axis derivatives compare with complex step h=1e-20.
For every coefficient block and output column require normalized maxabs
difference <=2e-8, scale=max(maxabs(analytic),maxabs(oracle),1e-280).
Also report componentwise residuals at outgoing0,139,140,270,310,311,312,313,
F and R_gamma. Zero/near-zero rows are reported with absolute errors and
column scale; no invented relative zero floor has physical meaning.
(C) Linear equation primal/tangent backward residual <=1024eps64 using
componentwise gross |M||X_k|+|M_k||X|+|s_k| and corresponding primal gross.
A zero gross requires exactly zero residual. These are floating diagnostics,
not rigorous enclosures.
(D) Electron-column zero M, common density/H M cancellation, pure-H combined
column and paired energy identities must hold to roundoff (512eps64*gross).
(E) Two fixed mixed directions in theta order:
 d1=(.1,-.2,.3,-.1,.2,-.3)
 d2=(.2,.2,-.1,.1,-.3,.2).
Central differences h=1e-6,5e-7,2.5e-7 for each; use original branch/stencil
ownership at each real endpoint and refuse a comparison crossing it.
At least one step per direction must have column-normalized outgoing/F/R
derivative residual <=2e-5. Record all steps, including worsening caused by
roundoff; do not claim asymptotic convergence from three points.
(F) Distinct manufactured linear systems with parameter-dependent M and s
verify implicit formula against exact rational derivatives; three cases
including nonsymmetric and nonzero coefficient derivative. At most16 small
RHS, dimension<=3. New escape-derivative probes vs 60-digit mpmath cover
zero/small/switch-adjacent/moderate/large depths, at most16values. Include
nonfinite, invalid density/H/temperature/source table domain and
branch-surface refusal controls, not old H01 test replay.
Value/derivative admission failure: finish saving current diagnostics then
return FINDING_RETURN_TO_ASTRA; do not widen tolerances or modify source.
Raw failure remains preserved. Root may authorize one targeted repair/probe
only after a concrete diagnosis, within cumulative cap.

## Execution budget (new finite unit)
Total cap60 inclusive child CPU seconds /180 execution-wall seconds,
1thread, RLIMIT_AS1GiB. Primary40CPU/120wall; targeted repair10CPU/30wall
reserved but not authorized; figures10CPU/30wall.
Planned large-system RHS columns: base1+tangent6+complex6+mixedFD12=25.
Hard ceiling25 for primary; no old RESP01 inverse/certificate or627RHS replay.
Small exact manufactured systems <=16RHS. Scientific primary1,
figure process1. No new IVP, native runtime, old campaign or completed science.
Resource limits enforced before child start; record command/environment,
input/code hashes before and after, inclusive getrusage CPU and process-scope
RSS/highwater, execution wall; do not claim live aggregate telemetry from
unobserved namespace. ProviderIO/packaging/fullturnelapsed separate.
Prior RESP016.076654CPU/6.112102264wall,REFINE01
4.832465CPU/4.895043831wall,H014.848191CPU/4.736567968wall are inherited
ledgers, not spending authority. Preserve older unknown costs.

## Outputs, figures and delivery
code/, inputs/, vendor source-only references, results/primary001,
evidence/execution, evidence/independent_review, THEORY,REPORT_KO,
CLAIM_GATES,BUDGET_LEDGER,STAGE_PROGRESS,GLOBAL_PROGRESS,NEXT_INPUT_CONTRACT,
HANDOFF_KO and delivery/PUBLICATION_STATE.
Two actual PNG/PDF figures from saved results: six-axis outgoing derivatives
with meaningful signed/symlog scales and derivative verification/residual
panel; ionization/number/energy response with units and clear primitive axes.
Root and fresh reviewer inspect first PNGs. Figure rendering runs no source
solver. Raw blocks and first PNGs remain preserved.

CheckpointS0: R1-R5,C1-C4 (9/20) contract/intake/inputs.
CheckpointS1: implementation C5 and preexec R6 (11/20), exact code prepared.
CheckpointS2: R7-R9,C6-C9 (18/20) only after actual run and independent
decision. R10/C10 close after actual Git+Dropbox+central receipts; final
delivery records20/20 if fulfilled. Every stage lists evidence, DAG slot,
local checkpoint and actual publication/backup state.
Git branch/draftPR and Dropbox backup authorized by current user.
No merge/ready/force push/provider activation. Central additive observation
patch on fresh HEAD, preserve original40contracts17edges, fixedhandoff
0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17, other38nodes and existingREC
observations. Assembler/renderer runs0.
H5physicalepsilon/reference/curvature/absolutehistorybound remain null;
full thermodynamic+angular/characteristic system Jacobian remains open beyond
this local6axis block. PhysicalHOLD,REC_U5HOLD_9_FAIL/HOLD_8_FAIL,
CLOSED_HOLD_NOT_RESET,global_convergenceNOT_RUN,productionNOT_APPROVED,
REI_activation=false,firstfailedREIrawHISTORICAL_LOCAL_ONLY preserved.

