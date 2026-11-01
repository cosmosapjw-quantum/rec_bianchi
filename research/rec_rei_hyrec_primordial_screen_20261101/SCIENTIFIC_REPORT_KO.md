# REC-owned original HyRec H+He primordial Thomson screen for REI IGM (2026-11-01)

## Source owner, qualified physical output
Immutable REC parent PR #186 HEAD `8af60c826f142f0a2e8de1b028bd72e7b5053d1b`. Original unchanged native HyRec2012 FULL H+He C stdout has 8001 redshift rows (z8000→0), stdout SHA256 `6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400`; raw gzip SHA256 `cfd1a7293431e4410e7ec597acc793d6b56e2d1f4eb5cd13ed3f48aaef4e26fb`. Exact 1581-row source-owned original REC reference `research/rec_r3c_rei_bridge_20261015/HYREC_FLRW_Z20_TO_1600.csv` Git blob `2b50008c744d9cb241d9985a4bf6ce8bcf83e09a`, parent native packet `REI_CONDITIONAL_BOUNDARY.json` blob `89cdfc766e2e613760d84274812f2b4432373354`, original conditional AXBI recipient scenario SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`.

**Original C output units audited:** the raw C third column is `T_m(z)/(T_CMB0*(1+z))`, *not kelvin*. All 1581 physical source rows agree with `Tgas_K=2.7255*(1+z)*raw_column_3` at maximum relative difference `4.440892098500626e-16`, and their native x_e values are exactly equal. A naive raw-file Kelvin import into REI is physically wrong; new producer rejects source drift.

## New physically sourced, non-IVP optical screen
For homogeneous source-equivalent FLRW `h=0.674, Ωm=.315, Ωr=.000092, ΩΛ=1-.315-.000092` and source electron density normalized to recipient REI n_H,
[
kappa(z)=rac{csigma_T n_e(z)}{(1+z)H_f(z)},quad
	au_{m REC}(20,z)=int_{20}^zkappa(z'),dz',quad
{cal T}(z)=e^{-	au_{m REC}},quad
g_{m REC}(z)=kappa(z)e^{-	au_{m REC}}.
]
The stored source field `dtaudlna` is a **positive opacity per absolute logarithmic scale-factor**, not the signed derivative of `tau(20,z)` with respect to forward `ln a`. All source variables are SI, `c=299792458 m/s`, `sigmaT=6.6524587321e-29 m²`. The original H/He electron fraction includes early helium; it is never globally relabelled `xHII`.

**Source-owned actual results (new 1581 model-derived physical rows):**
- `tau_REC(20,50)=0.0001242088036887898`
- `tau_REC(20,100)=0.000465184391491274`
- `tau_REC(20,300)=0.0033740794424056584`
- `tau_REC(20,600)=0.015074236360913805`
- `tau_REC(20,800)=0.04197565197565985`
- `tau_REC(20,1000)=0.3291685203546441`
- `tau_REC(20,1100)=1.1246680564687528`
- `tau_REC(20,1600)=32.55814961583067`, `transmission(20,1600)=7.24728400790639e-15`.
- The source-grid conditional visibility `g(z)` peaks at z=1078; linearly interpolated `tau_REC(20,z)=1` at z=1089.8705743259025. This is **not a new measured Earth-observer CMB last-scattering redshift**.
- Artificial **frozen x_e(z=20)** comparison: at z=100 `tau_fixed=0.0003941224891241955`, true source `tau=0.000465184391491274`; +18.03041042519284% effect relative to this non-evolving counterfactual. Do not mistake this control for a second recombination history.

At z20, original HyRec full q0 donor `x_e=.000210349192936`, `Tgas=9.306042400380866 K`, `n_e=.3697773871925435 m^-3`, positive `c sigmaT ne/H=6.231193488564117e-5`; original REI AXBI scenario approximate `xHII=.0002`, `Tgas=8.098143045064857K`, `ne=.351584317516303 m^-3`, `c sigmaT ne/H=5.924618394385755e-5`. Donor conditional opacity +5.174596468%, not automatically adopted. Recipient nH differs from native HyRec nH by ~0.0541154%; REC 1581-row `ne_m3` was **already** normalized to recipient density, do not scale twice. Ionizing astrophysical photons remain zero in original REI AXBI source.

## Validation, preservation, and claim gate
Source original + recipient packet SHA/BLOB exact, original native 8001 raw stdout x_e + Tm/Tgamma conversion checked all 1581 rows, n_e/H source opacity maximum relative discrepancy `1.1102230246251565e-15`, cumulative Simpson/3-8 versus trapezoid full-range relative difference `8.46584135276792e-8`, and `int_{20}^{1600} g dz ≈ 1-exp[-tau(20,1600)]`. Targeted GitHub Actions `41284733830` PASS, 11/11 Python normal and 11/11 Python -O. New 1581 source-derived output gzip CSV `ORIGINAL_HYREC_TO_REI_PRIMORDIAL_THOMSON_1581.csv.gz` SHA256 `879e51d67ab9a55be81a019a6bf08487ba425ab3bf97f30bc01cdda2825555a0`. GitHub Actions source-inclusive artifact #13074727633, size 380109 bytes, ZIP SHA256 `6e355c08d8cf4aa7a95209e72b768cd77f63f41404f57f65c3fd680bad919add`, CRC PASS. Standalone clean restore `11/11 + 11/11`, physical CSV **BYTE EXACT**. This is original C-source replay of *saved output*, not re-execution of original HyRec C itself this cycle.

General repository verify `41284733791` is **FAIL**, inherited unrelated trailing whitespace in `research/rec_source_synthesis_20261027/history_remainder/results/primary001/*.csv`; cannot claim full repo CI PASS. This is an implementation/format integration blocker, NOT evidence that the new source-locked HyRec physics failed.

**Scientific ownership:** `rec_bianchi` q=0 primordial H+He high-z source history `20≤z≤1600`; *not* native `rei_bianchi` H/He astrophysical F05 owner and *not* an admitted Bianchi directional or z0→zfull CMB visibility. Must add a separately accepted `z<20` REI-owned scattering/LoS interval to form a larger optical depth, avoiding overlap. Original REI F05 first complete interval remains `BLOCKED_MINIMUM_STEP` (160/131072 ticks, [160,161] old `2.1245050576368385e-4>2e-4`). REI canonical **28/88 (+0)**, REI working **33/88 (+0)**, REI Physical Fast 4/7 (+0); REC H5 physical **0/313 (+0)**. No original source owner or tolerance swap, no new REI IVP, no production, no merge, no force push, no auto next.

**Disposition:** REC→REI read-only primordial source packet + named conditional AXBI upstream optical consumer is **SOURCE_READY_READ_ONLY**. Actual native REI receiver injection, accepted F05/F08 history, full source/clock/geometry matching and all 313 H5 physical obligations **NOT_DONE**. Independent distinct-author referee NOT_RUN; one bounded same-author adversarial review performed.

Source literature: Ali-Haïmoud & Hirata, *HyRec: A fast and highly accurate primordial hydrogen and helium recombination code*, Phys. Rev. D 83, 043513 (2011), DOI 10.1103/PhysRevD.83.043513. Literature is context, source-native C bytes remain the actual numeric authority.

## Next REC-owned action
Obtain a **named source-locked REI AXBI LoS/opacity receiver** (not the unrelated original REI F05 microphysics state), perform one read-only z20 event/clock/nH/He-number/differential-opacity injection-parity check against the typed REC packet. Preserve disabled/opt-in adoption. If the named receiver cannot accept source, close the blocker as an explicit missing field, rather than fabricating a F05 pass or launching an unapproved IVP.
