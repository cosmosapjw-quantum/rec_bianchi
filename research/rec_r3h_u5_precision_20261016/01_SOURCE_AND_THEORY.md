# R3h phase 1: U5 precision mechanism and clock-refinement identity (2026-10-16)

Authority: PR #99 `e6596cf6083c0a1f28a26700170c971a20244d23`; original immutable October 2012 HyRec ZIP SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`. Read-only input R3g `thermal_transition_001/ROUNDOFF_AUDIT_REPAIR_001.json` Git blob `09732201ed91c017043ac0a330dde7177c7b9b4d`.

## Proven original-C formula

Unmodified `HyRec/hydrogen.c`, `rec_HMLA_2photon_dxHIIdlna`, lines 779–799:
for `tau>1e-6`, `one_minus_Pib = 1 - (1-exp(-tau))/tau`; at `tau<=1e-6` original uses `tau/2-tau^2/6`. Outgoing fminus uses `1-exp(-tau)` and the **mean virtual occupation** is directly `Dfnu_hist[b][iz] = xv[b]/x1s`, not an independent transported scalar. The existing Python `full_2012_atomic_source.py::_original_escape_factors` intentionally reproduces C libm order, whereas `accurate_escape_factors` is a separately labelled stable alternative.

Define `phi(t)=1-(1-exp(-t))/t`. Exact Taylor for positive t:
`phi(t)=t/2-t^2/6+t^3/24-t^4/120+t^5/720-...`.
Treating `u=exp(-t)` as a rounded intermediate, `d phi/du=1/t`; hence absolute error in `u` is amplified by ~`1/t`. In the nine observed bins `t` lies roughly `1.39e-6..8.31e-6`, and `Q` (diagnostic source coupling) lies `3.8e-10..4.7e-9`. A mean field represented as `A=f_in+phi(t)*Q` can therefore differ from the high-precision shadow by order `Q*u_machine/t`, reaching ~`1e-19` in the worst small-depth bins. This is an input-conditioned roundoff estimate, NOT a blanket replacement of the original tolerance.

The original U5 frozen check `|A_P-A_C|<=1e-7 max(|A_P|,|A_C|)+1e-10 f_BB` FAILS at 9 of 2,290,204 mean-field entries, maximum tolerance ratio 32.65, and stays **HOLD**. Separate already completed R3g common-input C/Python checks cover 18 owner states and all 625 channel fields each; max average tolerance ratio on identical states was 0.000222. Original cross-history FAIL is not converted to a PASS by common-state checks.

A **new, independent diagnostic** may test `(i)` C/Python stable-shadow mean `A80` inside the original unmodified tolerance, `(ii)` each literal source raw minus the shadow is bounded by a *predefined IEEE error budget* using `u=2^-53` and the actual recorded `tau,Q,f_in`, and `(iii)` deliberately perturbed raw fields fail. This is a new `ROUNDOFF_EXPLAINED` admission, not `U5_ORIGINAL_GATE_PASS`. Do not widen, edit or reclassify the frozen U5 verifier.

## h/2 physics (no time-grid coercion)

For emission ratio `E_source/E_target>1` and FLRW `eta=ln(a)`, `eta_emit=eta_face-ln(E_source/E_target)`. Each new time step h must rederive the RT start from original `izH0(h)`, original H/He stage transitions, history timestamps and retarded interpolation indices: `u=(eta_emit-eta_RT(h))/h`, `k=floor(u)`, `theta=u-k`, `f_in=(1-theta)*f_out[k]+theta*f_out[k+1]`. For an active query, `k+1<=j-1`. Earlier emission uses only the source-defined blackbody prehistory, zero *distortion*, without retroactively resetting generated photons. The same 311 energy bins can be retained at smaller h if their strict original causal spacing criterion remains satisfied. A coarse accepted checkpoint is not a refined initial state.

For a smooth component `f(eta)`, convex linear temporal interpolation has leading defect `+f''(eta_emit) theta(1-theta) h^2/2`; the original source 2-step increment `h(5f_j/4-f_{j-2}/4)` minus exact `integral_0^h f(eta_j+s)ds` has leading defect `-(2/3)h^3 f''(eta_j)`. Wolfram Language independently expanded the series and confirmed this coefficient. A global p=2 Richardson assertion requires smooth, stage-aligned histories and observed contraction; switching/snap and off-grid phase change make unconditional p=2 invalid.

## Phase DAG

- **P1** primary original-C source and nine-failure provenance: VERIFIED; mathematical phi-conditioning: DERIVED + Wolfram checked; published this document and independent Drive copy.
- **P2** sandbox IEEE-shadow audit (9 saved coordinates) plus deliberate corruption controls: READY.
- **P3** real original-C q0 H+He `h,h/2,h/4` source-variant reference run and causal interpolation prototype: READY, bounded sandbox only.
- **P4** integration of evidence, criterion-freeze and executable Codex handoff for *independent Python* h/2 primordial history: PENDING.

**Claims excluded:** the complete Python `h/2` trajectory, its convergence, nonzero Bianchi, REI initial-state adoption and CMB predictions remain NOT_RUN.
