# REC-HD-RECOIL-ONLY-BOUND01 | C1–C10 코딩 연구

**Owner** REC; base PR157 immutable `e209cd0180c8bf199fc476c37e3cbf8d50394b6c`, research-only add-only branch. No original raw molecule, source, PR156/157 code or production mutation.

**C1–C4.** Objective: falsifiable bounded recoil-only explanation of 8 original *public selected source* frequency pairs. Source input is `data/PR156_SELECTED_FREQUENCIES.json` with selected-field transcript only; stored upstream Git blob `5a99c9e31604347cf756abb4ab3ea1a134238e0d`. `M_min=2u`, reference `3u`; exact fraction 35Hz gate. Units SI. No CMB IVP, stationary solve, production release or native physics backend.

**C5.** `src/recoil.py`: exact `Fraction` mass shell, reciprocal mass bound, source transcript strict comparison, CLI JSON result. `src/recoil_crosscheck.cpp`: standalone C++20 independent numerical algorithm; `src/plot_results.py`: source-only two-panel visual test. Fail-closed source metadata and eight pinned triples prevent arbitrary synthetic values from being called frozen source.

**C6.** Executed `python -m unittest discover -s tests -v` 21 PASS, exit0, `python -O -m unittest discover -s tests -v` 21 PASS, exit0; `python -m compileall -q src tests` exit0. Tests include invalid mass, source tampering, exact emission/absorption rest-energy shell and sign, 35Hz frozen gate, threshold and three-sector energy closure.

**C7.** Wolfram mass-shell symbolic exact identity, Python Fraction input comparison, C++ emission/recoil and source difference from public transcript. **Actual physical molecular events, CDMS source choice and independent experimental ground truth NOT_VALIDATED.** This is kinematic model-check on previously frozen selected-field frequencies, not recovered source.

**C8.** g++ (`-std=c++20 -O2 -Wall -Wextra -pedantic`) compile and executable exit0. For 8 rows × 3 variables, C++ 19-decimal output vs 45-digit Python Fraction→Decimal matched with max relative discrepancy below `3.3e-19` for the printed values. Computational complexity O(n), no claimed production runtime speedup. Plot generated and visually inspected. No meaningful ODE stiffness/solver benchmark.

**C9.** Fresh independent author/tool delegation NOT_RUN (native agent missing), same-context reviewer checked sign, units and source distinction; code remains `PARTIAL_NONAUTHOR_NOT_RUN`.

**C10.** Source-only artifact and reproducible commands. All source and result files include exact identity. The planned stage checkpoints are file+hash records. Per-stage uploads/commits have their own receipts and cannot be inferred from the creation of one final archive.

## Commands

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
g++ -std=c++20 -O2 -Wall -Wextra -pedantic src/recoil_crosscheck.cpp -o evidence/recoil_crosscheck
./evidence/recoil_crosscheck > evidence/CPP_RESULTS.txt 2> evidence/CPP_STDERR.log
python src/recoil.py --transcript data/PR156_SELECTED_FREQUENCIES.json --output /tmp/rec_hd_recoil_RESULT_new.json
python src/plot_results.py
```

## Classified unsolved

(1) `input_missing`: CDMS v2 original raw .cat/.egy/.par/.fit/.lin + 2019 and 2011 .cat ambiguity. (2) `scientific`: rest-frame recoil alone insufficient for J2..J8 but medium/fit/source choices open. (3) `implementation`: source-bytes and native/generated runtime callsite completeness open. (4) `verification`: distinct-author R6/C9 not run. (5) `production`: HOLD.
