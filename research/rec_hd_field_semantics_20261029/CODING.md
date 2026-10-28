# REC-HD-FIELD-SEMANTICS01 coding loop C1–C10

Owner `rec_bianchi`, parent PR154 `2b86465fe641977aa8a584ed4fb66888fd300929`. Executed in current host Python 3.13.5 (PYTHON_PASS), g++ 14.2.0 (CPP_PASS capability probe, no C++ scientific code built). No native subagent delegation tool was exposed (`native_subagent=NOT_RUN`). The complete science path uses Python standard library; independent mpmath checks are tests only and matplotlib is figure-only.

**C1 baseline:** frozen source 2289 bytes SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`. Frozen 35 Hz 7/8 FAIL and PR154 exact joint interval scale are inherited, not retested or altered. Target new field-projection and local line-centre kernel only.

**C2 source-to-code:** `parse_lamda_hd` maps source level energies/weights, radiative A and p/o H2 rates to `core`; the optional `FREQ(GHz)` and `E_u/k(K)` columns go only to `optional_line_metadata`. Source strict BYTE_IDENTITY is separate from `core_sha256`, which is selected-literal CONTENT_IDENTITY; numerical equivalence requires a separate comparison. Original private raw HD file remains excluded from public Git.

**C3 algorithm:** exact Decimal token parser rejects NaN/Inf; source field parsing validates nine levels, eight radiative edges, both nine-row collision partner blocks and three temperature nodes. All ratios are exact `Fraction` from printed decimal literals. `nu_E=100c(w_u-w_l)`, `nu_P=1e9 FREQ`, `r=nu_P/nu_E`, `alpha_ratio=r^-3`, `S_ratio=r^3`, `j_peak_ratio=1`, `integrated_j_ratio=r`. No floating tolerance enters acceptance.

**C4 execution:** bounded single-process source parse and 8-row exact ratios. Python unittest with mutation controls and independent mpmath direct emissivity/opacity formulas; Wolfram rational source-literal crosscheck. No old 9x9 stationary solve, native/IVP, HPC, production mutation, or source replacement.

**C5 implementation:** `field_semantics.py` CLI `--source private_inputs/hd.dat --output results/FIELD_SEMANTICS.json`, `tests/test_field_semantics.py`, `plot_field_semantics.py`. Strict mode rejects nonmatching original source. Metamorphic mode is explicitly `require_original=False` and cannot claim original source lock. Output directory created safely.

**C6 software verification:** 16/16 unit and negative tests PASS in current Python runtime. Tests include SHA failure, metadata-only mutation, core-field mutations, absent optional frequency, NaN/Infinity, invalid A, collision partner ID and exact algebraic ratios.

**C7 scientific validation:** independent high-precision mpmath evaluation of direct Einstein A/B plus Gaussian phi at T=100 K, sigma_v=1200 m/s, lines J=1,2,6,8. Direct peak emissivity ratio equals 1 to <1e-80 and direct opacity ratio agrees with exact Fraction to <1e-78. Wolfram exact-rational extremum identifies J2 and maximum 5.332463622370740788...e-7. This does not validate Bianchi transport or a physical source-choice.

**C8 numerical/figure validation:** all eight exact rational ratios saved. Plot displays eight separate source rows without continuous interpolation. Initial plot printed the tiny J1 value as `-0.0000 ppm`; revised scientific notation `-9.24e-6 ppm` and reopened PNG. No performance claim or full error budget is made.

**C9 adversarial review:** same-context code inspection and independent computational methods (Fraction, mpmath, Wolfram). Tests explicitly falsify universal metadata-invariance for printed-frequency consumers and fixed-frequency-width emissivity invariance. No distinct-author native reviewer: `PARTIAL_NONAUTHOR_NOT_RUN`. No model-family independent review claimed.

**C10 delivery:** source code, tests, exact result, figure, THEORY, REPORT, DAG_DELTA and handoff packaged with local hashes/CRC. Each selected stage has a remote Git checkpoint. Provider backup status must be recorded from actual Drive/Dropbox ACK and metadata, not inferred. Canonical DAG 28/88(+0), REC physical 0/313(+0), H5 epsilon=null, H6/H7 OPEN, L4=false, REI activation false, production HOLD.
