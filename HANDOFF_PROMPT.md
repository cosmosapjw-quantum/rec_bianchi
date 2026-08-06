# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-04C3 / v0.57 — componentwise common ledger PASS; PR-04 COMPLETE_OPERATOR_CONTRACT**
Next bounded task: **PR-05A BackgroundSnapshot/RadiationFeedback schema and primitive original-HyRec operator source lock**.

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
   - `state/PR04C3_RECOVERY_RECEIPT.json` when present
   - `state/PR15_REMOTE_BASE_RECEIPT.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json` when present
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR05_PRIMITIVE_TRAJECTORY_INTERFACE_PLAN.md`
   - `docs/PR05_LITERATURE_BASIS.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C3_common_ledger_v0_57/PR04C3_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C3_common_ledger_v0_57/PR04C3_COMMON_LEDGER_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR04C3_common_ledger_v0_57/HARD_GATE_LEDGER.json`
   - the v0.56 through v0.51 ledgers in reverse chronological order.
3. Do not use transcript claims as evidence. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts. Never claim exact remote integration merely because the author tree is valid.
4. Preserve metric `(-,+,+,+)`; ordinary frequency in Hz; explicit `c,h,k_B`; homogeneous scalar background; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`. Internal May/October metadata differences are intrinsic to the official release.
6. Do not revive superseded routes: no direct native-to-COM state remap, no centre-inferred source cells, no fitted normalization, no silent high-resolution substitution, no broad-cell centroid substituted for exact face energy, and no cross-redshift residual summation.
7. Fixed v0.57 architecture:
   - original HyRec and COM–KHW retain separate representation-local states;
   - only `FR00` index 29 and `FB02` index 34 own interface deposition;
   - packet number is deposited as `sigma*n_H*q/g_cell` with normalized angular weights;
   - exact face energy is authoritative and pure representation crossing has zero atomic source;
   - occupations and packet multipliers are log-positive;
   - all in-step boundary-speed zeros are localized;
   - the common ledger contains exactly three ordered lanes and six unique packets with complete provenance;
   - every gate passes componentwise before taking a maximum normalized violation; signed sums/averages are forbidden;
   - `q_activity=1` is an unfitted operator-verification state, not a native-derived trajectory;
   - PR-04 is complete only at this source-conditioned split-domain operator-contract claim level.
8. PR-05A task:
   - freeze typed `BackgroundSnapshot`, `PrimitiveRateSnapshot`, `AtomicRadiationState`, `RadiationFeedback` and `TrajectoryStepLedger` schemas;
   - byte/source-lock `Alpha[2]`, `DAlpha[2]`, `Beta[2]`, `R2p2s`, `A2s`, `A3s3d`, `A4s4d`, with units, degeneracies, detailed balance and derivatives;
   - publish a one-owner removal/replacement matrix for Sobolev escape, native `A1s` diffusion, escape-compressed `Tvv` and scalar `Dfplus` feedback;
   - remove no compressed term until its explicit split-domain replacement is present in the same residual and conservation ledger;
   - assemble a bounded one-step source-conditioned primitive atomic/radiation residual and analytic block JVP at z~1300,1100,900;
   - close Saha/Planck, M-matrix/positivity, number/energy, restart, event and local Bianchi-firewall gates;
   - keep full trajectory integration in later PR-05 stages and FLRW history parity in PR-06.
9. Validate and actively use the pinned research/coding harnesses. Use current primary literature, Wolfram and Precise Special Functions when available and record exact receipts.
10. Every bounded stage must produce implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, Git commits, a self-contained feature Git bundle, a full recovery Git bundle and verification receipts. `.mbox` and raw binary diffs are not canonical delivery formats. Never force-push shared history.
