# Reproducing the source-bound HD non-LTE benchmark

The exact original raw files are in the GitHub child research branch under:
`research/rec_hd_neufeld2026_v2_source_benchmark_20261030/source_originals/`.

The 2026 full FITS is NOT in the local package; it was acquired and SHA/MD5 verified in the remote Wolfram session. The source-ref Git blobs for 2011 CDMS and the exact 2026 `.dat` are preserved in GitHub, not replaced by the 2019 or 2026 CDMS v3 catalogue.

From a checkout of the child research branch:

```bash
python src/neufeld15.py --source source_originals/neufeld2026_v2/hd_lamda.dat --output evidence/recomputed
python src/j1_rate_comparison.py
python src/cdms_2011_fit_covariance.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

Run commands from within the research-unit folder, or use explicit paths with the correct working directory. `neufeld15.py` SHA-256 checks the original source. It emits 45 source-convention and 45 SI-exact model cases, each with 15 populations and 14 emitted photon-power values. No CMB field, non-LTE shock chemistry, telescope fluxes or cosmological IVP is included. The source includes high-J collision-rate extrapolations.

To download from official servers on a network-enabled machine, use the optional `src/fetch_verified_sources.py --out source_originals_downloaded`; it checks exact SHA-256/MD5/size and refuses any substitution. The FITS source is 
`https://zenodo.org/api/records/21165907/files/hd_population_grids.fits/content`.

Difference of printed 2011 SPFIT parameter covariance from full precision, and original 35 Hz gate FAIL7/8, remain separate from this benchmark. Original archive contains all local code and selected evidence; raw binary FITS is not silently represented as included.
