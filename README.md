# rec_bianchi — Full Bianchi–HyRec durable research backup

This public repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C2C1B2B1D / v0.72**.
- Production macro entry now requires a content-addressed
  `AcceptedRadiationParent` with evidence class `SOURCE_DERIVED_ACCEPTED` and
  exact history/atomic/background/network/interface provenance.  Manufactured
  and operator-verification fixtures fail closed.
- The uploaded `bianchireview87` source is byte-locked and drives a validated
  **orthogonal Bianchi-II background-provider pilot**.  Its one-macro normalized
  endpoint error against the locked v0.48 sequence is below `3e-7`.
- This is not yet a physical accepted radiation parent and not all-11 provider
  validation.  Bianchi IX requires a D-normalized H-zero event; tilted
  exceptional `VI_-1/9` and all unvalidated families fail closed.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain available.
- Next: reconstruct one source-derived accepted parent at `z~1100`, Bianchi II;
  only then characterize slow modes and compare preconditioners.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_commit_range_whitespace.py
if test -f scripts/check_imports.py; then PYTHONPATH=src python scripts/check_imports.py; fi
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json),
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and
[`docs/PR05C2C1B2B1E_SOURCE_DERIVED_PARENT_PLAN.md`](docs/PR05C2C1B2B1E_SOURCE_DERIVED_PARENT_PLAN.md).

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

The fetched `origin/main` is the v0.71 compatibility-preserving integration at
`84ea39bf6e56ac5a6290482b614318413577ba1a`, tree
`582fd32ce19179cac96ccdb4e01d3b17136cc9df`.  The v0.72 delivery is not yet
assumed pushed.  Create a branch from fresh `origin/main`, apply only the v0.72
feature commits after comparing receipt provenance, rerun all gates, and never
rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.72 regeneration: `python scripts/run_pr05c2c1b2b1d_parent_provider_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
