Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-08`
Current stage: **PR-05C2C0 / v0.65 — scalar mathematical and physical theory contract PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2C1 direct thermodynamic compiler and characteristic angular solver**.

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
2. Read `state/PROJECT_STATE.json`, `state/PR05C2C0_RECOVERY_RECEIPT.json`,
   `state/PR23_REMOTE_BASE_RECEIPT.json`, `state/REMOTE_CHECK_LATEST.json`,
   `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`,
   `docs/PR05C2C0_THEORY_CLOSURE_FORMALISM.md`,
   `docs/PR05C2C0_THEORY_COMPLETION_REPORT.md`,
   `docs/PR05C2C1_DIRECT_COMPILER_CHARACTERISTIC_SOLVER_PLAN.md`, and the v0.65
   artifact ledgers/verifier.
3. Use Git state, canonical bytes, hashes, ledgers and tests; transcript claims
   are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`,
   homogeneous background, tetrad+1+3, all 11 Bianchi types, finite tilt and
   nonlinear large shear.
5. The v0.65 theory closure is scalar and unpolarized.  Its explicit extension
   axiom is local hydrogen-frame isotropy of the primitive atomic source and
   opacity.  Do not extend the claim to atomic alignment, polarization, fine
   structure or Raman production.
6. Do not revive instantaneous scalar-to-angular inversion, unconstrained
   harmonic interpolation, fitted normalization, centre-inferred native cells,
   broad-cell centroid face energy, or a preconditioner that ignores the Bose
   entropy metric and conserved activity nullspace.
7. PR-05C2C1 must implement the theorem contract: direct nonnegative reciprocal
   source-temperature event kernels, fixed-topology log interpolation, exact
   characteristic angular evolution, exact native face traces, conservative
   positive COM traces and a measured entropy/nullspace preconditioner.
8. Withheld-node, four-or-more-macro, rollback/restart and FLRW-reduction gates
   are mandatory before PR-06.  No direct compiler or multi-macro completion is
   inherited from prose.
9. Canonical delivery is a self-contained feature Git bundle plus full recovery
   bundle.  Never force-push shared history.
