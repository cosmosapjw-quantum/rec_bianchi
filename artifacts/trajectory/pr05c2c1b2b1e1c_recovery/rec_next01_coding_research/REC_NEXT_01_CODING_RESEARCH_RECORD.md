# REC-NEXT-01 coding research record

## Task contract

- Date: 2026-08-30
- Task layers: `diagnose -> design -> implement -> validate -> review -> document`
- User-visible outcome: repair the receipt portability contract and turn the
  directional-face research result into an executable, fail-closed coding
  spike.
- In scope: REC-LOCAL-02 receipt arithmetic/schema/validation, a nonproduction
  26-ordinate admission and geometry witness, tests, runners, evidence and
  handoff.
- Out of scope: selecting a physical deposition map, inventing physical
  `j_H/chi_H`, choosing a production angular-frame convention, adding fixed-node
  angular remap/advection, enabling downstream coupled operations, merge or
  ready transition.
- Preserved behavior: eight tracked source hashes, raw momentum owner, locked
  energy owner, zero number/locked-energy certificate, status, claim, physical
  blocker and all `NOT_RUN` operations.
- Completion bar: RED-first tests, focused and affected regression, numerical
  portability mutants, reproducible artifacts, independent diff/science review
  and explicit HOLD/PASS boundary.

## Canonical start and isolation

- Canonical commit:
  `37a943347bf319af998230bb77c6f89827feddff`
- Canonical tree:
  `da1b3062bd3e115df9b55c7fef933b8f8379cd7a`
- Parent:
  `dd0e080400bc76d6c5e6af382717e613a9fb32f8`
- Branch:
  `agent/research/rec-next01-portable-receipt-20260830`
- Isolated worktree:
  `/workspace/scratch/80ad147e66a7/worktrees/rec-next01-code-research-20260830`
- The canonical ancestry, tree, exact prior six-path diff and prior manifest
  passed before implementation. Existing checkouts and preserved evidence were
  not reset, cleaned or normalized.

## Reproduction acceptance

With Python 3.12.3, NumPy 2.4.2 and SciPy 1.17.0, toggling only
`NPY_DISABLE_CPU_FEATURES=X86_V4` reproduced the two historical V1 artifacts:

| Dispatch | Direct measure diagnostic | Legacy centroid diagnostic (eV) | Raw JSON SHA-256 |
|---|---:|---:|---|
| default X86_V4 | `1.0881876986956445e-08` | `5.545800263462297e-08` | `7bf0ebf143589b45308f5e0157a80ff842dc99783b5207748732f332a6c12912` |
| X86_V4 disabled | `1.0878134039731587e-08` | `5.5440194657307984e-08` | `1ea93ca2c007209ad25ca6cafcd76d0616a9a4cc88319d56d18f43a03e930e9d` |

All source/owner/invariant/claim fields were unchanged. This confirms a receipt
portability defect, not continuation or scientific-state corruption.

## Phase A implementation

The V2 receipt uses the tracked interval center and half-width directly:

\[
m=\nu_0+\frac{x_h+x_l}{2}\Delta\nu,qquad
d=\frac{x_h-x_l}{2}\Delta\nu,
\]

\[
M=\frac{16\pi d}{c^3}\left(m^2+\frac{d^2}{3}\right),qquad
\bar\nu=m\frac{m^2+d^2}{m^2+d^2/3}.
\]

The scalar binary64 operation and ascending-cell reduction order are versioned
as `CENTER_HALFWIDTH_TRACKED_X_BINARY64_V1`. The resulting diagnostics are:

- direct measure mismatch: `1.0868674430328898e-08`;
- centroid-to-locked-owner gap: `5.539951786204256e-08 eV`.

The receipt now separates:

1. exact tracked source hashes;
2. raw `momentum_scale` and derived locked-energy owner hashes;
3. a canonical authority projection of owner/invariant/claim/blocker fields;
4. a static diagnostic contract and dynamic nonauthoritative diagnostics;
5. the raw whole-JSON publication checksum.

An in-interval diagnostic mutation can change raw artifact bytes while leaving
portable authority unchanged. Owner, source, invariant, formula, dtype, layout,
endianness, order and quantum mutants fail validation or change the bound
digest. Cross-architecture bit identity is explicitly not claimed.

Current digests:

- authority projection:
  `65378bddc8e61389de6abb4a36c418aa526dd06df7ef00b6e74347762cc03462`;
- diagnostic contract:
  `1fc6c48a5711a25c8724a598a164a8a20ce9266e3f5cc6fd8fed4a24795961cd`;
- raw `momentum_scale` owner:
  `a32194fb664491fb50ecc1f26096d6b7d03d9be153a459c1db218ce4941de409`;
- derived locked energy:
  `19b9b6bb3d3d0657cb71745118ea396dc3cce92ed15491c20df8a9df8d91f8c8`;
- V2 raw receipt publication seal:
  `6fb642751e18a8ad85c3e36f76e3cd4907f2261e4570c64d06d4eeddff1c1272`.

## Phase B implementation boundary

The new `directional_face_admission.py` is a nonproduction research module.

- It keeps these authority labels disjoint:
  `SOURCE_IDENTICAL_SCALAR_PRIMITIVE`,
  `THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1`,
  `CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1`, and the reserved
  `SOURCE_IDENTICAL_DIRECTIONAL_FACE`.
- It binds the ordered 26-point quadrature to an explicit
  `HYDROGEN_ORTHONORMAL_FRAME_V1` spike hypothesis.
- At finite tilt, the tagged hydrogen interpretation gives red/blue inflow
  counts 2/24, while the legacy untagged-normal interpretation gives 3/23.
  The ownership masks differ on five nodes.
- Half-range ownership is exact: red inflow `v_red > 0`, blue inflow
  `v_blue < 0`; zero is a distinct grazing class.
- At Bianchi-II `tau=0.6073512349590596`, a frozen-background, zero-source
  manufactured solve reaches both actual line faces for all 52 ordered rays
  and preserves occupation. Geometry-result SHA-256:
  `125995384867ccc3b8e160a43dab41a7a7d5f65288948de1ac664886ff186c79`.
- At exact start `tau=0.6072662349590596`, nodes 0 and 1 have zero frequency
  speed and fail closed pending an event/restart contract.
- No physical/source-identical face was materialized. The geometry result is
  only `GEOMETRY_ONLY_MANUFACTURED`.
- The regenerated coding-research JSON publication seal is
  `721b1f4a18733fba338156124031de0b178cc08c7b91d6eff1328bb95e2ba87f`.
- Its portable coding-record semantic projection is
  `9284ed5b59437d474c293a9ecae24442ca31dc0ebad51432a959e22ccaf069d2`.

Production blockers remain:

- `BLOCKED_ANGULAR_FRAME_CONTRACT`;
- `BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY`;
- `BLOCKED_ANGULAR_REMAP_AUTHORITY` for fixed-node coupling;
- `BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT`;
- `BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION`;
- `SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`.

## RED-GREEN evidence

| Test lane | RED | GREEN |
|---|---|---|
| portable receipt core | 12 assertion/runtime failures, 0 collection errors | 19 passed (13 initial plus 6 review-hardening cases) |
| portable runner semantic check | 1 failure, 0 collection errors | included above |
| directional admission/geometry | 7 failures, 0 collection errors | 9 passed (8 initial plus 1 review-hardening case) |
| coding-research runner | 1 failure, 0 collection errors | included above |

Independent review then reproduced three additional RED conditions before the
hardening patch: excluded semantic fields survived a self-rebound portable
receipt, declaration-shaped hashes could empty the directional readiness
blocker list, and the coding-record validation command overwrote its tracked
artifact. Regression cases now reject all three paths and keep validation
read-only.

The legacy cancellation path exists only to reproduce the two historical
fingerprints in a forensic mutation test; the production runner always emits
and validates V2.

## Validation matrix

| Requirement | Result | Evidence |
|---|---|---|
| focused receipt/admission tests | PASS | `37 passed in 27.53s` |
| affected owner/transport/source tests | PASS | `68 passed in 30.63s` |
| portable dispatch mutant | PASS | legacy hashes differ as expected; V2 authority and diagnostic-contract hashes match |
| receipt regeneration twice | PASS | identical raw seal `6fb64275...c1272` |
| receipt semantic check | PASS | authority and diagnostic contract both match fresh computation |
| coding-record semantic check | PASS | read-only fresh projection match; physical-face promotion mutant rejected |
| number and locked-energy invariants | PASS | exact number residual, energy residual below `2e-15 eV` |
| half-range/frame discriminator | PASS | five-node mask difference; sign rules exact |
| 52-ray manufactured geometry | PASS | 52/52, zero occupation residual, face residual below `3e-13` |
| non-slow suite without unavailable direct import file | CONCERN | `459 passed, 2 failed, 37 deselected`; both failures are only missing `mpmath` |
| repository verifier | INHERITED_FAIL | preserved PR #42 trailing-whitespace/EOF evidence; no normalization allowed |
| cross-architecture bit identity | NOT_TESTED / NOT_CLAIMED | only X86_V4 on/off tested |
| physical source coefficients and incoming face authority | BLOCKED | no once-only pathwise four-channel law or directional incoming bytes |
| fixed-node angular remap/JVP | BLOCKED | no approved remap/advection authority |
| independent diff/science review | PASS | P1/P2 findings repaired; final science review `NO_BLOCKING_FINDINGS` |

## Failure log

- The full non-slow command excluded
  `tests/trajectory/test_characteristic_angular_solver.py`, whose direct
  module import requires the declared optional test dependency `mpmath`.
- Two additional `tests/recoil/test_event_weight.py` tests import `mpmath`
  inside high-precision calls and failed for the same environment-only reason.
- No dependency was installed and no test, tolerance or scientific code was
  weakened.
- `verify_repo.py --all` stops at the already preserved PR #42 evidence-byte
  policy. Any current-stage whitespace finding must be fixed; the inherited
  evidence files must remain byte-identical.

## Decision and compact state

- Phase A receipt portability repair: `PASS`.
- Phase B geometry/admission spike: `PASS_AS_RESEARCH_SPIKE`.
- Phase B physical production integration: `HOLD_BLOCKED`.
- Overall decision: `HOLD`.
- Current status:
  `BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`.
- Claim: `NO_PASS_REC_PHYSICAL_SPLIT`.
- All downstream operations remain `NOT_RUN`.
- Next minimal action: provide and approve one production frame convention,
  exact half-range incoming authority, once-only hash-bound
  `virtual_spike/one_photon/two_photon/raman` source law, and either a
  Lagrangian boundary or fixed-node remap/JVP contract, plus a speed-zero
  event/restart policy and an external verifier that resolves declarations
  against the approved authority package.
