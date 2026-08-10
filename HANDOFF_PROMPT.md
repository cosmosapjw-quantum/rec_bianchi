Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-10`
Current local stage: **PR-05C2C1B2B1E0 / v0.73 — accepted scalar-history point-characteristic bootstrap parent PASS**.
Next bounded task: **PR-05C2C1B2B1E1 single dynamic coupled macro at z~1100 Bianchi II**.

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
2. Read, in order:
   - `state/PROJECT_STATE.json`
   - `state/PR05C2C1B2B1E0_RECOVERY_RECEIPT.json` when present
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/PR05C2C1B2B1E0_SOURCE_DERIVED_PARENT_FORMALISM.md`
   - `docs/PR05C2C1B2B1E0_RESEARCH_REPORT.md`
   - `docs/PR05C2C1B2B1E1_SINGLE_MACRO_CONTINUATION_PLAN.md`
   - the v0.73 artifact ledger and compact verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous tetrad+1+3 backgrounds, finite tilt, nonlinear large shear and all-11 compatibility.
5. Do not revive the q=1 operator fixture, cached v0.64 endpoints, direct native-to-COM remap or absolute-unit-floor convergence metric.
6. The v0.73 parent is source-derived from accepted scalar original-HyRec history and uses the explicit isotropic hydrogen-frame initial-data axiom.  It is **not** a coupled macro endpoint and no history append is inherited.
7. Production macro entry must validate the exact v0.73 history/atomic/background/network/interface hashes and branch id.
8. Use `BianchiReviewBianchiIIProvider` only on the validated expanding orthogonal Bianchi-II lane.  All unvalidated family/tilt branches fail closed.
9. Couple one-/two-photon/Raman source, native characteristics, COM collision and interface ledgers on one canonical interval.  Internal pseudo-steps must not mutate accepted history.
10. Macro acceptance requires strict positivity, gross residual and photon number below `1e-11`, exact face energy, photon--atom four-force, JVP below `1e-8`, rollback/restart byte identity and exactly one history append.
11. Preconditioner selection is allowed only on this exact parent/residual path.  Rust remains parity-only until the Python reference converges.
12. Canonical delivery is a self-contained feature Git bundle plus a full recovery bundle. Never force-push shared history.
