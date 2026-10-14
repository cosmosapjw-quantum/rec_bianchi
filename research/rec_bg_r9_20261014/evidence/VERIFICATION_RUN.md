# R9 Verification inventory

- `python -m unittest -v test_interval_reference.py`: 17/17, exit0 (raw stderr in `unit_stderr.txt`). A small correction replaced an initial local-coordinate clipping with a typed out-of-cell error; all 16 were re-executed.
- `python check_numeric.py`: 60 rows (6 prescribed cases × 2 grid levels × 5 intervals), mpmath55dps. max dt relative 2.491689611916742e-14; max db relative 2.514924308128385e-14, exit0. This independent oracle treats binary64 supplied inputs as exact dyadics but is not directed interval arithmetic.
- Current cloud Wolfram 15.0.1: log-redshift, direction, Jacobian, Hermite full-cell integration four symbolic residuals exact0; sharp mu derivative 2/sqrt3.
- Local xAct: xTensor 1.3.0 availability explicitly verified. New inline one-shot package shadow error observed; no new xAct zero assertion. Reuse prior actual R7B/R8 exact xAct checks with unchanged definitions only.
- No production solver, no atomic provider run, no current science history regeneration, no native child agent.

- R9 bounded repair: pre-change new test RED exit1 at cross term 1e-5; post-change 17/17 GREEN exit0 and 60/60 numerical reference checks exit0. Original v1 ZIP is retained without overwrite.
