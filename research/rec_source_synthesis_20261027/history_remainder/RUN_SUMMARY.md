# Executed history remainder result

Primary and saved-output plotting both completed once after parent C4 GO. Both exit codes are 0. Constructor verification passed; independent admission review remains parent-owned.

## Actual exact checks

- 313/313 exact-grid cell witnesses and original source/sample/anchor metadata verified.
- 1240 retimings: 313 within-left, 313 within-right, 313 cross-left, 301 cross-right.
- 12 unavailable right crossings are SKIP_CAUSAL_PREFIX; 313 chords pass exact Peano equality and bounds.
- 30 small controls pass, including opposite-direction sign, starting-atom, zero-curvature/dropped-jump mutations, nonuniform affine, cancellation and invalid domains.
- 614 actual nonzero crossed-knot remainders detect the zero-jump mutation; no actual crossing remainder was zero.
- All 626 within-cell remainders are exactly zero. No numerical tolerance was needed.
- Saved result BYTE_IDENTITY between primary and plot receipts: True.

## Magnitudes

| Quantity | Display value | Exact rational |
|---|---:|---|
| Maximum absolute retiming remainder | 1.8566648889656617e-19 | `58840059023/316912650057057350374175801344` |
| Maximum retiming bound | 1.8566648889656617e-19 | `58840059023/316912650057057350374175801344` |
| Maximum absolute chord remainder | 1.6749900771700771e-19 | `83134105140488944538041967/496325956037574652509156103299029360604872704` |
| Maximum chord bound | 1.6749900771700771e-19 | `83134105140488944538041967/496325956037574652509156103299029360604872704` |
| Maximum stored-minus-native clock difference | 4.7173636524844298e-16 | `4351/9223372036854775808` |
| Maximum native-real nominal anchor radius | 1.8495299543650757e-29 | `2294924307050945/124081489009393663127289025824757340151218176` |
| Maximum preserved geometric anchor radius | 2.8063252708759118e-28 | `2125323597749/7573333069425850157122243222373270552576` |

Source ordering remains outgoing_virtual then outgoing_lyman. Native-real eta0, dlna and excluded endpoint are exact binary64 rationals recorded in summary.json. The original immutable history and context hashes match the frozen contract. Rounded native C was not executed.

## Actual bounded resources

| Phase | Child CPU s | Supervisor CPU s | Controlled CPU s | Wall s | Child peak RSS KiB |
|---|---:|---:|---:|---:|---:|
| primary | 5.064614 | 1.044857 | 6.109471 | 6.151483 | 69660 |
| plot | 3.182576 | 0.077575 | 3.260151 | 3.302582 | 85992 |

Cumulative controlled CPU: 9.369622/360 s. Each process used the frozen one-thread environment and 2 GiB address-space ceiling. Preparation, metadata readback and unmeasured post-measurement I/O tails remain UNKNOWN_NOT_ZERO.

## Scientific scope

physical_epsilon=null; physical_bound_coverage=0/313. No IVP, native/RHS, Ks or GEO execution occurred. This is a represented-history identity result, with no physical-admission or original programme numerator promotion.

## Evidence

- results/primary001/: controls.json, summary.json and exact/display JSON + CSV for retimings, chords, source bindings, clock differences and skips.
- evidence/: primary001 and plot001 receipts plus raw stdout/stderr.
- figures/history_remainders.png and figures/history_remainders.pdf, created exclusively from saved result JSON.
- freeze.json: exact commands, code/input byte identities, environment versions and caps.

The constructor inspected the PNG. Both panels and labels are legible. The zero within-cell series is explicitly identified; its symlog linear neighborhood appears below the smallest positive decade. The parent is to inspect the same PNG in its independent review.

Skill context used: physmath-research-loop 1.3.0 SKILL.md, references/CODING_LOOP.md selected C5–C8, and references/POLICY_INTEGRATION.md. Requested model: gpt-6.1-sol. Actual runtime model identity: UNKNOWN_NOT_EXPOSED.
