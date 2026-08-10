Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-10`
Current local stage: **PR-05C2C1B2B1E1A / v0.74 — source-conditioned roundoff-limited single-COM-macro root PASS**.
Next bounded task: **PR-05C2C1B2B1E1B dynamic atomic/native/history macro at z~1100 Bianchi II**.

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
   - `state/PR05C2C1B2B1E1A_RECOVERY_RECEIPT.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/PR05C2C1B2B1E1A_SINGLE_COM_MACRO_FORMALISM.md`
   - `docs/PR05C2C1B2B1E1A_RESEARCH_REPORT.md`
   - `docs/PR05C2C1B2B1E1B_DYNAMIC_ATOMIC_MACRO_PLAN.md`
   - the v0.74 artifact ledger, numerical metrics and compact verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous tetrad+1+3 backgrounds, finite tilt, nonlinear large shear and all-11 compatibility.
5. Do not revive the q=1 operator fixture, cached v0.64 endpoints, direct native-to-COM remap, fitted normalization or an absolute-unit-floor convergence metric.
6. The v0.74 root is only the COM nonlinear Bose collision plus conservative frequency-transport subblock.  Native boundaries are held; atomic one-/two-photon/Raman populations and accepted history are not advanced.
7. Keep the gross-event backward-error, explicit roundoff-bound, photon-number, gross-energy, positivity, entropy/four-force and pair-loop parity gates together.  The cancellation-amplified net/state and net-energy diagnostics remain public but are not sole hard gates.
8. Couple trial-dependent one-/two-photon/Raman source rates, real/virtual atomic solve, typed original-HyRec history and dynamic native boundary to the exact v0.73 parent and v0.74 COM solver path.
9. Internal nonlinear/pseudo-time iterations may create append candidates but may not mutate accepted history.  Commit exactly one history slice only after every physical gate passes.
10. Use `BianchiReviewBianchiIIProvider` only on the validated expanding orthogonal Bianchi-II lane.  Localize any face-speed, limiter, topology or branch event before the endpoint solve.  Unvalidated family/tilt branches fail closed.
11. Macro acceptance requires strict positivity, gross residual/number/gross-energy below `1e-11`, analytic JVP below `1e-8`, exact source ownership and photon--atom four-force, rollback/restart byte identity and accepted-history count exactly `+1`.
12. Preconditioner and Rust selection remain deferred until this exact full physical residual path converges.  Canonical delivery is a self-contained feature Git bundle plus full recovery bundle; never force-push shared history.
