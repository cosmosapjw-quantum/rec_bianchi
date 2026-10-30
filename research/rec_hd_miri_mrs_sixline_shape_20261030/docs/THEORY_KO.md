# REC-HD MIRI 6-line source-manifold geometry | THEORY (2026-10-30)

## Scientific authority and frozen boundary

Original Neufeld (2026) Zenodo v2 source files `hd_lamda.dat`, `hd_lamda_altex.dat`, two original FITS images. Original 2011 CDMS 35 Hz 7/8 FAIL is an independent unmodified owner gate. Parent PR #172 SHA `331602990e014e8ff532f6cc6179d6a74a1e3296`, protected parent #171 and sibling #170 are unchanged. This is a sourced *theoretical non-LTE physical model* calculation, not telescope sky flux or direct measured molecular spectroscopy.

## Definitions / equations

15 HD rotational states `J=0..14`; generator `M_{ij}` has off-diagonal inflows and conservative diagonal outflows, stationary populations satisfy `M p = 0`, `sum_J p_J=1`. At gas temperature `T_g`, de-excitation rate `n_H2 C_{u l}(T_g)` combines original para/ortho coefficients with fixed `f_ortho = 0.75`. Reverse collisional excitation uses molecular degeneracy and detailed balance,

`C_{l u} = C_{u l} (g_u/g_l) exp[-(E_u-E_l) hc/(k_B T_g)]`.

For isotropic CMB `T_gamma = 2.72548(1+z) K`, photon occupancy `N_ul = [exp(h nu_ul/(k_B T_gamma))-1]^-1`. The *net radiative power* per HD molecule is

`P_ul = h nu_ul A_ul [p_u(1+N_ul) - p_l (g_u/g_l) N_ul]`,

for six high-J lines `R(4)..R(9)`, upper levels `J=5..10`. Each `P_ul` in selected warm cases is positive; no clipping of populations or weak line powers. `c`, `h`, `k_B` retain SI units in source code. Source ν and energy-level gaps have a historically identified small mismatch; do not force equilibrium cancellation or use this to relax the separate 2011 CDMS 35-Hz gate.

Geometric observed wavelength `lambda_obs = (1+z)c/nu`. MIRI MRS *effective* range is `[4.9,27.9] μm`, from official STScI documentation, not NASA's less-conservative 28.8 μm nominal edge. Each source line may occur in multiple overlapping MRS subbands; A/B/C setting coverage is assessed explicitly. A single MRS exposure cannot record every A/B/C subband simultaneously.

To eliminate a *common unknown HD column normalization* and compare original source alternatives, let `d_i(T_a,n_a,z;T_s,n_s) = ln P_i^alt(T_a,n_a,z)-ln P_i^std(T_s,n_s,z)` over geometrically accessible lines. Define

`Delta_shape = max_i d_i - min_i d_i = max_(i,j) | ln[(P_i^alt/P_j^alt)/(P_i^std/P_j^std)] |`.

The strict nonnegative dimensionless metric is twice the minimal `L∞` log-power error after fitting a common additive log-normalization `a`:

`min_a max_i |d_i-a| = (max_i d_i-min_i d_i)/2`;

proof: writing `m=min d_i, M=max d_i`, any `a` has max error `≥max(|M-a|,|m-a|)≥(M-m)/2`, with equality at `a=(M+m)/2`. Verified by elementary proof and a Wolfram minimax sample (`{9/2,9/2}`).

Two nested nuisance profiles:

`Delta_n = min_{10^2≤n_s≤10^10 cm^-3} Delta_shape(T_s=T_a,n_s)`,

`Delta_Tn = min_{T_s in {1000,2000,3000,4000} K} min_{10^2≤n_s≤10^10 cm^-3} Delta_shape(T_s,n_s)`.

Thus necessarily `Delta_Tn ≤ Delta_n ≤ Delta_direct`. We *do not* invent continuous temperature rate interpolation, measurement covariance, error bars, detection probabilities or likelihoods. Minimization is deterministic but approximate (33-point log-density coarse grid + bracketed bounded refinements), not certified global convexity.

## Domain and limits

Exact original 4 source temperatures, densities `{1e2,1e4,1e6,1e8,1e10} cm^-3` for synthetic alternative targets, redshifts `{0,.1,.25,.5,.75,1,1.25}`. Standard source density fitted continuously only within original physical density domain; ortho-H2 fraction fixed to `.75`. Missing instrumental sensitivity, dust, line profile, sky flux, source parameter uncertainties, optical depth and statistical calibration invalidate a detection inference. For `<2` accessible lines, shape comparison cannot identify collision source under unknown amplitude; outputs 0 by definition, not a success claim.

## Primary resources

- D.A. Neufeld (2026), *Excitation of warm HD and H2 and implications for the interstellar deuterium abundance*, ApJ 1007:16, DOI 10.3847/1538-4357/ae851a; original data https://zenodo.org/records/21165907 (v2).
- STScI, *MIRI Medium Resolution Spectroscopy*, https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-medium-resolution-spectroscopy; 4.9–27.9 um effective wavelength, A/B/C subbands.
- Sung et al. (2023), JQSRT 295, 108412, DOI 10.1016/j.jqsrt.2022.108412; external experimental covariance NOT included.
