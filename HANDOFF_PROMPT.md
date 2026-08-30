# REC-NEXT-02 host-aware receipt validation continuation

This file is the complete local-execution prompt and locator. Preserve every
dirty or untracked checkout and evidence directory. Never reset, clean,
normalize, or regenerate preserved evidence. Work only in a new isolated
worktree.

## 1. Exact Git identity

- Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi`
- Delivery branch:
  `agent/fix/rec-next01-host-portability-policy-20260830-r1`
- Draft PR base:
  `agent/research/rec-next01-portable-receipt-20260830`
- Required REC-NEXT-02 base commit:
  `7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a`
- Required base tree:
  `99fafd552041a4df277179667a910632755d84e2`
- Required base parent:
  `37a943347bf319af998230bb77c6f89827feddff`
- New stage manifest:
  `artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next02_host_portability/MANIFEST.sha256`

Require the base commit to be an ancestor of the delivery HEAD. Require its
tree and parent above. The inherited PR #45 diff from the base parent to the
base commit must be exactly these 11 paths:

```text
HANDOFF_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02/REC_LOCAL_02_EXECUTION.json
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/MANIFEST.sha256
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/REC_NEXT_01_CODING_RESEARCH.json
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/REC_NEXT_01_CODING_RESEARCH_RECORD.md
scripts/run_rec_local02_source_bound_gate.py
scripts/run_rec_next01_coding_research.py
src/full_bianchi_hyrec/trajectory/directional_face_admission.py
src/full_bianchi_hyrec/trajectory/physical_split_reference.py
tests/trajectory/test_directional_face_admission.py
tests/trajectory/test_rec_local02_portable_receipt.py
```

The delivery diff from `7adb61ed...` to delivery HEAD must be exactly these
eight paths:

```text
AGENTS.md
HANDOFF_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next02_host_portability/MANIFEST.sha256
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next02_host_portability/REC_NEXT_02_RESEARCH_AND_CODING_RECORD.md
docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md
src/full_bianchi_hyrec/trajectory/directional_face_admission.py
tests/trajectory/test_directional_face_admission.py
tests/trajectory/test_rec_local02_portable_receipt.py
```

Any ancestry, tree, parent, path-set, or manifest mismatch is
`STOP_INVALID_CONTINUATION_IDENTITY`.

After checking out the delivery branch in the isolated worktree, run this
fail-fast identity check:

```bash
set -euo pipefail
rec_base=7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a
rec_parent=37a943347bf319af998230bb77c6f89827feddff
rec_tree=99fafd552041a4df277179667a910632755d84e2
test "$(git rev-parse "${rec_base}^{tree}")" = "$rec_tree"
test "$(git rev-parse "${rec_base}^")" = "$rec_parent"
git merge-base --is-ancestor "$rec_base" HEAD

rec_expected_base_paths='HANDOFF_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02/REC_LOCAL_02_EXECUTION.json
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/MANIFEST.sha256
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/REC_NEXT_01_CODING_RESEARCH.json
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/REC_NEXT_01_CODING_RESEARCH_RECORD.md
scripts/run_rec_local02_source_bound_gate.py
scripts/run_rec_next01_coding_research.py
src/full_bianchi_hyrec/trajectory/directional_face_admission.py
src/full_bianchi_hyrec/trajectory/physical_split_reference.py
tests/trajectory/test_directional_face_admission.py
tests/trajectory/test_rec_local02_portable_receipt.py'
test "$(git diff --name-only "$rec_parent" "$rec_base")" = \
  "$rec_expected_base_paths"

rec_expected_delivery_paths='AGENTS.md
HANDOFF_PROMPT.md
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next02_host_portability/MANIFEST.sha256
artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next02_host_portability/REC_NEXT_02_RESEARCH_AND_CODING_RECORD.md
docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md
src/full_bianchi_hyrec/trajectory/directional_face_admission.py
tests/trajectory/test_directional_face_admission.py
tests/trajectory/test_rec_local02_portable_receipt.py'
test "$(git diff --name-only "$rec_base" HEAD)" = \
  "$rec_expected_delivery_paths"
test -z "$(git status --porcelain)"
```

The REC-NEXT-01 manifest binds base bytes. Because REC-NEXT-02 intentionally
changes three files that it covered, verify that old manifest from a temporary
archive of the exact base, not from delivery HEAD:

```bash
set -euo pipefail
rec_prev_stage="$(mktemp -d)"
git archive 7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a |
  tar -x -C "$rec_prev_stage"
(
  cd "$rec_prev_stage"
  sha256sum -c \
    artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/MANIFEST.sha256
)
```

Verify the new fetched publication bytes from delivery HEAD with:

```bash
set -euo pipefail
sha256sum -c \
  artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next02_host_portability/MANIFEST.sha256
git diff --check
```

The new manifest intentionally excludes its own entry. Its bytes are bound by
the fetched Git tree and post-push readback; its seven listed payloads are
bound by SHA-256.

## 2. Identity contract

Read `AGENTS.md` and
`docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md` before changing any gate.

| Class | REC object | Required relation |
|---|---|---|
| 1 | tracked source/NPZ bytes, raw owner, locked energy | byte exact |
| 2 | fetched receipt, records, prompt, and manifest payloads | byte exact through the applicable stage manifest |
| 3 | freshly recomputed V2 diagnostics and coding semantics | authority/diagnostic projections, formula contract, invariants, and frozen intervals |
| 4 | host paths, timing, JSON presentation, unsealed host record digest | content/structural only unless explicitly sealed |

The historical V1 JSON hashes are conditional forensic fingerprints, not
portable scientific authority:

- actual NumPy X86_V4 lane: exact `7bf0ebf143589b45308f5e0157a80ff842dc99783b5207748732f332a6c12912`;
- actual NumPy X86_V3 lane: exact `1ea93ca2c007209ad25ca6cafcd76d0616a9a4cc88319d56d18f43a03e930e9d`;
- neither known lane: `HOST_LANE_UNAVAILABLE`; do not fabricate or require a
  historical fingerprint.

Every host must still pass the V2 authority, diagnostic-contract, invariant,
status, claim, and blocker checks. A missing V1 hardware lane is not a V2 PASS
or FAIL.

Current load-bearing values remain:

- authority projection `65378bddc8e61389de6abb4a36c418aa526dd06df7ef00b6e74347762cc03462`;
- diagnostic contract `1fc6c48a5711a25c8724a598a164a8a20ce9266e3f5cc6fd8fed4a24795961cd`;
- raw `momentum_scale` owner `a32194fb664491fb50ecc1f26096d6b7d03d9be153a459c1db218ce4941de409`;
- locked target energy `19b9b6bb3d3d0657cb71745118ea396dc3cce92ed15491c20df8a9df8d91f8c8`;
- V2 raw fetched-artifact seal `6fb642751e18a8ad85c3e36f76e3cd4907f2261e4570c64d06d4eeddff1c1272`.

## 3. What changed

- The forensic regression reads the actual NumPy X86_V4/X86_V3 feature lane.
  It asserts only a fingerprint that can exist on that host.
- A caller-provided `NPY_DISABLE_CPU_FEATURES=X86_V4` mask is preserved by the
  native probe.
- Exact macro-start zero drift now raises typed
  `FrequencySpeedZeroEventRequired` carrying ordered nodes `(0, 1)`.
- The four supplied progress/audit/identity/checkpoint directives are compiled
  into one repository policy plus a short agent map.

Nothing changes V2 arithmetic, evidence, tolerance, source authority, 52-ray
geometry, physical admission, or the scientific claim.

## 4. Ryzen 9 5900X local validation

Use Python 3.12.13, NumPy 2.4.2, SciPy 1.17.0, and pytest 9.1.1. Do not install
or upgrade dependencies. Remove an inherited NumPy dispatch mask only for the
native capability/readback and focused command:

```bash
env -u NPY_DISABLE_CPU_FEATURES python - <<'PY'
from numpy._core._multiarray_umath import __cpu_features__
for name in ("X86_V3", "X86_V4", "AVX2", "AVX512F"):
    print(name, bool(__cpu_features__.get(name, False)))
PY

env -u NPY_DISABLE_CPU_FEATURES \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python -m pytest -p no:cacheprovider -q \
  tests/trajectory/test_physical_split_reference.py \
  tests/trajectory/test_rec_local02_portable_receipt.py \
  tests/trajectory/test_directional_face_admission.py
```

Expected on Ryzen 9 5900X: X86_V3/AVX2 true, X86_V4/AVX512F false, focused
suite `38 passed`. Both native and explicit X86_V4-disabled child probes may
legitimately reproduce the same X86_V3 forensic SHA.

Run the directly affected dependency cone:

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

Expected: `68 passed`.

Run both semantic checks read-only:

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

Do not regenerate either tracked JSON to perform a semantic check. Do not run
an unbounded retry loop. A missing `mpmath` remains an environment gap; do not
install it or weaken a test in this cycle. The inherited PR #42 evidence-byte
exception must not be normalized.

## 5. Scientific firewall and stop

Manufactured geometry remains 52/52 rays with zero occupation residual, but no
physical face is materialized or admitted. Production integration still lacks:

1. an approved frame/tetrad/frequency convention;
2. authoritative incoming values on the exact red/blue half-ranges;
3. unit-locked, hash-bound `virtual_spike`, `one_photon`, `two_photon`, and
   `raman` source laws for `j_H`/`chi_H`;
4. Lagrangian boundary semantics or fixed-node remap/advection with
   conservation and JVP tests;
5. a speed-zero event/restart policy;
6. an external verifier resolving declarations to approved bytes.

The local-only next action is exactly one read-only Ryzen validation run:
preserve the feature readback and command stdout, report them, and stop. Do not
change code merely because both V1 probes produce the X86_V3 fingerprint.
Rust/JAX work and physical integration remain prohibited until one complete,
independently verifiable authority package resolves all six prerequisites.

Scientific terminal:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

Claim:

`NO_PASS_REC_PHYSICAL_SPLIT`

All downstream operations remain `NOT_RUN`. Keep every delivery PR draft. Do
not merge or mark ready.
