# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C2C0 / v0.65**.
- The scalar, unpolarized mathematical/physical contract is complete under an
  explicit hydrogen-frame isotropic-source axiom.
- Exact Bianchi/tilt characteristics generate the directional radiation field
  as an initial-boundary-value problem; one scalar instantaneous datum is still
  not relabelled angle-resolved source data.
- Direct thermodynamic COM--KHW kernels are required to be nonnegative
  reciprocal nodal event graphs.  Number, BE null, positivity and Bose
  free-energy dissipation follow structurally, and interpolation is restricted
  to fixed topology in logarithmic conductance variables.
- The stiff collision block has an entropy-metric graph-Laplacian form with an
  exact activity nullspace and an explicit stiffness-independent
  spectral-equivalence preconditioner bound.
- Exact native face traces, conservative positive COM traces, componentwise
  source ownership and fixed-branch index-one DAE well-posedness are locked.
- Estimated scalar theory completion is about **99%**.  Direct compilation,
  angular-solver implementation, multi-macro evidence and PR-06 FLRW history
  parity remain open.
- Next: **PR-05C2C1 direct thermodynamic compiler and characteristic angular
  solver**.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_commit_range_whitespace.py
PYTHONPATH=src python scripts/check_imports.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR05C2C1_DIRECT_COMPILER_CHARACTERISTIC_SOLVER_PLAN.md`](docs/PR05C2C1_DIRECT_COMPILER_CHARACTERISTIC_SOLVER_PLAN.md).

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

GitHub `main` contains merged PR #23 at
`2add22bb71c453900a1f79f14b29074971a348f6`, tree
`c07ffa8e686c5ecf8fafa1c421625f38ba819aa9`; PR-head CI run 78 completed
successfully.  v0.65 is developed on the exact author v0.64 lineage, so exact
remote-tree identity is not assumed.

Canonical patch delivery is a self-contained feature Git bundle with an ordered
commit receipt, plus a full recovery Git bundle. Create a branch from fresh
`origin/main`, cherry-pick only the receipt-listed v0.65 commits, rerun all
gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.65 regeneration: `python scripts/run_pr05c2c0_theory_closure_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
