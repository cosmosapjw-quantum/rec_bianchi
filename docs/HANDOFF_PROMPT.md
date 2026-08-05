# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-05`
Current stage: **PR-02 / v0.49 — nonlinear anisotropic Bose production integration PASS; PR-01 and PR-02 COMPLETE**
Next bounded task: **PR-03 full scalar COM–KHW amplitude**.

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
   - `archive/expanded/Full_Bianchi_HyRec_PR02_nonlinear_bose_runtime_v0_49/PR02_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR02_nonlinear_bose_runtime_v0_49/PR02_NONLINEAR_BOSE_RUNTIME_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48/PR01C_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48/PR01C_FRAME_ADAPTER_FORMALISM.md`
3. Do not use transcript claims as evidence. Use Git state, files, hashes, ledgers and tests. The owner reports v0.47 merged remotely, but the exact remote merge SHA remains unverified in this connector-less/network-isolated runtime.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`.
6. PR-01 and PR-02 are complete. Their architecture is fixed:
   - local scalar atomic/collision microphysics is Bianchi-type independent;
   - Bianchi geometry enters through `BackgroundSnapshot` characteristics;
   - every boundary-speed zero is localized inside the timestep;
   - adaptive angular policies remain `L=12` finite/mixed tilt, `L=20` nonlinear even shear, `L=24` directional crossing;
   - the nonlinear runtime uses the activity-reference-subtracted v0.47 action, exact JVP, and a log-occupation backward-Euler update;
   - photon and atom four-force contributions are opposite parts of the same event and close in hydrogen and normal frames.
7. Current PR-03 task:
   - replace the provisional unresolved scalar `2p` pole+crossed amplitude with the complete scalar bound-plus-continuum COM–KHW construction;
   - include seagull and interference terms with explicit gauge, reciprocity, normalization, ultraviolet and infrared audits;
   - regenerate pair-conductance moments without changing the PR-01 frame adapter or PR-02 nonlinear runtime API;
   - rerun BE, number, entropy/free-energy, positivity, exact-JVP, branch-event and total four-force regressions;
   - retain a clearly separated provisional/reference lane until complete-amplitude parity is demonstrated.
8. Use web search for current/niche literature; Wolfram for symbolic identities; Precise Special Functions for independent high-precision references when those tools are exposed. Record any unavailable connector and use an explicit independent fallback rather than claiming it ran.
9. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, ZIP bundle, Git commit, remote-check receipt and binary-safe patch export.
10. Never force-push shared history. If remote `main` has diverged or used a squash merge, fetch it, apply the raw patch or import the standalone bundle on a feature branch, and create a PR.
