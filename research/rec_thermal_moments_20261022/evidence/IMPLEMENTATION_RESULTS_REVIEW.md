# Independent implementation and numerics results review

Status: **PASS_WITH_EVIDENCE_LIMITATIONS**. Review used the eight raw trajectory NPZ files, their result/start receipts, the pinned donor files, and the raw Mao parameter table. No additional ODE was integrated. Analysis-script results were not used as authority.

## Independence and verified scope

The reviewer authored `recombination_moments.py`, its tests, the independent thermal-system tests, and the saved126 postprocessor. The reviewer did not author the coupled thermal source, system, or runner. Those shared dependencies are disclosed in the JSON receipt, which embeds the review scripts.

All eight trajectory hashes and sizes, source identities, and exact saved restart states were verified. There are 109 saved points per case, 872 in total. Every recomputed frozen saved-point gate passes. The maximum independent source-energy residual is 3.9476582e-16; the largest reconstructed diagnostic-field relative difference is 6.72319621e-15. Native neutron/tritium populations and decay flux are exactly zero at all saved points.

## Refinement and source comparison

| Pair | Refinement max abs ΔlnT | Refinement conditional-ion fraction | Refinement stress columns 1:6 | Refinement full signed six-vector | Refinement max abs Δtau |
|---|---:|---:|---:|---:|---:|
| s03_m03_r03 | 4.18140424e-07 | 3.40305699e-08 | 2.52848462e-13 | 1.26636787e-09 | 3.44254625e-11 |
| s04_m04_r04 | 4.18114888e-07 | 3.39204624e-08 | 1.02576302e-12 | 4.98918968e-09 | 3.29561239e-11 |

The signed six-vector is `(S_F, P_m, P_r, P_total, P_gamma, P_nu)`. `S_F` is signed shear; stress-only comparisons use columns 1:6. Both interpretations satisfy the frozen 3e-7 comparison threshold. The other frozen thresholds remain unchanged.

| Pair | Derivative minus Mao endpoint ΔT, K | Maximum abs ΔT, K | Maximum conditional-ion fraction change | Maximum stress-only change | Maximum abs Δtau |
|---|---:|---:|---:|---:|---:|
| s03_m03_r03 | -1.86021074 | 2.64121158 | 1.43249446e-05 | 5.65773421e-14 | 2.82266488e-09 |
| s04_m04_r04 | -1.85930532 | 2.63853339 | 1.43116701e-05 | 6.31506512e-13 | 2.81636381e-09 |

The source-induced stress changes are below the corresponding nominal/refined stress changes in both pairs. These results do not resolve a source-closure effect on signed stress. Source comparisons describe conditional closure sensitivity and are not probability intervals or total physical error estimates.

## Energy evidence and finite-sample limits

The reported 1025-node energy-integral residual reaches 8.54519616e-06, below the frozen 3e-4 threshold. Its arithmetic and endpoint energy were checked independently; the 513-to-1025 net-integral difference reaches 4.10100855e-05 in throughput units. The dense arrays and BDF interpolant were not retained, so the dense quadratures remain runner-reported. The independent 109-point coarse quadrature gives a maximum residual 0.000590787134; it is a different diagnostic and is not evaluated against the dense-grid gate.

Population/conservation checks apply to saved samples, and angular positivity uses a finite 129-angle grid. They certify neither all internal BDF steps nor the continuum. Two refinement comparisons establish finite agreement at those restarts, not global convergence. Early evolution before the exact stored node84 remains inherited prescribed-temperature history.

## Preserved arithmetic findings and resources

Ten initial scalar-summary discrepancies around 1e-16 were retained. Baryon-residual discrepancies came from converting Fortran-order NPZ abundances to C order before reduction; Einstein-residual discrepancies came from evaluating `3*H*H` versus the runner's `3*H**2`. Targeted original-order calculations reproduced every reported scalar. All scientific gates passed before and after that explanation; no tolerance was adjusted.

The campaign reports eight new integrations, zero old IVP reruns, 71.976452 s wall time and 71.060064 CPU seconds summed across cases, with 8521 RHS evaluations, 138 Jacobian evaluations and 622 LU decompositions. Counts are internally consistent. The longest case reports 20.781217 s, below the 240 s cooperative cap. Peak-memory telemetry was not persisted.

Physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, historical budget holds and REI_activation=false remain unchanged.
