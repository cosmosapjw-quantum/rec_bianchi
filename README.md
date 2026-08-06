# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-04C3 / v0.57**.
- **PR-04 COMPLETE at the source-conditioned split-domain operator-contract
  level.**
- Exactly three independent lanes (`z~1300,1100,900`) and six red/blue packets
  are locked in one typed componentwise common ledger.
- Cross-snapshot signed sums and averages are forbidden; the aggregate is the
  maximum normalized component violation.
- `epsilon_common=0`, exact transported face-energy cancellation, zero
  interface atom source, strict positivity, analytic JVP, nonpositive collision
  entropy, exact restart and Bianchi branch-zero localization all pass.
- The `q_activity=1` COM state remains an unfitted operator-verification state.
  A native-derived COM trajectory and full recombination history are not
  claimed.
- Next stage: **PR-05A BackgroundSnapshot/RadiationFeedback schema and primitive
  original-HyRec operator source lock**.

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
[`docs/PR05_PRIMITIVE_TRAJECTORY_INTERFACE_PLAN.md`](docs/PR05_PRIMITIVE_TRAJECTORY_INTERFACE_PLAN.md).

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

GitHub `main` contains merged PR #15 at
`ecd2d9e8b758dd1727c060d8cf210f08e723b9cf`, tree
`09a718222b13f6dfd4671d2e1b62cdb2ec9a880a`; the PR-head CI completed
successfully. v0.57 was developed on the exact author v0.56 lineage, so exact
remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed feature commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.57 regeneration: `python scripts/run_pr04c3_common_ledger_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
