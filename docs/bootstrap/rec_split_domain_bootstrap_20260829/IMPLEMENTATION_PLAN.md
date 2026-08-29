# rec_bianchi Split-Domain Replacement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use Superpowers subagent-driven-development or executing-plans task-by-task. Every task below ends in a separately testable commit.

**Goal:** Replace the overlapping full-native/interior-COM ownership at the locked z≈1100 Type-II snapshot with an exterior-native/interior-COM/single-interface residual, analytic JVP, conservation ledgers, and restart state.

**Architecture:** The canonical native point spikes `136..143` become the COM-owned interior. Native physics remains on the exterior. The crossing edges `(135,136)` and `(143,144)` are represented exactly once by a typed interface packet. A direct primitive operator remains the independent oracle; the production replacement uses a structured exterior Schur action.

**Tech stack:** Python 3, NumPy/SciPy sparse/dense linear algebra, existing original-HyRec source adapters and trajectory tests.

**Spec:** `docs/PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md` plus this package's `PACKAGE.json` and `WORK_UNITS.json`.

## Global constraints

- Exact source base: `4cd2c7bff00ca91c57997d7e6e1ff4c67f7fccd3`.
- Interior indices: `136..143`; crossing edges: `(135,136)` and `(143,144)`.
- No inferred native cells, fitted normalization, clipping, full-dynamic-macro promotion, Rust optimization, or preconditioner campaign.
- Immutable source/tables use byte/Git identity. Numerical vectors use justified residual, invariant, state and observable criteria.
- No full-suite reassurance. Run only directly invalidated selectors.
- One PHYS-MATH and one PHYS-MATH-CODE review; at most one reproduced P0/P1 repair.

---

### Task 1: Genuine split-domain RED

**Files**
- Create: `tests/trajectory/test_split_domain_replacement.py`
- Create: `artifacts/trajectory/pr05c2c1b2b1e1c/red/RED.json`

**Interfaces**
- Consumes: the existing ownership audit and locked source-conditioned snapshot.
- Produces: failing tests that later tasks must satisfy without changing the locked support.

- [ ] Write tests asserting `overlap_count == 0`, `unowned_process_count == 0`, exactly two crossing edges, and one owner per process.
- [ ] Write a direct-vs-placeholder replacement test that reaches a numerical exterior-observable assertion.
- [ ] Write number/energy equal-and-opposite interface-ledger assertions.
- [ ] Write an analytic-JVP availability and restart/history parity assertion.
- [ ] Run only the new test file and retain assertion failures; import or missing-file failure is not sufficient.
- [ ] Commit the genuine RED.

### Task 2: Replacement data model and owner swap

**Files**
- Create: `src/full_bianchi_hyrec/trajectory/split_domain_replacement.py`
- Modify: `src/full_bianchi_hyrec/trajectory/dynamic_macro_ownership.py`
- Test: `tests/trajectory/test_split_domain_replacement.py`

**Interfaces**
- `SplitDomainRegistry(interior_indices, cross_edges)`
- `SplitDomainReplacement.from_snapshot(snapshot, doppler_width_eV, interface_abs_x=21.25)`
- `residual(state, context) -> ndarray`
- `jvp(state, direction, context) -> ndarray`
- `ledger(state, context) -> SplitDomainLedger`
- `restart_record() -> dict`

- [ ] Implement the exact registry; reject any support different from the locked indices/edges.
- [ ] Implement exterior/native, interior/COM and interface packets with mutually exclusive process ownership.
- [ ] Disable old full-native interior terms only in the same commit that supplies residual, JVP, ledgers and restart state.
- [ ] Run the ownership and interface tests.
- [ ] Commit the owner swap.

### Task 3: Exterior Schur action and analytic JVP

**Files**
- Modify: `src/full_bianchi_hyrec/trajectory/split_domain_replacement.py`
- Test: `tests/trajectory/test_split_domain_replacement.py`

- [ ] Assemble an independent dense direct primitive matrix for the locked snapshot.
- [ ] Implement the structured exterior Schur action without fitting a normalization.
- [ ] Compare exterior state and selected observables against the direct reference.
- [ ] Compare analytic JVP to a preregistered central/complex directional derivative schedule.
- [ ] Report condition number and operator residual separately.
- [ ] Commit the operator/JVP closure.

### Task 4: Conservation and restart proof

**Files**
- Modify: `tests/trajectory/test_split_domain_replacement.py`
- Create: `artifacts/trajectory/pr05c2c1b2b1e1c/verification/`

- [ ] Close photon-number, exact photon-energy and four-force ledgers.
- [ ] Prove pure representation crossing has zero atom source.
- [ ] Prove restart serialization produces numerically and structurally equivalent continuation.
- [ ] Run compiled/source mutants: double owner, unowned edge, sign reversal and dropped ledger entry; require numerical/ledger assertion failures.
- [ ] If parallel work is added, prove ordered one-thread/N-thread result identity without timing.
- [ ] Commit durable verification.

### Task 5: Review and draft delivery

- [ ] Run one PHYS-MATH review and one PHYS-MATH-CODE review.
- [ ] Repair only a reproduced P0/P1 defect, at most once, and rerun only its dependency cone.
- [ ] Seal the evidence manifest and classify source, numerical and packaging identities separately.
- [ ] Ordinary-push one draft PR against `audit/ode-four-loop-external-audit-20260823`.
- [ ] Read back exact head/tree/path/evidence and stop without merge or ready transition.
