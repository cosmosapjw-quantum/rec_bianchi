# REC-NEXT-03 formal/source-contract continuation

This is the prompt-only locator for one bounded local validation. Preserve all
existing checkouts and evidence. Before evidence-producing execution, exactly
one project-specific Git ref materialization and one bounded external
toolchain-provisioning phase are allowed. After a verified setup receipt, work
in a new detached worktree with network disabled. Do not edit, regenerate,
normalize, commit, push, merge, or mark a PR ready.

## Immutable continuation identity

- repository: `https://github.com/cosmosapjw-quantum/rec_bianchi`
- delivery branch:
  `agent/research/rec-next03-formal-contracts-20260831-r1`
- stacked Draft-PR base branch:
  `agent/fix/rec-next01-host-portability-policy-20260830-r1`
- exact continuation base:
  `6f6ed7720505537c9f404656cb2bc53d117e40ab`
- exact base tree:
  `da55957cfc70f76120724677431b351c5f52d019`
- exact base parent:
  `7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a`
- stage manifest:
  `artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/MANIFEST.sha256`
- manifest payload entries: `35`

The delivery diff from the exact continuation base to the materialized delivery HEAD
must contain exactly these 36 paths:

```text
HANDOFF_PROMPT.md
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
tests/trajectory/test_paired_source_transfer.py
```

Before executing any validator, require the base tree and parent above, base
ancestry, the exact path set, a clean worktree, 35 manifest entries, and
`sha256sum -c` success. Any mismatch is
`STOP_INVALID_CONTINUATION_IDENTITY`; preserve it and stop.

## Bootstrap/ref-materialization contract

The prior local run stopped before intake because it required the delivery
remote-tracking ref while simultaneously forbidding the only operation that
could create it. That was a valid `STOP_INVALID_CONTINUATION_IDENTITY`, not a
scientific result. The repair is limited to the pre-intake bootstrap boundary.

Before reading the stage prompt or running any validator, run exactly one
network-enabled fetch with this positive refspec:

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

The fetch may update only that exact remote-tracking ref. A missing ref,
non-commit object, fetch error, or readback mismatch is terminal:
`STOP_INVALID_CONTINUATION_IDENTITY`. Preserve the log; do not fetch a
wildcard, use an alternate ref, reconstruct a bundle, or continue from a
transcript. Capture the fetched commit OID and create the detached worktree
from that OID. After the delivery identity and manifest pass, perform the
explicit provisioning phase below; then disable network access before all
evidence-producing tests and formal commands.

## Local Codex provisioning boundary

The local Codex executor is authorized to provision missing formal
prerequisites only in a caller-selected directory outside all Git worktrees.
This setup is not scientific evidence and must finish before the frozen
validation phase. The entrypoint is:

```bash
python scripts/provision_rec_next03_formal_toolchains.py --provision \
  --allow-network \
  --toolchain-root /absolute/path/outside/git/rec-next03-toolchains \
  --xact-archive /absolute/path/to/xAct_1.3.0.tgz
```

It installs only the exact Lean `v4.33.0` lane into an external `ELAN_HOME`,
materializes the locked mathlib `v4.33.0` checkout, validates its resolved
commit and clean origin, and seals the supplied xAct archive. If a host
prerequisite is absent, local Codex may install only the recorded prerequisite
needed for this contract (elan launcher, Git, Make, user/network namespace
utility, Sage/Singular, or Rocq 9.2.0 in an external switch); it must preserve
the package-manager command and resulting executable/version outside Git. It
must not install or relicense Wolfram Engine, substitute an unpinned formal
runtime, alter the repository, or run tests as part of setup.

After `--check` reports the exact workspace, export its private ELAN_HOME and
workspace path for the formal runner, disable ordinary network access, and
run the evidence contract. The runner itself independently verifies a distinct
user/network namespace through its namespace inode, live socket interfaces,
and routes; an inherited `/sys/class/net` view is diagnostic only.
If an existing local Wolfram job temporarily occupies the license, the runner
records the classified attempt and waits for at most 3600 seconds in 30-second
polls before resuming that backend. It never activates, relicenses, installs,
or terminates another Wolfram job. An exhausted wait is `ENVIRONMENT_GAP`, not
a formal `FAIL` or a synthetic pass.

The complete fail-fast commands, Ryzen 9 5900X host-lane procedure, pytest
focus and dependency cone, read-only receipt validators, isolated formal
runner, output schema, retry budget, and external-authority stop conditions
are in:

`artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next03_formal_source_contracts/LOCAL_EXECUTION_PROMPT.md`

Read that file only after its bytes pass the manifest. Follow it verbatim.

## Delivered boundary

This stage provides research-only typed source assembly, a nonauthoritative
signed-opacity transfer primitive, formal obligations, and isolated Wolfram+
xAct, Sage+Singular, Lean+mathlib, and Rocq runners. The Lean lane is pinned to
mathlib `v4.33.0` at official commit
`db584cd6d46c92f209a44c0f1c829460d327499d` and must rebuild from verified
offline source inside the external output directory; prebuilt `.olean` files
are not trusted.

No formal proof, manufactured ray, checksum, proposed ID, or local declaration
is source authority. The delivery does not provide the authenticated tetrad,
incoming half-range source bytes, reference-field adapter, once-only packet
deposition ledger, approved Lagrangian sampler or fixed-node remap, or accepted
multi-surface event/restart authority. It therefore does not materialize or
admit a physical face and does not authorize production Rust integration.

Scientific terminal:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

Claim: `NO_PASS_REC_PHYSICAL_SPLIT`.

Keep the delivery PR Draft. Do not merge or change ready state.
