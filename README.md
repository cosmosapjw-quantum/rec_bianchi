# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-04C1B/C2 / v0.56**.
- PASS: the six v0.55 source-identical face packets are attached only to the
  exact `FR00`/`FB02` far-boundary states, with no interior-cell collapse and no
  native-to-COM state remap.
- PASS: positive log-variable monolithic collision/interface residual, analytic
  block JVP, exact photon-number and transported-photon-energy ledgers, zero
  interface atom source, exact restart, and Bianchi branch-zero localization.
- Maximum gross-term backward error: `1.3200190226745005e-17`.
- Maximum independent number residual: `2.5609198306764287e-14`.
- Maximum analytic/JVP relative error: `1.279553711820355e-09`.
- The dilute-occupation-normalized net residual stalls near
  `1.73712431307357e-10`; it is retained as a diagnostic and is not relabelled
  as a strict `1e-11` pass. Acceptance after Newton stagnation requires both
  gross backward error and independent number closure below `1e-11`.
- Scientific boundary: the three runs are source-conditioned operator tests on
  an unfitted `q_activity=1` BE reference state, not a reconstructed physical
  native/COM trajectory. **PR-04 remains in progress.**
- Next stage: **PR-04C3 componentwise common-ledger closure**.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR04C3_COMMON_LEDGER_PLAN.md`](docs/PR04C3_COMMON_LEDGER_PLAN.md).

## Canonical source

`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, is
the owner-attested unique official-site October-2012 release. Internal
May/October metadata variations are intrinsic to that archive.

## Layout

- `src/`, `tests/`, `data/`: active implementation and regression data.
- `archive/bundles/`: immutable stage ZIPs.
- `archive/expanded/`: browsable stage artifacts and verifiers.
- `archive/inputs/`: canonical sources, host code and validated harnesses.
- `state/`: machine-readable state, provenance, recovery and receipts.
- `docs/`: current state, roadmap, research plans and handoff material.
- `scripts/`: stage generation, C instrumentation, verification and Git-bundle
  delivery tools.

## Remote and delivery policy

GitHub `main` contains merged PR #14 at
`47106fec89c176c3f3b91ed7e4ff198dea323968`, including the shared
compiler-dependent binary-hash gate. v0.56 was developed on the exact author
v0.55 lineage, so exact remote-tree identity is not assumed. Deliveries use a
self-contained feature Git bundle with an ordered cherry-pick list plus a full
recovery bundle. Fetch the feature bundle onto a branch created from fresh
`origin/main`; never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.56 regeneration: `python scripts/run_pr04c1b_c2_coupled_interface_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
