# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-05B2 / v0.60 — source-identical causal characteristic-history block PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05B3 scalar history ownership swap and coupled accepted-step residual**.

## Required recovery order

1. Clone/open the repository and run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/check_remote_state.py
   python scripts/check_hyrec_binary_hash_policy.py
   python scripts/verify_repo.py --quick
   pytest -q -m "not slow"
   ```
2. Read, in this order:
   - `state/PROJECT_STATE.json`
   - `state/PR05B2_RECOVERY_RECEIPT.json` when present
   - `state/PR18_REMOTE_BASE_RECEIPT.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR05B3_ATOMIC_OWNERSHIP_SWAP_PLAN.md`
   - `docs/PR05B2_CAUSAL_HISTORY_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR05B2_causal_characteristic_history_v0_60/HARD_GATE_LEDGER.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR05B2_causal_characteristic_history_v0_60/PR05B2_ledger.json`
   - the v0.59 through v0.51 ledgers in reverse chronological order.
3. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, tetrad+1+3, all 11 Bianchi types, finite tilt and nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
6. Do not revive superseded routes: no direct native-to-COM remap, fitted normalization, inferred source cells, silent high-resolution substitution, broad-cell centroid face energy, cross-redshift summation, interpretation of `DAlpha` as a derivative, centre-derived/fitted native local transient mass, mutation of history during rejected attempts, or derivatives through discrete characteristic-stencil switches.
7. Fixed v0.60 architecture:
   - local `eta=ln(a)` mass matrix remains rank one: `x_e` differential and 313 real/virtual rows algebraic;
   - accepted history contains source-indexed `Dfminus[311]`, `Dfminus_Ly[3]`, and `Dfnu[311]` with exact canonical `DLNA` and source hashes;
   - exactly 313 source-identical characteristic queries are used per snapshot;
   - a proposed step creates an immutable append candidate; only a successful accepted step may commit it;
   - reject, rollback and binary restart are byte-exact;
   - fixed-stencil history JVP is analytic; a stencil-index switch is an event requiring localization/restart;
   - free characteristic propagation conserves photon number per H, assigns energy change to cosmological redshift work and has zero atom source;
   - the scalar history replacement contract is complete but the owner swap has not occurred;
   - Sobolev Ly-alpha escape, native `A1s` diffusion and completed/Schur `Tvv` remain canonical.
8. PR-05B3 task:
   - introduce a fail-closed XOR owner registry for scalar `Dfplus`/`Dfplus_Ly` feedback;
   - compare canonical-C-derived and typed-history incoming/RHS/solution/electron/outgoing actions before disabling the canonical Python callback;
   - assemble the coupled accepted-step residual and analytic PETSc-style shifted IJacobian;
   - commit history exactly once after a successful step, discard rejected candidates, restore exact bytes after rollback, and restart after discrete stencil/coefficient events;
   - close number, redshift-energy-work, zero characteristic atom source, positivity, JVP, restart, causality and fixed-local-state Bianchi firewalls independently at z~1300,1100,900;
   - leave Sobolev, `A1s` and `Tvv` owners unchanged.
9. Use the pinned research/coding harnesses, current primary literature, Wolfram and Precise Special Functions; record exact receipts.
10. Every stage produces implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, commits, self-contained feature Git bundle, full recovery Git bundle and verification receipts. `.mbox`/raw patches are not canonical. Never force-push shared history.
