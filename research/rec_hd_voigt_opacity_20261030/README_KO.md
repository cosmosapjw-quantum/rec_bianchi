# REC HD laboratory line data → conditional 296 K Voigt spectral opacity atlas

Source: Sung et al. JQSRT 295, 108412, Table 4; input inherited without changing bytes from PR164 immutable SOURCE ZIP. Initial natural-abundance-weighted HITRAN line strength semantics retained; reference column is NOT independently measured HD column. Uses observed line parameters, *not* reprocessed actual experimental spectra. Voigt is an approximation distinct from experimental Rautian.

Run: `python -m unittest discover -s tests -v`, `python -O -m unittest discover -s tests -v`, `python src/voigt_opacity.py`, `python src/figures.py`.

Outputs: `evidence/SPECTRAL_CASES_36.csv`, `evidence/VOIGT_PROFILE_ATLAS_7236.csv`, `evidence/RESULTS.json`, 3 figures. Check `THEORY_KO.md`, `CODING_KO.md`, `REPORT_KO.md`, `SOURCE_IDENTITY.json`, `DAG_EVIDENCE_DELTA.json` for claims, SI conventions and gates.

Canonical DAG 28/88, REC Physical DAG 0/313 (+0). Original 35Hz FAIL7/8, source fit covariance unavailable; original parent data and other-owner main retained, no merge or auto-next.
