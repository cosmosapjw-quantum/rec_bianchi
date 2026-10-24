# REC-HISTORY-02R implementation map and reproduction

Scoped result: COMPLETE_SCOPED_CHARACTERISTIC_ADAPTER. Primary127 rows/776 numerical comparisons and one independent6-row/10-entry-call review support the constant-shear positive-rate Bianchi I represented-field leaf. Final review: `evidence/independent_review/FINAL_REVIEW.json`. Actual h4 uncertainty and angular/global thermal inputs remain downstream; parent REC-HISTORY is PARTIAL.

## Equation → implementation → data

| Equation / contract | Function | Input → output |
|---|---|---|
| a_i=1+b_i>0, trace b=0, unit normal propagation n | `characteristic_adapter.geometry` | finite n,b → normalized roundoff-admitted n,b,a |
| F(Δ)=ln||n exp(aΔ)||−Λ, q_s=Σa_i n_si², root bracket | `lognorm`, `crossing` | n,b,Λ,eta_t → Δ,eta_s,n_s,q_s,q_t,residual,bracket; lambda0/axis/FLRW exact values |
| Implicit dΔ and projected dn_s; q_t tangent distinct from q_s | `crossing_jvp` | crossing plus admitted dn,db,dΛ,deta_t → dΔ,deta_s,dn_s,dq_t; transformed overflow rejected |
| x_s=x_t exp(Λ−Δ), W=e^(−x), signed difference and derivative | `wien_x`, `reference` | x_t,Λ,Δ and tangent → log x_s,W_s,W_t,offset,doffset; xW limit0 |
| Strict retained prefix, fixed interpolation cell | `strict_interpolation` → unchanged vendor `interpolation` | eta0,h,values,iz,eta_s → stencil/value; missing prefix/future/knot tangent rejected |
| H=c0+v·n+nᵀQn; ten time-linear coefficients | `coeff_parts`, `angular`, `history_field` | coefficient history/source query and data/time/angular tangents → H,dH,cell |
| d_in=H+W_s−W_t; d_out=T d_in+A s | `compose` → unchanged vendor `boundary`, `boundary_jvp` | characteristic/field/reference and local target coefficients → departure,absolute occupation,boundary value/JVP |
| One local event number/energy ledger | vendor `line_ledger`, invoked by `compose` | local target q_t,H_t and boundary jump → number rate,opposite atomic/radiation energy,extra source0 |
| Supplied-tube error map epsΔ≤epsF/a_min and propagated bounds | `error_envelope` | e_H,K_eta,K_n,epsF,arithmetic plus local target coefficients → conditional input/output/number/energy bounds |
| Independent80-digit reference | `independent_reference.cross`, `cross_difference`, `offset`, `composite`, `composite_difference` | exact promoted binary inputs → bisection/prechosen1e-25 central differences; no adapter/vendor import |
| Actual scalar retained input | `verify_primary.actual_rows`, actual case branch | exact h4 NPZ314×24 assembled from virtual311+Lyman3 → eight own-domain scalar interpolation comparisons |

`inputs/CASE_PLAN.json` binds all127 cases and original thresholds. NPZ hash: b2489168155ad1a18a887a880eb0ca90376be5506c3c61d6bf06e9e70007c54c. No actual angular field or M2 is inferred. The represented-direction ledger is not an angularly integrated anisotropic global rate.

## Exact commands and preserved outputs

Commands below document actual bounded execution. They are **not automatic rerun instructions**. Existing controller labels/output folders refuse overwrite; reuse the saved evidence unless changed dependencies require an authorized new invocation.

Dependency repair, only if absent in an isolated reproduction environment:

```bash
python -m pip install --target environment/deps mpmath==1.3.0
```

The actual primary command from unit root was:

```bash
python code/run_bounded.py --cpu 15 --wall 44.8 primary002 env PYTHONPATH=/workspace/scratch/e3bcbaac138c/rec_next_work/research/rec_history_characteristic_resume_20261024/environment/deps python code/verify_primary.py --output results/primary002
```

The first primary001 import failure and all associated measured costs remain preserved. Exact environment origin/version and setup cost are in `ENVIRONMENT_REPAIR.json`; the final command binding is in `evidence/setup/PRIMARY002_ENVIRONMENT_FREEZE.json`. Source/input snapshots, command/environment, raw stdout/stderr and postexit inclusive child resource receipts reside under `execution/`.

Independent reviewer invocation, already completed by the reviewer:

```bash
python code/run_bounded.py --cpu 6 --wall 15 review001 env PYTHONPATH=/workspace/scratch/e3bcbaac138c/rec_next_work/research/rec_history_characteristic_resume_20261024/environment/deps python evidence/independent_review/run_probes.py
```

Saved-row presentation repair, already completed:

```bash
python code/run_bounded.py --cpu 4 --wall 15 figures002 python code/render_saved_rows.py
```

The renderer reads only primary002 saved JSONL/SUMMARY. First figures remain in `results/figures/`; accepted presentation repairs are in `results/figures_repaired/`. Original renderer snapshots and identity bindings are in `evidence/setup/`. Numerical inputs, criteria, adapter and independent oracle were unchanged by presentation repair. All failures, setup, runs and rendering are included in the combined new-local ledger; old-unit budgets remain separate.
