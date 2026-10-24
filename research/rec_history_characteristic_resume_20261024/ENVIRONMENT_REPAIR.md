# Environment repair — READY_ENV_REPAIRED

The default and runtime Python lacked mpmath; /usr/bin/python3 also lacked it. The first sandboxed pinned install was blocked by network restrictions; its stdout/stderr and measured cost remain preserved. The authorized network escalation installed only mpmath1.3.0 into environment/deps. Import-only smoke passes; versions/origins and separate non-scientific setup costs are in ENVIRONMENT_REPAIR.json and environment/ receipts. No numerical case executed, and failed primary001 remains intact. Adapter/reference/CASE thresholds unchanged.

Proposed command, NOT_RUN and requiring root GO:

```bash
PYTHONPATH=/workspace/scratch/e3bcbaac138c/rec_next_work/research/rec_history_characteristic_resume_20261024/environment/deps python code/run_bounded.py --cpu 15 --wall 44.8 primary002 python code/verify_primary.py --output results/primary002
```

This inherits PYTHONPATH into the single bounded child. Primary00215CPU/44.8wall plus spent primary001 fits the cumulative original16CPU/45wall primary allocation; historical budgets and failed cost are retained.
