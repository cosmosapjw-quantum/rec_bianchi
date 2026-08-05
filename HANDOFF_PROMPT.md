# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-04B2A / v0.53 — source-identical physical native edge-flux PASS; PR-04 IN PROGRESS**
Next bounded task: **PR-04B2B measure-preserving native-to-17-cell partition and trajectory parity**.

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
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_BASE_ASSUMPTION.json`
   - `state/REMOTE_CHECK_LATEST.json` when present
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR04B2B_PARTITION_AND_TRAJECTORY_PLAN.md`
   - `docs/GITHUB_PRIVATE_REPO_ACCESS.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53/PR04B2A_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53/PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53/COM_KHW_NATIVE_OVERLAP_AUDIT.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52/PR04B1_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51/PR04A_ledger.json`
3. Do not use transcript claims as evidence. Use Git state, canonical bytes, files, hashes, ledgers and tests. The owner performs remote fetch/push/PR locally; do not claim remote synchronization without a durable live-remote receipt.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; ordinary frequency `nu` in Hz; `y=ln nu`; `Delta nu=nu_target-nu_source`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Canonical provenance is fixed: `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, is the owner-attested unique official-site October-2012 archive. Internal May/October metadata differences are intrinsic release metadata and are not an uncertainty gate.
6. Do not revive superseded routes. In particular:
   - do not identify `x_b=x_1s f_nu_b`, raw `Aup/Adn`, or completed `Tvv` with literal physical photon cells;
   - do not infer finite-volume cells from centre inclusion alone;
   - do not ratio-fit v0.51 event mass to v0.53 net trajectory edge flux;
   - do not silently replace production `NVIRT=311` with the 1493-row high-resolution source table.
7. PR-04B2A is fixed:
   - guard-off binary/history and guard-on public history are source-identical;
   - one complete internal FULL-mode snapshot near `z=1100` is byte-locked;
   - `N_y=8 pi nu^3 Delta f/(c^3 n_H)` and `x_1s Gamma(f_eq-fbar)=H A(fminus-fplus)` close without a free scale;
   - canonical source, independent dense solve, and structured-Schur solve give the same physical edge action and spectral source moments through order four;
   - analytic JVP, implicit positivity, same-event energy, exact symbolic, and 100-digit gates pass;
   - direct v0.51 COM–KHW/native parity remains `OPEN_FAIL_CLOSED` because no common source/target cell partition has been established;
   - the initial `<1e-12` nearest-grid/public-output interpolation diagnostic was not met and is explicitly non-load-bearing; do not rewrite it as a pass.
8. Current PR-04B2B task:
   - audit the canonical 311-row production and 1493-row high-resolution two-photon tables as separate immutable lanes;
   - reconstruct source-defined frequency-cell boundaries and production/reference restriction maps;
   - determine rank, uniqueness, and positivity of a conservative native-to-17-cell moment-preserving projection;
   - compare source-conditioned actions at predeclared FLRW snapshots near `z=1300,1100,900` without a free normalization;
   - publish a proof/no-go result if a unique positive map is not identifiable;
   - keep PR-04 open unless normalization, conditional jump moments, conservation and trajectory parity close on one common measure.
9. Validate and actively use the pinned coding/research harnesses. Use web search for current or niche literature. Use Wolfram and Precise Special Functions when exposed; otherwise record `UNAVAILABLE_IN_RUNTIME` and use explicit independent symbolic/high-precision/numerical fallbacks.
10. Every bounded stage must produce implementation, tests, formalism, evidence ledger, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, local remote-check receipt, full bundle and binary-safe patches. Never force-push shared history.
