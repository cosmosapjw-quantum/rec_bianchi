# LINE02 — exclusive native Lyα source and frozen response

This runnable research unit follows LINE01 at REC PR128. Its complete scope is
one preserved z≈1100 native scalar snapshot, with2real+311virtual algebraic states.
The direct Lyα loss and blue-feedback source are replaced together. Original
diffusion, virtual operators and incoming history values are retained.

Read FROZEN_CONTRACT.md and PREEXEC_BOUND_ADDENDUM.md before executing.
THEORY.md gives the source mapping, exact Schur/rank-one response, residual and
solution JVP, stable event drive and propagated finite-opacity bounds.
provenance/RECOVERY_SCOPE.md records the observed scratch loss and exact recovery.
Current rebuilt-code validation is separate from six historical off-grid checks
whose full raw arrays were lost.

## Run a fresh isolated copy

`python reproduce.py --prepare-only` copies this complete unit into a new temporary
directory and verifies immutable source hashes without running numerical cases.
`python reproduce.py` executes the bounded finite study in that isolated copy.
It uses Python, NumPy, SciPy and Matplotlib, threads1 and timeout180s.
The delivered successful raw directory is never overwritten. This reproduction
command is supplied for future use and is not an extra campaign in the current run.

The primary runner refuses to overwrite an existing results/attempt001 directory.
Direct invocation, only in a fresh unit copy:
`python code/run_line02.py`.

This unit has no new local/cosmological IVP or native history execution.
Prior REC119126,REI220129,warm729,THERM02,ANGULAR01,LINE01 and ANGTHERM01 completed
calculations are not dependencies that must be rerun.

## Meaning of the result

A rank-one source response and an event energy ledger do not close a new history,
radiation spectrum, thermal equation or Einstein system. Native departure conventions
are preserved; the separate LINE01 Planck/stimulated model is not silently added.
Physical/REC U5 HOLD, CLOSED_HOLD_NOT_RESET,global convergence NOT_RUN,
production NOT_APPROVED and REI_activation=false remain.
See REPORT_KO.md,GLOBAL_DAG.json and HANDOFF_KO.md for final admission and next work.

