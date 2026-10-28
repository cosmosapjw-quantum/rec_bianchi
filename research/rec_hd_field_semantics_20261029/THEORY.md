# REC-HD-FIELD-SEMANTICS01: LAMDA optional-frequency semantics and conditional radiative kernels

Date: 2026-10-29 KST. Owner: `cosmosapjw-quantum/rec_bianchi`. Immutable parent: PR #154, commit `2b86465fe641977aa8a584ed4fb66888fd300929`. Research scope is **source-format semantics and a local conditional radiative-transfer kernel**, not spectroscopic source selection, recombination, HD chemistry, or production Einstein–Boltzmann integration.

## R1. Scientific question and acceptance

Does the mismatch between the nine printed HD level energies and eight printed photon frequencies necessarily affect every LAMDA-consuming solver? If a consumer explicitly uses either energy-derived or printed frequency, what is the exact local line-centre emissivity/absorption response at fixed Einstein A, populations, and Gaussian Doppler velocity width? Acceptance: verify the original LAMDA source identity; prove a conditional source-field projection invariant; derive exact ratios with units/signs; test all eight transitions and adversarial mutations; **do not** change original source, 35 Hz gate, H5 epsilon, H6/H7, L4, REI or canonical DAG.

## R2. Source literature and owner evidence

- The [official LAMDA format](https://home.strw.leidenuniv.nl/~moldata/molformat.html) specifies level energies in cm^-1, statistical weights and Einstein A as core fields. It describes printed transition frequencies as optional information *not used by the program described there*. The E_u/k and quantum-number display fields are likewise not required to calculate the core. This statement is about the documented format/consumer, **not** a universal rule for all codes.
- [myRadex](https://github.com/fjdu/myRadex) explicitly reports that since 2021-11-25 it uses the input-file frequency by default, with `recalculateFreqWithEupElow` available as an alternative. [pythonradex example](https://pythonradex.readthedocs.io/en/latest/notebooks/reading_LAMDA_files.html) explicitly sets `read_frequencies=True`. These demonstrate that consumer policy is implementation-specific.
- [LAMDA HD](https://home.strw.leidenuniv.nl/~moldata/HD.html) attributes its spectroscopy to CDMS Dec-2011 v2 and collisions to Flower (1999); its HD file was introduced on 2021-06-07 per [database history](https://home.strw.leidenuniv.nl/~moldata/database.history). The original 2289-byte file has SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`, verified from PR154's immutable private SOURCE ZIP in this execution. All nine level, eight photon and two nine-row collision-partner records were parsed.
- PR #150 already computed a source-conditional LTE Kirchhoff mismatch; #151 performed 26-channel stationary diagnostics; #152 proved rank 8/18/8/10; #153 established print-only seven failures; #154 proved exact joint enclosure infeasibility with scale `9137862803786/174896229`. Reuse all without repeating prior stationary/native/IVP work. The original 35 Hz gate is FAIL7/8.
- CDMS v2 original `.cat/.egy/.par/.fit/.lin` and field-level LAMDA conversion remain **NOT_ACQUIRED**. The official archived directory HTML is not a byte-locked original; `c003501.cat` has a later 2019 timestamp. The current container network has DNS failure and Exa/official file retrieval still lacks raw bytes. This is an input/service blocker, not a physical theorem.

## R3. Conventions and definitions

Ordinary frequency ν in Hz (not angular ω), c=299792458 m s^-1, h=6.62607015e-34 J s, k_B=1.380649e-23 J K^-1. For transition u>l, E_j=h c (100 w_j) with w_j in cm^-1; ν_E=(E_u-E_l)/h=100 c(w_u-w_l); ν_P=10^9 ν_print(GHz). Define δν=ν_E-ν_P. The original source has 9 rotational labels J=0..8, 8 radiative edges, 9 para-H2 and 9 ortho-H2 collisional edges. No vibrational quantum number is independently authenticated by the source. T>0 where LTE is invoked. Metric signature (-,+,+,+) has no role in the local rest-frame algebra.

Define `P_core(file)` as the ordered tuple of molecule label/mass, level identities/energies/statistical weights, radiative upper/lower indices and A, collision partner identities/temperature nodes/transition indices/rates. Define `P_meta(file)` as printed ν and E_u/k display columns. A consumer is **core-only** only when its actual code depends on `P_core` and not on `P_meta`; other consumers may use either or both. The source file hash and the selected-field canonical **content** hash are separate typed identities; `core_sha256` does not prove numerical/semantic equivalence under alternate decimal formatting.

For the line-centre diagnostic fix A_ul>0, n_l>0, n_u>=0, g_l,g_u>0, and a Gaussian Doppler velocity dispersion σ_v>0 in the local emitter frame. Let σ_ν=ν σ_v/c and φ_ν(ν)=1/(sqrt(2π)σ_ν) at its own centre. The comparison holds the same A, populations and σ_v across both frequency conventions. For absorption positivity in the LTE illustration, n_u/n_l=(g_u/g_l) exp[-(E_u-E_l)/(k_B T)].

## R4. Candidate representations

(A) A universal `ν=ν_E` rule for all consumers is **rejected** by actual myRadex policy. (B) A universal `ν=ν_P` rule is **rejected** by the official LAMDA format's documented core semantics. (C) Use an explicit typed source-policy bifurcation, with a core projection and a separately selected frequency convention; derive effects but do not silently choose a production branch. (C) is adopted. Frequency metadata can change without changing the core; A/energy/collision changes cannot.

## R5. Constructive derivation

**Projection lemma (conditional).** For any two syntactically valid HD LAMDA inputs X,Y with `P_core(X)=P_core(Y)` and any consumer F=f∘P_core, F(X)=F(Y). This is immediate by function composition, and it says nothing about consumers that read ν or E_u/k. In particular a change in printed FREQ cannot be interpreted as a physical source correction, nor can it alter a proven core-only computation. The core projection's SHA256 is a canonical **CONTENT_IDENTITY** of selected literal fields, not the original file's byte identity or a general numerical/semantic equivalence certificate.

**Einstein line-centre kernel.** For an explicitly selected ν>0, Einstein B_ul=A_ul c²/(2hν³), B_lu=(g_u/g_l)B_ul. At each convention's own centre, with φ_0=c/(sqrt(2π)νσ_v),

    j_0(ν) = (hν/4π) n_u A_ul φ_0
           = h c n_u A_ul/(4π sqrt(2π) σ_v),

    α_0(ν) = (hν/4π)(n_l B_lu-n_u B_ul) φ_0
           = [A_ul c³/(8π sqrt(2π) σ_v ν³)] [n_l g_u/g_l-n_u].

Hence for **fixed A, populations, velocity width**,

    j_0(ν_P)/j_0(ν_E) = 1,
    α_0(ν_P)/α_0(ν_E) = (ν_E/ν_P)^3,
    S_0(ν_P)/S_0(ν_E) = (ν_P/ν_E)^3,
    (∫j_ν dν)_P/(∫j_ν dν)_E = ν_P/ν_E.

The last ratio explicitly prevents confusing peak and integrated emissivity. If the *frequency* dispersion σ_ν rather than velocity dispersion σ_v is fixed, the peak emissivity ratio is instead ν_P/ν_E; this is a negative control. If comparing intensity at a common observing frequency instead of each moving line centre, the profile shifts and these centre ratios do not apply.

Under level-LTE populations, `S_0(ν)=2hν³/c²/[exp(ΔE/k_B T)-1]`, so

    S_0(ν)/B_ν(T) = [exp(hν/k_B T)-1]/[exp(ΔE/k_B T)-1].

At ν_E this equals 1. At ν_P this recovers PR150's *conditional* Kirchhoff mismatch. This is not new entropy production or a new astrophysical rate. A Bianchi tetrad/redshift, velocity gradient, line-overlap or full frequency redistribution would require additional transport derivation and is outside this local scope.

## R6. Review and falsification targets

Check Einstein B dimensions (J m^-2 sr^-1 convention of mean intensity), ν power, line-profile normalization, sign of δν, population positivity, fixed-width meaning, optional metadata invariance, and source byte lock. In particular the false claim `j_peak invariant at fixed σ_ν` must fail, as must any claim of invariance for consumers that read printed ν. Wolfram exact rational arithmetic and an independent mpmath direct-kernel evaluator check these algebraic results, but no genuine native nonauthor subagent is exposed this turn: **R6 PARTIAL_NONAUTHOR_NOT_RUN**. The formal proof above remains derived; no novelty-level strong no-go is asserted.

## R7. Source-conditioned numerical check

Exact Fraction arithmetic on all eight byte-verified HD transitions gives maximum absolute relative peak-opacity response

    max_J |α_P/α_E - 1| = 5.332463622370740788... × 10^-7, attained at J=2→1,

with sign negative there because ν_P>ν_E. The largest absolute relative frequency difference is 1.777488506016470869...×10^-7, also J=2→1. Wolfram exact rational ratios independently agree with the extrema; source-locked Python test and direct mpmath kernels agree to the specified high precision. These numbers are conditional source-policy differences, not physical error bars.

## R8. Scientific admission

Admit the **format-level policy distinction** as literature-supported and the projection lemma / conditional Gaussian line-centre ratios as derived and numerically checked. This establishes a concrete reason to audit consumer call sites before treating the 35 Hz source mismatch as a universal physics failure. It does not establish that any REC/BASS production call site is core-only, nor that CDMS v2 source values are authenticated. No physical H5/H6/H7 or canonical DAG completion is promoted.

## R9. Computational interface

The standalone `field_semantics.py` reads the exact private source in strict SHA/byte mode, emits a canonical `core_sha256`, keeps `P_meta` separate, and produces exact Fraction ratios for ν_E, ν_P, α_peak, S_peak and integrated emissivity. Loose mode exists solely for metamorphic tests and always sets `raw_verified_this_execution=false`. The core excludes optional ν and E_u/k but retains every p/o collision rate. An absent optional ν remains valid for core-only use but cannot produce printed-policy ratios. Output-only plotting is discrete and source-conditioned.

## R10. Stop condition and handoff

This unit ends at a finite source-format/line-kernel result and implementation test. Next admissible independent work is `REC_HD_CONSUMER_CALLSITE_AUDIT`: trace exact code paths in REC/BASS/REI that consume ν or compute it from ΔE, including frame and line-profile conventions, before considering any physics gate. Separately `CDMS_V2_SOURCE_RECOVERY` remains the predecessor to physical source-choice and requires original bytes/version/QNs/TAG/uncertainties/conversion recipe. The two branches may progress independently; neither changes canonical 28/88, REC physical 0/313, H5 epsilon=null, H6/H7 OPEN, L4=false, REI_activation=false, production HOLD.
