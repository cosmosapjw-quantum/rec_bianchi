# Sole independent design-review receipt

DATE: 2026-08-23

REVIEWED_OBJECT: `/tmp/rec_bianchi_algoseed_coding_research_record.md` before reconciliation

REVIEWED_SHA256: `42408ae8b425cc997d4ab31add2085202d15553316d9883c2baa0e2253f516c0`

VERDICT: `REWORK`

The reviewer was not told an expected verdict and made no repository or candidate-harness edits.

## Mechanical result

- 6 unique N rows.
- 56 unique consecutive R rows.
- 16 unique V gates.
- Every R01--R56 mapped to at least one V gate.
- Totals `45 CONFIRMED / 11 CORRECTED` were arithmetically consistent.
- Mapping was not accepted as proof of discriminating coverage.

## Required reconciliation

1. Declare conversion and JVP between per-second operators and `eta=ln(a)`: `y_eta=R_t/H`, `D(R_t/H)=DR_t/H-R_t DH/H^2`; give every suboperator a clock, orientation and unit contract.
2. Replace mask-plus-rank reasoning with square row/variable partitions, scaled `rank(F_ydot)`, regularity of `lambda F_ydot+F_y`, semi-explicit `g_z` nonsingularity, current-cell sweeps and explicit higher-index rejection.
3. Do not call the nonlinear Jacobian-scaled residual an exact componentwise backward error. Require an assembled/upper-bounding absolute-Jacobian action plus remainder scope, or rename it; independently validate the denominator.
4. Make stage outcome enums exhaustive, including event uncertified, remap infeasible, incomplete/unsupported problem, nonfinite output and budget exhaustion; declare retry/serialize/transition/publish rights.
5. Give the second half-step an attempt-local provisional history/dense overlay without mutating accepted history.
6. Make event semantics determinate: one standard continuous signature, derivative/discontinuous guard rules, simultaneous-event priority/batch, left/right state, zero-speed and Zeno/chattering handling. Positive controls must certify and converge; always-uncertified fails.
7. Do not treat NumPy read-only flags as immutable identity. Protect owning storage and derived-cache coherence; attack aliases, views and `setflags` at V01.
8. Compare problem/restart schema against an independent consumed-dependency manifest/access trace so jointly omitted dependencies fail. Register callable/code identity and exact binary/BLAS/thread/CPU/runtime identity.

## Focal row findings

- R31: require kernel-specific typed subpolicies; reject bool-as-int, nonintegral/overflow limits and unknown/unconsumed fields.
- R35: preregister grid/stiffness regimes and quantitative iteration/memory thresholds.
- R41: retain fail-closed; do not call missing ALE/GCL/remap an implemented cure.
- R42: packet identity must be face/ordinate/sign/time-segment granular with mixed-sign, zero-crossing, replay and drop controls.
- R43: outcome inconsistency is fatal until the exhaustive taxonomy exists.
- R47: add omitted-dependency detection, callable identity, cross-field and full environment coherence.
- R51: add subprocess-kill recovery, parent-directory fsync, concurrent-reader tests and a local-filesystem-only atomicity claim.
- R54: no uncaptured 129-test receipt may enter admission; V16 needs exact full-suite argv/raw output.
- R55: keep the frame/API blocker and physics cure inconclusive.
- R56: copy-before-freeze is insufficient; detect post-construction primitive mutation/stale derived data.

## Nondiscriminating preimage gates

- V01/V12 could not discover omitted fields.
- V02's owner oracle had to be independent of `ProblemSpec` and residual code.
- V03 lacked current-cell/pencil checks.
- V04 lacked an independent absolute-Jacobian denominator oracle.
- V06 allowed always-uncertified.
- V09 lacked a feasible root that must converge.
- V13 lacked frozen regimes/thresholds.
- V14 allowed an all-unsupported stub.
- V15 exception injection was not crash/power-loss evidence.
- V16 lacked exact argv/environment/diff/raw receipts.

## Plan result

The preimage total order was unsafe: T0 intentionally created red tests, T4 depended on V15 implemented only in T7, and physically blocked residual work could delay independent R51 publication safety. The reviewer required a dependency DAG, an unmerged T0 witness, early crash-safe generation storage, later admitted-step integration, and typed retained blockers.

## Claim ceiling

The receipt supports bounded counterexamples, complete mechanical coverage and a candidate design only. It supports no implemented cure, production trajectory, convergence/AP/scalability result, scientific endpoint authority or public promotion. Reconciliation does not change this verdict without a new independent review.

## Custody

- HEAD: `5a09f3797210284f83a1a1adb0e0092d1ac48475`
- TREE: `4002915ad851afc2ab71f94a882cc99d81748062`
- Sole repository dirt: pre-existing `M state/REMOTE_CHECK_LATEST.json`
- Reviewer edits: none
