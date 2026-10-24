# Isolated mpmath1.3.0 environment

The exact official wheel is retained under `environment/wheels/`. Its size is536198B and SHA256 is `a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c`. Root supplied the downloaded wheel after the original normal-sandbox attempts failed. The transfer receipt is `OFFICIAL_WHEEL_TRANSFER.json`; installation and metadata evidence are separate.

From this unit directory, restoring an absent isolated dependency directory requires no network:

```bash
python -m pip install --no-index --no-deps --no-compile --disable-pip-version-check --target environment/deps environment/wheels/mpmath-1.3.0-py3-none-any.whl
```

The dependency is selected explicitly using the recorded absolute PYTHONPATH. After root execution authorization and checkpoint backup:

```bash
env PYTHONPATH=/workspace/scratch/e3bcbaac138c/rec_history_next_20261024/research/rec_history_thermo_20261024/environment/deps PYTHONDONTWRITEBYTECODE=1 python code/run_bounded.py primary --authorization evidence/execution/RUN_READY.json
```

The later saved-data figure command uses the same environment:

```bash
env PYTHONPATH=/workspace/scratch/e3bcbaac138c/rec_history_next_20261024/research/rec_history_thermo_20261024/environment/deps PYTHONDONTWRITEBYTECODE=1 python code/run_bounded.py figures --authorization evidence/execution/FIGURES_READY.json
```

No numerical import, source evaluation or probe was performed during setup. Version1.3.0 and the isolated module origin were confirmed through distribution metadata and module-spec lookup only. The original23-file code/input snapshot remains unchanged; environment artifacts are separately identified in `EXECUTION_ENVIRONMENT.json`. A root RUN_READY receipt remains required before either scientific execution command.
