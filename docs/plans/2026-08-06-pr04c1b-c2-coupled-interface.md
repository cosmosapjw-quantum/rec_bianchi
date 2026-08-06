# PR-04C1B/C2 Coupled Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Couple the six v0.55 source-identical face packets to the exact `FR00`/`FB02` boundary states with a positive monolithic backward-Euler residual, exact number/transported-energy ledgers, analytic JVP, restart support and branch-zero localization.

**Architecture:** The COM occupation receives only photon number at the exact far-boundary cell through `Delta f=sigma n_H q/g`; exact face energy remains an independently audited transfer accumulator, including the finite-cell centroid correction. Positive occupations and positive packet multipliers are represented logarithmically. Collision and interface terms share one residual; an interface-off path delegates unchanged to the existing collision solver.

**Tech Stack:** Python 3.11+, NumPy, SciPy `LinearOperator`/GMRES, mpmath reference checks, pytest, canonical NPZ/CSV artifacts, Git bundles.

## Global Constraints

- Metric signature `(-,+,+,+)`.
- Keep `c`, `h`, and `k_B` explicit.
- Ordinary frequency `nu` in Hz and `x=(nu-nu_Lya)/Delta_nu_D`.
- Homogeneous scalar background only in v0.56.
- No fitted normalization, direct native/COM state equality, inferred source cells, or silent high-resolution substitution.
- `FR00` and `FB02` are the only resolved COM states touched by the interface.
- The interface atom source is exactly zero; collision events retain recoil ownership.
- Full trajectory integration is PR-05; FLRW history parity is PR-06.

---

### Task 1: Prevent a third compiler-hash gate regression

**Files:**
- Create: `scripts/check_hyrec_binary_hash_policy.py`
- Create: `tests/test_hyrec_binary_hash_policy.py`
- Modify: `scripts/verify_repo.py`

**Interfaces:**
- Produces: `audit_binary_hash_assertions(root: Path) -> list[str]`, returning policy violations.
- Policy: every `assert` involving `ORIGINAL_HYREC_PORTABLE_BINARY_SHA256` must be lexically nested under `if binary_hash_is_meaningful:`.

- [ ] Write an AST-based failing test with one guarded and one unguarded synthetic module.
- [ ] Run `PYTHONPATH=src pytest -q tests/test_hyrec_binary_hash_policy.py` and verify RED because the scanner does not exist.
- [ ] Implement the scanner and CLI; add it to `verify_repo.py --quick` before bundle verification.
- [ ] Run the targeted test and `python scripts/check_hyrec_binary_hash_policy.py`; both must pass.
- [ ] Commit as `test(policy): forbid unguarded HyRec binary hash assertions`.

### Task 2: Exact far-boundary adapter and transfer accumulator

**Files:**
- Create: `src/full_bianchi_hyrec/recoil/coupled_interface.py`
- Create: `tests/recoil/test_coupled_interface.py`

**Interfaces:**
- `FarBoundaryCell(side, label, index, interval, mode_measure_m3, equilibrium_weight_m3, centroid_frequency_Hz, face_x)`.
- `FarBoundaryAdapter.from_network(network) -> FarBoundaryAdapter`.
- `BoundaryTransferAccumulator.from_packet(packet, dt_s) -> BoundaryTransferAccumulator`.
- `BoundaryTransferAccumulator.to_dict()/from_dict()` and `sha256`.
- `FarBoundaryAdapter.occupation_increment(accumulator, n_H_m3, n_angle) -> ndarray`.

- [ ] Write failing tests pinning `FR00` index 29 and `FB02` index 34, exact intervals/measures and centroid frequencies from momentum scale.
- [ ] Write failing tests for side/direction mismatch, nonpositive duration, component mismatch and exact JSON round-trip.
- [ ] Write failing number-conversion test: weighted COM number change equals `sigma n_H q` to roundoff.
- [ ] Implement immutable validated dataclasses and adapter; do not infer labels by position alone.
- [ ] Run `PYTHONPATH=src pytest -q tests/recoil/test_coupled_interface.py -k 'adapter or accumulator or increment'`.
- [ ] Commit as `feat(interface): add exact far-boundary adapter and accumulators`.

### Task 3: Exact number/energy/cell-correction ledger

**Files:**
- Modify: `src/full_bianchi_hyrec/recoil/coupled_interface.py`
- Modify: `tests/recoil/test_coupled_interface.py`

**Interfaces:**
- `InterfaceTransferLedger.from_accumulators(adapter, accumulators, n_H_m3)`.
- Fields include native/COM number changes, native/COM transported energies, zero atom source, resolved-cell energy proxy and unresolved correction.

- [ ] Write failing tests proving native+COM number and transported energy are exactly zero.
- [ ] Write a failing test proving the face/cell energy correction is nonzero for at least one v0.55 packet and reconstructs exact COM transported energy.
- [ ] Implement the ledger with face frequency authoritative and cell-centroid energy diagnostic only.
- [ ] Run targeted ledger tests.
- [ ] Commit as `feat(interface): close exact number and transported-energy ledgers`.

### Task 4: Monolithic residual and analytic block JVP

**Files:**
- Modify: `src/full_bianchi_hyrec/recoil/coupled_interface.py`
- Modify: `tests/recoil/test_coupled_interface.py`

**Interfaces:**
- `CoupledInterfaceProblem(network, grid, packets, n_H_m3, dt_s, enabled=True)`.
- `pack(log_f, log_rho)`, `unpack(vector)`.
- `unscaled_residual(vector, old_occupation) -> ndarray`.
- `scaled_residual(...) -> ndarray`.
- `jvp(vector, direction, old_occupation, scaled=True) -> ndarray`.
- Transfer amount `q_s=dt Phi_s exp(v_s)`; `R_rho=exp(v_s)-1`.

- [ ] Write a failing central-difference JVP test on the existing two-state/six-angle synthetic network.
- [ ] Write a failing unpreconditioned number-ledger residual test.
- [ ] Implement residual/JVP using existing `apply_nonlinear_bose_operator` and `apply_nonlinear_bose_jvp`.
- [ ] Confirm relative JVP error `<1e-8` over at least three step sizes.
- [ ] Commit as `feat(interface): add monolithic residual and analytic JVP`.

### Task 5: Positive Newton-GMRES solve and guard-off parity

**Files:**
- Modify: `src/full_bianchi_hyrec/recoil/coupled_interface.py`
- Modify: `tests/recoil/test_coupled_interface.py`

**Interfaces:**
- `CoupledInterfaceStepResult` with occupation, accumulators, ledger, convergence metrics, GMRES count, entropy/free-energy diagnostics and restart payload.
- `solve_coupled_interface(old_occupation, problem, nonlinear_rtol=1e-11, ...)`.

- [ ] Write a failing red-removal test whose explicit trial is negative but implicit solution must remain positive.
- [ ] Write a failing guard-off test requiring exact equality with `implicit_bose_step` output and no accumulator.
- [ ] Implement matrix-free Newton-GMRES with log variables, block scaling, diagonal block preconditioner and residual-decreasing line search.
- [ ] Gate raw relative residual `<1e-11`, minimum occupation `>0`, number residual to roundoff and nonnegative collision entropy production.
- [ ] Run all coupled-interface tests.
- [ ] Commit as `feat(interface): solve positive coupled boundary residual`.

### Task 6: Bianchi branch-zero audit

**Files:**
- Modify: `src/full_bianchi_hyrec/recoil/coupled_interface.py`
- Modify: `tests/recoil/test_coupled_interface.py`

**Interfaces:**
- `audit_boundary_speed_history(times, red_speed, blue_speed) -> BoundarySpeedAudit`.
- Stores exact roots, positive/negative integrals and endpoint-heuristic discrepancy.

- [ ] Write failing synthetic crossing tests where endpoint classification gives the wrong integrated direction.
- [ ] Write failing data-driven tests for Bianchi II, `VI_h`, and `VI_-1/9` using `pr01c_background_snapshots_v048.npz`.
- [ ] Implement via existing `piecewise_linear_roots` and exact signed piecewise-linear integration; do not introduce sampled sign heuristics.
- [ ] Commit as `feat(interface): localize Bianchi boundary-speed branch events`.

### Task 7: Three-snapshot stage runner and independent references

**Files:**
- Create: `scripts/run_pr04c1b_c2_coupled_interface_stage.py`
- Create: `archive/expanded/Full_Bianchi_HyRec_PR04C1B_C2_coupled_interface_v0_56/` outputs
- Create: `data/pr04c_coupled_interface_v056.npz`

**Interfaces:**
- Load v0.55 packet CSV/NPZ, full v0.50 collision network and v0.48 background speeds.
- Use fixed `dt_s=1e5` and an unfitted `q_activity=1` Bose-Einstein initial state for operator verification.
- Emit adapter registry, energy corrections, residual/JVP metrics, branch roots, restart payload, hard-gate ledger, formalism and immutable manifest.

- [ ] Run harness validators and record hashes/exit codes.
- [ ] Generate RED log before implementation outputs are accepted.
- [ ] Run z=1300/1100/900 coupled solves and write CSV/NPZ evidence.
- [ ] Independently verify the scalar two-state system with mpmath and symbolic identities with Wolfram.
- [ ] Run artifact verifier.
- [ ] Commit as `feat(interface): close PR04C1B/C2 coupled interface stage`.

### Task 8: State transition, complete verification and Git bundles

**Files:**
- Modify: `README.md`, `HANDOFF_PROMPT.md`, `docs/CURRENT_STATE.md`, `docs/ROADMAP_12PR.md`, `docs/ARTIFACT_INDEX.md`, `state/PROJECT_STATE.json`, `state/BUNDLE_INDEX.json`, `scripts/verify_repo.py`
- Create: v0.56 receipts, scientific logs and research-harness closeout documents.

- [ ] Update status to `PASS_PR04C1B_C2_PR04C3_OPEN`; do not close PR-04.
- [ ] Run import smoke, quick verifier, fast tests, every slow file, targeted artifact verifier, `git diff --check`, `git fsck --full`, manifest and secret scan.
- [ ] Verify a fresh clone from the full bundle.
- [ ] Create a full `.bundle` and a standalone feature `.bundle`; no mbox is the canonical patch deliverable.
- [ ] Write exact apply instructions: fetch bundle, inspect commits, cherry-pick feature range onto current `main`.
- [ ] Seal SHA-256 receipts and commit as `chore(recovery): seal v0.56 verification and bundle delivery`.
