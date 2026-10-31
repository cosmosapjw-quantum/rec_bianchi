# Reproducible self-contained supplementary HD censored atlas

Python 3 with `numpy`, `scipy`, and `matplotlib` (only for plot); no independent runtime download required. Original Neufeld v2 HD source bytes and frozen inherited parent solver are in this ZIP. The Francis final normalized printed-cell table is in `inputs/` and has been cross-checked against Zenodo Appendix F (source PDF not duplicated).

From this extraction root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -O -m unittest discover -s tests -v
PYTHONPATH=src python src/censored_atlas.py --root .
PYTHONPATH=src python verification/independent_checks.py
```

The science command regenerates `outputs/HD_CENSORED_29640_PROFILES.csv` (29,640 grid deviance rows), `HD_CENSORED_104_BEST.csv`, `HD_APERTURE_52_MODEL_CONTRASTS.csv`, `HD_NO_DETECTION_EXACT_FLUX_ENVELOPES.csv` and `figures/HD_26_APERTURE_CONDITIONAL_CONTRAST.png`. `verification/INDEPENDENT_NUMERIC_CHECKS.json` is the numerical cross-check; `MANIFEST_SHA256.json` authenticates every other payload file. Both normal and Python -O tests must PASS. No 313 physical DAG node admitted.

Original Francis source reference: https://zenodo.org/records/14592550, PDF MD5 `652ec146b75c860c20628e5bd906d8ad`; Neufeld v2 source: https://zenodo.org/records/21165907; immutable Git predecessor: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/175 (`dbe708e6c6bc9d52625321678809d7d816ecf029`).
