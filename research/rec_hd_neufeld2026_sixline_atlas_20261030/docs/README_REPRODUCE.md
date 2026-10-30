# REC HD Neufeld2026 six-line extrapolation sensitivity atlas (2026-10-30)

Source: David A. Neufeld, *ApJ* 1007, 16 (2026), DOI 10.3847/1538-4357/ae851a; original Zenodo v2 21165907 (standard/alternate .dat and .fits). Parent `rec_bianchi` PR171 head `8e1f51397cc3019642668daf4b2f2c39ff5126d5`, full archived raw source source inclusive. This project is independent and no parent/main/owner mutation.

Read `docs/THEORY_KO.md` and `docs/REPORT_KO.md` before using any empirical result. Two `.dat` files, two `.fits` files, and two 270/3780 source-model tables have mandatory SHA256 pins in `src/sixline_atlas.py` and `checkpoint/INHERITED_SOURCE_LOCK.json`.

```bash
python src/sixline_atlas.py --root .
python src/density_degeneracy.py --root .
python src/independent_scipy.py
python src/render_figures.py --root .
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

This calculation is not optical-depth transfer or measured JWST spectra. No 35Hz relaxation, no canonical/physical DAG promotion, no merge, no production. R6/C9 distinct-author NOT_RUN. Source output can be compared to PR171 archived source model grid and will fail on source byte tampering.
