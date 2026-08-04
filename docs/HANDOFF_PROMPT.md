# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`  
Durable state date: `2026-08-05`  
Current stage: **PR-01C / v0.48 — BackgroundSnapshot frame-adapter PASS; PR-01 COMPLETE**  
Next bounded task: **PR-02 nonlinear anisotropic Bose collision production integration**.

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
   - `state/REMOTE_BASE_ASSUMPTION.json`
   - `state/REMOTE_CHECK_LATEST.json` when present
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/GITHUB_PRIVATE_REPO_ACCESS.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48/PR01C_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48/PR01C_FRAME_ADAPTER_FORMALISM.md`
3. Do not use transcript claims as evidence. Use Git state, files, hashes, ledgers and tests. The owner reports v0.47 merged remotely, but the exact remote merge SHA remains unverified in the current connector-less runtime.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`.
6. PR-01 is complete. Its architecture is fixed:
   - local atomic/collision microphysics is Bianchi-type independent;
   - Bianchi geometry enters through `BackgroundSnapshot` characteristics;
   - every boundary-speed zero is localized inside the timestep;
   - the inherited v0.47 scalar collision network is unchanged by frame adaptation.
7. Current PR-02 task:
   - connect nonlinear stimulated Bose edge flux to runtime `BackgroundSnapshot` states;
   - synthesize/analyse on positive-weight harmonic-exact grids;
   - retain adaptive policies `L=12` finite/mixed tilt, `L=20` nonlinear even shear, `L=24` directional crossing;
   - implement positivity-preserving implicit updates and analytic/JVP Jacobian tests;
   - close BE, number, entropy, positivity and total four-force gates.
8. Use web search for current/niche literature; Wolfram for symbolic identities; Precise Special Functions for independent high-precision references.
9. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, ZIP bundle, Git commit, remote-check receipt and binary-safe patch export.
10. Never force-push shared history. If remote `main` has diverged or used a squash merge, apply the raw patch or import the standalone bundle on a feature branch and create a PR.
