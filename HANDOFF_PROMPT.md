# REC-LOCAL-02 momentum-owner continuation

This prompt is the complete locator. Do **not** require, reconstruct, or wait
for `FETCH_AND_VALIDATE.py`; no external locator helper is part of this
continuation.

## Canonical Git locator

- Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi`
- Continuation branch:
  `agent/fix/rec-local02-momentum-scale-20260830-r1`
- Stacked parent: draft PR #42
- Required parent commit:
  `dd0e080400bc76d6c5e6af382717e613a9fb32f8`
- Required parent tree:
  `1baed7d1d072fcc94b583e66a6461c657e6520c8`
- Byte manifest:
  `artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02_momentum_scale_repair/MANIFEST.sha256`

If the repository is absent, clone it. If it is present and dirty, preserve it
and create a separate worktree; never reset or clean an existing checkout.

```bash
set -euo pipefail
git fetch origin refs/heads/agent/fix/rec-local02-momentum-scale-20260830-r1
git merge-base --is-ancestor dd0e080400bc76d6c5e6af382717e613a9fb32f8 FETCH_HEAD || {
  echo STOP_INVALID_CONTINUATION_IDENTITY
  exit 1
}
expected_paths='HANDOFF_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02/REC_LOCAL_02_EXECUTION.json
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02_momentum_scale_repair/MANIFEST.sha256
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02_momentum_scale_repair/REC_LOCAL_02_MOMENTUM_SCALE_REPAIR_RECORD.md
src/full_bianchi_hyrec/trajectory/physical_split_reference.py
tests/trajectory/test_physical_split_reference.py'
test "$(git diff --name-only dd0e080400bc76d6c5e6af382717e613a9fb32f8 FETCH_HEAD)" = "$expected_paths" || {
  echo STOP_INVALID_CONTINUATION_IDENTITY
  exit 1
}
git worktree add --detach ../rec-local02-momentum-scale-r1 FETCH_HEAD
cd ../rec-local02-momentum-scale-r1
sha256sum -c artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02_momentum_scale_repair/MANIFEST.sha256 || {
  echo STOP_INVALID_CONTINUATION_IDENTITY
  exit 1
}
```

The ancestry, exact-path, and manifest checks are mandatory. Stop with
`STOP_INVALID_CONTINUATION_IDENTITY` if any check fails.

## Admitted state

The bounded `momentum_scale` P1 is repaired and independently rereviewed:

- target authority is the tracked `CollisionNetwork.momentum_scale` array;
- cell energy is exactly `momentum_scale*c/electron_volt`;
- the 35x8 exploratory witness conserves each source column's number and
  locked energy with zero recorded residual;
- the witness remains `EXPLORATORY_NONAUTHORITATIVE` and no physical map is
  selected;
- the legacy line/interval centroid remains diagnostic-only and differs from
  the locked owner by about `5.55e-08 eV`;
- claim remains `NO_PASS_REC_PHYSICAL_SPLIT`.

The old `REC_LOCAL_02_REVIEW_RECORD.md` is immutable history for the exhausted
earlier budget. The additive current record is:

`artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02_momentum_scale_repair/REC_LOCAL_02_MOMENTUM_SCALE_REPAIR_RECORD.md`.

## Required read-only validation

Use Python 3.12 with NumPy 2.4.2, SciPy 1.17.0, and pytest 9.1.1 when that
exact environment is available.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/trajectory/test_physical_split_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/trajectory/test_physical_split_reference.py tests/trajectory/test_direct_thermodynamic_nodes.py tests/trajectory/test_direct_thermodynamic_family.py tests/recoil/test_coupled_interface.py tests/recoil/test_nonlinear_bose_runtime.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/run_rec_local02_source_bound_gate.py
git diff --exit-code -- artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02/REC_LOCAL_02_EXECUTION.json
```

Expected focused results are `9 passed` and `61 passed`. The regenerated
execution record must be byte-identical.

`python scripts/verify_repo.py --all` is expected to remain non-green because
PR #42 intentionally preserves evidence bytes that the range-whitespace
checker rejects. Do not normalize these files:

- `.../evidence/MUTANT_drop_density_jvp.log`
- `.../rec_local01_admission/preservation_inventory.txt`

Full non-slow collection also requires the declared development dependency
`mpmath`. Missing `mpmath` is an environment blocker, not permission to edit
scientific code or weaken tests.

## Current terminal boundary

The former `STOP_BUDGET_P1_UNRESOLVED` applies only to the historical review
cycle and is superseded for the repaired momentum-owner dependency cone. The
current stop is:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`.

The scalar history has angular rank 1 while the interface requires rank 26.
Deposition selection, moving-map JVP, four-force ledgers, response, and
restart/history transactions remain exactly `NOT_RUN`. Do not claim
`PASS_REC_ISOTROPIC_PHYSICAL_REFERENCE_ONLY`.

Proceed beyond read-only validation only after a new explicit authorization
that supplies either (a) source-defined 26-direction face authority or (b) a
policy decision for the immutable-evidence verifier exception. Keep all PRs
draft, do not merge, and do not mark ready in this handoff.
