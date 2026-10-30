# REC-HD | JWST line-flux conditional covariance science unit | 2026-10-31

## Scientific authority and scope

Repository `cosmosapjw-quantum/rec_bianchi`; frozen parent Draft PR #174 HEAD `4a5916761c60bf68163ab1f3845db35cbb789d97`; its base PR #173 HEAD `90d883c77b3823322f2ecdb09888442b9a620a97`. Original parent ZIP `REC_HD_CMB15_FULLLINE_TRANSFER_20261030_SOURCE.zip`, SHA256 `a8766c178f9cdecca26ce1f2ccc19574babe1391adcc00ce43a6943ecc6d65d1`. Parent ZIP was CRC checked and the parent 18/18 normal and 18/18 `-O` source tests passed in the resumed environment. This is an **add-only auxiliary scientific research** package, not the REC owner's 35 Hz source replacement, not the public `main` branch, and not a fully restored observational likelihood.

### Primary literature / primary provenance

- L. Francis et al., *JOYS: The [D/H] abundance derived from protostellar outflows across the Galactic disk measured with JWST*, A&A **694**, A174 (2025); doi:10.1051/0004-6361/202451629. The original *arXiv v1 manuscript* 2501.02085, pp. 25–26, Tables **E.1** (H2) and **E.2** (HD), was used as a **manual numeric transcription from the publicly retrieved PDF's parsed page text**. The journal-final source locates these as Zenodo Appendix F, record 14592550, file `appendix_zenodo_jan7.pdf`. We did not download and byte-verify that final PDF. The transcribed arXiv v1 entries must not be equated to byte-authentic final Zenodo data before a table-level reconciliation.
- David A. Neufeld, *Excitation of Warm HD and H2 and Implications for the Interstellar Deuterium Abundance*, ApJ **1007**, 16 (2026), doi:10.3847/1538-4357/ae851a; Zenodo v2 original HD 15-level `.dat/.fits` source record 21165907. Four original bytes are preserved in `source/zenodo_v2` and verified by per-file SHA256 in `hd_line_transfer.read_models`. The original 15-level solver is frozen from parent source ZIP. Neufeld's independent 6% spectrophotometric calibration error is used **only as an explicit assumed scenario**; actual across-line calibration covariance is unknown.
- Sung et al., *The rotational spectrum of HD broadened by H2 at temperatures between 100–296 K*, JQSRT **295**, 108412 (2023), doi:10.1016/j.jqsrt.2022.108412: **laboratory** broadening parameter covariance, not a surrogate for astrophysical JWST line-flux covariance. Earlier parallel PR #166 has nine laboratory closure measurements; this unit does not change it.

## Exact observed printed table structure (derived transcription)

`26 apertures × [8 H2 S(1..8) + 6 HD R(4..9)] = 364` printed entries, un-extinction-corrected observed line flux unit `10^-15 erg cm^-2 s^-1`. Statuses: **283** detections with positive *printed* error, **8** with reported uncertainty rounded to `0.00`, **73** limits reported as `<value`. The original manuscript uses an empirical 3-sigma upper-limit rule. No upper limit is treated as a detection. Printed `0.00` is not promoted to a true zero measurement uncertainty. The Gaussian profile uses only HD positive-printed-error detections at positions with >=3 valid lines: **16 of 26**, excluding 10, for an honest lower-dimensional conditional diagnostic. All 364 original printed entries are preserved in `outputs/francis2025_arxiv_v1_line_flux_364.csv` with species, line, aperture, censoring status and source-version marker.

## HD non-LTE source model and flux formula

Signature (-,+,+,+) is irrelevant to the molecular-radiative stationary solver. Original SI constants c = 299792458 m/s, h=6.62607015e-34 J s, k_B=1.380649e-23 J/K maintained. For each exact original-source temperature knot `T∈{100,200,300,400,600,1000,2000,3000,4000} K`, the **single-component** model uses a 19-point `n(H2)∈[10²,10⁸] cm^-3` logarithmic density grid. Independently, the **two-component isobaric** model uses 19 pressure points `log10[(p/k_B)/(K cm^-3)] = 7 + j/6, j=0..18` (thus 7 through **10**), with `n(H2)=(p/k_B)/T`. At redshift z=0, CMB T=2.72548 K, ortho-H2 fraction exactly 0.75. The statistical equilibrium generator includes 15 HD J-levels, radiative spontaneous/stimulated and CMB absorption rates, original standard and explicitly source-provided alternate HD–H2 collisional coefficients. Radiative net photon power per HD per R(J) is sourced **unchanged** from the parent `line_power_records[].net_W_per_HD`; in general it includes spontaneous and stimulated emission minus CMB absorption. In these high-J z=0 cases the latter two are negligible but were not removed from the source solver. Positive source amplitudes absorb HD abundance, distance, geometry, aperture, and unit conversion. One temperature model: `F_model = a q(T,p/T)`; two-temperature model `F_model = a q(Twarm,p/Twarm)+b q(Thot,p/Thot)` with a,b>=0, Twarm<Thot and common pressure. **The fitted amplitudes cannot be interpreted as source columns** without missing extinction, calibration/beam, emission geometry and radiative transfer.

Physical grids: 2 original extrapolation choices × 19 **density** values × 9 exact T = **342 single-component emitter states**, 2 × 19 **common-pressure** values × 36 distinct temperature pairs = **1,368 two-component isobaric emitter models**. Highest absolute rate stationarity residual <1.12e-17 s^-1; 15-state probabilities were nonnegative, normalized to one. Results use original source collision T knots, not fabricated intermediate temperatures.

## Conditional covariance family and mathematical identity

For retained line flux vector `F_i>0`, printed positive statistical uncertainty `s_i>0` (same flux unit), and *assumed* cross-line fractional calibration correlation `rho∈[0,1]` (not measured), define:

`C_rho = diag(s_i^2 + (1-rho)epsilon^2 F_i^2) + rho epsilon^2 F F^T`, with `epsilon=0.06`.

`rho=0`: Neufeld-style independent per-line 6% quadrature; `rho=1`: fully common multiplicative calibration hypothesis. Full rank in the restricted data because all s_i>0. The Jacobian of log ratio `ln(F_i/F_j)` yields

`Var[ln(F_i/F_j)] ≈ (s_i/F_i)^2 + (s_j/F_j)^2 + 2 epsilon^2(1-rho)`, i != j,

and a 2×2 principal minor determinant `s_i²s_j² + epsilon²(F_i²s_j² + F_j²s_i²) + epsilon⁴ F_i²F_j²(1-rho²) > 0` for positive s. Wolfram Language evaluator independently simplified both expressions. General rank-one calibration `F=(1+a) M(theta)+noise`, `a~N(0,epsilon²)` induces `C(theta)=D+epsilon² M(theta)M(theta)^T`, and **the model-dependent likelihood must include logdet C(theta)**. Our C_rho instead plugs in observed F to make a fixed positive-definite **sensitivity** metric, not a generative joint likelihood. Comparing chi² across different assumed rho does *not* yield evidence for rho or a Bayes factor. Inter-line extraction covariance, dust extinction and wavelength-subband calibration structure remain unmeasured. The H2 likelihood is *not* implemented.

For each model row Q, compute `chi²_rho=min_{a>=0,b>=0}(F-Qa)^T C_rho^-1(F-Qa)` using analytic two-variable active-set NNLS in whitened coordinates. The SciPy NNLS solution independently matches on randomized nontrivial two-component systems with rho=0,0.45,1. Cholesky-PSD checks and positive stationary populations executed. A total of **54,720** profile grid scores were evaluated across 16 apertures × 2 covariance assumptions × (342+1368) source options; results of best fits are recorded for each source and model class (64 rows). This is a descriptive grid search; no distribution of the χ² values under nuisance selection, no global p-value, and no cosmological inference. The grids deliberately match the previously archived scope, instead of the abandoned wider numerical exploration.

## Physically informative discriminant and negative findings

HH 211 aperture 7, 6 HD detected lines all with positive printed errors, modeled from source-authentic HD equations:

| Profile | Independent 6% rho=0 | Fully common 6% rho=1 |
|---|---:|---:|
| single-temperature (best across two original-source rate variants) | 28.7931250 | 32.7576560 |
| two-temperature isobaric (best across variants) | 0.44990423 | 0.55554966 |
| two-temperature standard rates only | 0.55270866 | 0.73519895 |

The global two-T alternate-source sensitivity row selects exact T_warm=600 K, T_hot=2000 K, at log10[(p/k_B)/(K cm^-3)]=**10, the upper grid boundary**. The standard-source optimum is instead interior at log10(p/k_B)=9.6666667 and (600 K, 3000 K). The standard-source result is nearly equivalent at the conditional GLS level. A pressure profile across all 19 grid points is recorded in `HH211_ap7_pressure_profile.csv`; at the high-pressure edge the alternate-source fit keeps improving, so **the finite-grid upper boundary is active**; the boundary optimum is not a resolved pressure measurement, cannot imply observed high-density gas, and cannot be interpreted as a posterior fit. Likewise nonnegative two-component models possess more effective fit flexibility than single T: raw χ² comparisons are *not* a detection significance without selection/complexity treatment.

There is no observed inverted/masing HD line demonstrated here; the parental low-J inversion is conditional theoretical population. There is no self-consistent trapping or dust extinction in these comparisons. HD R(6) can blend H2O and R(7) CO2 in the real instrument, which can bias the printed flux. No inference of absolute [D/H], deuterium depletion, or Galactic evolution is justified by these provisional scores.

## Blind referee within current model context

- **Major:** Original cross-line JWST covariance absent. Failure kind `input_missing`; prevents authentic observational joint likelihood, Bayes factor, significance claim. Smallest correction: obtain extracted spectra, fit Jacobian/normal matrix, calibration covariance and original flux tables; compute full likelihood with data-source certainty.
- **Major:** Paper-final Appendix F raw bytes not acquired here. Transcription is from arXiv v1 rendered tables, **not a publisher-final byte-authentic source**; require exact agreement test with Zenodo Francis Appendix D–G PDF.
- **Major:** Ignored upper limits and printed 0.00-error lines in Gaussian scoring. Explicit exclusion is safer than fake errors but prevents complete sample inference; eventual likelihood needs 3σ censored terms and proper error budget.
- **Major:** Source-only HD fit omits H2 emission, fitted OPR, extinction and chemistry; cannot reproduce full Neufeld isobaric joint H2–HD posterior.
- **Major:** Grid-wide minima, especially at pressure boundary, are not confidence intervals and cannot be compared between rho scenarios as likelihood-ratio significance.
- **Scientific distinction:** Sung inter-parameter lab covariance is physically distinct from JWST cross-line flux covariance and CDMS v2 full parameter covariance. The different claims cannot be jointly promoted by algebraic substitution.
- **Source integrity:** 4 original Neufeld bytes preserved and SHA-locked; alternate rates used as *sensitivity only*, no owner-source switch.
- **Verification:** Self-check and independent SciPy *algorithmic oracle* obtained; `R6/C9` genuine distinct-author independent review **NOT_RUN**; native subagent tool not exposed. One self-adversarial pass only, no review recursion.

## Admission boundary

`CLAIM=EXPLORATORY_NONAUTHORITATIVE_PHYSICAL_SHAPE_DATA` under original HD model, not independent empirical result; `JOINT_LIKELIHOOD=NOT_RECONSTRUCTED`; `SUNG_FULL_COVARIANCE=SOURCE_ACQUISITION_PENDING`; `ORIGINAL_35HZ=FAIL7/8`; `GITHUB_CI=FAIL_VERIFY_REPO_QUICK` at parent (not fixed); `CANONICAL_DAG=28/88`, `REC_PHYSICAL_DAG=0/313`, `R_C_SCOPED=18/20` unchanged. `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_OWNER_SOURCE_SWITCH=true`, `NO_35HZ_RELAXATION=true`, `AUTO_NEXT_NODE=false`. No new canonical or physical DAG node can be admitted from these source-conditional data.

## Direct cross-check against pre-existing same-unit Library science bundle

The current calculation was carried out with a separately written conditional-GLS implementation, and **then matched back** to the earlier immutable Library FULL ZIP `REC_JWST_FLUX_COV_SOURCE_DIAGNOSTIC_20261031_FULL.zip` (SHA-256 `56e54a8ce165560b3be3ad52bbb6b98b6d0c9534059c3802faa9d9f791d34079`). Both models use the same original Neufeld15 rate files and solver implementation; this is an algorithmic cross-check, **not independent authorship**. On the aligned originally scoped grids, observed entries agree **364/364**, the **10,944** one-T source-scores have max absolute χ² discrepancy **2.877698079828406×10^-13**, and the **43,776** two-T source-scores have max discrepancy **6.629363724641735×10^-12** (record `outputs/existing_archive_numeric_comparison.json`; predeclared numerical cross-check threshold `1×10^-6`). The earlier independently archived pipeline also passed **24/24** normal and **24/24** Python `-O` tests during this resumption. Both prior and current source bundles are preserved without mutation. An abandoned pilot extended the two-T pressure upper boundary to log10(p/kB)=11.5, giving different conditional minima; that exploratory range is **not** promoted, published as a scientific result, or mixed with the original-scope comparison.
