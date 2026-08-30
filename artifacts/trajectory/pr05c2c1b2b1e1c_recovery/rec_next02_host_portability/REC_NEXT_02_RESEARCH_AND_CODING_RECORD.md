# REC-NEXT-02 research and coding record

## Decision

The REC-NEXT-01 continuation identity and portable V2 receipt remain valid.
The focused-suite failure observed on AMD Ryzen 9 5900X is a host-capability
error in a V1 forensic regression, not a V2 authority or scientific failure.

- Research verdict: `PARTIALLY_CONFIRMED_WITH_SCOPE_CORRECTION`; the scoped
  Ryzen 9 5900X host-capability false FAIL is confirmed.
- Coding verdict: `PASS_HOST_AWARE_FORENSIC_TEST_AND_ZERO_NODE_BINDING`.
- Production integration: `HOLD_BLOCKED`.
- Scientific terminal:
  `BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`.
- Claim: `NO_PASS_REC_PHYSICAL_SPLIT`.

No receipt arithmetic, tracked input, fixture, tolerance, physical source,
authority digest, manufactured result, or production-admission flag changed.

## Canonical continuation and scope

- Base commit: `7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a`.
- Base tree: `99fafd552041a4df277179667a910632755d84e2`.
- Base parent: `37a943347bf319af998230bb77c6f89827feddff`.
- Base REC-NEXT-01 manifest: all 10 entries passed.
- Worktree: isolated from every preserved evidence checkout.

In scope:

1. distinguish unavailable V1 SIMD lanes from failed scientific results;
2. preserve exact known V1 fingerprints where their NumPy lane exists;
3. keep V2 authority and semantic validation mandatory on every host;
4. bind the exact ordered zero-speed nodes `(0, 1)` to a typed fail-closed
   event signal;
5. adopt the four progress/identity/checkpoint directives as a compact
   repository policy and agent map;
6. provide a self-contained local continuation prompt.

Out of scope: Rust or JAX implementation, `mpmath` installation, evidence
normalization, receipt regeneration, physical face materialization, production
source or remap implementation, claim promotion, merge, and ready transition.

## Research loop

### Frozen hypotheses and falsifiers

| Hypothesis | Prediction | Falsifier |
|---|---|---|
| H1 host capability | V1 exact fingerprints are asserted only for an actually available known X86_V4 or X86_V3 lane | reported lane and known fingerprint disagree on the pinned NumPy/input stack |
| H2 V2 portability | authority projection, diagnostic contract, source/owner identities, invariant, status, and claim agree across dispatch choices | any load-bearing V2 field changes |
| H3 zero-speed ownership | the exact macro-start zero set is the ordered tuple `(0, 1)` | full ordered scan yields another set or nonzero value |
| H4 authority firewall | no authority admitted by the current repository gates resolves all six production blockers | an independently resolvable approved authority package is admitted |

The initial H1 wording treated every non-X86_V4 host as X86_V3. Independent
review correctly rejected that overreach. The implemented lanes are now
`X86_V4`, `X86_V3`, and `HOST_LANE_UNAVAILABLE`. A host with neither known x86
lane skips only the unavailable historical V1 fingerprint; it still executes
all V2 semantic checks.

### Reproduction evidence

The user-provided Ryzen 9 5900X environment was Python 3.12.13, NumPy 2.4.2,
SciPy 1.17.0, and pytest 9.1.1. It reported X86_V3/AVX2 without X86_V4/AVX-512.
Both native and `NPY_DISABLE_CPU_FEATURES=X86_V4` therefore produced the same
known X86_V3 V1 fingerprint `1ea93ca2...`. The portable checker, V2 authority
projection `65378bdd...`, diagnostic contract `1fc6c48a...`, raw owner
`a32194fb...`, locked energy `19b9b6bb...`, and V2 raw publication seal
`6fb64275...` all matched.

On the available X86_V4 verification host, the native and X86_V4-disabled
lanes reproduced both historical fingerprints:

| Actual NumPy lane | Direct diagnostic | Centroid diagnostic (eV) | V1 raw SHA-256 |
|---|---:|---:|---|
| X86_V4 | `1.0881876986956445e-08` | `5.545800263462297e-08` | `7bf0ebf143589b45308f5e0157a80ff842dc99783b5207748732f332a6c12912` |
| X86_V3 | `1.0878134039731587e-08` | `5.5440194657307984e-08` | `1ea93ca2c007209ad25ca6cafcd76d0616a9a4cc88319d56d18f43a03e930e9d` |

### Mathematical and literature check

Wolfram exact-rational evaluation of the printed decimals gives

\[
\Delta d = 3.742947224858\times 10^{-12},\qquad
\Delta E = 1.7807977314986\times 10^{-11}\ \mathrm{eV}.
\]

The V4, V3, and portable V2 values all remain inside the already frozen closed
diagnostic intervals `[1.08e-8, 1.10e-8]` and
`[5.5e-8, 5.6e-8] eV`; no interval or tolerance was changed after observation.

The interpretation is consistent with work showing that ordinary
floating-point reductions are not automatically bitwise reproducible across
operation order and architectures, and that reproducibility requires a
deliberate algorithm: Ahrens, Demmel, and Nguyen,
<https://doi.org/10.1145/3389360>; Guo, Laguna, and Rubio-González,
<https://doi.org/10.1109/SC41405.2020.00053>.

At Bianchi-II macro start `tau=0.6072662349590596`, a full ordered scan found
zero frequency-drift rates exactly at nodes `[0, 1]`, both binary64 values
`0.0`; the next-smallest nonzero absolute rate was
`8.390069024029656e-15 s^-1`.

## Audit-compiled implementation

| Observed failure or risk | Required invariant | Mechanical detector/control |
|---|---|---|
| native X86_V4 was assumed on every host | a missing hardware lane is not a failed V1 fingerprint | child probe reports actual NumPy V4/V3 features and selects a known lane or `HOST_LANE_UNAVAILABLE` |
| a caller-supplied feature mask could be erased | the process environment owns an existing dispatch mask | regression runs the native helper under a preconfigured X86_V4 mask |
| generic zero-speed exception hid which rays stopped | the complete ordered zero set is `(0, 1)` | typed `FrequencySpeedZeroEventRequired.node_indices` and exact assertion |
| raw-byte mismatch could be promoted to science failure | V1 forensic, V2 semantic, and stored-artifact byte identities remain distinct | repository typed-identity policy plus existing read-only V2 checker and manifest |
| geometry witness could be overclaimed | physical admission remains false under all six blockers | unchanged readiness/admission tests and affected dependency cone |
| audit could recurse without execution delta | one objective, one verification, one independent review, one repair, then stop | repository progress-first policy and this checkpoint |

The geometry runner now computes all 26 ordered local characteristic rates
once. If any are exactly zero, it raises one structured fail-closed exception
containing the complete ordered node tuple before launching either face. At a
nonzero snapshot the 52-ray manufactured result and all physical blockers are
unchanged.

## RED-GREEN evidence

- Initial acceptance RED: two focused failures with no collection error — the
  probe lacked an actual-lane field and the structured zero-speed exception did
  not exist.
- First GREEN: the two focused selectors passed.
- Negative RED: a preconfigured X86_V4 mask was erased by the helper.
- Targeted repair: preserve caller environment state; the regression passed.
- Independent-review repair: split the overbroad non-V4 case into X86_V3 and
  `HOST_LANE_UNAVAILABLE`; native V4, V4-disabled X86_V3, preconfigured mask,
  and exact-zero selectors all passed.

## Identity and claim boundary

| Object | Identity class | Continuation rule |
|---|---|---|
| tracked NPZ/source and locked owner arrays | immutable source/input | exact bytes |
| fetched receipt, research record, handoff, manifest entries | stored publication evidence | exact bytes via stage manifest |
| fresh receipt diagnostics and coding semantics | numerical/scientific output | V2 projection, formula contract, invariants, and justified intervals |
| V1 whole JSON from a known SIMD lane | conditional forensic evidence | exact known fingerprint only when that lane is available |
| host path, timestamp, JSON presentation | packaging/metadata | structural/content identity unless explicitly sealed |

Independent review confirmed the operational HOLD but did not claim an
exhaustive census of every external binary that could exist outside the
repository. The current authority gates admit no resolvable package. The six
unresolved production prerequisites remain:

1. approved frame/tetrad/frequency convention;
2. exact authoritative incoming red/blue half-range values;
3. unit-locked once-only `virtual_spike`, `one_photon`, `two_photon`, and
   `raman` source laws for `j_H`/`chi_H`;
4. Lagrangian boundary semantics or fixed-node remap/advection with
   conservation and JVP tests;
5. speed-zero event/restart semantics;
6. an external verifier resolving every declaration to approved bytes.

Therefore no result may be relabelled `SOURCE_IDENTICAL_DIRECTIONAL_FACE`, no
deposition map may be selected, and every downstream physical operation stays
`NOT_RUN`.

## Fresh verification and independent audit

The final integrated bytes before manifest generation produced:

- focused three-file suite: `38 passed`;
- directly affected seven-file suite: `68 passed`;
- native X86_V4, X86_V4-disabled X86_V3, preconfigured-mask, and exact-zero
  focused selectors: PASS;
- simulated `HOST_LANE_UNAVAILABLE` selector: PASS;
- read-only portable receipt checker: PASS, including authority
  `65378bdd...`, diagnostic contract `1fc6c48a...`, and raw stored seal
  `6fb64275...`;
- read-only coding-record checker: semantic digest `9284ed5b...` matched; the
  differing fresh raw digest remained explicitly archival-only.

The independent verifier reported no P0. It confirmed H2 and H3, confirmed the
scoped Ryzen portion of H1, and accepted H4 only as an operational HOLD rather
than a universal inventory of external files. Its two exact-base P1 findings
were the unconditional native-X86_V4 assertion and the generic zero-speed
regression; both are closed by this diff. Remaining P2s are the test-only use
of NumPy's private CPU-feature map and the disclosed late creation of the
durable research file. No claim relies on either as production authority.

## Closeout checkpoint

- Completed: host-aware forensic lane classification, caller-mask regression,
  exact zero-node typed signal, compact repo policy/agent map, research record,
  manifest, and prompt-only handoff.
- Unresolved: the six physical authority prerequisites above.
- Assumption: the historical V1 hashes are evidence only for the two observed
  NumPy 2.4.2 x86 dispatch lanes; no cross-architecture V1 identity is claimed.
- Verification: targeted, focused `38 passed`, affected `68 passed`, and both
  semantic checkers passed. Manifest, syntax, and diff checks are recorded in
  the final delivery report after sealing.
- One next action: run the handoff validation unchanged on the Ryzen 9 5900X
  and preserve its lane/result receipt; do not start production code unless a
  complete authority package is supplied and independently verified.
