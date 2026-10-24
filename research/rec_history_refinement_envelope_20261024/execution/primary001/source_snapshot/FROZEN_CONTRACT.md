# REC-HISTORY-REFINE01 — frozen existing-history comparison

Frozen by the Astra controller on 2026-10-24, before numerical comparison of the selected arrays. Workflow: physmath-research-loop built-in1.0.0 / approved designv0.2. The lower-tier executor may implement this contract and perform the bounded comparison after the S1 checkpoint. Changes affecting a convention, acceptance criterion, input identity or claim require return to the controller.

## Objective and admission boundary

Compute the piecewise-affine discrepancy of two actual, independently generated outgoing photon histories on their common early-time domain. Separate common-node discrepancy from the fine-grid midpoint detail. Compute the exact mathematical cell supremum and outward-rounded binary64 enclosures of that supremum. Preserve startup and event ownership in the measured summaries.

The fixed original REC target remains T0=2.728 K, nH0=0.18745798773143102 m^-3, with 313 retarded queries at z=1100.092189396162...1133.87330719964. The selected pair has its own common cosmology and early-time support; its coverage of the original target is 0/313. This unit advances the usable history-comparison operator and measures real candidate data. Admission of the original target, an absolute physical error, an integration order, or a global convergence claim is not an output of this unit.

## Immutable identities and allowed work

- Repository: cosmosapjw-quantum/rec_bianchi; parent commit ae189694c15e09c6f96c44ef6b74b48afc2632ac; parent tree a783a3269d263f24bfac7f0ed3a9db63f7ff5b4d.
- Proposed new branch: research/rec-history-refinement-envelope-20261024. Create only after confirming it does not already identify other work; never force-update another owner's branch.
- Owned path: research/rec_history_refinement_envelope_20261024/ in the snapshot workspace rec_history_next_work. No clone/worktree. Existing code and evidence remain unchanged.
- Fixed central authority: rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17. Intake central observation: d5aa6c94a77b5687052d3d6902d140e2df9ef798, to be refreshed before any additive observation patch.
- Coarse original: research/rec_r3i_time_refinement_20261016/h2_continuation_001/ncp_run_001/python_continuation.npz; 3710522 bytes; Git blob be6e267cbe9bcfa309eec9b2dd458b0ceecbed44; SHA256 70274c9631b33e4ed1c4b8761608cd9ce22f82d96b0afbcb36c0e786e2c04c6d.
- Fine original: research/rec_r3q_h4_continuation_20261020/ncp_event_001/python_continuation.npz; 7390437 bytes; Git blob d91967045a484c5d164edf6c051e01dab57f7dbc; SHA256 7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9.
- Local originals: rec_history_next_intake_20261024/rec_sources/raw/h2_continuation_python_continuation.npz and h4_event_python_continuation.npz. Copy byte-for-byte to inputs/ for the self-contained unit; existing Git blobs can be reused at the new paths.
- All intake source bytes, inventory and known failed read attempt are preserved under provenance/survey/. Exclude duplicate input bytes from that survey copy; inputs/ owns their new package location.

## Physical and storage conventions

The two candidates use T0=2.7255 K, nH0=0.18971712352134673 m^-3, the same original archive SHA256 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27 and scalar FLRW source frame. The source manifest and exact producer-receipt binding establish the remaining cosmological parameters. The h4 input does not import an h2 or C state.

Use only virtual_out[311,N] followed by lyman_out[3,N], in that order, giving 314 signed dimensionless occupation-departure channels. Preserve original per-field names and indices in all summaries. average_virtual is a separate field and is not a comparison input. The histories are departures from the same source Wien reference, so the common reference cancels at each common eta. No angular measure, direction remapping, q substitution, or thermodynamic closure is introduced.

H=h2=4.245e-5; h4=2.1225e-5; eta0=-log(8001)+36446 H=-log(8001)+72892 h4. Integer nested coordinates own alignment; independently rounded eta calculations do not select a different cell. Coarse columns 0...759 and fine columns 0...1518 define 759 cells m=0...758. The original coarse column760 remains preserved but lies outside this comparison. Photon columnj belongs to input state g0+j, not the accepted state g0+j+1.

The mathematical represented-function closure is x=(eta-eta0)/H in [0,759]. Operational queries require 0<=x<759, with committed prefixes sufficiently long to contain both bracketing samples. Native iz>=2 constrains current prefix length, not retarded query coordinate. x=759 is retained solely as an endpoint/one-sided-limit witness for the supremum; operational queries at that endpoint reject. No extrapolation.

Masks: startup-origin cells m=0...7; post-startup cells m=8...758; continuation cells before the event m=8...757; event-straddling cell m=758. Continuation-only does not remove propagated startup error. In the last cell C758/F1516 are H_HE input, F1517 is the first H_ONLY input, and C759/F1518 are H_ONLY. Both producers zero incoming during local j<2, which spans different physical time lengths. Their initial trajectories/predictor memories and seed arithmetic order also differ. These effects remain in the measured nodal discrepancy.

## Frozen equations and numerical algorithm

For channelk and cellm, define E0=C_m-F_2m, E1=C_(m+1)-F_(2m+2), delta=(F_2m+F_(2m+2))/2-F_(2m+1), phi(u)=2 min(u,1-u), and

    D(u)=(1-u)E0+u E1+phi(u) delta,  0<=u<=1.
    Dmid=(C_m+C_(m+1))/2-F_(2m+1).
    B=max(abs(E0),abs(Dmid),abs(E1)).

The theory proves these identities and the exact real-arithmetic supremum. Compute Dmid directly from the coarse midpoint and fine midpoint as well as by the decomposition, so cancellation is observable. Save E0,E1,delta,Dmid,direct-minus-decomposed midpoint residual and B for all 314x759 cells. Save the arrays in a compressed NPZ, with channel mapping and masks, rather than expanding them into huge JSON rows.

For a rigorous enclosure of the supremum of the stored binary64 interpolants, treat finite input floats as exact real values. Use monotone interval operations under IEEE binary64 round-to-nearest: every subtraction/addition result is widened with nextafter toward minus/plus infinity. Widen multiplication by 0.5 as well, including subnormals, then add and subtract for the midpoint. For each of E0,Dmid,E1 obtain [lo,hi]. Its absolute-value lower bound is zero if the interval contains zero, otherwise min(abs(lo),abs(hi)); upper bound is max(abs(lo),abs(hi)). B_lower is the maximum of three lower bounds and B_upper the maximum of three upper bounds. These enclose the exact stored-function supremum. Reject nonfinite inputs or interval overflow. No assertion about an unrepresented physical solution follows from this enclosure.

Implement one direct query path for the original coarse/fine piecewise-affine fields and one decomposed query path. The operational API rejects nonfinite, negative and upper-exclusive coordinates and an insufficient prefix. A separate clearly named closure-evaluation path permits endpoint witnesses for analysis. Require exact expected input identity, finite binary64 arrays, shapes, 2:1 step ratio, aligned eta origin, source/frame/cosmology binding, and 314-channel mapping. Avoid a generalized provider registry.

If an independently justified nonnegative finite same-domain fine-reference error eps_ref is supplied, the conditional physical bound is max(0,abs(D)-eps_ref)<=abs(I_C-physical)<=abs(D)+eps_ref. For cell-level upper bounds, B_upper+eps_ref_cell is valid when eps_ref_cell bounds the fine-reference error across the same cell. The API returns UNAVAILABLE and null numerical physical bounds when eps_ref is absent. All actual eps_ref, endpoint uncertainty, physical M2, absolute physical bounds and convergence-order fields stay null in this unit. A sample-derived second difference is not accepted as a continuous M2.

## Planned controls and acceptance

- Analyze exactly 238326 channel-cells and their three supremum witnesses, with no threshold that forces the measured physical discrepancy to be small.
- Independent arithmetic oracle: Python fractions.Fraction.from_float on channels [0,1,154,310,311,312,313], cells [0,1,3,4,7,8,379,756,757,758], u=[0,1/4,1/2,3/4,1], 350 evaluations. Construct each interpolant directly in exact rational arithmetic; do not import the decomposition implementation into the reference function. Check B_lower<=exact B<=B_upper for the 70 selected channel-cells, using exact conversion of interval endpoints.
- Point comparisons use absolute tolerance 64*eps64*max(abs(C0),abs(C1),abs(F0),abs(Fmid),abs(F1))+8*smallest_subnormal. No max(scale,1) floor. Record the worst residual/tolerance and its indices. This allowance tests arithmetic implementation; it is not a physical error allocation.
- Full-array midpoint decomposition residual must satisfy the same local arithmetic allowance. No dense trajectory solves or history regeneration.
- Meaningful synthetic controls: constant and affine exact agreement; quadratic midpoint detail f'' H^2/8; nonzero nodal error with zero detail; cancellation of midpoint terms; sign-changing difference; zero-scale normalization; interval/subnormal coverage; rejection of nonfinite data, mismatched contract metadata, incomplete domain/prefix and operational x=759. Preserve every failed attempt and diagnose before a repair.
- Per-channel CSV and summary: absolute B and fine-detail maxima, channel history scale max(abs(C),abs(F)) over the admitted representation, normalized discrepancy with zero-scale explicitly handled; argmax cell, knot u, eta and z; all four masks. Normalization is descriptive and not a physical acceptance test.
- Two saved-data PNG/PDF figures: channel envelopes with nodal/detail contributions, and time/cell envelopes with startup/event regions and a last-cell detail. The first PNGs are preserved and actually inspected; any layout repair uses saved results and is recorded separately.
- A fresh Astra reviewer receives the code/diff, theory, original arrays, frozen contract and raw outputs. One review session addresses material findings and any one targeted authorized repair. Additional probing requires a concrete residual risk, not recursive audit.

## Bounded execution and stopping rule

New independent allocation: cumulative 30 CPU seconds / 90 execution wall seconds / one thread / 1 GiB address-space cap. Planned allocations: primary+controls 16 CPU/45 wall; independent selected review probes 6 CPU/15 wall; figure rendering and a diagnosed repair 8 CPU/30 wall. Limits apply to all scientific attempts including failed starts. A process-local time/resource controller enforces the cumulative remaining budget; post-exit inclusive getrusage is reported as such, not as live aggregate enforcement. Set OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS and NUMEXPR_NUM_THREADS to1 before imports. The original source inputs are read-only. A single full comparison is planned; no replay of prior H01/ADM01/02R runs.

Exact commands to be supplied at S1, under this owned path:

    python code/run_bounded.py --label primary001 --cpu 16 --wall 45 -- python code/analyze_pair.py --contract inputs/CASE_PLAN.json --out results/primary001
    python code/run_bounded.py --label figures001 --cpu 8 --wall 30 -- python code/render_results.py --results results/primary001 --out results/figures

The controller may adapt syntax to the reused bounded runner; the actual command and argv must be frozen in S1 before execution. Environment versions and the used runner are preserved. Standard-library Fraction avoids installing a numerical oracle dependency. Do not run an IVP, native recombination executable, dense RHS, global solver or old campaign. Unchanged prior result identities and resource ledgers are reused, not reset or borrowed.

Wolfram symbolic check is separately limited to one evaluator request with timeConstraint=5 seconds and three algebraic identities (left half, right half, quadratic detail). Its service-reported/request duration is not presented as local CPU measurement. SciSpace discovery and primary literature are source intake, not a physical reference provider.

Stop and return to Astra on source/shape identity disagreement, ambiguity in the convention, a substantive failed acceptance, missing original output, or exhausted limits. Preserve command, stdout/stderr, return code, source snapshot and resource observations. Implement only the smallest diagnosed repair that Astra authorizes within the remaining cumulative budget.

## Delivery and retained state

S0 saves this contract, theory, source intake and case plan; S1 saves implementation before execution; S2 saves actual raw comparison and inspected figures; S3 saves independent decision, final report, stage table and handoff. Per-stage progress references these checkpoints rather than claiming 20 distinct scientific experiments. Git writes create a draft branch/PR; no merge or activation. Dropbox checkpoints use new unique filenames in the established project folder. Drive records actual acknowledgement or unresolved status, with no duplicate retry of the older 02R stalled upload. No backup wait reruns science.

Central changes, if made, update only REC-LINE02/REC-HISTORY observed fields and one companion return on the actual latest parent. Preserve original40 nodes/contracts,17 integration edges, fixed authority, dependency fields, HE-X1 and parallel CR/HE updates. Do not run the whole assembler/renderer.

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false; first failed REI raw HISTORICAL_LOCAL_ONLY. REC-HISTORY parent PARTIAL; H5 INPUT_DEPENDENT_UNCALIBRATED. Full angular supplier/measure and thermodynamic Jacobian remain their existing input obligations. Physical goal completion percent is null.
