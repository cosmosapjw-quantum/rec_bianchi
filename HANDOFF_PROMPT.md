# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-04B2B / v0.54 — native/common partition identifiability PASS_NO_GO; PR-04 IN PROGRESS**
Next bounded task: **PR-04C split-domain conservative exchange contract and multi-snapshot closure**.

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
   - `docs/PR04C_SPLIT_DOMAIN_EXCHANGE_PLAN.md`
   - `docs/GITHUB_PRIVATE_REPO_ACCESS.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B2B_native_common_partition_no_go_v0_54/PR04B2B_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B2B_native_common_partition_no_go_v0_54/PR04B2B_PARTITION_NO_GO_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53/PR04B2A_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52/PR04B1_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51/PR04A_ledger.json`
3. Do not use transcript claims as evidence. Use Git state, canonical bytes, files, hashes, ledgers and tests. The owner performs remote fetch/push/PR locally; do not claim remote synchronization without a durable live-remote receipt.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; ordinary frequency `nu` in Hz; `x=(nu-nu_Lya)/Delta_nu_D`; `y=ln nu`; `Delta nu=nu_target-nu_source`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Canonical provenance is fixed: `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, is the owner-attested unique official-site October-2012 archive. Internal May/October metadata differences are intrinsic release metadata.
6. Do not revive superseded routes. In particular:
   - do not identify `x_b=x_1s f_nu_b`, raw `Aup/Adn`, or completed `Tvv` with literal physical photon cells;
   - do not infer source cells from frequency centres alone;
   - do not ratio-fit v0.51 event mass to v0.53 net trajectory edge flux;
   - do not silently replace production `NVIRT=311` with the 1493-row high-resolution table;
   - do not construct a global positive native-to-17-cell projection: v0.54 proves it cannot preserve native `M0,M2`, and five moments leave target nullity 12;
   - do not choose maximum entropy, optimal transport or another regularizer and relabel it canonical.
7. PR-04B2B is fixed:
   - production/high-resolution tables are byte locked at shapes `(311,5)` and `(1493,5)`;
   - their centre grids have zero exact common production centres and no archive-defined restriction map;
   - the canonical runtime archive has no numerical edge array, dedicated table-generator member or bundled-table write path;
   - only two diffusion centres in each lane lie inside `|x|<=4.25`;
   - any positive 17-cell target has `M2/M0<=18.0625`, whereas the full and diffusion native measures give `1.344707749773356e8` and `2.1808728753005056e4`;
   - exact target moment rank/nullity is `5/12`, with constructive strictly positive non-uniqueness witnesses;
   - multi-snapshot direct parity is blocked rather than fabricated.
8. Current PR-04C task:
   - keep the 35-state COM–KHW collision domain on `x in [-21.25,21.25]` and original-HyRec on its full native support;
   - define red/blue interface variables carrying photon number and photon/atom energy flux, not a global state remap;
   - publish an operator-ownership matrix with exactly one owner for every collision, escape, redshift and cross-interface term;
   - instrument exact nearest-grid FLRW snapshots near `z=1300,1100,900` under source-identical guards;
   - evaluate each interface flux once and apply it with opposite signs;
   - implement positivity-preserving implicit updates and analytic/JVP tests;
   - close number, energy, equilibrium, positivity, branch, primitive/direct/Schur and local Bianchi-firewall gates;
   - keep higher moments representation-local unless an independently source-derived positive packet measure exists.
9. Validate and actively use the pinned coding/research harnesses. Use web search for current or niche literature. Use Wolfram and Precise Special Functions when exposed; otherwise record `UNAVAILABLE_IN_RUNTIME` and use explicit independent symbolic/high-precision/numerical fallbacks.
10. Every bounded stage must produce implementation, tests, formalism, evidence ledger, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, local remote-check receipt, full bundle and binary-safe patches. Never force-push shared history.
