# REC thermal moments: bounded continuation contract

Parent: REC PR119, `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`.
The 125 main and one opacity control are complete. Reuse their saved bytes; never submit those IVPs again.

## Selected next unit

Derive and implement kinetic RR/DR energy loss, quantify the thermal forcing hidden in the prescribed-temperature pilot, then run a small distinct dynamic-temperature restart family. The physical state has 63 coordinates: the inherited geometry/radiation40, native isotope/ion21, optical depth1, and log temperature1. All inherited number rates, UV, geometry, signed matter/radiation definitions, and isotope scaling remain fixed. This changes the temperature equation and thus creates new IVPs; it does not replace old results.

Primary RR closure is `L_RR = k_B T alpha_parent f_Mao2017`, explicitly a **Mao-factor hybrid** with unchanged parent number rates. The independent alternative uses `L_RR = k_B T (3 alpha_parent/2 + d alpha_parent/d ln T)`. DR uses the signed fitted resonance energy moment, with physical accuracy beyond the fit unresolved. These two closures measure source sensitivity, not a probability interval or total model error.

For the existing single-charge-step Li-I 1s model, primary photoelectron energy thermalizes locally; the remaining core energy escapes radiatively. This is a selected conditional prompt/case-A closure. Direct multiple photoionization, shake-off, secondary ionization, CI/CX, free-free, collisional excitation, Compton transfer, nuclear energy and radiative transport are not supplied by this unit. The photon Thomson block remains the inherited elastic block. No new assumption that all missing effects are small is made.

## Initial and boundary conditions

Native n/T inventories stay zero. New trajectories start from the **stored node nearest z=8**, with its exact geometry, isotope states and accumulated optical depth, and the old prescribed temperature at that same node. No interpolation or reintegration produces the initial state. Continue to z=2. Accepted temperature must remain in the shared100..1e6K coefficient domain; no temperature floor/clipping/extrapolation. Early z20→restart evolution is inherited, not a new self-consistent thermal history. Baryon thermal energy remains a test-fluid diagnostic. Metric (-,+,+,+), SI c and k_B retained.

## Planned finite execution and gates

- Four primary restarts: `s00_m02_r02`, `s03_m03_r03`, `s04_m04_r04`, `s02_m04_r01`.
- Two refined integrations: `s03_m03_r03` and `s04_m04_r04` primary, rtol2e-9 (nominal2e-8), maxstep0.0125 (nominal0.025), atol reduced10x.
- Two rate-derivative alternatives: `s03_m03_r03` and `s04_m04_r04`. Eight distinct new integration configurations; old IVP reruns0.
- Reuse all126 saved donor trajectories for the new thermal-source diagnostics. This is postprocessing, not126 new integrations.
- Source table formula/table agreement must allow only the published max deviation plus published decimal rounding: absolute tolerance `(mdp/100+0.0005)*f_table+0.0005`. The extra0.0005 relative accounts for max-deviation rounding by0.05 percentage points; it is not a changed physics tolerance.
- Analytic Jacobian directional relative-to-max(1,RHS,Jv) error <3e-6 at explicitly selected physical states; all63 columns covered at one state. Rates remain byte-identical to parent at tested temperature nodes.
- Accepted scaled populations >=-2e-8; isotope residual <2e-7, baryon residual <2e-8; no nonfinite output or unsupported temperature. Thermal and chemical energy source balance <5e-12 relative to sum of absolute terms. This algebraic gate is separate from numerical convergence.
- Nominal/refined same-restart saved differences: max|delta lnT|<3e-5, conditional ionic fractions<3e-5, signed stresses<3e-7, optical depth<3e-7. A finite tolerance refinement comparison does not certify the entire model's global convergence.
- Numerical energy-integral residual on a dense1025-node diagnostic grid <3e-4 relative to total energy throughput; report grid513→1025 difference separately.

The current host has CPU quota8 and RAM8GiB. Execute new cases serially with one BLAS/OMP thread and a240s cooperative per-case wall cap; total bounded campaign wall<=1200s. This is a new finite sandbox allocation. Historical U5 budgets stay CLOSED_HOLD_NOT_RESET. No benchmark or NCP campaign.

## Dependencies and publication

REI220 compact33 is a separate completed129-case cohort. REI219 nuclear/daughter contracts remain distinct; its new T/n sources would invalidate the current compact isotope equivalence. This unit retains native isotope coordinates and zero nuclear flux. It imports no passive nuclear history as a coupled prediction.

Stage A: intake+sources+contract. Stage B: derived sources+implementation+targeted verification. Stage C: saved-data diagnostics+new finite restarts+source/refinement comparisons+direct figure and independent review. Commit/checkpoint each stage; final draft PR is stacked on PR119, never merged automatically. Backup receipts distinguish acknowledged storage from actual byte readback.

Physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET and REI_activation=false remain.
