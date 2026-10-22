# Sandbox execution and reproducibility

Run from this unit directory with Python 3.12.14 and the package versions in
`requirements.txt`. All numerical source files are included in `vendor/`.
The execution entry point sets each numerical thread count to one before
importing NumPy/SciPy. No remote runtime or donor campaign is dispatched.

```bash
python code/run.py --preflight
python code/run.py --run
python code/run.py --plot
```

The first command is a no-ODE runner contract check. Its matching retained
receipt is reused by `--run`; adapter checks are not automatically repeated.
`--run` admits only the frozen eight case IDs. It reuses already completed
cases only when source/config and every recorded artifact match exactly.
Preserved failures, partial attempts, or identity changes stop execution.
`--plot` reads completed raw arrays. No arguments print help without running.

Do not rerun completed donor cohorts. The two exact THERM01 comparison
trajectories are retained under `baseline/`. The independent PR122 proposed
restart cohort is outside this unit.

The resource ceilings are cooperative: 180 s per case including diagnostics,
1,200 s cumulative science including failed attempts. A successful solver
return preserves actual accepted BDF nodes, separately from 193 evaluation
nodes. If an exception is thrown inside solve_ivp before it returns, the
last RHS trial and exception are preserved; accepted-step data are then
unavailable through that API. Source, solver and raw-state scopes are recorded
without promoting them to a continuum/global convergence claim.
