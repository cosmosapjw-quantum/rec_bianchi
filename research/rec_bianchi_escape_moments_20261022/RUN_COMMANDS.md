# Reproduction and retained-result commands

## Read completed results first
This unit has already completed its single production study. Read
`results/attempt_001/FINAL_DECISION.json` together with the preserved initial
`study_summary.json`; the original FAIL is not overwritten.

```bash
cd research/rec_bianchi_escape_moments_20261022
python -c 'import json; print(json.load(open("results/attempt_001/FINAL_DECISION.json")))'
```

## Original executed study (do not repeat to resume)
The actual launch, environment and source hashes are in
evidence/FIRST_STUDY_LAUNCH.json and results/attempt_001/EXECUTION_REQUEST.json.
It used one thread and an external 240-second hard timeout; the runner also
has a 180-second target and preserves partial rows.
The command was `python code/run_study.py --execute --attempt attempt_001`
under that recorded environment/timeout. Existing attempt directories cannot
be overwritten. This command is provenance, not a next-step instruction.

## Reuse the implementation in a new selected unit
```python
import sys
import numpy as np
sys.path.insert(0, "code")
from escape_moments import angular_moments

S = np.diag([-0.4, -0.2, 0.6])       # sigma/H, symmetric tracefree
moment = angular_moments(100.0, S)   # t = C_S/H, dimensionless
print(moment.method, moment.mean, moment.pstf)
print(moment.analytic_bounds)
```
This illustrative input lies inside the analytic-thick gate. It is not a
new cosmological background solution or a physical radiation stress.
For a genuinely new experiment, bind its own inputs and finite acceptance
before evaluating it. Existing valid data and the completed figures need no
rerender or rerun to continue the next physics stage.

## Reviewer and repair scope
The independent review's spot_audit.py is retained as executed provenance.
Do not rerun it for reassurance. Five saved failed rows were re-adjudicated
with an algebraically equivalent stable validator and unchanged tolerance.
The original raw data and numerical source remain unchanged.

