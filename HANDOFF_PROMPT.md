Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-09`
Current local stage: **PR-05C2C1B2B1B / v0.71 — physical acceptance gate and residual/JVP connection PASS**.
Next bounded task: **PR-05C2C1B2B1C safeguarded matrix-free continuation on one z~1100 Bianchi-II accepted parent**.

## Required recovery order

1. Run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/check_remote_state.py
   python scripts/check_hyrec_binary_hash_policy.py
   python scripts/check_commit_range_whitespace.py
   if test -f scripts/check_imports.py; then PYTHONPATH=src python scripts/check_imports.py; fi
   python scripts/verify_repo.py --quick
   pytest -q -m "not slow"
   ```
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C1B2B1B_RECOVERY_RECEIPT.json`,
   `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`,
   `docs/PR05C2C1B2B1B_PHYSICAL_ACCEPTANCE_GATE_FORMALISM.md`,
   `docs/PR05C2C1B2B1B_RESEARCH_REPORT.md`, and
   `docs/PR05C2C1B2B1C_MATRIX_FREE_CONTINUATION_PLAN.md`.
3. Use Git state, hashes, ledgers, tests, canonical bytes, and the v0.71 plot;
   transcript claims are not evidence.
4. Preserve `(-,+,+,+)`, ordinary Hz, explicit `c,h,k_B`, homogeneous
   tetrad+1+3 backgrounds, finite tilt, nonlinear large shear, and all-11
   compatibility.
5. Do not revive the v0.64 recorded macro endpoints or the v0.70 generic
   acceptance metric with `max(|state|,1)`.  Both are superseded.
6. Macro acceptance requires strict positivity plus both the physical gross
   backward-error and independent photon-number gates below `1e-11`.
7. Use the analytic shifted `LinearOperator`; dense 910x910 assembly is audit
   only.  Start with the existing diagonal/AP baseline and explicit
   left-nullspace-compatible RHS projection.
8. Do not begin the Rust backend or 9x4 macro expansion before one z~1100
   Bianchi-II physical macro converges with restart and conservation evidence.
9. Canonical delivery remains feature/full Git bundles. Never force-push shared
   history.
