# REC-NEXT-03 local execution prompt

Run exactly one bounded local continuation with a distinct setup and evidence
phase. A single project-specific Git ref materialization and one external
formal-toolchain provisioning phase are permitted before evidence-producing
execution. After a verified setup receipt, do not install or upgrade anything,
access the ordinary network, edit source or tests, regenerate tracked evidence,
normalize preserved files, commit, push, change a PR, merge, or mark a PR
ready.

## Preconditions and immutable identity

Use an existing clone and preserve it. The bootstrap block below materializes
exactly the named delivery branch into the named remote-tracking ref; no other
ref or worktree is changed. After the immutable identity gate passes, the
expressly described external provisioning step may use the network. Every
subsequent test and formal command is network-frozen and evidence-producing.

- repository: `cosmosapjw-quantum/rec_bianchi`
- delivery branch:
  `agent/research/rec-next03-formal-contracts-20260831-r1`
- exact continuation base:
  `6f6ed7720505537c9f404656cb2bc53d117e40ab`
- exact base tree:
  `da55957cfc70f76120724677431b351c5f52d019`
- exact base parent:
  `7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a`
- stage manifest:
  `artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/MANIFEST.sha256`
- expected manifest payload entries: `35`

### One-time ref materialization (before any validator)

Run this block once, from a shell with network access, and preserve its raw
stdout/stderr outside the repository. Do not replace the positive refspec with
a wildcard, fetch all branches, or use `FETCH_HEAD` as an unpinned locator:

```bash
set -euo pipefail
rec_repo=/absolute/path/to/existing/rec_bianchi
rec_delivery_branch=agent/research/rec-next03-formal-contracts-20260831-r1
rec_delivery_ref=refs/remotes/origin/$rec_delivery_branch
: "\${REC_NEXT03_EXPECTED_HEAD:?set from the current GitHub PR readback}"
: "\${REC_NEXT03_EXPECTED_TREE:?set from the current GitHub PR readback}"
rec_bootstrap_log=/absolute/path/to/external-output/rec-next03-bootstrap.log
mkdir -p "$(dirname "$rec_bootstrap_log")"
{
  printf 'remote=origin\nbranch=%s\nref=%s\n' \
    "$rec_delivery_branch" "$rec_delivery_ref"
  git -C "$rec_repo" fetch --no-tags --no-prune origin \
    "+refs/heads/$rec_delivery_branch:$rec_delivery_ref"
  git -C "$rec_repo" show-ref --verify "$rec_delivery_ref"
  rec_fetched_head=$(git -C "$rec_repo" rev-parse "$rec_delivery_ref")
  test "$(git -C "$rec_repo" cat-file -t "$rec_fetched_head")" = commit
  test "$rec_fetched_head" = "$REC_NEXT03_EXPECTED_HEAD"
  test "$(git -C "$rec_repo" rev-parse "$rec_fetched_head^{tree}")" = "$REC_NEXT03_EXPECTED_TREE"
  printf 'fetched_head=%s\n' "$rec_fetched_head"
} >"$rec_bootstrap_log" 2>&1
test -s "$rec_bootstrap_log"
```

If the fetch, ref readback, or object-type check fails, preserve the log and
stop as `STOP_INVALID_CONTINUATION_IDENTITY`. Do not substitute another ref,
reconstruct a bundle, or proceed transcript-only. After this block, disable
ordinary network access except for the explicit provisioning phase that follows
the immutable identity and manifest gate.

Create a new detached worktree at the captured fetched commit. Choose an
explicit safe path; do not use an existing or preserved worktree:

```bash
set -euo pipefail
rec_repo=/absolute/path/to/existing/rec_bianchi
rec_worktree=/absolute/path/to/new/rec-next03-validation
test ! -e "$rec_worktree"
rec_delivery_ref=refs/remotes/origin/agent/research/rec-next03-formal-contracts-20260831-r1
git -C "$rec_repo" show-ref --verify "$rec_delivery_ref"
rec_fetched_head=$(git -C "$rec_repo" rev-parse "$rec_delivery_ref")
git -C "$rec_repo" worktree add --detach "$rec_worktree" "$rec_fetched_head"
cd "$rec_worktree"
```

Validate the continuation and exact delivery paths before running anything:

```bash
set -euo pipefail
rec_base=6f6ed7720505537c9f404656cb2bc53d117e40ab
rec_tree=da55957cfc70f76120724677431b351c5f52d019
rec_parent=7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a
test "$(git rev-parse "$rec_base^{tree}")" = "$rec_tree"
test "$(git rev-parse "$rec_base^")" = "$rec_parent"
git merge-base --is-ancestor "$rec_base" HEAD

rec_expected_delivery_paths='HANDOFF_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/LOCAL_EXECUTION_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/MANIFEST.sha256
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/REC_NEXT_03_RESEARCH_AND_CODING_RECORD.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/RESULTS.json
docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md
formal/rec_next03/CONTRACT.md
formal/rec_next03/OBLIGATIONS.json
formal/rec_next03/README.md
formal/rec_next03/SOURCE_MAP.json
formal/rec_next03/TOOLCHAINS.lock.json
formal/rec_next03/lean/RecNext03.lean
formal/rec_next03/lean/RecNext03/All.lean
formal/rec_next03/lean/RecNext03/Contracts.lean
formal/rec_next03/lean/lakefile.toml
formal/rec_next03/lean/lean-toolchain
formal/rec_next03/prompts/lean.json
formal/rec_next03/prompts/rocq.json
formal/rec_next03/prompts/sage.json
formal/rec_next03/prompts/wolfram.json
formal/rec_next03/rocq/All.v
formal/rec_next03/rocq/RecNext03Contracts.v
formal/rec_next03/rocq/_CoqProject
formal/rec_next03/rocq/rocq-toolchain
formal/rec_next03/sage/verify_remap_event.sage
formal/rec_next03/wolfram/verify_frame_face_event.wls
scripts/provision_rec_next03_formal_toolchains.py
scripts/run_rec_next03_formal_contracts.py
src/full_bianchi_hyrec/trajectory/directional_face_admission.py
src/full_bianchi_hyrec/trajectory/directional_source_assembly.py
src/full_bianchi_hyrec/trajectory/hyrec_source_adapter.py
src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py
src/full_bianchi_hyrec/trajectory/paired_source_transfer.py
tests/trajectory/test_directional_face_admission.py
tests/trajectory/test_directional_source_assembly.py
tests/trajectory/test_paired_source_transfer.py'
test "$(git diff --name-only "$rec_base" HEAD)" = \
  "$rec_expected_delivery_paths"
test -z "$(git status --porcelain)"

rec_manifest=artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/MANIFEST.sha256
test -f "$rec_manifest"
test "$(awk 'NF {count += 1} END {print count + 0}' "$rec_manifest")" = \
  "35"
sha256sum -c "$rec_manifest"
git diff --check
```

Any ancestry, tree, parent, exact-path, manifest-count, manifest-byte, dirty-
worktree, or diff-check mismatch is `STOP_INVALID_CONTINUATION_IDENTITY`.
Preserve the output and stop. Do not repair the checkout.

## LOCAL_CODEX_PROVISIONING

This is the only setup window after the delivery identity/manifest gate and
before all evidence-producing commands. Local Codex is explicitly authorized
to install the missing formal prerequisites, but it must put every mutation,
download, package-manager log, and setup receipt in a new caller-selected
directory outside all Git worktrees. It may not modify this worktree, install
or relicense Wolfram Engine, alter a scientific claim, or run a backend outside
the formal runner.

First verify the exact xAct archive and provision the exact Lean/mathlib lane.
The provisioner installs Lean `leanprover/lean4:v4.33.0` through an existing
`elan` launcher into a private `ELAN_HOME`, copies the checked-in Lean sources
to an external workspace, performs the one permitted `lake update` there, and
requires the resulting clean mathlib checkout at
`db584cd6d46c92f209a44c0f1c829460d327499d`.

```bash
set -euo pipefail
rec_toolchain_root=/absolute/path/outside/git/rec-next03-toolchains
rec_xact_archive=/absolute/path/to/xAct_1.3.0.tgz

python scripts/provision_rec_next03_formal_toolchains.py --plan \
  --toolchain-root "$rec_toolchain_root" \
  --xact-archive "$rec_xact_archive"

python scripts/provision_rec_next03_formal_toolchains.py --provision \
  --allow-network \
  --toolchain-root "$rec_toolchain_root" \
  --xact-archive "$rec_xact_archive"

python scripts/provision_rec_next03_formal_toolchains.py --check \
  --toolchain-root "$rec_toolchain_root" \
  --xact-archive "$rec_xact_archive"

export ELAN_HOME="$rec_toolchain_root/elan"
export PATH="$ELAN_HOME/bin:$PATH"
export REC_NEXT03_LEAN_WORKSPACE="$rec_toolchain_root/lean-workspace"
```

If `elan`, Git, Make, a user/network namespace utility, Sage/Singular, or
Rocq 9.2.0 is missing, local Codex may install only that prerequisite using the
host's official package manager or an external per-user switch. It must record
the exact command, package/source, resulting executable path, and version in
`$rec_toolchain_root` before returning to this prompt. No system-wide or
unrecorded version substitution establishes a pass. Wolfram Engine remains a
licensed host dependency: Codex may use an existing installation but may not
download, activate, or relicense it.

After the check passes, disable ordinary network access. `lake update`, package
installation, Git fetch/pull, and all dependency resolution are forbidden for
the remaining tests and formal run. The runner independently checks the child
network-namespace inode, live `socket.if_nameindex()` result, and routes; an
inherited `/sys/class/net` view is diagnostic only.

## LOCAL_EXECUTION_REQUIRED

### 1. Record the Ryzen/NumPy lane

The Ryzen 9 5900X normally provides X86_V3/AVX2 and not
X86_V4/AVX-512. Absence of X86_V4 is `HOST_LANE_UNAVAILABLE`, not a V2
scientific failure.

```bash
env -u NPY_DISABLE_CPU_FEATURES \
  PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
from numpy._core._multiarray_umath import __cpu_features__
for name in ("X86_V3", "X86_V4", "AVX2", "AVX512F"):
    print(name, bool(__cpu_features__.get(name, False)))
PY
```

Do not force or emulate an unavailable AVX-512/X86_V4 lane. Native and
X86_V4-disabled forensic probes may both produce the historical X86_V3
fingerprint on this CPU.

### 2. Run the focused host-aware and new-contract tests

Use the provisioned or already-installed Python 3.12.13, NumPy 2.4.2, SciPy
1.17.0, and pytest 9.1.1 environment. After the provisioning boundary, do not
install `mpmath` or any missing dependency.

```bash
env -u NPY_DISABLE_CPU_FEATURES \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python -m pytest -p no:cacheprovider -q \
  tests/trajectory/test_physical_split_reference.py \
  tests/trajectory/test_rec_local02_portable_receipt.py \
  tests/trajectory/test_directional_face_admission.py \
  tests/trajectory/test_directional_source_assembly.py \
  tests/trajectory/test_paired_source_transfer.py \
  tests/trajectory/test_hyrec_source_adapter.py \
  tests/trajectory/test_hyrec_two_photon_raman.py
```

Required semantic result: every selected test that is applicable to the
installed host lane passes. An unavailable V1 X86_V4 lane must be reported as
unavailable according to the host-aware contract, not fabricated.

Run the inherited directly affected dependency cone:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python -m pytest -p no:cacheprovider -q \
  tests/trajectory/test_direct_thermodynamic_nodes.py \
  tests/trajectory/test_direct_thermodynamic_family.py \
  tests/recoil/test_coupled_interface.py \
  tests/recoil/test_nonlinear_bose_runtime.py \
  tests/trajectory/test_bianchi_characteristic_face_solver.py \
  tests/trajectory/test_hyrec_source_adapter.py \
  tests/trajectory/test_source_derived_parent.py
```

The inherited expected count was `68 passed`. If the selected files have
changed in the fetched delivery, report the collected/pass/fail counts without
editing expectations.

### 3. Re-run the semantic validators read-only

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python \
  scripts/run_rec_local02_source_bound_gate.py \
  --check-portable-receipt \
  artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02/REC_LOCAL_02_EXECUTION.json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python \
  scripts/run_rec_next01_coding_research.py \
  --check-record \
  artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/REC_NEXT_01_CODING_RESEARCH.json
```

The REC-NEXT-01 semantic digest must remain
`9284ed5b59437d474c293a9ecae24442ca31dc0ebad51432a959e22ccaf069d2`.
Do not regenerate either tracked JSON. Raw JSON hashes remain archival seals;
the documented canonical semantic projections govern fresh recomputation.

### 4. Validate and execute the formal package outside Git

The local host is expected to provide Wolfram+xAct, Sage+Singular,
Lean+mathlib, and Rocq. First run the repository-only contract checker:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  scripts/run_rec_next03_formal_contracts.py --check-contract \
  > /tmp/rec-next03-check-contract.json
```

Then create a new empty output directory outside every Git repository and run
all backends through the isolated runner. Point the variables below at the
provisioned offline inputs and at a distinct nonexistent rebuild path inside
that output directory; do not download or update anything during this phase:

```bash
rec_formal_output="$(mktemp -d /var/tmp/rec-next03-formal.XXXXXX)"
: "${rec_toolchain_root:?reuse the verified provisioning root}"
: "${rec_xact_archive:?reuse the verified xAct archive path}"
export REC_NEXT03_XACT_ARCHIVE="$rec_xact_archive"
export REC_NEXT03_LEAN_WORKSPACE="$rec_toolchain_root/lean-workspace"
export ELAN_HOME="$rec_toolchain_root/elan"
export PATH="$ELAN_HOME/bin:$PATH"
export REC_NEXT03_LEAN_REBUILD_WORKSPACE="$rec_formal_output/lean-rebuild-workspace"
rec_wolfram_license_wait_seconds=3600
rec_wolfram_license_poll_seconds=30
test ! -e "$REC_NEXT03_LEAN_REBUILD_WORKSPACE"
test "$(sha256sum "$REC_NEXT03_XACT_ARCHIVE" | awk '{print $1}')" = \
  7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be
test -f "$REC_NEXT03_LEAN_WORKSPACE/lake-manifest.json"
test -d "$REC_NEXT03_LEAN_WORKSPACE/.lake/packages/mathlib"
test "$(git -C "$REC_NEXT03_LEAN_WORKSPACE/.lake/packages/mathlib" rev-parse HEAD)" = \
  db584cd6d46c92f209a44c0f1c829460d327499d
git -C "$REC_NEXT03_LEAN_WORKSPACE/.lake/packages/mathlib" diff --quiet
git -C "$REC_NEXT03_LEAN_WORKSPACE/.lake/packages/mathlib" diff --cached --quiet

PYTHONDONTWRITEBYTECODE=1 python \
  scripts/run_rec_next03_formal_contracts.py \
  --run-all \
  --output-dir "$rec_formal_output" \
  --timeout-seconds 3600 \
  --wolfram-license-wait-seconds "$rec_wolfram_license_wait_seconds" \
  --wolfram-license-poll-seconds "$rec_wolfram_license_poll_seconds" \
  > "$rec_formal_output.console.json"
printf '%s\n' "$rec_formal_output"
```

The runner copies formal inputs into `$rec_formal_output`; it confines homes,
caches, temporary state, builds, logs, version probes, backend reports, and
`formal-run.json` there. For Lean it verifies the unique manifest entry and
the exact clean official mathlib source commit, makes a separate output-only
copy, purges every pre-existing build artifact, then performs a network-
disabled clean dependency rebuild and aggregate compile. Pre-materialized
`.olean` files are never trusted. The runner clears inherited Lean, Rocq,
Python, Sage, and user-package search-path overrides; Rocq additionally seals
the resolved 9.2 Stdlib root and selected module bytes. Do not run `lake
update`, fetch mathlib, install xAct, or write generated files under
`formal/rec_next03`.

An observed Wolfram license-slot or activation-availability message is not a
formal counterexample. The runner preserves its per-attempt logs and waits only
for that classified external condition, at most
`$rec_wolfram_license_wait_seconds` seconds in
`$rec_wolfram_license_poll_seconds`-second polls. It must not activate,
relicense, install, or terminate another Wolfram job. If the deadline expires,
record the Wolfram backend as `ENVIRONMENT_GAP` and continue the remaining
backend receipts; any non-license Wolfram command failure remains `FAIL`.

Every evidence-producing external command must run inside the runner's
verified OS network namespace. Dead proxy variables, Git URL rewrites, and an
inherited `/sys/class/net` mount alone are insufficient. The runner requires a
child namespace inode distinct from the parent, a live socket interface index
of exactly `lo`, and no non-loopback route. If the host cannot establish and
probe that boundary, record `ENVIRONMENT_GAP` and exit `69`; do not execute the
backend outside isolation or synthesize a PASS.

A backend PASS establishes only the encoded conditional identity. It does not
establish source bytes, implementation parity, physical authority, production
admission, or a scientific pass. A missing/wrong local toolchain is recorded
as `ENVIRONMENT_GAP` (exit `69`) or `TOOLCHAIN_MISMATCH` (exit `65`); do not
synthesize a PASS. Lean must report 4.33.0 with mathlib `v4.33.0` at official
commit `db584cd6d46c92f209a44c0f1c829460d327499d`, rebuilt from verified source
inside the output directory. Rocq must report 9.2.0, and xAct must load from
the exact archive seal above. Wolfram, Sage, and Singular runtime versions are
captured verbatim in the receipt. Lean's exact 25 `#print axioms` and Rocq's
exact 25 `Print Assumptions` results must stay within their narrow pinned
foundation allowlists.

### 5. Final read-only state check and report

```bash
test -z "$(git status --porcelain)"
sha256sum -c \
  artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/MANIFEST.sha256
git diff --check
```

Report:

- checked-out HEAD/tree and exact-path result;
- manifest result;
- CPU feature readback;
- each pytest command's collected/pass/fail/skip counts;
- both semantic validator results and semantic digest;
- `formal-run.json` overall status plus each backend status/version;
- confirmation that the worktree stayed clean;
- no scientific or PR-state promotion.

Preserve raw local output outside the worktree. Run no retries unless a failure
has a materially different, documented cause; one equivalent repeat exhausts
this handoff budget.

## EXTERNAL_AUTHORITY_REQUIRED

Local execution cannot resolve the following. Do not convert any local CAS,
kernel, checksum, manufactured vector, mode string, boolean, or digest-shaped
declaration into authority:

1. authenticated normal/hydrogen tetrad and frequency convention;
2. source-identical incoming data on the exact red/blue half-ranges;
3. a byte-locked `Delta_f` reference field/adapter/JVP and complete
   one-photon/two-photon/Raman source/deposition ownership ledger;
4. approved once-only `n_H/mu_i` deposition, profile normalization, bin
   ownership, and resonant-channel exclusions;
5. an executable approved Lagrangian backtraced sampler, or fixed-node
   remap/advection with positivity, conservation, and JVP;
6. distinct turning/red/blue plus simultaneous/tangential accepted
   event/restart semantics;
7. an external verifier resolving every prerequisite to approved immutable
   source bytes and executable contracts.

Until those records exist, do not begin production Rust integration, do not
use JAX as a load-bearing path, and do not materialize or admit a physical
directional face.

Scientific terminal:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

Claim: `NO_PASS_REC_PHYSICAL_SPLIT`

Keep the delivery PR draft. Do not merge or mark it ready. All downstream
scientific, performance, and publication stages remain `NOT_RUN`.
