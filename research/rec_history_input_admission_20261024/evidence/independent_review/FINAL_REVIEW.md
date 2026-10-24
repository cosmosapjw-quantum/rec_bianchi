# Independent changed-source review: REC-HISTORY-ADM01

## Decision

The bounded scientific conclusion is supported: **h/2 U5 supplies retained interpolation cells for the 313 fixed LINE02 queries; the other three recovered candidates supply none. Physical-reference and error calibration remain unadmitted.** This is an input-selection result, not a physical absence theorem. REC-HISTORY remains PARTIAL and H5 remains INPUT_DEPENDENT_UNCALIBRATED.

The production code's use of the actual input-state photon clock, strict interpolation endpoint, and face-causal prefix is consistent with the sources read. Three finite independent probes passed. They did not replay the 313-query primary, the historical 608+14 boundary verification, an IVP, native recombination, or a campaign. The original U5 FAIL/HOLD result remains intact.

The initial narrow provenance gap for the full U5 cosmology tuple was **closed within this same review** by the actual execution source manifest and caller. The independently reconstructed actual U5 temperature agrees with that caller binding. Both identified figure presentation defects were also repaired and visually checked in this same pass. **All three concrete review findings are closed; no current-task scientific or delivery finding remains open.**

## Scope, skill and independence

This is the single fresh-context review requested by the parent for source pin `93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`. I read `FROZEN_CONTRACT.md`, `PREEXEC_ADDENDUM.md`, `inputs/INPUTS.json`, `admit_history.py`, `run_bounded.py`, the source mapper's actual files, `SUMMARY.json`, saved candidate-query rows, and the produced PNG. I did not alter production code or publish externally. The separate HISTORY02 characteristic/Wien owner was not touched.

Skill context actually used: `c38/physmath-research-loop`, version 1.3.0, `SKILL.md`, `references/POLICY_INTEGRATION.md`, and the R1/R2/R6 and selected-stage binding sections of `references/THEORY_LOOP.md`. Applied rules were the frozen scientific scope, source-backed reuse, Physics/Math before implementation mapping, typed identity, finite one-pass review, smallest useful probes, and scoped no-go language. No child reviewers were spawned.

The source-reading and finite probes are independent of the primary implementation. The 1,252 saved rows were read and counted, not recomputed. Only three selected U5 query values were independently reconstructed. Thus 386 primary checks are preserved primary evidence, not 386 independently repeated checks.

## Physics and mathematics assessment

For scalar FLRW propagation with eta = ln(a), constant E*a implies `(1+z_s)=(1+z_t) E_s/E_t`. All native owners read use the upstream higher energy, making eta_s earlier than eta_t. Source `hydrogen.c::fplus_from_fminus` owns the 311 virtual incoming channels and the two Ly-alpha/Ly-beta incoming channels. The production routing uses the next virtual bin except at destinations 139, 270 and 310, which use outgoing Ly-alpha, Ly-beta and Ly-gamma respectively. Incoming line channels 311 and 312 use virtual channels 140 and 271. These match the literal native loops.

The retained histories use dimensionless signed departures in the native reference convention. The atomic source explicitly writes outgoing virtual departures and the three Lyman departures, while `average_virtual` is a separate field. The admission code selects `virtual_out` and `lyman_out`. It does not replace these with the in-bin average. No nonzero-shear or different-reference extrapolation was admitted here.

The producer evaluates and writes photon column `j=g-g0` at input state g, then records the accepted thermodynamic state at g+1. Accordingly the last state is one index later than the last photon knot. Both h/2 producers and the h/4 continuation source implement this order. The native `interp_Dfnu` rule excludes its latest retained knot as a query endpoint. The new code also intersects the archive with knots strictly before the fixed target face. This avoids interpreting a later saved continuation as causally available input.

For linear interpolation the conditional bound

`e_u <= (M2 h^2/2) alpha(1-alpha) + (1-alpha)e_L + alpha e_R + e_arithmetic`

has the correct dimensional structure in eta, provided M2 bounds the exact second eta derivative on the actual cell and e_L/e_R bound endpoint errors in the same physical problem and departure basis. None of these input-specific quantities is supplied by a same-h Python/C parity check. A two-grid discrepancy alone also does not supply them. The retained result correctly leaves every error upper bound null and calibration unadmitted.

## Independent finite evidence

Exact executed scientific command:

```text
python run_bounded.py --cpu 4 --wall 15 review001 python evidence/independent_review/tiny_review.py
```

Exit status was 0, with no timeout. Recorded inclusive CPU was 0.3538700779999999 s, execution wall 0.36609879699972225 s, and child peak RSS 91,420 KiB. The wrapper enforced CPU 4 s, wall 15 s, and address space 1 GiB; all four numerical thread environment variables were 1. Its receipt does not claim a live aggregate monitor. The reviewer script SHA256 is `26b9ad6fc8bf33a774bf72f5d425863f54e5dc0c38724a6e56ae38c0fddb3f35`; this supplements the wrapper's root-only source inventory.

| Probe | Actual result |
|---|---|
| P1: saved-row counts and independently calculated source interval endpoints | 1,252 rows; h2 U4, h4 event and h4 smoke each have 313 endpoint exclusions; h2 U5 has 313 covered cells. All row-level physical-reference flags are false and error bounds are null. Last-state/last-photon separation is consistent. |
| P2: three selected U5 cells | Destinations 0, 311 and 139 reconstruct the saved endpoints and interpolation values. They include the earliest query, latest query, and a Lyman-source gap. The face-causal prefix is 10,277 columns. Nearest checked upper brackets precede the target by 8.490000000094255e-5 in eta, so the result does not depend on admitting a target-coincident/future bracket. |
| P3: actual U5 thermal event | The recorded event at g=53177 and actual saved state imply T0=2.7255 K independently of the dataclass-default assumption. |

For P3, the producer defines `delta=1-Tm/[T0(1+z)]`. The actual retained state gives Tm=2280.4085186856096 K and z=836.1122428311476; the original receipt records delta=0.0005000545426558922 at the same index. Therefore `T0=Tm/[(1+z)(1-delta)]=2.7255 K`. The fixed target's source-emitted TR, nH, fsR and meR imply T0=2.7279999999999998 K and nH0=0.18745798773143102 m^-3. The actual U5 T0 differs from the target. This probe does not independently identify U5's entire cosmology tuple or nH0.

Probe output: `evidence/independent_review/PROBE_RESULTS.json`. Execution evidence: `execution/review001/RESOURCE_RECEIPT.json`, `stdout.log`, `stderr.log`, and `SOURCE_IDENTITIES.json`.

## Findings and smallest repairs

### F1 — U5 full cosmology tuple attribution: CLOSED

- **Object:** `admit_history.py` lines 75–88; `SUMMARY.json` physical-domain `candidate_parameters` and `candidate_nH0_m3`; the figure's unqualified candidate density difference.
- **Initially observed defect:** one dataclass-default tuple is assigned to every actual candidate. The U4 caller explicitly constructs `HyRec2012Cosmology()`. The h4 class rejects a changed parameter tuple and its continuation requires that exact class. For U5, the initially provided producer accepted a cosmology argument without an included actual caller. The original receipt bound the producer and NPZ, but did not itself spell out the supplied tuple.
- **Impact before repair:** exact U5 nH0=0.18971712352134673 m^-3 and its +1.2051424520529637% density difference needed stronger execution attribution. The physical HOLD was already supported by P3's independently reconstructed actual temperature.
- **Completed smallest repair:** the parent supplied `provenance/u5_execution_binding/verify_r3i_h2_u5_thermal.py`, `SOURCE_MANIFEST_V3.json`, and `IDENTITY.json`. Direct SHA256 inspection confirms manifest `b5c7c856f7517da4ebc8edae91d287333abf072eb9c8064aef202089bf58e7f2`, exactly the original U5 receipt's `capsule_source_closure.manifest_sha256`. Its caller entry `0681b98a86f54719480fe0d1a8aca882c20b50d41d349f3d24676b1e5ef6a559` and cosmology-source entry `bd72cd1c35718d11a13aee0905babe0c74af4d941545e5245562fcb3a5630e77` match the actual read files. The caller constructs the default cosmology at line 248, builds its source at 251, passes both to U5 at 314, and writes/hashes this NPZ at 343–348. `make_hmla_source` forwards the actual T0, omega_b and YHe into the source. The receipt binds the resulting NPZ SHA to the recovered candidate.
- **Status at review close:** CLOSED by actual caller/manifest/NPZ binding; actual U5 T0 mismatch separately CLOSED by P3. The full tuple and nH0 attribution is now supported without a primary rerun.

### F2 — Figure title overlaps the first retained interval: CLOSED

- **Object:** `results/figures/history_input_domain.png`, top panel.
- **Observed defect:** the large title is inside the plotting area and overlaps the h/2 U4 bar at the top row. Visual inspection was performed on the rendered PNG, not inferred from code.
- **Impact:** the first candidate's interval is partly obscured. Numerical evidence is unaffected.
- **Completed smallest repair:** the renderer moved the main title outside the axes and reserved margin. The modified PNG was opened and inspected; the full U4 interval is visible with no title overlap. No scientific rerun was performed.
- **Status at review close:** CLOSED, delivery only.

### F3 — Figure does not distinguish the admissible past prefix from the future archive: CLOSED

- **Object:** the h/2 U5 retained interval in the same PNG.
- **Observed defect:** the bar is uniformly colored from z≈1702 to z≈836 although only 10,277 of its 16,733 columns precede the fixed face. The numerical code applies this causal restriction correctly; the graphic only labels total columns.
- **Impact:** a reader can interpret the full bar as the input available at the face. This is a visual interpretation risk and does not invalidate 313/313 coverage, since the required band is entirely on the past side.
- **Completed smallest repair:** the face-causal part is solid teal, the future archive is a muted dashed segment, and the legend explicitly calls the latter ineligible at the target face. A last-causal-knot tick and the full-archive strict-endpoint marker are distinguished in the caption. The saved 313/313 retained-cell coverage and physical/error HOLD caption are preserved. The modified PNG was opened and inspected.
- **Status at review close:** CLOSED, delivery representation only.

The repaired PNG SHA256 is `6620d720e455d18174c386c835155ecb4a87183d933422dcf28a95588e33da91`. The original PNG is preserved under `results/figures_original001/` with SHA256 `1d0ade26c1dcd215c032102d8c755a4c471629b0e24276ab9a8ea5417cef0e61`. The parent-owned figure002 receipt records exit 0, CPU 1.53922272 s, wall 1.5693057280004723 s, RSS 87,756 KiB, and one thread for `python render_coverage.py`. This is rendering evidence from saved numerical results, not an additional scientific probe.

## Typed identity and disposition

Data/source SHA identities establish the stated BYTE_IDENTITY. The exact energy comparison and checked source/clock mapping establish the relevant numerical and structural identities. They do not establish SCIENTIFIC_EQUIVALENCE between different cosmologies or calibrate trajectory error. This separation is respected by the admission flags and should also be explicit in the final narrative/figure.

RESULT_VALIDITY: supported for the bounded source/domain result and physical HOLD. PROVENANCE_VALIDITY: supported for coverage and actual candidate cosmology after F1 closure. PACKAGING_VALIDITY: repaired PNG visually checked with F2/F3 closed. No new strong no-go, full-history convergence, production approval, or REI activation is admitted.

The finite scientific and figure review is complete. All concrete findings were closed in its single repair episode without another scientific review cycle or a historical campaign replay. Any subsequently requested central-observation diff can be checked separately as a delivery-preservation appendix; no central diff was included in this scientific review.
