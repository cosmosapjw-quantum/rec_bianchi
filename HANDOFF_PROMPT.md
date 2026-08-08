Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-08`
Current local stage: **PR-05C2C1B2B0 / v0.69 — macro-evidence integrity bounded no-go**.
Next bounded task: **PR-05C2C1B2B1 accepted-state pseudo-transient/micro-macro continuation**.

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
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C1B2B0_RECOVERY_RECEIPT.json`,
   `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`,
   `docs/PR05C2C1B2B0_MACRO_EVIDENCE_INTEGRITY_FORMALISM.md`, and
   `docs/PR05C2C1B2B1_PSEUDOTRANSIENT_CONTINUATION_PLAN.md`.
3. Use Git state, hashes, ledgers, tests, and canonical bytes; transcript claims
   and the missing v0.64 worker are not evidence.
4. Preserve `(-,+,+,+)`, ordinary Hz, explicit `c,h,k_B`, homogeneous
   tetrad+1+3 backgrounds, finite tilt, nonlinear large shear, and all-11
   compatibility.
5. Do not reuse or chain v0.64 recorded macro endpoints.  Their artifact bytes
   remain durable, but their nine macro-convergence rows are superseded.
6. Preserve v0.65 theory and v0.66--v0.68 direct-node/source adapters.  Do not
   fit normalization or infer a missing parent.
7. Reconstruct an accepted-state path with pseudo-transient/adaptive microsteps.
   Preconditioners must be compared on the same reconstructed path and selected
   only by original residual plus total wall time and memory.
8. Canonical delivery remains feature/full Git bundles; never force-push shared
   history.
