# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-06`
Current stage: **PR-05A / v0.58 — primitive rate/schema and bounded one-step DAE PASS; PR-05 IN PROGRESS**
Next bounded task: **PR-05B time-dependent primitive native/atomic radiation block**.

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
   - `state/PR05A_RECOVERY_RECEIPT.json` when present
   - `state/PR16_REMOTE_BASE_RECEIPT.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR05B_TIME_DEPENDENT_NATIVE_BLOCK_PLAN.md`
   - `docs/PR05A_PRIMITIVE_TRAJECTORY_FORMALISM.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR05A_primitive_rate_schema_v0_58/HARD_GATE_LEDGER.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR05A_primitive_rate_schema_v0_58/PR05A_ledger.json`
   - the v0.57 through v0.51 ledgers in reverse chronological order.
3. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, tetrad+1+3, all 11 Bianchi types, finite tilt and nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
6. Do not revive superseded routes: no direct native-to-COM remap, fitted normalization, inferred source cells, silent high-resolution substitution, broad-cell centroid face energy, cross-redshift summation, or interpretation of `DAlpha` as a derivative.
7. Fixed v0.58 architecture:
   - public alpha/delta-alpha rates are SI m^3/s; Beta/R/A rates are s^-1;
   - `delta_alpha=Alpha(Tm,Tr)-Alpha(Tr,Tr)` and analytic derivatives are separate fields;
   - original-HyRec native and COM states remain representation-local;
   - compressed Sobolev/diffusion/Schur/history terms remain active until complete replacements exist in the same residual/JVP/ledger;
   - PR-05A native block is an algebraic DAE projection, not a time-dependent trajectory;
   - q_activity=1 is operator verification only.
8. PR-05B task:
   - declare the differential/algebraic state split and mass matrix;
   - make native radiation and real atomic populations dynamical;
   - replace selected compressed terms jointly and atomically;
   - implement the full analytic IJacobian/JVP;
   - close Saha/Planck, positivity, number/energy/four-force, entropy, restart, causality and Bianchi firewall gates at z~1300,1100,900;
   - publish a bounded no-go rather than fitting any unidentified primitive timescale.
9. Use the pinned research/coding harnesses, current primary literature, Wolfram and Precise Special Functions; record exact receipts.
10. Every stage produces implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, commits, self-contained feature Git bundle, full recovery Git bundle and verification receipts. `.mbox`/raw patches are not canonical. Never force-push shared history.
