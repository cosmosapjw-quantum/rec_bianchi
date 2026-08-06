# PR-04C0/C1A v0.55 implementation plan

> **Execution rule:** implement by strict red-green-refactor TDD. Do not write production code until the corresponding test has failed for the expected missing-feature reason.

**Goal:** close the operator-ownership/no-double-counting theorem and extract source-identical red/blue boundary packets from canonical October-2012 original HyRec at predeclared nearest-grid snapshots near z=1300, 1100, and 900. This bounded release does not yet deposit packets into the 35-state COM–KHW Liouville boundary state; that is PR-04C1B/C2.

**Architecture:** retain original HyRec and the 35-state COM–KHW collision network as separate representation-local operators. A new interface module owns exactly the two cross-boundary processes. It represents each one-directional FLRW crossing as a positive total-photon packet plus a signed distortion decomposition and applies number/photon-energy/atom-energy entries with exactly opposite signs to the two subdomain ledgers. Canonical C diagnostics reconstruct the occupation at the exact physical interfaces x=±21.25 from the source free-streaming history using the same two-point positive interpolation as `interp_Dfnu`.

**Conventions and dimensions:** metric `(-,+,+,+)`; hydrogen orthonormal tetrad; ordinary frequency `nu` in Hz; `x=(nu-nu_Lya)/Delta_nu_D`; `Delta nu=nu_target-nu_source`; `Delta E_gamma=h Delta nu`; `Delta E_H=-h Delta nu`; `Phi_N` in photons H^-1 s^-1; `Phi_E` in W H^-1. Keep `c`, `h`, and `k_B` explicit.

---

## Task 1 — Recovery and baseline receipt

**Files:**
- Create: `state/PR04C0C1A_RECOVERY_INVENTORY.json`
- Create: `state/PR04C0C1A_TDD_RED.log`

**Steps:**
1. Record v0.54 bundle HEAD/tree, remote GitHub main HEAD/tree reported by the connector, file hashes, harness hashes, canonical HyRec archive hash, and baseline command outputs.
2. Run `./scripts/bootstrap_sandbox.sh --offline`.
3. Run `python scripts/verify_repo.py --quick`.
4. Run `pytest -q -m "not slow"` and require the v0.54 baseline to pass before modification.

## Task 2 — Ownership registry and fail-closed validation

**Files:**
- Create: `tests/recoil/test_split_domain_exchange.py`
- Create: `src/full_bianchi_hyrec/recoil/split_domain_exchange.py`

**RED tests:**
1. `test_default_ownership_registry_has_exactly_one_owner_per_process`.
2. `test_registry_rejects_duplicate_and_unowned_processes`.
3. `test_replacement_switch_off_is_exact_identity`.
4. `test_cross_interface_packet_is_evaluated_once_and_applied_twice_with_opposite_signs`.
5. Run `pytest -q tests/recoil/test_split_domain_exchange.py` and save the expected import/missing-feature failure.

**GREEN implementation:**
1. Add explicit owner enum values for native transport, COM collision, COM Liouville, analytic background, and interface.
2. Add immutable process records and a registry validator.
3. Add a baseline-off operator path that returns exact copies and a zero ledger.
4. Add application ledger counters and fail if evaluation count is not one or application count is not two.

## Task 3 — Exchange packet units, signs, positivity, and serialization

**Files:**
- Modify: `tests/recoil/test_split_domain_exchange.py`
- Modify: `src/full_bianchi_hyrec/recoil/split_domain_exchange.py`

**RED tests:**
1. Reject nonpositive total number flux, nonfinite quantities, wrong photon/atom energy signs, and a centroid on the wrong interface side.
2. Accept a signed distortion component only when the total packet remains positive.
3. Round-trip packet JSON without changing any float or enum field.
4. Verify `nu_bar=Phi_Egamma/(h Phi_N)` and its Hz dimension convention.

**GREEN implementation:**
1. Add `InterfaceSide`, `ExchangeDirection`, and immutable `ExchangePacket`.
2. Store total, blackbody-reference, and signed-distortion number/energy components.
3. Require exact component additivity within a scale-aware roundoff tolerance.
4. Add `to_dict`/`from_dict` and stable SHA-256 serialization.

## Task 4 — Canonical three-snapshot C instrumentation

**Files:**
- Create: `tests/recoil/test_original_hyrec_boundary_instrumentation.py`
- Create: `scripts/c_harness/instrument_original_hyrec_pr04c.py`
- Modify: `src/full_bianchi_hyrec/recoil/original_hyrec_physical_flux.py`

**RED tests:**
1. Instrumenting the canonical source adds only `#ifdef PR04C_DIAGNOSTICS` guarded code.
2. Guard-off source compiles to the canonical binary SHA-256 and produces the canonical 8001-row history SHA-256.
3. Parse three separate snapshot CSVs and require exactly two interface rows per snapshot.
4. Recompute each interface interpolation source index, history indices, interpolation fraction, occupation, mode factor, total/distortion number flux, and total/distortion energy flux in Python.
5. Reject an interface sample whose next-higher native source index is not minimal or whose interpolation fraction is outside `[0,1]`.

**GREEN implementation:**
1. Parameterize targets `{1300,1100,900}` in C diagnostics.
2. At each target, compute `Delta E_D=E21 sqrt(2 T_m/m_H)` and `E_interface=E21+x_interface Delta E_D` for x=±21.25.
3. Select the least native table energy strictly above the interface and use the source's `interp_Dfnu` time interpolation exactly.
4. Dump source index, query `ln a`, interpolation indices/fraction, distortion occupation, Planck occupation, total occupation, `A=8 pi nu^3/(c^3 n_H)`, and redward fluxes.
5. Extend Python parsers with immutable boundary-sample records and independent recomputation helpers.

## Task 5 — Native packet construction and three-snapshot gates

**Files:**
- Modify: `tests/recoil/test_split_domain_exchange.py`
- Modify: `tests/recoil/test_original_hyrec_boundary_instrumentation.py`
- Modify: `src/full_bianchi_hyrec/recoil/split_domain_exchange.py`
- Create: `scripts/run_pr04c0c1a_split_domain_stage.py`

**RED tests:**
1. Blue interface maps to `native_to_com`; red interface maps to `com_to_native` under FLRW redshifting.
2. Packet number and energy are positive, distortion may be signed, and photon+atom energy cancels.
3. Applying the same packet to native and COM ledgers gives exact global number and energy cancellation.
4. Boundary packet construction is independent of Bianchi type when the local hydrogen-frame state is identical.

**GREEN implementation:**
1. Construct total/reference/distortion packets from source-identical boundary samples.
2. Use a single-owner ledger; never distribute the packet over COM cells in this stage.
3. Produce three-snapshot CSV/NPZ evidence, ownership matrix, symbolic and high-precision receipts, and a local-state geometry firewall.

## Task 6 — Independent symbolic and precision checks

**Files:**
- Create: `archive/expanded/<artifact>/WOLFRAM_SYMBOLIC_RECEIPT.json`
- Create: `archive/expanded/<artifact>/PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json`

**Checks:**
1. Wolfram: backward-Euler positivity, opposite-sign number/energy cancellation, and `Integral[x^2/(Exp[x]-1),0,Infinity]=2 Zeta[3]`.
2. Precise Special Functions: 100-digit `Zeta[3]` and `Gamma[3]=2` for the blackbody photon-number normalization.
3. Compare with an independent `mpmath` evaluation used by the stage verifier.

## Task 7 — Durable stage artifact and state transition

**Files:**
- Create: `archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/*`
- Create: `archive/bundles/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55.zip`
- Create: `data/pr04c_split_domain_boundary_v055.npz`
- Modify: `state/PROJECT_STATE.json`
- Modify: `state/SUPERSESSION_LEDGER.json`
- Modify: `docs/CURRENT_STATE.md`
- Modify: `docs/ROADMAP_12PR.md`
- Modify: `HANDOFF_PROMPT.md`
- Modify: `docs/HANDOFF_PROMPT.md`
- Modify: `README.md`
- Modify: `docs/ARTIFACT_INDEX.md`
- Modify: `scripts/verify_repo.py`

**Required artifact contents:** formalism, ownership matrix CSV/JSON, three-snapshot boundary CSV/NPZ, hard-gate ledger, validation matrix, evidence ledger, source diff, canonical guard-off hashes, symbolic/precision receipts, manifest, verifier, and restart packet JSON.

**Status language:** `PASS_PR04C0_OWNERSHIP_PR04C1A_NATIVE_BOUNDARY_INSTRUMENTATION_PR04C1B_C2_OPEN`. Do not claim PR-04 complete.

## Task 8 — Fresh verification, bundle, and patch export

**Commands:**
1. `./scripts/bootstrap_sandbox.sh --offline`
2. `python scripts/verify_repo.py --quick`
3. `python scripts/verify_repo.py --all`
4. `pytest -q -m "not slow"`
5. Run every slow test file in a fresh interpreter.
6. Run the immutable artifact verifier.
7. `git diff --check`
8. `git fsck --full --no-dangling`
9. Clone the full bundle and repeat quick/all/fast plus artifact verification.
10. Export and validate binary-safe patches from exact v0.54 and from the last confirmed remote milestone; compare the final tree, not replayed commit identities.

## Next bounded stage after v0.55

PR-04C1B/C2 will connect the unresolved packets to the existing far-boundary/Liouville ghost state and solve the coupled implicit residual. It must add COM boundary occupation/action, packet deposition/removal, analytic block JVP, restart, branch-zero localization, and multi-snapshot number/energy/positivity closure. PR-04 remains open until that succeeds without fitted normalization.
