# Reproducing the bounded Neufeld-2026 MIRI MRS six-line atlas

This source-inclusive capsule has four exact Neufeld (2026) Zenodo v2 files. The original binary FITS are retained untouched. The new code uses the original two collision `.dat` records and original source-based 15-level stationary solver without interpolating collision-rate temperatures or replacing the CDMS2011 owner.

```
cd <extracted-capsule-root>
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python src/miri_sixline_profile.py --root .
PYTHONPATH=src python src/plot_miri_profile.py --root .
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

Two original documents required for instrument/physics justification:

- Neufeld 2026 original source: https://zenodo.org/records/21165907
- STScI MIRI MRS: https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-medium-resolution-spectroscopy

The scores describe a normalized model *shape* difference, not sky flux likelihood or 2011 CDMS source-family equivalence.
