# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-05`
Current stage: **PR-03 / v0.50 — full scalar elastic COM–KHW production amplitude PASS; PR-01 through PR-03 COMPLETE**
Next bounded task: **PR-04 HYREC common-measure moment projection**.

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
   - `archive/expanded/Full_Bianchi_HyRec_PR03_full_scalar_COM_KHW_v0_50/PR03_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR03_full_scalar_COM_KHW_v0_50/PR03_FULL_SCALAR_COM_KHW_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR02_nonlinear_bose_runtime_v0_49/PR02_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48/PR01C_ledger.json`
3. Do not use transcript claims as evidence. Use Git state, files, hashes, ledgers and tests. The owner reports v0.47 merged remotely, but the exact remote merge SHA remains unverified in this connector-less/network-isolated runtime.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; frequencies are ordinary frequencies in Hz unless a source explicitly uses angular frequency; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`.
6. PR-01 through PR-03 are complete. Their architecture is fixed:
   - local scalar atomic/collision microphysics is Bianchi-type independent;
   - Bianchi geometry enters through `BackgroundSnapshot` characteristics;
   - every directional boundary-speed zero is localized inside the timestep;
   - adaptive angular policies remain `L=12` finite/mixed tilt, `L=20` nonlinear even shear, `L=24` directional crossing;
   - the nonlinear runtime uses activity-reference subtraction, exact JVP, and a log-occupation backward-Euler update;
   - photon and atom four-force contributions are opposite parts of the same event and close in hydrogen and normal frames;
   - the production scalar elastic amplitude is the v0.50 bound-plus-continuum COM–KHW lane with seagull, both time orderings and scalar interference;
   - the `provisional_2p` lane is retained only for explicit transition parity, not as the production default.
7. PR-03 scope is bounded. Do not silently enlarge its claim:
   - production window `|x|<=21.25`, below the Lyman limit;
   - scalar elastic `1s -> 1s` only; no Raman production lane;
   - only unresolved `2p` natural width;
   - velocity/length gauge identity proved only in the fixed-nucleus, zero-width audit; finite-recoil production is validated by statewise PT reciprocity;
   - fine structure, J-state interference, polarization and alignment remain excluded.
8. Current PR-04 task:
   - source-lock the exact native HyRec/HyRec-2 implementation and its Ly-alpha transfer measure before writing production code;
   - establish ordinary-frequency versus angular-frequency, bin measure, degeneracy, sign, recoil and unit conventions in a machine-readable input lock;
   - define `Gamma` and `M1`–`M4` as direct common-measure projections of the v0.50 event kernel, with no fitted normalization;
   - compare direct event integration, continuum quadrature and native HyRec discretization;
   - close normalization, detailed balance, recoil-energy, `M2`–`M4`, positivity and analytic/JVP Jacobian gates;
   - preserve the PR-01 frame adapter and PR-02 nonlinear runtime APIs.
9. Use web search for current/niche literature and exact source provenance. Use Wolfram for symbolic identities and Precise Special Functions for independent high-precision references only when those tools are actually exposed. Record unavailable connectors and use explicit independent fallbacks rather than claiming they ran.
10. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, remote-check receipt and binary-safe patch export.
11. Never force-push shared history. If remote `main` has diverged or used a squash merge, fetch it, apply the raw patch or import the standalone bundle on a feature branch, and create a PR.
