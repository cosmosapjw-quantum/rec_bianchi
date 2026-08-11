# rec_bianchi — Full Bianchi–HyRec durable research backup

This public repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable local stage: **PR-05C2C1B2B1E1B0 / v0.75**.
- The immediate dynamic atomic/native/history macro is fail-closed: eight canonical original-HyRec virtual point spikes and six native diffusion edges lie inside the COM support, while two diffusion edges cross its interfaces.
- About 98% of canonical Aup/Adn real--virtual rate mass lies inside the COM domain. Adding the full native/atomic block to the v0.74 COM root would double-own physical processes.
- The admissible target is an exterior-native / interior-COM / single-interface replacement with residual, analytic JVP, conservation ledger and restart parity in one stage. The target contract is a witness, not an implementation claim.
- v0.73 source-derived parent and v0.74 positive COM subblock root remain valid; no full dynamic macro or history append is claimed.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain available.
- Next: **PR-05C2C1B2B1E1C split-domain replacement**.

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
[`docs/PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md`](docs/PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md).

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

The fetched `origin/main` is the v0.74 current-main integration at
`e6b64e0df25d0b1db7cf8b776866db0afc14721e`, tree
`97e5c71b93e9d0bf4429698aff9b651f974ee1fb`. The v0.75 incremental delivery
is integrated locally but is not pushed. For remote application, create a
branch from fresh `origin/main`, compare receipt provenance, apply only the
three v0.75 source commits, rerun all gates, and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.75 regeneration: `python scripts/run_pr05c2c1b2b1e1b0_dynamic_ownership_stage.py`.
- Git-bundle export: `python scripts/export_git_bundle_delivery.py --help`.
