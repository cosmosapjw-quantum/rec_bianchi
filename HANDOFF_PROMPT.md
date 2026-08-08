Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-08`
Current stage: **PR-05C2C1A / v0.66 — direct nodal network and characteristic-face solver PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2C1B physical source adapter, full withheld validation and multi-macro closure**.

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
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C1A_RECOVERY_RECEIPT.json`,
   `state/PR24_REMOTE_BASE_RECEIPT.json`, `state/REMOTE_CHECK_LATEST.json`,
   `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`,
   `docs/PR05C2C1A_DIRECT_COMPILER_CHARACTERISTIC_FORMALISM.md`,
   `docs/PR05C2C1B_SOURCE_ADAPTER_MULTI_MACRO_PLAN.md`, and the v0.66 artifact
   ledgers/verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims
   are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`,
   homogeneous background, tetrad+1+3, all 11 Bianchi types, finite tilt and
   nonlinear large shear.
5. The v0.66 direct nodes and characteristic solver are bounded evidence.  Do
   not infer full withheld same-cell convergence, a complete physical HyRec
   emissivity/opacity adapter, a selected scalable preconditioner or a
   multi-macro trajectory.
6. The virtual-spike source adapter must use the canonical source-rounded
   `h c` constant for source parity; CODATA substitution changes `Dtau` by
   about `2.66e-7` and is not source-identical.
7. PR-05C2C1B must source-lock one-/two-photon, Raman and diffusion coefficients,
   validate every pair and same-cell block at withheld/refinement nodes, select
   a preconditioner only by original residual and total wall time, and run at
   least four canonical macro intervals per locked lane.
8. Canonical delivery is a self-contained feature Git bundle plus full recovery
   bundle. Never force-push shared history.
