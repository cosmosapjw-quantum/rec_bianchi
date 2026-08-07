# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C2A / v0.63**.
- Actual v0.48 Bianchi snapshot sequences drive direction-resolved conservative
  frequency transport on the locked 35-state COM–KHW domain.
- Nine source-conditioned actual-background pilot lanes close bounded-step
  number, exact face-energy, four-force, positivity, entropy and analytic-JVP
  gates on the frozen v0.50 COM grid.
- Full source-identical anisotropic coupling is **not yet identified**: original
  HyRec supplies scalar boundary history, the COM finite-volume state has no
  source-defined face trace, and source-temperature mode measures differ from
  the frozen grid by up to about 9.5 percent.
- Canonical macro collision stiffness is `O(1e9)`. PR-05C2B must add an explicit
  angular/face closure, thermodynamic grid/kernel adapter and block or
  asymptotic-preserving preconditioner before adaptive macro trajectories.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_commit_range_whitespace.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR05C2B_PRECONDITIONED_FULL_COUPLING_PLAN.md`](docs/PR05C2B_PRECONDITIONED_FULL_COUPLING_PLAN.md).

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

GitHub `main` contains merged PR #21 at `ee54cb44838409f021d6c5fdb502450a11779ec4`, tree
`369655209849c77c55f10f813fe8fecf8a4f7dbe`. Its PR-head CI completed successfully. v0.63 is developed on
the exact author v0.62 lineage, so exact remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed v0.63 commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.63 regeneration: `python scripts/run_pr05c2a_directional_preflight_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
