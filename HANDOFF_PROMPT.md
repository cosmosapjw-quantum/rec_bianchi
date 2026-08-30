# REC-NEXT-01 portable receipt and directional-face admission continuation

This prompt is the complete locator. Do **not** require or reconstruct
`FETCH_AND_VALIDATE.py`. Preserve every dirty/untracked checkout and evidence
directory; never reset or clean another worktree.

## Git locator

- Repository: `https://github.com/cosmosapjw-quantum/rec_bianchi`
- Delivery branch:
  `agent/research/rec-next01-portable-receipt-20260830`
- Required canonical starting commit:
  `37a943347bf319af998230bb77c6f89827feddff`
- Required starting tree:
  `da1b3062bd3e115df9b55c7fef933b8f8379cd7a`
- Required starting parent:
  `dd0e080400bc76d6c5e6af382717e613a9fb32f8`
- Current-stage manifest:
  `artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/MANIFEST.sha256`

Fetch the delivery branch, require the canonical starting commit to be an
ancestor, require the exact changed path set below, validate the current-stage
manifest, and create a new isolated worktree. A mismatch is
`STOP_INVALID_CONTINUATION_IDENTITY`.

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

The previous momentum-repair manifest binds the previous tree and is immutable
history. Use the current-stage manifest above for this continuation.

## Admitted Phase A state

The receipt portability defect is repaired without changing the scientific
claim:

- the two historical V1 SIMD-dependent receipts remain reproducible for
  forensic comparison only;
- the V2 frequency-moment diagnostics use the tracked-x centre/half-width
  kernel `CENTER_HALFWIDTH_TRACKED_X_BINARY64_V1`;
- raw `momentum_scale` owner bytes and derived locked-energy bytes remain
  distinct exact authorities;
- authoritative source/owner/invariant fields are hashed through a canonical
  projection;
- the two nonauthoritative float diagnostics are validated by a versioned
  formula, operation order, decimal quantum, and closed intervals;
- raw whole-receipt SHA-256 is an archival publication seal, not a portable
  continuation or scientific-authority oracle.

Current digests:

- authority projection:
  `65378bddc8e61389de6abb4a36c418aa526dd06df7ef00b6e74347762cc03462`
- diagnostic contract:
  `1fc6c48a5711a25c8724a598a164a8a20ce9266e3f5cc6fd8fed4a24795961cd`
- raw `momentum_scale` owner:
  `a32194fb664491fb50ecc1f26096d6b7d03d9be153a459c1db218ce4941de409`
- derived locked target energy:
  `19b9b6bb3d3d0657cb71745118ea396dc3cce92ed15491c20df8a9df8d91f8c8`
- current raw receipt publication seal:
  `6fb642751e18a8ad85c3e36f76e3cd4907f2261e4570c64d06d4eeddff1c1272`

Validate portable semantics read-only with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python \
  scripts/run_rec_local02_source_bound_gate.py \
  --check-portable-receipt \
  artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02/REC_LOCAL_02_EXECUTION.json
```

Do not replace this with `git diff` on a regenerated raw JSON file. Exact raw
bytes remain required when checking the fetched publication artifact through
the stage manifest; fresh cross-host recomputation is admitted by matching the
authority and diagnostic-contract digests plus diagnostic validation.

## Phase B coding-research result and stop

The additive module is a fail-closed research spike, not a coupled production
implementation.

- It binds one explicit
  `HYDROGEN_ORTHONORMAL_FRAME_V1` hypothesis and the ordered 26-point grid.
- A finite-tilt Bianchi VI_h witness proves that the existing hydrogen-frame
  and legacy untagged-normal interpretations change inflow ownership on five
  nodes.
- It enforces red inflow `v_red > 0`, blue inflow `v_blue < 0`, and explicit
  grazing classification.
- It executes all 26 nodes on both faces for a frozen-background, zero-source
  manufactured Bianchi-II characteristic problem: 52/52 rays reach their face
  and preserve occupation.
- The result is labelled `GEOMETRY_ONLY_MANUFACTURED`; no physical face array
  is materialized or admitted.
- At the exact macro start, two zero-speed directions require an unimplemented
  event/restart contract and fail closed.

Production integration remains blocked by all of the following:

- `BLOCKED_ANGULAR_FRAME_CONTRACT`
- `BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY`
- `BLOCKED_ANGULAR_REMAP_AUTHORITY` for fixed-node coupling
- `BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT`
- `BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION`
- `SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

Before any physical-face implementation, supply and approve:

1. one production frame/tetrad/measure convention;
2. independently authoritative incoming values on the exact red/blue
   half-ranges;
3. once-only, unit-locked, hash-bound pathwise source channels
   `virtual_spike`, `one_photon`, `two_photon`, and `raman` for
   `j_H(t,nu)`/`chi_H(t,nu)`;
4. either the Lagrangian backtraced sampler boundary or a fixed-node angular
   remap/advection operator with conservation and JVP tests;
5. a speed-zero event/restart policy;
6. an external verifier that resolves every declared digest against the
   approved source/incoming bytes and authority package.

Until then, do not relabel any output as
`SOURCE_IDENTICAL_DIRECTIONAL_FACE`, do not select a deposition map, and do
not enable any downstream operation.

## Validation route

Use Python 3.12 with NumPy 2.4.2, SciPy 1.17.0 and pytest 9.1.1 when available.
Disable bytecode and pytest cache writes.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q \
  tests/trajectory/test_physical_split_reference.py \
  tests/trajectory/test_rec_local02_portable_receipt.py \
  tests/trajectory/test_directional_face_admission.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q \
  tests/trajectory/test_direct_thermodynamic_nodes.py \
  tests/trajectory/test_direct_thermodynamic_family.py \
  tests/recoil/test_coupled_interface.py \
  tests/recoil/test_nonlinear_bose_runtime.py \
  tests/trajectory/test_bianchi_characteristic_face_solver.py \
  tests/trajectory/test_hyrec_source_adapter.py \
  tests/trajectory/test_source_derived_parent.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python \
  scripts/run_rec_next01_coding_research.py \
  --check-record \
  artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research/REC_NEXT_01_CODING_RESEARCH.json
git diff --check
```

Full non-slow collection still requires the declared development dependency
`mpmath`. Do not install it silently and do not weaken tests if it is absent.
The inherited PR #42 evidence-byte failure in `verify_repo.py --all` remains a
documented non-scientific repository-verifier exception; never normalize the
preserved evidence to make that command green.

## Terminal claim and delivery policy

Scientific terminal state remains:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

Claim remains:

`NO_PASS_REC_PHYSICAL_SPLIT`

All downstream operations remain `NOT_RUN`. Keep the delivery PR draft. Do
not merge or mark ready.
