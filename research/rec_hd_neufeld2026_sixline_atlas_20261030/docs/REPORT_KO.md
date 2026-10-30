# REC-HD Neufeld2026 six-line source-extrapolation atlas

2026-10-30. Independent source-locked research auxiliary, conditional physical model, no new observational measurements. Parent: `cosmosapjw-quantum/rec_bianchi` PR #171 HEAD `8e1f51397cc3019642668daf4b2f2c39ff5126d5`. PR #170 is a sibling. Canonical DAG **28/88**; REC physical **0/313**; original CDMS2011 v2 35 Hz **FAIL7/8**; production **HOLD**.

## Source authority and scope

The four original Zenodo v2 Neufeld (2026) files, `hd_lamda.dat`, `hd_lamda_altex.dat`, `hd_population_grids.fits`, `hd_population_grids_altex.fits`, are included with byte-preserving SHA256 locks. The 270 original-model standard/alternate CMB states and 3,780 per-line comparisons were restored from parent PR #171's full SOURCE archive. Fresh execution of the original 15-level source model reproduced the source CSVs **byte for byte**, SHA256 `77ff228765534fc2ed1e53524676748174936d33bca21a285bc7a0c55963943f` and `34df6177f1a219c8537741aea4dfb82e90752f3a00c0b0b28919565b85534365`. The two HD collision-rate sources differ in 54 of 210 collider-rate rows, all with upper J>=9 (extrapolated high-J rates). They are models, not new scattering measurements. No 2011 CDMS owner source was replaced.

## New original-source model observables

The six lines R(4)..R(9) are defined as J+1 -> J; original Einstein A and frequencies are used, including stimulated and CMB absorption. The optically thin per-HD net power is

\[F_J^{(s)}=h\nu_J A_J\{p^{(s)}_{J+1}[1+\bar n_J]-p^{(s)}_J(g_{J+1}/g_J)\bar n_J\},\quad \bar n_J=[\exp(h\nu_J/k_BT_{CMB})-1]^{-1}.\]

For any pair a>b, \(\mathcal R_{a/b}=F_a/F_b\), and \(\delta_{a/b}=\mathcal R_{a/b}^{alt}/\mathcal R_{a/b}^{std}-1\). Warm 1000/2000/3000/4000 K x 5 original-source densities x 6 CMB redshifts = **120 source-model physical conditions**, times **15 line ratios** = **1,800 new comparisons**. Of these, **1,512** pass the explicitly defined **1% source-model relative line-power floor**; 1,272 pass a stricter 5% floor. This floor is a scientific selection convention, *not* a JWST instrumental threshold or covariance.

At 1% floor, the largest fractional source contrast is **+100.980545%** for **R(9)/R(7)** at T=1000 K, n(H2)=1e6 cm^-3, z=30. Standard ratio = **0.0595818716674**; alternative = **0.119747970456**; minimum of the four relevant source-line powers is **2.51276%** of the maximum of the same six-line spectra. At z=0, the analogous contrast is **+100.980518%**. The more restrictive 5% source floor admits a maximum **+38.843719%**, R(9)/R(7) at T=2000 K, n=1e6, z=100. These are model-dependent intrinsic HD per-molecule radiation powers, not measured flux ratios.

For T=1000K, z=0, the source-model R9/R7 difference varies with n(H2) = 1e2, 1e4, 1e6, 1e8, 1e10 cm^-3 as **0.06643%, 9.39058%, 100.98052%, 1.56461%, 0.01549%**. The low/high density source-independence follows analytically from the common radiative generator at n=0 and the same collision detailed-balance Boltzmann stationary vector at n->infinity, conditional on irreducibility and nonvanishing ratio. Wolfram two-level symbolic calculation confirms source dependence tends to zero at both limits; this is not a claim that finite 15-state output is exactly zero at Tgas=TCMB when source rounded nu and DeltaE mismatch.

## Source uncertainty versus gas-density degeneracy

At the true physical density n=1e6 cm^-3, z=0, adjust *standard* collision model density until R9/R7 equals the alternative model ratio at fixed T. For T=1000,2000,3000,4000 K, the equivalent standard densities are **2.457883, 2.122723, 1.975266, 1.858047** times 1e6 cm^-3. Thus a single high-J source-ratio measurement cannot independently distinguish the collision-rate source from H2 density. A held-out R9/R4 comparison at the matched density retains **-21.75569%, -8.53932%, -5.09481%, -3.69147%** residual source differences respectively. This suggests complementary lines may reduce that degeneracy within the stated model; no observational identification, statistical significance, line flux likelihood or external calibration has been computed.

R(9) rest wavelength 12.47183 micron and R(7) 15.02195 micron. STScI documents JWST/MIRI MRS 4.9–27.9 micron bandpass; both lines lie within this *rest-frame* range for nearby emission. For high z the observed wavelengths are multiplied by (1+z), so the z>=10 CMB model grid is **not** JWST MIRI-observable. No optical-depth, dust, geometry, velocity or actual JOYS detector completeness calculation is made.

## Actual verification

- Source lock: all four original Neufeld Zenodo v2 .dat/.fits SHA256 plus the 270/3780 original-source CSV SHA256: PASS; 2011 owner remains frozen. Previous PR171 source generator executed anew and both input CSVs matched archived originals bytewise.
- 270 original CMB states x 14 transitions: net line sum versus model total energy residual below 3e-14 relative. Derived 120 conditions and 1,800 ratios; 1%/5% cuts exactly 1,512/1,272.
- New Python: **20/20 normal and 20/20 -O** tests; `compileall` PASS. Includes source tampering rejection. Independent SciPy dense original 15x15 solver vs source original M-matrix on 8 model/source cases: max abs population difference 1.81e-16 and maximum significant line-power relative difference 1.38e-14.
- Wolfram exactly verified two-level source-change difference zero at n->0 and n->infinity. Independent distinct-author R6/C9 **NOT_RUN**, native subagents not available. See `docs/BLIND_REFEREE_SAME_CONTEXT_KO.md`.
- Source/whole model inputs and new scientific CSV/figures are in the self-contained ZIP archive. Earlier sibling R9/R4 Git CSV was contaminated by a sheet-text adapter; this research does **not** import from that Git CSV. Git publication of new large numeric CSV is not needed for source identity: immutable ZIP is canonical numerical artifact.

## Admission and remaining source gaps

`NEW_AUXILIARY=1/1_SCOPED`; R/C 18/20 with R6 and C9 distinct-author NOT_RUN; original canonical 28/88, REC physical 0/313, original 35 Hz FAIL7/8, H5 epsilon null, H6/H7 OPEN, L4 false, REI activation false, PRODUCTION HOLD. No merge, no source switch, AUTO_NEXT_NODE=false.

Original experiments needed for eventual observational GLS: Sung et al. *JQSRT* 295 (2023) 108412 DOI `10.1016/j.jqsrt.2022.108412`: actual R(0)..R(3) multispectrum raw files, frequency-calibration nuisance covariance and joint line-center error covariance; 2011 CDMS v2 full-precision SPFIT `.var` or source-owned correlation. Official `HD.fit` only has a **rounded printed** correlation. These are not contained in the papers' accessible outputs; user need not provide files right now but a corresponding-author or CDMS curator request can unblock future experimental admission.

## Bibliography

Neufeld, D. A. (2026), *ApJ* **1007**, 16, DOI 10.3847/1538-4357/ae851a, original data DOI 10.5281/zenodo.21165907. Wan, Y., Balakrishnan, N., Yang, B. H., Forrey, R. C., Stancil, P. C. (2019), *MNRAS* **488**, 381–386, DOI 10.1093/mnras/stz1735. Sung et al. (2023), *JQSRT* **295**, 108412, DOI 10.1016/j.jqsrt.2022.108412. JWST MIRI MRS: https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-medium-resolution-spectroscopy .
