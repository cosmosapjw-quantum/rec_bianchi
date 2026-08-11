Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-11`
Current stage: **PR-05C2C1B2B1E1B0 / v0.75 — dynamic macro ownership overlap PASS_BOUNDED_NO_GO**
Next bounded task: **PR-05C2C1B2B1E1C exterior-native / interior-COM / interface replacement**.

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
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C1B2B1E1B0_RECOVERY_RECEIPT.json`, `state/REMOTE_CHECK_LATEST.json`, `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`, `docs/PR05C2C1B2B1E1B0_DYNAMIC_MACRO_OWNERSHIP_FORMALISM.md`, `docs/PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md`, and the v0.75 artifact ledger.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, finite tilt/large shear architecture and all-11-compatible interfaces.
5. Do not infer native cells, fit a normalization, revive full-native plus COM additive ownership, or treat the passing contract witness as implemented physics.
6. Exact locked support at z~1100: native indices 136..143 lie in the COM domain; diffusion edges (135,136) and (143,144) cross the interfaces.
7. The owner swap is complete only when replacement residual, analytic JVP, number/energy/four-force ledger, restart and primitive/exterior-Schur/interface parity coexist.
8. Do not attempt the dynamic macro, preconditioner selection or Rust optimization before this replacement gate passes.
9. Canonical delivery is a self-contained feature Git bundle plus a full recovery bundle; never force-push shared history.
