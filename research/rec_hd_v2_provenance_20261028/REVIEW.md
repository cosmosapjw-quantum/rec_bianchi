# Finite PHYS-MATH / PHYS-MATH-CODE / plot audit

Review origin: parent same-context and independent numerical method. **No separate native nonauthor reviewer**. Fresh R6/C9 full scientific acceptance NOT_RUN.

1. Sign/dimensions: delta_nu = c100(upper-lower cm^-1) - 1e9 nu_GHz, Hz. The dimensionless LTE Kirchhoff factor is (exp(hnu/kT)-1)/(exp(DeltaE/kT)-1); positive delta_nu gives a negative factor minus one. PASS on all 24 computed cases and toy DeltaE=hnu limit.
2. Source identity: restored original source file has exact 2289 bytes and SHA256. One-based J state/level identity and all original 7 failing line IDs are preserved. PASS.
3. Precision: original mpmath oracle first reused 80-digit exponential inputs; replaced in one bounded targeted repair by **independent raw numeric literal reconstruction** in 120-digit mpmath. Original code snapshot is stored in code/hd_source_thermal_INITIAL.py, final 80/120 maximum residual 3.106928524226738e-79, required <1e-65. The previous diagnostic RESULT was overwritten only by the diagnosed precision path, and its original invocation stdout/receipts survive. No source data/gate changed. PASS_SCOPED.
4. Adversarial: corrupt source byte, check wrong sign, toy equal-energy case, and source-version documentary absence. Tests 7/7 PASS. No inference of lab error or exact catalog row identity.
5. Figure: initially generated footnote overlaps xlabel. First PNG/PDF preserved; saved-data-only repair removes footnote, final PNG opened and inspected. Upper points signed defects and lower points at 3 printed temperatures, no inter-point curves. PASS presentation.
6. Original 35 Hz criterion not physical error: no relaxation and no correction; result stays 1/8 PASS, 7/8 FAIL. FULL HD source acceptance HOLD.
7. R6/C9 externally different reviewer not available. Independent mpmath is numerical-method diversity, not a new independent scientific reviewer. Separate CDMS v2 raw bytes/fit provenance and source choices are missing. NO_FINAL_PHYSICAL_PROMOTION.
