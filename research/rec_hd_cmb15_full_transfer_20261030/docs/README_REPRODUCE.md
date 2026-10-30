# REC-HD 15-level CMB and line-transfer scientific reproducibility

Extract archive into an isolated directory; do not write into parent/owner worktree. Source original .dat/.fits bytes are frozen and checked at every computational entrypoint.

```bash
PYTHONPATH=src python src/hd_line_transfer.py --root .
PYTHONPATH=src python src/independent_dense_validator.py --root .
PYTHONPATH=src python src/inversion_window.py --root .
PYTHONPATH=src python src/inversion_phase_diagram.py --root .
PYTHONPATH=src python src/inversion_mechanism.py --root .
python src/render_science_plots.py --root .
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

Source identity: `source/zenodo_v2/hd_lamda*.dat`, `hd_population_grids*.fits` have their exact SHA256 in `evidence/FULLLINE_SCIENCE_SUMMARY.json`. Model input T and H2 density source units are K and cm^-3; HD column is cm^-2, output intensities are W m^-2 sr^-1. The observational posterior CSV.gz is not an input. Do not interpret numbers as observed telescope line fluxes or saturated maser predictions.
