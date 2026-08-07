# Current state

- Durable stage: **PR-05C1 / v0.62**.
- Status: `PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN`.
- Original-HyRec accepted history remains on the exact canonical `DLNA=8.49e-5` macro grid.
- Adaptive backward-Euler trial steps, rejection and event restart occur only inside one macro interval.
- A successful macro endpoint commits exactly one history slice; rejected attempts and rollback do not mutate history.
- Source-conditioned DAE lanes near z=1300,1100,900 pass positivity and residual gates.
- Full COM-KHW/interface/background coupling is **not** claimed and remains PR-05C2.
