Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-10`
Current local stage: **PR-05C2C1B2B1D / v0.72 — accepted-parent provenance firewall and orthogonal Bianchi-II background-provider pilot PASS**.
Next bounded task: **PR-05C2C1B2B1E source-derived accepted-parent reconstruction at z~1100 Bianchi II**.

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
   - `state/PR05C2C1B2B1D_RECOVERY_RECEIPT.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/PR05C2C1B2B1D_PARENT_PROVIDER_FORMALISM.md`
   - `docs/PR05C2C1B2B1D_RESEARCH_REPORT.md`
   - `docs/PR05C2C1B2B1E_SOURCE_DERIVED_PARENT_PLAN.md`
   - the v0.72 artifact ledger and compact verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous tetrad+1+3 backgrounds, finite tilt, nonlinear large shear and all-11 compatibility.
5. Do not revive the operator-verification COM parent, cached v0.64 endpoints, or the absolute-unit-floor convergence metric.  They are superseded.
6. Production macro entry must go through `AcceptedRadiationParent` and requires evidence class `SOURCE_DERIVED_ACCEPTED` plus exact accepted-history index/hash, atomic/background/network/interface hashes and branch id.
7. The v0.72 source-derived object is a schema witness only.  PR-05C2C1B2B1E must construct the physical parent from the preceding accepted atomic/radiation history; it must not relabel the witness as physical evidence.
8. Use `BianchiReviewBianchiIIProvider` only on the validated expanding orthogonal Bianchi-II lane.  Bianchi IX must trigger the D-normalized H-zero event, tilted exceptional `VI_-1/9` and every unvalidated family must fail closed.
9. Macro acceptance requires strict positivity, componentwise source ownership, photon number, exact face energy, photon--atom four-force, rollback/restart byte identity and exactly one canonical history append.
10. Do not begin preconditioner selection, Rust production work or 9x4 macro expansion before one source-derived Bianchi-II parent is reconstructed and accepted.
11. Canonical delivery is a self-contained feature Git bundle plus a full recovery bundle. Never force-push shared history.
