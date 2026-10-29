# REC HD 2021 9-level source-transcribed physical-model code (C1–C10)

C1–C2: use `data/LAMDA_HD_SOURCE_TRANSCRIPTION.json` with 9 levels, 8 radiative lines, 9 collision channels × two H₂ spin partners × 50/100/200 K. Original official 2289-byte data is NOT reconstructed from flattened extraction, and no raw byte SHA is asserted. Parent source PR160 immutable. Three separate science objects: source field transcription, J1 gate-qualified two-level, source-unqualified full-nine diagnostic. Full source gate remains FAIL7/8.

C3–C4: elementary two-state exact stationary probability and positive q10/q01; finite 9×9 Markov generator and stationary linear solve; no IVP, numerical speed benchmark or cosmological source term. SI h,c,kB, with collider density cm^-3 and collision coefficients cm³/s. Graph includes special collision 2→0. nH₂ grid [0,1,100,1e4,1e6,1e8,1e10] cm^-3; f_ortho=[0,0.5,1]; T=[50,100,200] K only.

C5: `src/hd_nlte.py` and source `data/...json` generate raw computational JSON `evidence/NONLTE_GRID.json` 63 two-level and 63 full-nine rows. `src/export_tables.py` creates CSV of 54 source collisions, 63 J1 cooling rows, 63 full9 model rows and 504 line powers. `src/render_figures.py` generates 3 scientific plots.

C6: `python -m unittest discover -s tests -v`, `python -O -m unittest ...` 22/22 each PASS; compileall PASS. Source tamper cases fail with ValueError even under -O. First actual test failure at nH₂=1e10 for high-density balance due to subtracting nearly equal large collision fluxes and demanding fractional tolerance relative only to tiny radiative term. After observed cancellation, test uses a floating error bound relative to the largest terms of the actual subtraction; **no physical acceptance or source gate was widened**. See evidence/PYTHON_TESTS.log and evidence/PYTHON_O_TESTS.log, initial log preserved as `evidence/FIRST_FAILED_TEST_RECORDED.json`.

C7: Wolfram exact T=50/100/200K two-level n_half, P∞ and ortho independence; source J1 gap -8.2410162 Hz. Full 9-level power is not source-confirmed because seven lines fail 35 Hz. All unobserved physical source/transport/history claims HOLD.

C8: separate mpmath 80-digit solver *not importing production solver* for all 63 full-nine cases; max relative total source-formula power error 2.1014e-11 and max absolute population error 1.241e-15. This checks numerics on a prescribed steady model, **not** native C++/Rust/GPU or actual cosmological experiment. 3 figures directly read. No solver performance speedup claim.

C9: native independent different-author code audit NOT_RUN. Same-context one-pass source shape, physics, units and source-consistency audit performed; no fabricated subagent dispatch.

C10: reports, CSV, JSON, tests, exact input source and immutable predecessor archive are checkpointed. Original J1 two-level science can be reused scoped; larger production and 2011 CDMS v2 raw remain HOLD. New research auxiliary 1/2, canonical 28/88, REC physical 0/313. Production default unchanged; no merge/force push.

## Reproduce

```bash
cd REC_HD_NONLTE_PHYSICS_20261030
python src/hd_nlte.py --source data/LAMDA_HD_SOURCE_TRANSCRIPTION.json --output evidence/NONLTE_GRID.json
python src/export_tables.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
python tests/independent_mpmath.py
python src/render_figures.py
```