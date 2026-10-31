# REC-HD: Source-authentic 7 H2 + 6 HD KP5 and HD alternate-collider sensitivity (2026-10-31)

**Draft / exploratory / source-conditional / NOT production.** Immutable parent: [PR #180](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/180), HEAD `ab8faf1b509899fc7b67cc15f85de2e19c211071`. New research is isolated, add-only, no merge. Do not change CDMS 35 Hz, owner-source, or original gates.

## Scientific result

Author-original source inputs:
- Francis et al. (2025), *A&A* 694 A174, DOI `10.1051/0004-6361/202451629`; final Appendix F Zenodo [14592550](https://zenodo.org/records/14592550). Published 26 apertures x 14 lines = 364 entries.
- Neufeld (2026), *ApJ* 1007, 16, DOI `10.3847/1538-4357/ae851a`; original source Zenodo v2 [21165907](https://zenodo.org/records/21165907). Both **standard** and **alternate extrapolation** HD rotational population FITS and matching LAMDA files were verified by SHA-256, not a fabricated rate perturbation.
- Pontoppidan et al. (2024), *RNAAS* 8, 68, DOI `10.3847/2515-5172/ad303f`, original KP5 P24 v5 file [dust_extinction v1.7/p24.dat](https://github.com/karllark/dust_extinction/blob/v1.7/dust_extinction/data/p24.dat), Git blob SHA-1 `96d42fe318938d42d584f96e23661abd3cce96d5`. Original inverse-wavelength interpolation, extinction `kabs+ksca`.

**Real calculated physical source products:** 52 original isobaric two-temperature states, standard/alternate HD R(4..9) 156 physical line pairs; separately 52 original isochoric states with another 156 paired intrinsic HD lines, without imputing missing source H2-emitter OPR. The standard isobaric `N_upper` reproduces 156 original source lines with max fractional residual `1.63202784619898e-14`.

**Real published-flux working fits:** 26 apertures x 7 H2 S(1..7) + 6 HD R(4..9) = 338 source-observed line rows. H2 S(8) deliberately excluded (26 rows); eight HD observations with printed rounded-zero uncertainties excluded from likelihood. Each aperture profiled in original Neufeld isobaric physical-source bestfit under standard and alternate HD grids at assumed independent calibration epsilon 0 and 6%: **104** conditional fits, **1,352** predicted observed-frame line fluxes and **52** paired fitted contrasts. Source temperatures/columns, H2 non-LTE populations and KP5 shape unchanged.

At 26 fixed source states, per-line median `I_alt/I_std - 1`:
| HD line | Median fractional physical intensity change |
|---|---:|
| R(4) | -0.0343848924% |
| R(5) | -0.0756467591% |
| R(6) | -0.2265808286% |
| R(7) | -0.4450378422% |
| R(8) | +6.8664739519% |
| R(9) | +33.7288260554% |

Maximum individual R(9) fractional change `+96.2693856105%`. Isochoric median R(9) fractional change `+19.7766789883%`. For the 17 apertures with HD detected (epsilon=0), the **paired** median fitted molecular `x_HD,alt / x_HD,std = 1.000063655055278`, range `0.9812112476..1.0133339023`. These are descriptive *source-conditioned working-likelihood* quantities, **not** elemental D/H, significance or an independent posterior. All 54 changed high-J collision rate vectors are original source differences; no lower-J rate-switch ownership claim.

## Equations and scientific scope

For optically thin HD `I_ul = h c A_ul (N_u,1+N_u,2)/(4*pi*lambda_cm)`, `N_u,c = N_H2,c x_HD (2J_u+1) 10^LOGPOP(T_c,n_c,J_u)`. The source provides `LOGPOP = log10(f_u/g_u)`, grid coordinates `log10 T, log10 n`; no NaN replacement or grid extrapolation. Isobaric component density `n_c=(p/kB)/T_c`; isochoric components `n_1=n_2`, with individual pressures `p_c/kB=n T_c`. Fundamental `h,c` retained in cgs, emission in `erg cm^-2 s^-1 sr^-1`.

KP5 two-anchor working transfer uses `w(lambda)=[kappa_ext(lambda)-kappa_ext(S1)]/[kappa_ext(S2)-kappa_ext(S1)]`, `mu_H2=I_H2 exp[(1-w)(gamma1+delta1)+w(gamma2+delta2)]`, `mu_HD=(I_HD/x_HD,author) u*1e-5 exp[(1-w)(gamma1+delta1)+w(gamma2+delta2)]`. Baseline `gamma_i=ln(observed H2 S(i)/intrinsic H2 S(i))`. They include beam filling, aperture extraction and dust; they are **not physical dust optical depths**. Source-fixed `w(S3)=2.86475235`: extrapolation outside two anchor wavelengths, and HD R(4)-R(5) also extrapolate. Fit `delta1,delta2` and nonnegative `u` with Gaussian detected positive-error fluxes and declared upper-limit working term `-2 log Phi[(L-mu)/sqrt((L/3)^2+(epsilon mu)^2)]`; epsilon = 0 or 0.06 with per-line plug-in independent model-dependent variance. Missing empirical cross-line MIRI covariance does not block scoped work but **does** block full instrumental likelihood claims.

## Verified source artifacts & backup

Complete runnable code, tests, original source-conditional result CSV/JSON, two plots, stage ledger, manifests and reproduce instructions are archived as:
- **ZIP**: `REC_HD_PUBLIC_7H2_6HD_KP5_ALTEXT_ISOCHORIC_20261031_SOURCE.zip` (199,333 bytes)
- **SHA-256**: `282ac7f5b703ba73b8533e5dbf2d352e408550f5ea6ee44f4f47d451cca88e92`
- [Google Drive source ZIP](https://drive.google.com/file/d/1FExGNpbVHVlS8ynQYZ-dfDUQ0HWAayRL/view): upload success and full provider **raw-byte readback SHA-256 identical**, ZIP CRC clean.
- Dropbox: `/bianchi/rec_bianchi/20261031/REC_HD_PUBLIC_7H2_6HD_KP5_ALTEXT_ISOCHORIC_20261031_SOURCE.zip` ID `id:BSpOijBcT10AAAAAAEHWcQ`. Provider file size 199,333, Dropbox content hash `306829aff2d710de08eb44595922bcf5e329b95d02556c9fa1b068fc77cc8049` exactly matched independent computation from local ZIP. **Remote double-backup verified.**
- ZIP includes `src/joint_kp5_altex.py`, `src/isochoric_hd_alt_bridge.py`, `tests/test_joint_kp5_altex.py` and `docs/README_REPRODUCE.md`. This Git PR provides textual scientific checkpoint and pointers to binary source artifact; it does **not** claim the ZIP is stored in Git.

Scope-specific tests rerun after interruption: **16/16 normal PASS**, **16/16 Python -O PASS**, **12/12 scientific replay byte-exact**. Same-author adversarial mathematical/cgs, source-locked SciPy interpolation and Powell optimization tests. **Distinct-author R6/C9: NOT_RUN; native subagents: NOT_RUN.**

## Original gates remain fully frozen

`CANONICAL_DAG=28/88`, `REC_PHYSICAL_DAG=0/313`, `EXISTING_SCOPED_R_C=18/20`; two new physical **side-science** units, **not admitted** to 313-node DAG without original acceptance. `ORIGINAL_35HZ=FAIL7/8`, historical `verify_repo --quick` GitHub CI failure, `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_OWNER_SOURCE_SWITCH=true`, `NO_35HZ_RELAXATION=true`, `AUTO_NEXT_NODE=false`.

Next candidate only: retrieve and verify *full original* `posterior_isochoric.csv.gz` directly from Zenodo v2 (MD5 `6458f83f324a19c8e28fd656dcce2022`) to obtain omitted emitter OPR1/2 before any isochoric 7H2+6HD flux fit, and independently assess KP5 extrapolation/calibration robustness. No private covariance or author correspondence is a blocker to exploratory source-conditional science.
