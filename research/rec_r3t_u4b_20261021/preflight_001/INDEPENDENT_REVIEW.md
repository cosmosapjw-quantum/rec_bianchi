# R3T-U4B prelaunch independent review

## Verdict

`PASS_SCOPED_PRELAUNCH_A_C`: supervisor terminal accounting, U4B descendant
input contract, native event/stage boundary behavior, and the narrow whitespace
exception are reviewed for one possible U4B allocation. This is not a numerical
result or physical admission.

## Review scope

Fresh read-only review of the working diff in:

- `scripts/run_r3t_u4a_supervised.py`
- `scripts/probe_r3t_u4a_terminal_accounting.py`
- `scripts/verify_r3t_u4a.py`
- `scripts/c_harness/original_hyrec_r3t_u4a_restart.c`
- `src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_u4a.py`
- related targeted tests and `scripts/check_commit_range_whitespace.py`

Initial review findings were repaired and re-reviewed: launcher registration
 timeout now kills and reaps its process before propagating failure; native U4B
checks thermal/RT gates before RHS/history writes and stops after the first
accepted post-Saha exit; U4A split continuation retains its prior behavior.

## Evidence used

- NCP systemd 255.4 dummy probe, 8 cases, result SHA256:
  `dd64a1aba590392a4890aa3a4fa9684126f47ae2a6cfa127273b9e249d5f9b33`.
- Every dummy process recorded `RLIMIT_AS=[2147483648,2147483648]`; CPUQuota
  was 100%, MemoryMax 2 GiB, normal and abnormal worker exits were distinct,
  and cap-killed cases had terminal service counters.
- Actual U4A final checkpoint SHA256:
  `7d7cf81dafd46672be8018cd7dacaa26f2aa21653a47774206005716ef967529`.
  Its U4B loader verified global index 74443, 32 accepted steps, 1551 causal
  history columns, the frozen predictor tail and source/input bindings.
- Targeted local suite: 33 passed; native C harness syntax check passed;
  `scripts/verify_repo.py --quick` passed; `git diff --check` passed.

The reviewer did not execute the scientific worker. This verdict authorizes
only the separate bounded preflight allocation once source identity and CI are
fixed. Preserve all historical U5 and production claim ceilings.
