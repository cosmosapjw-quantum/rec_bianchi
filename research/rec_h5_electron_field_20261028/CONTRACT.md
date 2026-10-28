# REC-H5-ELECTRON-FIELD01 — frozen R1 contract

Workflow physmath-research-loop1.0.0. Date2026-10-28UTC. Owner cosmosapjw-quantum/rec_bianchi. Parent native PR144 HEAD29e8427fa02ae089b004bce13c3d29ef663c89b4. Owned path research/rec_h5_electron_field_20261028. Branch research/rec-h5-electron-field-20261028.

## Objective and deliverable

Implement a source-equivalent, side-effect-free FULL electron point field with explicit radiation incoming data. Reuse captured132 final writer states and map their results to313 unchanged query records/626 endpoint references. Provide code, source equation proof, meaningful controls, one bounded new primary evaluation, independent R6/C9, plots, actual per-stage publication and dual-provider backups. Deliver a complete source package and copyable handoff. No new integration campaign is required.

## Frozen physical and numerical scope

P=(xe,xHII,nH,H,TM,TR,fsR,meR) is the original represented binary64 dispatcher input. nH is cm^-3,H s^-1,TM/TR eV. eta=ln(a) is dimensionless. Incoming=(Dfplus[311],Dfplus_Ly[2]) comprises signed occupation departures. Primary scope is FULL(model3),H_STEADY,He-neutral,xe=xHII,fsR=meR=1; therefore total Fe=FH. Other phases require separate hydrogen/helium source accounting and are excluded from this primary. Metric convention(-,+,+,+); c,hbar,k_B remain in the source physical definitions and the frozen unit conversions; no new normalization is introduced.

Use the original dispatcher temperature path exactly once: ratio=TM/TR; rescale_T(&TR,fsR,meR); TM=ratio*TR. Its binary64 ratio roundtrip matters even at fsR=meR=1. Captured coefficient temperatures must not be supplied as dispatcher temperatures. Preserve matrix orientation, original allocator initialization, summation order, native cubic table interpolation, original1e-6 optical-depth branch and feature macros. Incoming,real and virtual departures are signed and must not be clamped to nonnegative values.

All scalars/incoming finite;H,nH,TM,TR>0;0<=xHII<1;xe>=0;after native rescale TR in[0.004,0.4]eV and TM/TR in[0.1,1]. The actual algebraic solve must have nonzero pivots/Schur determinant and finite outputs. No claim of coefficient-box-wide nonsingularity or inverse gain is added; that remains the separate QSS03 work.

## Exact source equation and side-effect boundary

With p=xHII,x1s=1-p,s=SAHA_FACT*TR^(3/2)*exp(-EI/TR)/nH,Delta=xe*p-s*x1s,
FH=-(1/H)sum_i=0,1 {nH[s*x1s*DAlpha_i+Alpha_i*Delta]-xr_i*Beta_i}.
The implementation order is explicit incoming -> original populateTS_2photon -> original solve_real_virt -> source FH scalar. The original history interpolation and subsequent history writes are outside the new adapter. Caller inputs/tables/history/files remain unmodified; diagnostics use fresh local arrays. xr=(2s,2p),xv=x1s*Dfnu. At fixed P/tables, an affine incoming dependence may be stated only after verifying from the original assembly that its matrix is independent of incoming and its source is affine.

## Source identity and reuse

Original native SOURCE ZIP:110654069bytes,SHA25694b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c; actually recovered by byte concatenation of its two Drive parts and full SHA verified this turn. The archive is unmodified. LAST_WRITERS,QSS_WRITES and CALLS join by(call_id,slot) with expected132 final writers, no missing/duplicate binding. All313 original query records,89 distinct geometric cells,626 endpoint references,geometric endpoints/query/exact alpha are preserved.

BGJET source/review HEAD0cb5c5ee16f5be57e71ea6694a8fd93af0394467 and native source/delivery HEAD29e8427fa02ae089b004bce13c3d29ef663c89b4 are reused. Thermal PR145 HEAD7d3db873dacac29bab40cb5576d1c14b629afa87 SOURCE1608787bytes,SHA2564a9d83540a404c8f9eb4f6ab934694c5d81af7a54738217c774f1a36389d090d was read/restored. Its existing affine thermal residual is retained as a separate result with fresh R6/C9 pending, not rerun/admitted by this point-field unit. QSS03 HEAD5438f2a082f7ed204603e441866ca63d1e0bf9de is separate12/20,C3,target certificate NOT_RUN. Existing source zip/failures/budgets remain preserved.

## Acceptance fixed before the first execution

Report bitwise equality of FH,xr and xv to saved source records as an explicit count; do not invent equality. Required floating-point FH parity gate is |FH_new-FH_saved| <=512*eps64*S_F, where S_F=(1/H)sum_i {nH(|s*x1s*DAlpha_i|+|Alpha_i*Delta|)+|xr_i*Beta_i|}. If S_F=0, exact zero difference is required. This is a predeclared source-parity tolerance, not a mathematical roundoff enclosure. No post-failure tolerance widening.

Require normalized block residual max_k |(M X-S)_k|/(sum_l |M_kl X_l|+|S_k|) <=4096*eps64, with exact zero numerator when denominator zero. Compute it in an independent reconstruction of original block orientation. Preserve detailed residuals and original raw outputs. Require complete132 writer binding,626 endpoint mapping, source/input integrity, finite/domain/shape checks, dispatcher-to-coefficient provenance, and input/table nonmutation. Controls must expose input-unit mistakes, double rescale/roundtrip, incorrect phase/species interpretation, source changes, and lost incoming dependence without requiring arbitrary radiation values to be positive.

## Resources and stage ordering

New scientific child CPU cap60s total, per child<=30wall-s/512MiB,single-thread. Initial allocation build/contract tests10CPU,primary20,independent validation/controls20,plots10; preserve failures and all charges. A targeted repair uses remaining cumulative budget and requires a new diagnosis. No unrelated optional reruns. Parent/model/network/metadata/packaging costs are separately UNKNOWN_NOT_ZERO unless measured; this is not a whole-session cost claim. Historical BGJET/thermal/native/REI allocations are closed/nontransferable; REI NO_MORE_IVPs remains effective. Old producer/reference/native full-history/oldtests/audit/QSS03 certificate executions remain0; new point-kernel calls are explicitly counted.

R1-R10 then C1-C10: publish each actual stage, make its distinct immutable capsule, obtain Drive/Dropbox final ACK and separate size readback, publish the stage receipt before moving to the next stage. Stage status and scientific admission are separate. Independent native fresh-context nonauthor R6/C9 are actual reviews; model-family diversity is not assumed. A library copy of the final complete report/handoff is retained.

## Scientific ceilings and next-unit authorization

Canonical28/88,+0; separateREI33/88 not added. Physical0/313;physical query/K/M2/defect/L/tube/e0/epsilon/outgoing=null;H6/H7OPEN,L4false,REIactivationfalse. A native-clock FH versus geometric affine slope discrepancy is a labelled point diagnostic, not a whole-cell continuous physical defect. This unit supplies the source-point Fe component; it does not yet supply an autonomous full-state field, model discrepancy, initial error or positive physical tube.

The current user request explicitly authorizes the next R/C unit after survey, superseding the prior stop for the completed task only. AUTO_NEXT_NODE=OFF_AFTER_THIS_SELECTED_UNIT. No main merge or unrelated owner change. Earlier REI-only instructions from a separate historical integration conversation do not override this explicitly continued REC project task. Survey completion is scoped: all accessible relevant Git branch/PR collections enumerated; full conversation transcripts and several archive listings remain unavailable/partial and are recorded, not called exhaustive content validation.
