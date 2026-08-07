# Copy-paste handoff prompt — Full Bianchi–HyRec

Treat the session as **RUNTIME_INTERRUPTION_RECOVERY**, not as a normal conversational continuation.

Repository: `git@github.com:cosmosapjw-quantum/rec_bianchi.git`
Durable state date: `2026-08-07`
Current stage: **PR-05C2A / v0.63 — directional conservative pilot PASS_BOUNDED_NO_GO; PR-05 IN PROGRESS**
Next bounded task: **PR-05C2B preconditioned angle-resolved full coupling**.

## Required recovery order

1. Clone/open the repository and run:
   ```bash
   ./scripts/bootstrap_sandbox.sh --offline
   python scripts/check_remote_state.py
   python scripts/check_hyrec_binary_hash_policy.py
   python scripts/check_commit_range_whitespace.py
   python scripts/verify_repo.py --quick
   pytest -q -m "not slow"
   ```
2. Read, in this order:
   - `state/PROJECT_STATE.json`
   - `state/PR05C2A_RECOVERY_RECEIPT.json`
   - `state/REMOTE_CHECK_LATEST.json`
   - `state/ORIGINAL_HYREC_CANONICAL_PROVENANCE.json`
   - `state/SUPERSESSION_LEDGER.json`
   - `docs/CURRENT_STATE.md`
   - `docs/ROADMAP_12PR.md`
   - `docs/PR05C2A_DIRECTIONAL_COUPLING_FORMALISM.md`
   - `docs/PR05C2B_PRECONDITIONED_FULL_COUPLING_PLAN.md`
   - `archive/expanded/Full_Bianchi_HyRec_PR05C2A_directional_coupling_preflight_v0_63/HARD_GATE_LEDGER.json`
   - `archive/expanded/Full_Bianchi_HyRec_PR05C2A_directional_coupling_preflight_v0_63/PR05C2A_ledger.json`
   - the v0.62 through v0.51 ledgers in reverse chronological order.
3. Use Git state, canonical bytes, hashes, ledgers, tests and connector receipts; transcript claims are not evidence.
4. Preserve metric `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, tetrad+1+3, all 11 Bianchi types, finite tilt and nonlinear large shear.
5. Canonical original HyRec is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
6. Do not revive superseded routes: no direct native-to-COM remap, fitted normalization, inferred source cells, silent high-resolution substitution, broad-cell centroid face energy, cross-redshift summation, centre-derived native transient mass, mutation during rejected attempts, derivatives through discrete stencil switches, or simultaneous canonical and typed scalar-history owners.
7. Fixed v0.63 result:
   - actual locked Bianchi II, class-B `VI_h`, and exceptional `VI_-1/9` snapshot sequences drive the directional pilot;
   - conservative finite-volume face flux closes photon number and exact face-energy ledgers with zero computational-interface atom source;
   - bounded one-second log-positive collision/transport pilots converge with analytic JVP and nonpositive collision entropy production;
   - original-HyRec native boundary history has angular rank one, while the 26-direction COM boundary needs at least rank four for number-plus-momentum and rank 26 for an exact face trace;
   - the P0 upwind face value is an explicit pilot closure, not canonical source data;
   - source-temperature COM mode measures differ from the frozen v0.50 grid by up to about 9.5 percent;
   - canonical macro collision stiffness is `O(1e9)`, so a block/AP preconditioner is required.
8. PR-05C2B task:
   - define an explicit positive angle-resolved native boundary closure and state its claim downgrade;
   - add refinement-tested COM face reconstruction;
   - build a source-temperature mode-measure/collision-kernel adapter or a controlled network family;
   - implement harmonic-block or asymptotic-preserving preconditioning;
   - rerun adaptive canonical macro trajectories with componentwise number, exact face-energy, redshift-work and collision four-force gates.
9. Use the pinned research/coding harnesses, current primary literature, Wolfram and Precise Special Functions; record exact receipts.
10. Every stage produces implementation, tests, formalism, ledgers, adversarial audit, CSV/NPZ evidence, SHA-256 manifest, immutable ZIP, commits, self-contained feature Git bundle, full recovery Git bundle and verification receipts. Never force-push shared history.
