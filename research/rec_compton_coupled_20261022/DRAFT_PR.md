## Problem and result

The previous fixed-trajectory budget found substantial Compton forcing,
but could not determine the temperature and opacity response of a gas that
actually evolves with it. This unit adds the selected Compton source to the
native full63 atomic/thermal system and completes the prescribed eight
bounded IVPs without replaying an earlier baseline.

The refined actual-hot endpoints at z=2 are 8896.57 K and 8885.22 K, about
12.08% and 12.17% below the matching saved no-Compton solutions. The selected
new-path Compton losses are 2.173 and 2.184 eV/baryon. A separate prescribed
Planck bath is retained as an exclusive reference branch, with shared UV.

## Changes and evidence

- An analytic single-row RHS/Jacobian update preserves the original 62
  equations at a common state and retains all 63 coupled solver variables.
- Eight new IVPs and four nominal/refined pairs pass the frozen admissions;
  accepted nodes and 109/513/1025 grids, source ledgers, support masks and
  provenance are retained. Old IVP reruns: zero.
- Independent preflight, saved-array physics, analyzer-binding and actual
  PNG/data reviews are retained with the real failed attempts and fixes.
- Three final PNG/PDF figure pairs and their 58 plotted arrays/five tables
  are in figures/v2. REPORT_KO.md and HANDOFF_KO.md explain the result.
- Measured integration time is 58.18 s versus 249.05 s for diagnostics and
  persistence. NEXT_UNIT_CONTRACT.md proposes zero-new-IVP equivalence and
  profiling work; no successor benchmark or speedup is claimed.

## Interpretation and delivery

This is a finite test-fluid gas pilot. Opposite radiation sources are
ledger-only; actual spectral recoil/induced closure, Einstein energy
backreaction, new collision dynamics and nuclear activation are outside
this unit. Physical HOLD, production NOT_APPROVED, global convergence
NOT_RUN, REI_activation=false and U5 CLOSED_HOLD_NOT_RESET remain in force.

This draft is stacked on PR122. A/B GitHub and Dropbox receipts are retained
in evidence/delivery. The final PR body is updated after actual Stage C
whole-tree verification and archive/readback receipts; the committed body
does not preclaim those future operations. The final archive is pinned to
this completed science snapshot. No merge or public backup link is created.
