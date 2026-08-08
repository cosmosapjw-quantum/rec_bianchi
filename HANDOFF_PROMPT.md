Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-08`
Current stage: **PR-05C2B / v0.64 — explicit-closure optimized canonical-macro reference PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2C direct thermodynamic network and native angular evolution**.

## Required recovery order

1. Run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/check_remote_state.py
   python scripts/check_hyrec_binary_hash_policy.py
   python scripts/check_commit_range_whitespace.py
   PYTHONPATH=src python scripts/check_imports.py
   python scripts/verify_repo.py --quick
   pytest -q -m "not slow"
   ```
2. Read `state/PROJECT_STATE.json`, `state/PR05C2B_RECOVERY_RECEIPT.json`,
   `state/REMOTE_CHECK_LATEST.json`, `state/SUPERSESSION_LEDGER.json`,
   `docs/CURRENT_STATE.md`, `docs/PR05C2B_RESEARCH_AND_OPTIMIZATION_REPORT.md`,
   `docs/PR05C2C_DIRECT_NETWORK_NATIVE_ANGULAR_PLAN.md`, and the v0.64 artifact
   ledger/formalism.
3. Use Git state, hashes, ledgers and tests; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`,
   homogeneous background, tetrad+1+3, all 11 Bianchi types, finite tilt and
   nonlinear large shear.
5. Do not relabel isotropic/maximum-entropy lifting or the thermodynamic
   conductance adapter as source-identical.  Do not fit a global normalization.
6. Keep pair-loop collision code as an audit oracle; production action/JVP is
   vectorized and dense assembly is batched.
7. PR-05C2C must directly compile validation network nodes, introduce a sourced
   or explicitly downgraded angular evolution, and show a measured
   preconditioner improvement before selection.
8. Canonical delivery is a feature Git bundle plus full recovery bundle; never
   force-push shared history.
