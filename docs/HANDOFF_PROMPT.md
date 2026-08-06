# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-04C0/C1A / v0.55 — ownership and source-identical split-domain boundary packets PASS; PR-04 IN PROGRESS**
Next bounded task: **PR-04C1B/C2 far-boundary deposition and coupled implicit interface operator**.

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
   - `state/PR04C0C1A_RECOVERY_INVENTORY.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json` when present
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR04C1B_C2_COUPLED_INTERFACE_PLAN.md`
   - `docs/PR04C_SPLIT_DOMAIN_EXCHANGE_PLAN.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/PR04C0C1A_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/PR04C0C1A_SPLIT_DOMAIN_FORMALISM.md`
   - the v0.54, v0.53, v0.52 and v0.51 ledgers in reverse chronological order.
3. Do not use transcript claims as evidence. Use Git state, canonical bytes, hashes, ledgers and tests. The owner performs push/PR locally.
4. Preserve metric `(-,+,+,+)`; ordinary frequency in Hz; explicit `c,h,k_B`; homogeneous background; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`. Internal May/October metadata differences are intrinsic to the official release.
6. Do not revive superseded routes: no direct native-to-COM state remap, no centre-inferred source cells, no fitted normalization, no silent high-resolution substitution.
7. Fixed v0.55 architecture:
   - original HyRec and COM–KHW retain separate representation-local states;
   - the cross-interface object owns only `x=+-21.25` transfer;
   - blue packets are `native_to_com`, red packets are `com_to_native` under FLRW redshift;
   - packet total number and transported photon energy are positive;
   - Planck reference is nonnegative; distortion may be signed;
   - a pure computational crossing has **zero atomic source**; physical recoil remains owned by collision terms;
   - current HyRec history endpoint may be used only after it has been solved and stored; future endpoints are forbidden.
8. Current task:
   - connect packets only to `FB02`/`FR00` far-boundary/Liouville ghost states;
   - construct the coupled implicit residual and analytic block JVP;
   - preserve log-variable positivity and exact number/transported-energy ledgers;
   - localize every boundary-speed zero inside the timestep;
   - run z~1300,1100,900 plus Bianchi II, class-B and `VI_-1/9` gates;
   - do not claim PR-04 complete until PR-04C3 closes the common ledger.
9. Validate and actively use the pinned research/coding harnesses. Use web search, Wolfram and Precise Special Functions when available and record exact receipts.
10. Every bounded stage must produce implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, full bundle and binary-safe patches. Never force-push shared history.
