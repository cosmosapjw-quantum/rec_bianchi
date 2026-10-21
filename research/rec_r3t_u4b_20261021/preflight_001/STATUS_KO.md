# R3T-U4B preflight status

- Existing U4A allocation: **REUSED**, not relaunched; original supervisor
  `CAP_HOLD` result and terminal journal remain byte-identical.
- New U4B science: **NOT_RUN** at preflight closeout.
- NCP current host: `s1a0e5abed09`; systemd 255.4; no U4A/U4B worker was
  found at intake (the `pgrep` output contained only its own shell command).
- U4A final checkpoint and accepted causal streams bind the new run start to
  74443 and exactly 1551 prefix columns. Predictor tail is
  `(-0.07114765752633298, -0.07119959986036085)`.
- Probe first attempt exposed a Python harness API error (`Popen` does not
  accept `capture_output`); this was corrected. Final NCP probe003 exit was 0.
- Final preflight review: `PASS_SCOPED_PRELAUNCH_A_C`.
- Targeted tests: 33 passed; quick repository gate: PASS; native C syntax:
  PASS; whitespace: PASS.
- The next action is one separately registered allocation, at most 32
  accepted steps from 74443, only after this source is committed and new CI
  passes. No automatic continuation is allowed.
