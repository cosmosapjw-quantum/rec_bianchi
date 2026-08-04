# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`  
Durable state date: `2026-08-04`  
Current stage: **PR-01B1-B3B3B1 / v0.47 — core-to-boundary scalar release PASS, PR-01C open**  
Next bounded task: **PR-01C BackgroundSnapshot frame-adapter closure**.

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
   - `archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3B1_far_scalar_release_v0_47/PR01B1B3B3B1_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3B1_far_scalar_release_v0_47/FAR_SCALAR_RELEASE_FORMALISM.md`
3. Do not use transcript claims as evidence. Use only Git state, files, hashes, ledgers and tests.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`.
6. Current scientific task:
   - load representative primitive-background snapshots for Bianchi II, class B and exceptional `VI_-1/9`;
   - map normal-frame ray characteristics and finite hydrogen tilt to hydrogen-frame frequency/direction characteristics;
   - localize every red/blue boundary-speed zero inside a timestep;
   - couple the v0.47 35-state scalar collision operator without making microphysics Bianchi-type dependent;
   - close number, branch, positivity and same-event four-force gates;
   - publish the PR-01 closure ledger.
7. The v0.47 nonlinear angular policies are `L=12` finite/mixed tilt, `L=20` nonlinear even shear and `L=24` directional crossing. The nonlinear `L=12` grid is the positive-weight 302-point rule, not the superseded 230-point rule.
8. Use web search for current/niche literature; Wolfram for symbolic identities; Precise Special Functions for independent high-precision references.
9. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, ZIP bundle, Git commit, remote-check receipt and binary-safe patch export.
10. Never force-push shared history. If remote `main` has diverged, apply patches on a feature branch and create a PR.
