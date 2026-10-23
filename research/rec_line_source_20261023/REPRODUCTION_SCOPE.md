# Sandbox use and completed-evidence preservation

This unit is self-contained under its research directory: original source bytes,
one actual saved CSV, donor angular kernel, native source cards, new Python code,
raw attempt/continuation evidence, independent review and PNG/PDF/CSV are included.
No remote runtime, compiler, data download, credentials or native HyRec binary is
required for the local operator.

Observed execution environment: Python3.12.14, NumPy2.3.5, SciPy1.17.0,
mpmath1.4.1, with Matplotlib for figures. These are recorded installed versions,
not a claim about public package-release chronology or a requirement to install
another version in this sandbox. Thread caps were OPENBLAS_NUM_THREADS=1 and
OMP_NUM_THREADS=1; the production command had a180s upper limit.

## Entry points

`code/line_source.py` provides immutable source cards, validated `LineState`,
`native_snapshot_state`, `exchange_source`, the exact donor-class loader,
`solve_log_flow`, and `thick_local_step`. A new source caller must supply its own
physical population/background provenance and respect the detached owner guard.
Finite source evaluation and analytic thick population updating are separate APIs.
The canonical native population/feedback/diffusion runtime is not changed.

`code/run_line01.py` documents the original finite production path. The patched
current core no longer has the original bracket defect. Exact code that produced
the original failed attempt is preserved under evidence/attempt001_code.
`code/resume_line01.py` documents the targeted continuation and reads the original
successful raw prefix. Neither script overwrites its evidence directory.

**Do not run these completed campaigns merely to resume this thread.** Read saved
JSONL/CSV/manifests. If a future user explicitly requests fresh reproduction, use
a separate new output location and count it separately; do not erase the current
attempts or relabel new rows as historical originals. The frozen selected-input
acceptance is not a proof of numerical behavior over every finite floating input.

## Numerical guarantees and limits

The thick map is exact for the declared held-input model. Its root is computed in
binary64 and was checked with an independent90-digit W0 expression. Whole-path
finite-opacity bounds are analytic model bounds; floating evaluation is not
directed-rounding interval arithmetic. A one-ULP outward root bracket handles the
observed small-departure endpoint coalescence. More extreme numerical conditioning
is rejected or remains outside the finite tested domain; it is not silently certified.

Source data precision, coincident-line/fine-structure approximation, Sobolev
quasi-stationarity, redistribution and canonical owner replacement remain separate
physical questions. The next selected obligation is the exclusive native
source/residual/JVP handoff in GLOBAL_DAG, not another completed-grid run.
