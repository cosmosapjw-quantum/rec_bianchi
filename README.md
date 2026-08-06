# rec_bianchi — Full Bianchi–HyRec durable research backup

This private repository is the durable active workspace for the scalar Full
Bianchi–HyRec program: homogeneous all-11 Bianchi backgrounds, tetrad and 1+3
formalism, finite tilt, nonlinear large shear, HYREC-grade atomic physics and
angle/frequency-resolved Ly-alpha transfer.

## Current state

- Durable stage: **PR-04C0/C1A / v0.55**.
- PASS: a fail-closed ten-process ownership registry and six source-identical
  positive photon packets at `x=+-21.25` for `z~1300,1100,900`.
- Maximum boundary reconstruction residual:
  `1.6537648327370854e-16`.
- Number and transported photon-energy interface ledgers cancel exactly.
- A pure computational representation crossing has zero atomic source; recoil
  remains owned by physical collision terms.
- Scientific boundary: no packet has yet been deposited into the COM–KHW
  far-boundary/Liouville state. **PR-04 remains in progress.**
- Next stage: **PR-04C1B/C2 coupled far-boundary interface operator**.

Start with:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/verify_repo.py --quick
pytest -q -m "not slow"
```

Then read [`HANDOFF_PROMPT.md`](HANDOFF_PROMPT.md),
[`state/PROJECT_STATE.json`](state/PROJECT_STATE.json), and
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

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
- `scripts/`: stage generation, C instrumentation, verification and patch tools.

## Remote policy

The read-only connector can inspect GitHub, but the owner performs fetch,
push and PR operations locally. Apply v0.55 on a feature branch, verify the
final tree and never rewrite shared history.

## Test tiers

- Fast: `pytest -q -m "not slow"`.
- Repository: `python scripts/verify_repo.py --all`.
- Scientific: `python scripts/verify_repo.py --scientific`.
- v0.55 regeneration: `python scripts/run_pr04c0c1a_split_domain_stage.py`.
