# REC-HD J1 CMB actual-source-conditioned transfer atlas

Independent add-only research continuation of frozen PR167, no source-owner or production modifications.

- Source LAMDA data: byte-pinned 2021 visible text transcription, not original raw download; J1 original 35Hz PASS only, other seven FAIL.
- Source Sung data: byte-pinned parent archive, not used as substitute for J1 source frequency or Einstein A.
- Derived actual scientific numeric records: 432 conditional J1 one-pass radiative transfer cases and 138,672 sampled spectra with real source A/q and explicit gas/CMB parameters; they are predictions, not measured sky.
- Theory and validation: `THEORY_KO.md`, `tests`, `results/RESULTS.json`, `results/INDEPENDENT_QUAD_12.json`.

Reproduce in an isolated Python environment with numpy/scipy/mpmath/matplotlib:

```bash
python src/j1_cmb_rt.py --input input --out results
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python tests/independent_quad.py
python src/render_science.py
python -m compileall -q src tests
```

No FITS or v2 raw authenticity claims. Full 9-level and production remain HOLD. See `HANDOFF_NEXT_THREAD_KO.md`.
