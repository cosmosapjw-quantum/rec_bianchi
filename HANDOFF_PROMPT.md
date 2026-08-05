# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-05`
Current stage: **PR-04B1 / v0.52 — original-HyRec byte/source lock and native proxy-map PASS; PR-04 IN PROGRESS**
Next bounded task: **PR-04B2 physical native-measure and full-trajectory FLRW closure**.

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
   - `archive/expanded/Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52/PR04B1_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52/ORIGINAL_HYREC_SOURCE_LOCK.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52/PR04B1_ORIGINAL_HYREC_NATIVE_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51/PR04A_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_C3B1_native_sparse_block_v0_27/C3B1_ledger.json`
3. Do not use transcript claims as evidence. Use Git state, files, hashes, ledgers and tests. The owner performs remote fetch/push/PR locally; this runtime must not claim remote synchronization without a durable remote receipt.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; ordinary frequency `nu` in Hz in the project adapter; `Delta nu=nu_target-nu_source`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes. In particular, do not identify original-HyRec `Aup/Adn`, `x_b=x_1s f_nu_b`, or a completed `Tvv` block directly with the physical PR-04A finite-volume photon measure, and do not fit a free normalization to force parity.
6. PR-04B1 is fixed:
   - `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip` has SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, size 726954 bytes, 29 safe ZIP entries, and no duplicate/path-traversal/symlink members;
   - independent fresh-download equality with the official server is **not verified**;
   - source-byte-unchanged GNU build and 8001-line baseline run pass;
   - original C and Python diffusion rates agree; original C, dense, and structured-Schur full-system solutions agree;
   - the 81-state native diffusion proxy network and 2p Schur reduction conserve their native proxy measure and satisfy detailed balance;
   - direct physical finite-volume substitution fails its intended firewall and remains forbidden.
7. Current PR-04B2 task:
   - instrument a source-identical original-HyRec run to dump `Dfplus`, `Dfminus`, `xv`, `Dtau`, real/virtual blocks, and local thermodynamic state at a locked hydrogen-recombination snapshot;
   - derive the logarithmic redshift-flux and escape map from the native algebraic proxy to physical photons per H per `d ln nu`, retaining all dimensions and signs;
   - project the v0.51 direct COM–KHW event tensor and native primitive/Schur actions onto one physical measure without a fitted scale;
   - close normalization, detailed balance, recoil-energy, analytic/JVP, positivity, and one full FLRW snapshot parity gate;
   - keep PR-04 open if any physical normalization identity remains unresolved.
8. Use web search for current/niche literature. Use Wolfram and Precise Special Functions when exposed; otherwise record `UNAVAILABLE_IN_RUNTIME` and use explicit independent symbolic/high-precision/numerical fallbacks rather than claiming a plugin ran.
9. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, remote-check receipt and binary-safe patch export.
10. Never force-push shared history. Export an incremental v0.51-to-current patch, a cumulative declared-base patch, and a standalone bundle. The owner will fetch remote `main`, apply on a feature branch, run tests, push, and open the PR locally.
