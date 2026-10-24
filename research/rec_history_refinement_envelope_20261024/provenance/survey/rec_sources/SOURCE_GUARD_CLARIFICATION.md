# Source-only clarification: prefix length and emission coordinate

Source reading only; no numerical execution or array comparison.

## Decision

The native condition `iz >= 2` constrains the current local step and the number of committed past columns. It does **not** require the retarded emission coordinate `(eta_emit-eta0)/h` to be at least 2.

For a sufficiently long frozen prefix, nonthermal interpolation permits

`0 <= x_emit < iz-1`, where `x_emit=(eta_emit-eta0)/h`.

Thus the selected pair has a represented-function closure `[0,759]` in coarse coordinates and common retained-data query domain `[0,759)`. The interval `[2,759)` would impose an extra lower emission cutoff absent from the native source. Physical incoming queries also need the source-owned prefix actually available at their face, the channel's retarded map, and the separate strict upper guard. A fixed retained-data domain alone does not establish admissibility at every face.

## Exact source witnesses

### Native C

Repository path:

`research/rec_r3s_ncp_campaign_20261021/ncp_execution_001/evidence/campaign_001/jobs/h4_legacy16/run/worker/source_extract/HyRec/hydrogen.c`

Local preserved source:

`/workspace/scratch/e3bcbaac138c/rec_admission_work/research/rec_history_input_admission_20261024/provenance/source_mapper/fetched/research/rec_r3s_ncp_campaign_20261021/ncp_execution_001/evidence/campaign_001/jobs/h4_legacy16/run/worker/source_extract/HyRec/hydrogen.c`

`interp_Dfnu`, lines633–654:

- Lines637–639: `iz==0 || iz==1 || lna<lna_start` returns thermal zero. The first condition is a prefix-size condition; the second is prehistory.
- Lines641–645: `lna >= lna_start + dlna*(iz-1)` rejects future/unavailable interpolation.
- Lines648–652: `ind=floor((lna-lna_start)/dlna)` and the convex combination of `ytab[ind]`, `ytab[ind+1]`. `ind=0` is allowed when the prefix has at least two columns.

`fplus_from_fminus`, lines656–668:

- Lines657–658 explicitly define `iz` as current time step and `fminus[0..iz-1]` as known.
- Lines672–678 show that `lna_start=-log(1+zstart)` and the emitted query is independently determined by the energy ratio and face redshift.

### Python source adapter

Repository path: `src/full_bianchi_hyrec/trajectory/causal_virtual_redshift.py`.

Local preserved source:

`/workspace/scratch/e3bcbaac138c/rec_admission_work/research/rec_history_input_admission_20261024/provenance/source_mapper/fetched/src/full_bianchi_hyrec/trajectory/causal_virtual_redshift.py`

`causal_incoming_from_accepted_histories`, lines171–263:

- Lines180–184: shapes use the prefix length `iz`; samples0..iz-1 are committed and indexiz is never read.
- Lines191–192 reject `iz<2` as fewer than two accepted past steps.
- Lines228–243 distinguish `eta_emit`, `eta_start`, and `upper_accepted=eta_start+dlna*(iz-1)`; FLRW prehistory receives the native thermal fallback, while anisotropic prehistory is rejected.
- Lines245–251 retain the last interpolation interval `[iz-2,iz-1)` and permit a cell index beginning at0. There is no emission lower guard `x_emit>=2`.

### Completed02R strict wrapper

Repository path: `research/rec_history_characteristic_resume_20261024/code/characteristic_adapter.py`.

Local file:

`/workspace/scratch/e3bcbaac138c/rec_next_work/research/rec_history_characteristic_resume_20261024/code/characteristic_adapter.py`

`strict_interpolation`, lines127–134:

- Line130 rejects `eta<eta0 OR iz<2 OR eta>=eta0+h*(iz-1)`.
- This deliberately rejects native thermal fallback as an admission policy; it does not shift the retained emission domain's lower end to `eta0+2h`.

Preserved vendor `history_boundary.py`, `interpolation`, lines72–103, returns thermal zero at lines80–82 for `iz<2` or `eta<eta0`; lines83–95 separately handle the endpoint, cell index, and two values. The wrapper's contract is also explicit in `FROZEN_CONTRACT.md` lines100–103.

## Notation for the new contract

Use different symbols for:

1. `N` or `iz`: committed prefix length/current source step.
2. `x_emit`: retarded emission coordinate.
3. `m`: coarse cell index in the represented-function discrepancy calculation.

The legacy/source condition is `N>=2` and `0<=x_emit<N-1` for nonthermal retained interpolation. For the complete selected pair, taking the intersection in coarse units gives `[0,759)`. The 759-cell represented-function comparison remains `[0,759]` as its continuous closure.
