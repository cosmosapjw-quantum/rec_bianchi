# rec_bianchi — Full Bianchi–HyRec durable research backup

This public repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-05C2C1B2B1E1A / v0.74**.
- v0.74 establishes a positive, roundoff-limited root for the source-conditioned
  35-state by 26-direction COM collision--frequency-transport subblock at the
  dynamic orthogonal Bianchi-II endpoint. Native boundaries remain fixed at the
  v0.73 source-derived parent; atomic sources and accepted history are not
  evolved or appended.
- Production macro entry now requires a content-addressed
  `AcceptedRadiationParent` with evidence class `SOURCE_DERIVED_ACCEPTED` and
  exact history/atomic/background/network/interface provenance.  Manufactured
  and operator-verification fixtures fail closed.
- The uploaded `bianchireview87` source is byte-locked and drives a validated
  **orthogonal Bianchi-II background-provider pilot**.  Its one-macro normalized
  endpoint error against the locked v0.48 sequence is below `3e-7`.
- This is not yet an accepted coupled Bianchi--HyRec macro endpoint or all-11
  provider validation. Bianchi IX requires a D-normalized H-zero event; tilted
  exceptional `VI_-1/9` and all unvalidated families fail closed.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain available.
- Next: advance one dynamic atomic/native/history macro from the same `z~1100`
  Bianchi-II parent and v0.74 COM residual path. Internal iterations must not
  append accepted history; exactly one append requires all physical gates.

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
[`docs/PR05C2C1B2B1E1A_SINGLE_COM_MACRO_FORMALISM.md`](docs/PR05C2C1B2B1E1A_SINGLE_COM_MACRO_FORMALISM.md).

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

The fetched `origin/main` is the v0.73 current-main integration at
`a560054603735ad1d444e5fa1239f57595f2067b`, tree
`49ddbc1acd94dae48c8d6010db76a6a9cb0dc06e`. The v0.74 incremental delivery
is integrated locally but is not pushed. For remote application, create a
branch from fresh `origin/main`, compare receipt provenance, apply only the
three v0.74 source commits, rerun all gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.74 regeneration: `python scripts/run_pr05c2c1b2b1e1a_single_com_macro_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
