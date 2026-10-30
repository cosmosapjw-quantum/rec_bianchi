# REC-HD source-owned 15-state CMB line transfer | scientific report (2026-10-30)

## Source and physical outputs

New bounded auxiliary from frozen PR #173 source, Neufeld (2026) v2 standard and alternate HD collision rates, exact original 15 energy levels, Einstein A and radiative frequencies. The source .dat/.fits files are protected by SHA256 and contained in the entire source ZIP, not promoted to the original CDMS2011 owner.

- Real model solutions: **160 15-level stationary source+CMB states**, **17920** resolved per-line Gaussian transfer rows for 14 rotational lines, two microturbulent widths and four HD columns. This is physical-model data, not measured JWST flux.
- Signed excess line brightness: emission **16128** rows, CMB absorption **1792** rows.
- Screened small optical depth: **17346** rows with |tau0|<0.1; **574** formal-only rows outside that self-consistency guard. Max tau0=6.62316205; min tau0=-0.000585319941 at the chosen column upper bound 1e20 cm^-2.
- Signed negative optical depth (weak inversion): **80** rows. Note this repeats 10 physically distinct source/T/n/z states across line width and column choices, not 80 independent observations.
- Original source-knot inversion phase: **14490** density evaluations across **90** source/T/z conditions; **28** source-condition rows with two bounded roots. Standard source z=0,T=4000K n(on/off) = 522.85138472, 13766.58895242 cm^-3. The alternative original gives essentially the same window, but this is not an independent observational confirmation.
- The J1 inversion is absent in the isolated 2-level model and J<=2 truncation, but present in J<=3 (four levels), and persists across f_ortho=0,0.25,0.5,0.75,1 at the T=4000K nH2=1e4 cm^-3 z=0 test state. This strongly indicates multi-level pump/cascade within model; no novel molecular maser detection is claimed.

## Verification

Independent algorithm: 16 dense linear solves max |population difference|=7.8825835e-15 and 9 adaptive transfer integrals max |beta difference|=5.2530202e-13. Source SHA256 4/4 original immutable .dat/.fits verified. Normal and Python -O unittest suites, compileall, and clean-restored source replay run receipts in logs. Native distinct-author review NOT_RUN, same-context blind review attached. The underlying Neufeld source collision J>8 extrapolations and the observed JOYS shock gas interpretation are not promoted beyond source support.

## Origin and next scientific dependency

Official Neufeld Zenodo v2 additionally includes **posterior_isobaric.csv.gz** and **posterior_isochoric.csv.gz**, sourced from published Francis et al. (2025) JOYS/MIRI measurements. Exact v2 archive checksums: MD5 f21c0527fcf00829ad95888887d20afd and 6458f83f324a19c8e28fd656dcce2022. The current direct binary fetch path was blocked; Exa text-fetched gzip is irreversibly decoded, and these files are NOT part of this new capsule. No user-provided data is assumed. Source download URLs: https://zenodo.org/records/21165907/files/posterior_isobaric.csv.gz?download=1 and https://zenodo.org/records/21165907/files/posterior_isochoric.csv.gz?download=1. Next separate bounded research unit could ingest those **literal original bytes** and compare published source-owned isobaric/isochoric posterior medians without new fitting claims, then later obtain raw Francis HD/H2 flux and covariance to perform independent likelihood inference.

Original CDMS2011 35Hz 7/8 FAIL, H5 epsilon null, H6/H7 OPEN, L4 false, REI false; original canonical **28/88**, physical **0/313**, production HOLD. This new standalone auxiliary **1/1 SCOPED** does not add a canonical/physical node.

## Rendered figures and data

- `figures/HD_J1_INVERSION_DENSITY_z0.png`, `_z100.png`: source alternative and redshift dependence of overpopulation at the exact 4000 K original source knot.
- `figures/J1_INVERSION_T_Z_PHASE_WINDOWS.png`: original-temperature-knot onset and offset density windows, no invented temperature interpolation.
- `figures/HD_14LINE_CMB_ABSORPTION.png`: z=100 and Tgas=100 K net background absorption, not detection.
- `figures/HD_14LINE_WARM_EXCESS.png`: Tgas=4000 K warm emission, not detection.
- `figures/HD_14LINE_OPACITY_SCREEN.png`: optical-depth regime and 0.1 screening threshold.
- `evidence/FULLLINE_SLAB_TRANSFER_ATLAS.csv`, `J1_INVERSION_T_Z_N_DENSE_ATLAS.csv`, `J1_INVERSION_T_Z_PHASE_WINDOWS.csv`, `LOWJ_PUMPING_MECHANISM.csv`, `OPR_INVERSION_SENSITIVITY.csv` plus JSON summary and SciPy evidence.
