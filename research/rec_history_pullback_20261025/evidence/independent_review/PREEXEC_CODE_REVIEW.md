# REC-HISTORY-PB01 — independent preexecution code review

## Verdict and exact scope

**PASS_RUN_READY — static implementation readiness only.**

Review closure: 2026-10-25 07:39:26 UTC.
Reviewer: the continuing independent Astra reviewer, separate from the lower-tier
implementation executor. This is the same theory/code/results review episode.
No review recursion or new scientific subtask was opened.

The original pre-interruption C5 review was NOT_RUN. This review actually read
the current recovered source. It does not inherit an unread historical C5
readiness claim. The earlier theory verdict remains historical; its reconstructed
review text is labelled separately. The current THEORY.md and
FROZEN_CONTRACT.md have the original exact hashes.

There is one finding, PB01-PREEXEC-001, now CLOSED. There are no remaining
blocking findings within the frozen scope. The reviewer performed static reads,
identity-metadata inspection and selected file SHA256 reads only. Primary,
tests, numerical arrays, interval calculations and figures were not executed or
recomputed by the reviewer. Numerical A–G results and actual PNG acceptance H
remain NOT_RUN.

This verdict does not issue runtime authorization. Root must retain actual
S0R/S1 delivery acknowledgements and write its own RUN_READY authorization
before the single primary. Figure execution has its separate authorization.

## Exact reviewed snapshot

| Item | SHA256 |
|---|---|
| Corrected code/primary.py | bc63fd1868710548f27381a6bbaea8d6b445357436a5fdc009e8997c03a66b26 |
| inputs/EXECUTION_IDENTITIES.json, 18 entries | 34140f9a776162b13f19b39be0a1353952c1918a5d5fc250a0fdb3dd3c7dc0e0 |
| THEORY.md | a556d2c61e20db01a5d94a2b5251471c42634c6b9ddd5c8041e110169563883a |
| FROZEN_CONTRACT.md | 7e552d59c2b7c7cc103e8bb57bfbfd9b419ac8d9755bd23c1df73250217dc112 |
| Preserved pre-correction primary.py | 82e5368ea09973ab001f2a6192535bc187818afbb1d1c798bfff69d27794d123 |

The corrected primary is 15075 bytes. Its only change is the position of one
existing action charge. The execution manifest retains the same 18 used entries;
only the primary entry changes. The immutable source history, K candidates,
K interval arrays, event rows, accepted query witness, scalar adapter and interval
vendor have unchanged accepted identities in that manifest.

The recovery provenance is explicit: primary and exact_controls matched historical
printed hashes before correction; the other reconstructed new modules have newly
recorded hashes; vendor files come from verified immutable archives. No old
unrecovered manifest byte identity is claimed. The 203-byte K CERTIFICATE.json
is the inherited scalar certificate receipt, not a newly generated certificate.
Its fields record norm [1.17562722922718,1.1756272292401908], rho
3.458800151575591e-12 and represented-binary64 status. prepare.py binds that file
to its immutable KS01 S2 payload-manifest entry. This review reuses the prior
scientific proof and root's archive recovery; it does not rerun that proof.

## Closed finding

**PB01-PREEXEC-001 — before-action accounting.**

In the originally recovered primary.py:23–26, the vector of 313 retained scalar
interpolation_jvp calls ran before its REUSED_NATIVE_HISTORY_JVP action charge.
An exception or kill during that work could omit the attempted action from the
persisted ledger. It also contradicted the code README's before-action rule.

The implementation executor moved the same charge to the line before
native_jvp=[] and the loop. The label and count are unchanged. The reviewed
diff changes no formula, perturbation, tolerance, input, accepted scope or total
planned action count. The original primary is preserved at
evidence/implementation_history/preexec001/primary.py, with
COUNTER_PLACEMENT.diff and REVIEWER_FINDING.json. The additive
delivery/C5_PREEXEC_CORRECTION_RECEIPT.json records the new fingerprint; the
original C5_RECOVERY_MANIFEST.json is not overwritten.

The focused corrected-region, diff, receipt and current manifest read closes
this finding. PREEXEC_INITIAL_FINDING.md preserves the initial disposition.

## A–H static assessment

### A. Input identity, routing and source anchor — ready for actual admission

common.verify compares the complete used-file identity dictionary with the frozen
execution manifest before work and after all controls. Paths resolve through the
manifest. prepare.py binds the five main inputs to accepted intake identities,
the scalar vendor to its retained identity, the interval vendor to its fixed hash,
and the K scalar receipt to the immutable S2 manifest.

chart.gather constructs the retained native source routing, verifies the source
permutation 1..313, accepted row/source ownership, the exact represented query
obtained from the frozen redshift and energy ratio, native cell equality and the
strict prefix 5127. It retains source-owned endpoint slots and requires 626
distinct slots before applying the endpoint norm lemma. Each admitted row is
written as a separate witness.

Native fractions use the retained (q-eta0)/h-k order. The accepted saved-eta
fraction, both base reconstructions and the stored incoming are retained separately.
The 5e-9 base-reconstruction gate is unchanged. Connected incoming is stored u0
plus the exact-chart increment. No theta/source reconstruction is introduced.
The runtime hash and 313-row admission outcomes remain pending.

### B. Tangent and coordinate adjoint — ready

The sparse derivative is (1-a)dy_L+a dy_R+g xi, with g the nearest point candidate
for the exact represented slope. Explicit P, A=Khat P and C=Khat diag(ghat) provide
the independent dense-action path. The retained scalar interpolation_jvp provides
the native-order diagnostic; it remains distinct from the exact rational slope
enclosure.

The VJP first applies Khat transpose, then the endpoint scatter and query diagonal.
The two fixed directions and two nontrivial receiver covectors match the contract.
Pairing normalization is the sum of absolute terms from both sides, with the
frozen 1e-280 floor. The 2e-12 checks are unchanged. Fraction toy derivatives and
transpose identities, the disjoint-support norm equality, shared-support
cancellation and exact-zero controls are implemented. Coordinate cotangents do
not introduce a physical measure or Riesz map.

### C. Finite remainder and native arithmetic bridge — ready

Each case saves requested and rounded endpoint/query coordinates before case
work. Fraction forms exact actual differences of the represented coordinates.
The exact-chart increment, tangent and mixed remainder obey
r=(xi/h)(dy_R-dy_L); the code asserts that identity before using point products.

The finite native fraction is reevaluated with the retained interpolation.
The code separately forms delta_alpha=a_prime-a-xi_actual/h and the bridge
delta_alpha*(new_right-new_left), and asserts the exact rational native/chart
identity. It does not substitute requested perturbations for actual rounded
differences. Native evaluation/subtraction rounding remains in the residual.

All eight fixed cases use the specified directions and t=1,1/2,1/4,1/8.
The native bridge normalization and 5e-12 criterion are unchanged. The recorded
arithmetic floor and above-100-floor labels govern the 1.9..2.1 Taylor order
checks; at least two non-floor ratios in one direction are required. These are
local controls and are not a global convergence claim.

Requested inputs, exact scalar records, completed case arrays/boxes/metrics,
cumulative completed cases and exceptions have explicit save paths. Completed
cases survive a failure in a later case; partially completed current work is not
misrepresented as completed evidence.

### D. Outward interval composition and norm — ready

The reused interval vendor validates finite ordered endpoints and uses outward
nextafter expansion for elementary operations and sequential sums. Claimed
enclosures do not use BLAS sums as proofs. Fraction-to-float slope enclosures
compare the rounded float with the exact rational, then expand in the necessary
direction.

C intervals multiply the inherited K intervals by exact-slope enclosures. Row
norm lower contributions are zero for intervals spanning zero; upper contributions
use maximum endpoint magnitude. The maximum row bounds enclose the infinity norm.
Point candidates must lie inside the intervals. Positive norm lower bound and
relative-width <=1e-6 are enforced. A zero lower bound writes the absolute interval
and returns to root instead of selecting a new tolerance.

Endpoint norm inheritance is conditional on the actual source census and positive
partition already enforced by the native interior admission. It reuses the KS01
norm interval without an inverse or certificate rerun. Common-clock and
radius-scaled quantities have separate arrays/labels. The rational toy query
product containment check is present.

### E. Conditional finite boxes — ready within the defined chart

conditional_box computes outward bounds for
(1-a)e_L+a e_R+|g|tau+(tau/h)(e_L+e_R), followed by an outward point-coefficient
dot with W=max(abs(Klo),abs(Khi)). All radii must have the actual shape, be finite
and nonnegative, and fit strictly within the fixed-cell intersection.

Actual numerical boxes use upper enclosures of the exact rounded endpoint/query
differences. The exact toy and actual chart/native point probes are checked.
The certified formula belongs to the anchored exact-real chart; observed native
numerical-probe containment is a separate empirical control, not a replacement
proof that omits native floating arithmetic error. All physical epsilon/bound
fields stay null, including the no-radii return.

### F. Branch/domain ownership — ready

The stored-knot, native-knot, chart and prefix margins remain distinct exact
rational quantities. The safe radius is rounded inward. Actual finite probes
must remain in the strict intersection and retain the same native cell/prefix.
The scalar adapter retains exact-knot query refusal and selected-knot endpoint
variation. Implemented controls cover wrong source/prefix/shape, nonfinite
tangent/query, cell crossing, strict upper prefix, negative/nonfinite box radii
and an oversized query box.

No generic Bianchi query law or physical retiming rule is chosen here.

### G. Event composition — ready

The inherited F, proper-time, number, radiation and atomic rows compose through
the same endpoint weights and slopes. Paired atomic/radiation arrays and interval
endpoints preserve the same event's opposite signs. Numerical point event actions
are compared with explicit endpoint/query actions. Stored response identities
retain source H and incident subtraction; no new H, volume or source coefficient
is inserted. Unit metadata distinguishes per-ln(a), per-second, number-volume
rate and energy-volume rate responses.

### H. Saved-data figures and review transition — prepared; actual inspection pending

The figure script reads saved constants, composed operators, finite-case and
adjoint results only. It contains no source, solve or K action. The planned plots
show signed cell margins/query row gains and the local remainder/adjoint checks.
Exact zeros are preserved, symlog thresholds are named, and the adjoint threshold
is plotted. The remainder plot is labelled as local controls rather than global
convergence.

No PNG has been produced or inspected in this preexecution review. Root and this
same reviewer must inspect actual first images after the authorized saved-data
render. This static readiness does not satisfy actual-image criterion H.

## Counters, hard limits and remaining authorization

The corrected main-path charged-action plan, counted statically from the source,
is 97 point/operator actions and 200 row-level event actions, below caps 256 and
512. These are planned counts, not observed runtime totals. Point actions include
the two 313-component native JVP diagnostics as vector actions. Matrix construction,
scalar admission and refusal checks are not represented as additional K matvecs.
The counter persists a reservation before each charged action; a partially
completed reserved action is conservatively retained.

The interval counter records named passes: one composition stage, eight actual
finite-box stages and one toy-box stage. It is not a count of every elementary
interval operation. Runtime receipts must report the actual counters.

The primary wrapper refuses missing root RUN_READY and existing attempt paths.
It sets six thread environments to one and imposes CPU30s, wall90s, 1GiB address
space and core0, preserving stdout/stderr and an inclusive-child resource receipt.
The figure wrapper has a separate readiness token, no-overwrite gate and
CPU10s/wall30s/1GiB limits. Neither wrapper retries automatically.

The unit allocation remains CPU50s/wall150s, including the reserved repair and
review allocations. Zero new source coefficient reconstruction, linear-system
RHS, solve, inverse, native build, IVP and campaign replay remains the intended
scope. Review static reads are not scientific executions; their full wall/host
cost is not silently booked as zero measured child cost.

## Limits carried forward

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
H5 physical endpoint/reference/curvature calibration remains unassigned. H6 actual
incident trace/geodesic/frame/measure/clock provider remains an external admission.
The numerical Js block and the certified stable Ks proof have distinct scopes.
No global, production, CI, merge or activation PASS is inferred.

Skill context used: parent-frozen physmath-research-loop built-in1.0.0 /
approved v0.2; preserve prior evidence and failures; distinguish byte identity
from scientific validity; use this continuing independent review episode;
do not execute science as the reviewer or open reviewer recursion.

