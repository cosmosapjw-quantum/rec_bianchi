Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-08`
Current stage: **PR-05C2C1B2A / v0.68 — canonical two-photon/Raman source adapter PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2C1B2B measured preconditioner and multi-macro closure**.

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
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C1B2A_RECOVERY_RECEIPT.json`,
   `state/REMOTE_CHECK_LATEST.json`, `state/SUPERSESSION_LEDGER.json`,
   `docs/CURRENT_STATE.md`,
   `docs/PR05C2C1B2A_TWO_PHOTON_RAMAN_SOURCE_FORMALISM.md`,
   `docs/PR05C2C1B2A_RESEARCH_REPORT.md`,
   `docs/PR05C2C1B2B_PRECONDITIONER_MULTI_MACRO_PLAN.md`, and the v0.68
   artifact ledgers/verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims
   are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`,
   homogeneous background, tetrad+1+3, all 11 Bianchi types, finite tilt and
   nonlinear large shear.
5. Keep source-identical integrated-bin/matrix coefficients separate from the
   positive angle-resolved physical paired-action contract.  Do not relabel the
   latter as an explicitly stored original-HyRec decomposition.
6. Do not introduce a global normalization, infer hidden native cells, perform
   instantaneous scalar-to-angular inversion, use broad-cell centroid energy at
   a face, or differentiate through topology/frequency-speed/limiter events.
7. PR-05C2C1B2B must couple the source to exact characteristics, compare
   preconditioners on residual/iterations/wall/RSS, and close at least four
   canonical macro intervals in all nine locked lanes.
8. PR-06 remains full FLRW history/visibility parity.  Canonical delivery is a
   self-contained cumulative feature Git bundle plus full recovery bundle.
   Never force-push shared history.
