# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`  
Durable state date: `2026-08-04`  
Current stage: **PR-01B1-B3B3A / v0.45 — PASS, exterior open**  
Next bounded task: **PR-01B1-B3B3B exterior deposition and full scalar release**.

## Required recovery order

1. Clone/open the repository and run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/verify_repo.py --quick
   pytest -q
   ```
2. Read, in this order:
   - `state/PROJECT_STATE.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3A_same_cell_regular_v0_45/PR01B1B3B3A_ledger.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3A_same_cell_regular_v0_45/SAME_CELL_REGULARIZATION_FORMALISM.md`
3. Do not use transcript claims as evidence. Use only files, hashes, ledgers, tests, and Git state.
4. Preserve conventions: metric `(-,+,+,+)`; keep `c`, `h`, and `k_B`; homogeneous background only; tetrad + 1+3; all 11 Bianchi types; finite tilt; nonlinear large shear.
5. Do not revive superseded routes listed in `state/SUPERSESSION_LEDGER.json`.
6. Current task:
   - integrate red/blue exterior unordered conductances for all 17 source cells;
   - compute exterior photon and hydrogen four-force from the same microscopic events;
   - combine v0.44 off-diagonal, v0.45 same-cell regularized, and exterior blocks;
   - build adaptive `L=12/20/24` scalar operators;
   - require BE null, photon number, entropy, positivity, quadrature, ell-tail, and total four-force gates;
   - then run PR-1C against the user-supplied primitive background through `BackgroundSnapshot`.
7. Use web search for current/niche literature; use Wolfram for symbolic identities; use Precise Special Functions for independent high-precision special-function references.
8. Every bounded stage must produce: implementation, tests, formalism, JSON ledger, CSV/NPZ evidence, SHA-256 manifest, ZIP bundle, Git commit, and remote push/PR evidence.
9. Never force-push shared history. If remote `main` has unrelated commits, push a dedicated backup/feature branch and create a PR.
10. Update `state/PROJECT_STATE.json`, `state/SUPERSESSION_LEDGER.json`, and `docs/CURRENT_STATE.md` before ending the stage.
