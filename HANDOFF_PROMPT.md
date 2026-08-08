Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-08`
Current stage: **PR-05C2C1B1 / v0.67 — canonical spike/source adapter and full withheld audit PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2C1B2 canonical two-photon/Raman source, measured preconditioner and multi-macro closure**.

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
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C1B1_RECOVERY_RECEIPT.json`,
   `state/PR24_REMOTE_BASE_RECEIPT.json`, `state/REMOTE_CHECK_LATEST.json`,
   `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`,
   `docs/PR05C2C1B1_SOURCE_ADAPTER_WITHHELD_FORMALISM.md`,
   `docs/PR05C2C1B1_RESEARCH_REPORT.md`,
   `docs/PR05C2C1B2_PRECONDITIONER_MULTI_MACRO_PLAN.md`, and the v0.67 artifact
   ledgers/verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims
   are not evidence.  The unsealed v0.66 delivery is superseded by v0.67.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`,
   homogeneous background, tetrad+1+3, all 11 Bianchi types, finite tilt and
   nonlinear large shear.
5. Keep canonical original-HyRec virtual spikes separate from the derived
   positive one-photon paired-rate adapter.  Do not relabel the latter as a
   source-identical coefficient decomposition.
6. Do not revive scalar-to-angular inversion, fitted normalization, inferred
   native cells, broad-cell centroid face energy, or derivatives through
   frequency-speed/topology/limiter events.
7. PR-05C2C1B2 must lock canonical two-photon/Raman source conventions, compare
   preconditioners on residual/iterations/wall/RSS, and close at least four
   canonical macro intervals in all nine locked redshift/background lanes.
8. PR-06 remains the full FLRW `x_e(z)`/visibility parity gate.  Never
   force-push shared history.
