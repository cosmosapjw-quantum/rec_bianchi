# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`  
Durable state date: `2026-08-04`  
Current stage: **PR-01B1-B3B3B0 / v0.46 — near exterior PASS, far boundary open**  
Next bounded task: **PR-01B1-B3B3B1 far-flux and adaptive scalar release**.

## Required recovery order

1. Clone/open the repository and run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/check_remote_state.py
   python scripts/verify_repo.py --quick
   pytest -q -m "not slow"
   ```
2. Read, in this order:
   - `state/PROJECT_STATE.json`
   - `state/REMOTE_CHECK_LATEST.json` when present
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/REPO_CHECK_PATCH_POLICY.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3B0_exterior_interface_v0_46/PR01B1B3B3B0_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3B0_exterior_interface_v0_46/EXTERIOR_INTERFACE_FORMALISM.md`
3. Do not use transcript claims as evidence. Use only Git state, files, hashes, ledgers and tests.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`.
6. Current scientific task:
   - integrate direct interior-to-far scattering beyond `|x|=10.25`;
   - retain near red/blue exterior cells as dynamic states;
   - apply nonlinear stimulated edge flux on harmonic-exact `L=12/20/24` grids;
   - close BE, number, entropy, positivity, ell-tail and total four-force gates;
   - then run PR-01C using the primitive `BackgroundSnapshot` finite-tilt/large-shear adapter.
7. Use web search for current/niche literature; Wolfram for symbolic identities; Precise Special Functions for independent high-precision references.
8. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, ZIP bundle, Git commit, remote-check receipt and binary-safe patch export.
9. Never force-push shared history. If remote `main` has diverged, apply patches on a feature branch and create a PR.
10. Update `state/PROJECT_STATE.json`, `state/SUPERSESSION_LEDGER.json`, `docs/CURRENT_STATE.md`, and the patch base only after a verified common ancestor is established.
