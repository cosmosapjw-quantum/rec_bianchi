# Current state

- Durable stage: **PR-05C1 / v0.62**, reconstructed under `RUNTIME_INTERRUPTION_RECOVERY` from the verified v0.61 full Git bundle.
- Status: `PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN`.
- Original-HyRec accepted history remains on the exact canonical `DLNA=8.49e-5` macro grid.
- Adaptive backward-Euler full and both half-step trials occur only inside a canonical macro interval; every trial independently passes convergence, positivity, backward-error and algebraic-residual gates.
- A successful macro endpoint commits exactly one history slice; rejected attempts, event rollback and restart do not mutate accepted history.
- Source-conditioned rank-one DAE lanes near `z~1300,1100,900` pass positivity, residual, causality and restart gates.
- The Bianchi-shaped speed profiles in v0.62 are deterministic event-controller regressions, not source-derived `BackgroundSnapshot` trajectories.
- Full COM-KHW collision/interface/background coupling is **not** claimed and remains **PR-05C2**.
- Artifact SHA-256: `294f390aa3094092b9c54885c0fa1b305b845e2b2e7f7d5df89d16d3f4929348`.

## Recovery note

The first v0.62 delivery reached local Git/artifact generation but its conversation attachment registration failed. The generated-file registry therefore omitted v0.62 even though Git objects and bundle bytes survived in the runtime. Recovery inventoried those bytes, reproduced the stage from v0.61, found and fixed an all-trial step-doubling gate defect, regenerated the immutable artifact, and requires fresh final receipts and bundle replay before release.

- Committed feature-range whitespace, staged changes and unstaged changes are now checked by `scripts/check_commit_range_whitespace.py`; only verbatim `state/*.log` evidence is excluded.
- Current remote routing baseline is merged PR #20/v0.61; v0.62 remains local delivery only.
