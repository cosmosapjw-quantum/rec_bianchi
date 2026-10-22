# Prepared draft PR — not submitted

Repository: `cosmosapjw-quantum/rec_bianchi`

Base: `research/rec-rei-hheli-sandbox-20261021` (REC PR119)

Head: `research/rec-thermal-moments-20261022`

Title: `REC: close retained RR/DR thermal moments and add full63 restart pilot`

## Why

PR119 evolves the isotope/ion network with prescribed temperature. Its number rates alone do not specify the kinetic energy carried away by recombining electrons, so the imposed thermal history leaves an external heat budget unresolved.

## Changes and resulting behavior

This stacked research unit adds source-bound RR/DR kinetic moments, a Mao2017 factor hybrid with unchanged number rates, and a fit-derivative alternative. It derives the variable-particle-number temperature equation and couples log-temperature to the native full62 system with an analytic full63 Jacobian.

All125 existing main trajectories and the separate opacity control are reused. Their prescribed z20→2 histories require a conditional net external sink of19.6551–19.7207eV per baryon under this closure. No old IVP is rerun.

Eight distinct new configurations restart from exact saved node84 atz7.963732801243163:4primary,2tolerance refinements and2RR-source alternatives. All complete. Four primary sampled peaks are14167.03–14177.03K; z2 endpoints are10116.85–10119.08K. The largest conditional ionic-fraction departure from the prescribed path is about0.12035, in transient LiIV. This does not imply dominant absolute electron production by rare Li.

## Evidence

- 9 moment and 10 thermal-system test methods; 63 Jacobian columns and 24 mixed directions; 114 original source points and deliberately wrong log/unit/row mappings.
- Two paired numerical refinements pass the frozen gates. Max differences: lnT 4.1814e-7, ion fraction 3.4031e-8, signed shear/stress six-vector 4.9892e-9, tau 3.4425e-11.
- Mao/derivative source differences exceed observed primary refinement changes for T, ions and tau; stress-only and full signed-vector source changes remain below corresponding refinement differences.
- Independent PHYS-MATH and IMPLEMENTATION/NUMERICS reviews, source/trajectory hashes, actual raw outputs, five PNG/PDF figures and exact plot data.
- Actual new8 wall 71.976452s, CPU 71.060064s; no failed or repeated IVPs.

## Limits

The earlier z20→restart history is inherited. Baryon thermal energy remains a test-fluid budget. Case-A escape, instantaneous primary thermalization, ground-state electronic rates, zero n/T and isotope electronic equality remain conditional assumptions. Missing CI/CX, collisional excitation, secondary, free-free, Compton energy transfer, multiple photoionization, nuclear energy and radiative transport are not shown to be small.

The runner's1025-point dense energy diagnostic passes its frozen gate, but intermediate dense arrays/interpolant were not persisted. Independent review verified endpoints and receipt arithmetic, and retained a separate109-point coarse integral. Dense replay is not claimed. Next new execution must preserve the diagnostic arrays.

Physical HOLD; production NOT_APPROVED; global convergence NOT_RUN; historical U5 CLOSED_HOLD_NOT_RESET; REI_activation=false.

## Review and delivery

Read `REPORT_KO.md`, `THEORY_KO.md`, `FROZEN_CONTRACT.md`, `evidence/*RESULTS_REVIEW*` and `HANDOFF_KO.md` in `research/rec_thermal_moments_20261022`.

This body is prepared locally. Automatic approval review rejected the initial push because external publication authorization was not established in the current message. No PR, merge or remote backup success is claimed. After explicit authorization, push this branch, open this PR as draft, and record actual publication and backup receipts.
