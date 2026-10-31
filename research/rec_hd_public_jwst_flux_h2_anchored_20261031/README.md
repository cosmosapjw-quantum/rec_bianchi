# REC-HD | Published Francis H2/HD flux likelihood (DRAFT / HOLD)

**Immutable parent:** PR #178 HEAD `4dd4bd18505287d944c47d89524f29c17f667843`. Changes solely in this independent add-only directory. Do not merge, activate production, change original CDMS source owner or relax original 35 Hz FAIL7/8.

## Source authority: all already publicly released
- **Observed flux SSOT**: Francis et al. (2025), A&A 694 A174 DOI 10.1051/0004-6361/202451629, final Appendix F DOI 10.5281/zenodo.14592550. 26 apertures × 14 lines = **364** printed cells. 207 H2 and 76 HD positive-error detections, one H2 and 72 HD upper limits, eight HD rounded-zero printed errors excluded.
- **Physical SSOT**: Neufeld (2026), ApJ 1007:16 DOI 10.3847/1538-4357/ae851a, original Zenodo v2 DOI 10.5281/zenodo.21165907: exact H2 para/ortho and HD non-LTE FITS, original 26 aperture isobaric posterior. Their original source bytes MD5 passed. Source-author-bestfit T/n/N/emitter OPR and original population grids **fixed**.
- **Reusable original code**: Neufeld Zenodo v2 `test_fitsread.py` for LOGPOP+state degeneracies, and original official STScI `spacetelescope/jwst` MIRI `extract_1d`/`calwebb_spec3` docs as instrument reduction authority. They do NOT provide recovered author cross-line covariance.
- **Published extinction reference**: Pontoppidan et al. 2024 KP5 DOI 10.3847/2515-5172/ad303f. Exact KP5 optical numerical curve was not locked for this scoped run, so no fabricated extinction kernel was used.
- Frozen PR #176 **29,640 HD profiles not rerun** and PR #178 **364 nonLTE intrinsic H2/HD lines** source data reused by exact CSV identity, not regenerated.

## New measured-flux physical data and statistical scope
Two H2 observed anchor lines S(1) at 17.03 µm and S(2) at 12.28 µm fix per-aperture effective throughput `G=F_obs/I_intrinsic`. Two log-throughput nuisance parameters are profiled jointly with `xHD=N(HD)/N(H2)>=0`; HD predicted fluxes are `mu_HD,j=(xHD/xHD_author) * I_HD_author,j * exp((1-w)log G_S1 + w log G_S2)`, `w=log(lambda/lambda_S1)/log(lambda_S2/lambda_S1)`.

**Working likelihood** uses published positive-error Gaussian detections and `Phi((L-mu)/(L/3))` for published three-sigma upper limits. Assume diagonal source errors and compare epsilon=0 vs additional independent 6% model-dependent flux scatter. This is neither recovered cross-line instrumental covariance, nor original Neufeld generative likelihood, nor an independent posterior. The previously published author posterior used the same Francis observational data.

**104 new 3-parameter source-conditional observed-flux working fits**, **520 HD line predictions**, **52 H2 effective transmission observables**, 26 apertures; full HD R4-R9 six-line and R6-R9 four-line in-range-only subsets × epsilon=0,0.06. R4/R5 are explicitly **extrapolated beyond H2 anchor wavelength interval** and sensitivity is separately reported.

For the 17 source apertures with HD positive printed-error detections, `full_HD,epsilon=0` fitted **molecular** xHD median `1.350110547772967e-5` (not elemental D/H); 9 all-limit apertures have zero-amplitude optima, never pressure measurements. Bracket-only positive detections 16, median `1.457029366358308e-5`.

## Actual validation (scoped)
- **27/27 Python normal + 27/27 Python -O PASS**; full 104-case numerical independent-method oracle **104/104 PASS**.
- Geometry: original Francis 1 arcsec radius aperture `Omega=7.38413463084415e-11 sr`; 52 conditional H2 transmission ratios 0.0059609176 to 0.754834619, none exceed 1.
- Original-inclusive source archive: `REC_HD_PUBLIC_JWST_FLUX_20261031_SOURCE.zip` **3,916,018 bytes, SHA256 `d67bbe7c497192fd33469ae860fa6813cdd45da8ec18fbc98025652e89833079`**, source manifest **54/54 exact, ZIP CRC PASS**, isolated science/plot replay **10/10 byte-exact**, all local tests pass. Full archive Drive file https://drive.google.com/file/d/1IHcSdyRDjD9kZCixZa8UE7Ys-fCjh8Gp/view, provider ACK + size verified; remote full-archive SHA256 readback **NOT_VERIFIED**.
- **Compact Git science ZIP** includes 45 individual files, code, tests, 104/520/52 data, four plots, and R1–R10/C1–C10 stage records, but not original FITS/CSV: `REC_HD_PUBLIC_JWST_FLUX_20261031_THIN_GIT_SCIENCE.zip`, 201,724 bytes, SHA256 `7cd59a4d5bd4448b110423a2d64b6e3b6e158969873664d7452885ddc8dc048f`. **Actual remote Drive raw byte fetch -> Git blob SHA1 `ba89209d60a458ecd0b45fa30ea69366bb4a7297` matches local Git hash**. Thus new science/code and 20 stages are doubly stored byte-exact, though individual separate per-stage file uploads NOT_RUN. Drive https://drive.google.com/file/d/1E5aY8TMSO18-WJCFX917gF3miwvUl_e2/view.
- GitHub parent `verify-durable-backup` workflow run 41173233309 **FAIL** at historical `scripts/verify_repo.py --quick` due old pre-existing trailing whitespace/blank EOF, pytest SKIPPED. New standalone tests do not repair this baseline repo CI failure.

## Admission and further science
`CANONICAL_DAG=28/88 (+0)`, `REC_PHYSICAL_DAG=0/313 (+0)`, scoped R/C `18/20`; true independent-author R6/C9 `NOT_RUN`, only same-context scientific/code blind review; original 35 Hz FAIL7/8; `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_OWNER_SOURCE_SWITCH=true`, `NO_35HZ_RELAXATION=true`, `AUTO_NEXT_NODE=false`.

Next science should use additional **published** measurements/opacities and author v2 isochoric posterior, compare H2 anchor extrapolation and true KP5, rather than block indefinitely on private author covariance. No independent D/H chemistry or formal pressure intervals from this unit.
