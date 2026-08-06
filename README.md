# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05A / v0.58**.
- Primitive original-HyRec rate tables and source semantics are byte locked and
  exposed through immutable SI-adapted schemas with analytic interpolation
  JVPs.
- Canonical `DAlpha` is `delta_alpha=Alpha(Tm,Tr)-Alpha(Tr,Tr)`, not a
  derivative; cancellation-amplified raw relative values remain diagnostics.
- Three source-conditioned lanes close Saha balance, native algebraic DAE
  projection, M-matrix positivity evidence, COM interface-off equilibrium,
  analytic JVP, number/energy/four-force, restart, causality and Bianchi
  firewall gates.
- No compressed native term has been removed. A time-dependent native/atomic
  trajectory is not yet claimed.
- Next stage: **PR-05B time-dependent primitive native/atomic radiation block**.

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
[`docs/PR05B_TIME_DEPENDENT_NATIVE_BLOCK_PLAN.md`](docs/PR05B_TIME_DEPENDENT_NATIVE_BLOCK_PLAN.md).

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
- `scripts/`: stage generation, C instrumentation, verification and Git-bundle delivery tools.

## Remote and delivery policy

GitHub `main` contains merged PR #16 at
`5fb7aec1cf1cfcd65e40ffeb097c8c1237cfe19c`, tree
`0638ad71941c258a90375148674264de5ff14608`; the PR-head CI completed
successfully. v0.58 was developed on the exact author v0.57 lineage, so exact
remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed feature commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.58 regeneration: `python scripts/run_pr05a_primitive_trajectory_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
