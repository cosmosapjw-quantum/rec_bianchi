# JWST line-flux conditional-covariance source bundle

Execute using the source-inclusive ZIP (do **not** move into a production worktree):

```bash
unzip -q REC_HD_JWST_LINE_FLUX_COVARIANCE_20261031_INDEPENDENT_REPLAY_SOURCE.zip -d rec_jwst
cd rec_jwst
PYTHONPATH=src python src/jwst_conditional_fit.py --root .
PYTHONPATH=src python src/pressure_profile.py .
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

Required: Python 3.11+, numpy, scipy, matplotlib. No network or proprietary library needed at replay. Source original HD files are SHA-locked in `hd_line_transfer.py`. 26-aperture Francis et al. arXiv v1 Tables E.1/E.2 observations are a **provenance-labeled, human-transcribed** dataset. Only upper limits and 0.00 printed-error values are omitted from the conditional GLS profile, never silently assigned an error. `src/hd_cmb15.py`, `hd_line_transfer.py`, `pr169_neufeld15_reference.py` are untouched original parent source code. 

Expected: 364 line-flux records, 342 single-T and 1368 two-T source models, 54,720 evaluated conditional score rows, 16 fit-eligible apertures, 10 excluded, two figures; 12 new tests and original parent 18 tests (the parent 18 tests remain in the parent ZIP, not copied to this child tests directory). Do not run a full χ² test of the observational system on these inputs. `MANIFEST_SHA256.json` is a transport/internal-entry digest, not verification of arXiv PDF original bytes.

Source paper: Francis et al. A&A 694 A174 (2025), DOI 10.1051/0004-6361/202451629, final Appendix D–G Zenodo 14592550. Neufeld ApJ1007:16 (2026), DOI 10.3847/1538-4357/ae851a, original HD input Zenodo 21165907 v2.
