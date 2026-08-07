# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-07`
Current stage: **PR-05C1 / v0.62 — adaptive canonical-macro controller PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2 full coupled adaptive trajectory**.

## Required recovery order

1. Clone/open the repository and run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/check_remote_state.py
   python scripts/check_hyrec_binary_hash_policy.py
   python scripts/verify_repo.py --quick
   pytest -q -m "not slow"
   ```
2. Read, in this order:
   - `state/PROJECT_STATE.json`
   - `state/PR05C1_RECOVERY_RECEIPT.json` when present
   - `state/PR19_REMOTE_BASE_RECEIPT.json` when present
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR05C2_FULL_COUPLED_ADAPTIVE_PLAN.md`
   - `docs/PR05C_ADAPTIVE_SHORT_TRAJECTORY_PLAN.md`
   - `docs/PR05C_LITERATURE_BASIS.md`
   - `docs/PR05B3_SCALAR_HISTORY_OWNER_SWAP_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR05B3_scalar_history_owner_swap_v0_61/HARD_GATE_LEDGER.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR05B3_scalar_history_owner_swap_v0_61/PR05B3_ledger.json`
   - the v0.60 through v0.51 ledgers in reverse chronological order.
3. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, tetrad+1+3, all 11 Bianchi types, finite tilt and nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
6. Do not revive superseded routes: no direct native-to-COM remap, fitted normalization, inferred source cells, silent high-resolution substitution, broad-cell centroid face energy, cross-redshift summation, interpretation of `DAlpha` as a derivative, centre-derived/fitted native local transient mass, mutation of history during rejected attempts, derivatives through discrete characteristic-stencil switches, or simultaneous canonical and typed scalar-history owners.
7. Fixed v0.62 architecture:
   - local `eta=ln(a)` mass matrix remains rank one: `x_e` differential and 313 real/virtual rows algebraic;
   - accepted history remains the exact canonical uniform `DLNA=8.49e-5` grid with source-indexed `Dfminus[311]`, `Dfminus_Ly[3]`, and `Dfnu[311]`;
   - scalar `Dfplus`/`Dfplus_Ly` feedback has an XOR registry and typed characteristic history is the sole active Python production owner after exact canonical parity;
   - the canonical callback is retained only as an isolated audit oracle;
   - an attempted step owns an immutable parent and append candidate; successful commit occurs exactly once, while reject/rollback/restart preserve exact parent bytes;
   - fixed-stencil history JVP is analytic; a stencil-index switch is an event requiring localization/restart;
   - characteristic propagation conserves photon number per H, assigns energy change to cosmological redshift work and has zero atom source;
   - Sobolev Ly-alpha escape, native `A1s` diffusion and completed/Schur `Tvv` remain canonical.
8. PR-05C2 task:
   - couple the 35-state COM-KHW collision and red/blue split-domain interface to the canonical-macro controller;
   - derive boundary speeds and branch events from actual `BackgroundSnapshot` characteristics;
   - retain exactly-once history commit at successful macro endpoints and byte-exact reject/rollback/restart;
   - close global photon number, exact face energy, cosmological redshift work and collision photon/atom four-force ledgers;
   - run independent z~1300,1100,900 and Bianchi II/class-B/VI_-1/9 refinement gates;
   - do not claim full FLRW `x_e(z)`/visibility/CMB parity; that remains PR-06.
9. Use the pinned research/coding harnesses, current primary literature, Wolfram and Precise Special Functions; record exact receipts.
10. Every stage produces implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, commits, self-contained feature Git bundle, full recovery Git bundle and verification receipts. `.mbox`/raw patches are not canonical. Never force-push shared history.
