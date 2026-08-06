# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-05B1 / v0.59 — source-identifiable rank-one local DAE PASS and finite native local time-measure PASS_BOUNDED_NO_GO; PR-05 IN PROGRESS**
Next bounded task: **PR-05B2 source-identical causal characteristic-history block**.

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
   - `state/PR05B1_RECOVERY_RECEIPT.json` when present
   - `state/PR17_REMOTE_BASE_RECEIPT.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR05B2_CAUSAL_HISTORY_BLOCK_PLAN.md`
   - `docs/PR05B1_SOURCE_IDENTIFIABLE_DAE_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR05B1_source_identifiable_DAE_native_time_measure_no_go_v0_59/HARD_GATE_LEDGER.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR05B1_source_identifiable_DAE_native_time_measure_no_go_v0_59/PR05B1_ledger.json`
   - the v0.58 through v0.51 ledgers in reverse chronological order.
3. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, tetrad+1+3, all 11 Bianchi types, finite tilt and nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
6. Do not revive superseded routes: no direct native-to-COM remap, fitted normalization, inferred source cells, silent high-resolution substitution, broad-cell centroid face energy, cross-redshift summation, interpretation of `DAlpha` as a derivative, or centre-derived/fitted native local transient mass.
7. Fixed v0.59 architecture:
   - the local eta=ln(a) state has one differential row (`x_e`) and 313 algebraic real/virtual rows;
   - `Dfminus_hist`, `Dfminus_Ly_hist`, and `Dfnu_hist` are accepted-step causal memory outside the local mass matrix;
   - the canonical archive does not identify finite virtual support widths, cell edges or spike shape;
   - two admissible finite supports give masses in ratio two and the same zero-width algebraic limit, so no finite local native-radiation mass is promoted;
   - all compressed terms remain owned and active until a complete residual/JVP/conservation/restart replacement exists;
   - q_activity=1 remains operator verification only.
8. PR-05B2 task:
   - implement typed accepted history, transaction-safe append/rollback and exact restart;
   - reproduce every `hydrogen.c::fplus_from_fminus` characteristic query and two-neighbour interpolation;
   - reject future endpoints, non-monotone grids and discrete stencil switches that are not event-localized;
   - implement analytic history JVP and source C/Python parity at z~1300,1100,900;
   - couple history input to the 313-row algebraic solve and differential electron row;
   - complete no compressed-term owner swap unless the replacement residual, JVP, number/energy ledger, rollback and source parity close together.
9. Use the pinned research/coding harnesses, current primary literature, Wolfram and Precise Special Functions; record exact receipts.
10. Every stage produces implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, commits, self-contained feature Git bundle, full recovery Git bundle and verification receipts. `.mbox`/raw patches are not canonical. Never force-push shared history.
