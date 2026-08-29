# Codex handoff — rec_bianchi split-domain bootstrap

```text
repository: cosmosapjw-quantum/rec_bianchi
base main: 5a09f3797210284f83a1a1adb0e0092d1ac48475
base tree: 4002915ad851afc2ab71f94a882cc99d81748062
audit source: 4cd2c7bff00ca91c57997d7e6e1ff4c67f7fccd3
audit tree: 3f8731cfab9c9493fcdaa18d855d95768eee1d47
exact next action: PR05C2C1B2B1E1C_BOOTSTRAP_RED
claim: NO_PASS_SPLIT_DOMAIN_REPLACEMENT
```

## Preserve

Use an authenticated clone and a new isolated worktree. Preserve all existing
untracked files and worktrees. Do not clean, reset, stash, rebase, amend,
force-push or merge the complete audit branch.

## Intake

Fetch the package branch and verify its exact commit/tree from the separate
publication receipt. Materialize this directory, run its manifest, offline
validator and `--live` validator.

Then run:

```bash
./scripts/bootstrap_sandbox.sh --offline
python scripts/check_remote_state.py
python scripts/check_hyrec_binary_hash_policy.py
python scripts/check_commit_range_whitespace.py
if test -f scripts/check_imports.py; then PYTHONPATH=src python scripts/check_imports.py; fi
python scripts/verify_repo.py --quick
pytest -q \
  tests/recoil/test_nonlinear_bose_release.py \
  tests/recoil/test_nonlinear_bose_runtime.py \
  tests/trajectory/test_adaptive_canonical_macro.py \
  tests/trajectory/test_causal_characteristic_history.py \
  tests/trajectory/test_characteristic_angular_solver.py \
  tests/trajectory/test_full_coupled_transport.py \
  tests/trajectory/test_pseudotransient_continuation.py
```

The audit-reported 51 focused and 884 full passes are carried evidence only.
Record actual fresh counts.

## Execute

Follow `PACKAGE.json#implementation_plan` and `PACKAGE.json#work_units`. Start with genuine
split-domain RED, then implement the one-owner replacement, targeted proof,
bounded dual review, at most one repair, ordinary push and one draft PR.

Do not start the dynamic macro, preconditioner selection or Rust optimization.
Do not import BASS kinetic code. Reuse only generic BASS verification rules in
`PACKAGE.json#method_transfer`.

## Cross-repo boundary

`rei_bianchi` may monitor this branch but cannot import rates, histories or
activate a recombination adapter. Only a terminal
`PASS_PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT` may populate the provisional
rec→rei export schema.

Final headings:

```text
STATUS
ACTUAL PROGRESS
VERIFIED
DEFERRED
BLOCKERS
NEXT
```
