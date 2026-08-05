# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-05`
Current stage: **PR-04A / v0.51 — HYREC-2 source/convention lock and 17-cell common-measure core PASS; PR-04 IN PROGRESS**
Next bounded task: **PR-04B original-HyRec archive and native primitive common-measure parity**.

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
   - `archive/expanded/Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51/PR04A_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51/PR04_INPUT_LOCK.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51/PR04A_COMMON_MEASURE_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_C3B0_HYREC2_source_lock_v0_26/C3B0_SOURCE_LOCK.md`
   - `archive/expanded/Full_Bianchi_HyRec_C3B1_native_sparse_block_v0_27/C3B1_ledger.json`
3. Do not use transcript claims as evidence. Use Git state, files, hashes, ledgers and tests. The owner performs remote fetch/push/PR locally; this runtime must not claim remote synchronization without a durable remote receipt.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; ordinary frequency `nu` in Hz; `Delta nu=nu_target-nu_source`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`. In particular, do not directly substitute the completed HYREC `Tvv` block or fit a free normalization to match HyRec output.
6. PR-01 through PR-03 are complete. PR-04A is fixed:
   - the accepted v0.50 off-diagonal `C0` pair mass is reproduced exactly;
   - `M1`–`M4` are conditional moments of the same positive COM–KHW event measure;
   - `S^(r)_ji=(-1)^r S^(r)_ij`;
   - `[S^(r)]=m^-3 s^-1 Hz^r`, `[Gamma]=s^-1`, `[M_r]=Hz^r s^-1`;
   - local common-measure microphysics has no Bianchi-type argument;
   - native HYREC-2 `Aup/Adn` arrays remain diagnostic until the virtual-state/escape map is derived.
7. Current PR-04B task:
   - acquire the official October-2012 original-HyRec archive and record exact bytes, SHA-256, file inventory and build receipt;
   - identify the native radiation variable, frequency/bin measure, coefficient dimensions, time derivative, diffusion sign, recoil term, and stimulated factors from source;
   - derive the original native primitive-to-common-measure map with no fitted scale;
   - compare direct v0.51 event moments, native primitive moments and Schur-reduced moments;
   - close normalization, detailed balance, recoil energy, positivity, analytic/JVP Jacobian, and one FLRW snapshot parity gate;
   - keep PR-04 incomplete if the archive or any native normalization identity remains unavailable.
8. Use web search for current/niche literature. Use Wolfram and Precise Special Functions when exposed; otherwise record `UNAVAILABLE_IN_RUNTIME` and use explicit independent SymPy/mpmath/SciPy fallbacks rather than claiming a plugin ran.
9. Every bounded stage must produce implementation, tests, formalism, ledger, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, remote-check receipt and binary-safe patch export.
10. Never force-push shared history. Export an incremental v0.50-to-current patch, a cumulative declared-base patch, and a standalone bundle. The owner will fetch remote `main`, apply on a feature branch, run tests, push, and open the PR locally.
