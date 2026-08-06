# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-04C1B/C2 / v0.56 — exact far-boundary deposition and positive coupled interface operator PASS; PR-04 IN PROGRESS**
Next bounded task: **PR-04C3 componentwise common-ledger closure**.

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
   - `state/PR04C1B_C2_RECOVERY_RECEIPT.json` when present
   - `state/PR14_REMOTE_BASE_RECEIPT.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json` when present
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR04C3_COMMON_LEDGER_PLAN.md`
   - `docs/PR04C1B_C2_COUPLED_INTERFACE_PLAN.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C1B_C2_coupled_interface_v0_56/PR04C1B_C2_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C1B_C2_coupled_interface_v0_56/PR04C1B_C2_COUPLED_INTERFACE_FORMALISM.md`
   - the v0.55 through v0.51 ledgers in reverse chronological order.
3. Do not use transcript claims as evidence. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts. Never claim exact remote integration merely because the author tree is valid.
4. Preserve metric `(-,+,+,+)`; ordinary frequency in Hz; explicit `c,h,k_B`; homogeneous scalar background; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`. Internal May/October metadata differences are intrinsic to the official release.
6. Do not revive superseded routes: no direct native-to-COM state remap, no centre-inferred source cells, no fitted normalization, no silent high-resolution substitution, and no broad-cell centroid substituted for exact face energy.
7. Fixed v0.56 architecture:
   - original HyRec and COM–KHW retain separate representation-local states;
   - only `FR00` index 29 and `FB02` index 34 own the interface deposition;
   - `Delta f=sigma n_H Delta t Phi_N/g_cell` with normalized angular weights;
   - exact face energy is authoritative; the cell-centroid mismatch remains an unresolved representation correction;
   - `f=exp(u)>0`, packet multipliers are log-positive, and the analytic block JVP is production;
   - a pure computational crossing has zero atomic source;
   - all in-step boundary-speed zeros are localized;
   - after strict Newton stagnation, convergence requires both gross backward error and independent number closure below `1e-11`; the net dilute residual floor near `1.7e-10` is diagnostic, not a strict pass.
8. PR-04C3 task:
   - build one typed common-ledger schema indexed separately by z~1300,1100,900;
   - forbid summing snapshots so that opposite errors cancel;
   - lock packet, network, background, adapter, restart and source hashes;
   - re-evaluate native primitive/dense/Schur and COM collision/interface actions through shared conserved flux variables only;
   - close number, exact face energy, zero interface atom source, positivity, JVP, entropy, restart and branch gates componentwise;
   - label `q_activity=1` as an operator-verification state, not a reconstructed physical trajectory;
   - issue operator-contract closure or a bounded no-go; never fabricate direct trajectory parity.
9. Validate and actively use the pinned research/coding harnesses. Use current primary literature, Wolfram and Precise Special Functions when available and record exact receipts.
10. Every bounded stage must produce implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, a self-contained feature Git bundle, a full recovery Git bundle and verification receipts. `.mbox` and raw binary diffs are no longer canonical delivery formats. Never force-push shared history.
