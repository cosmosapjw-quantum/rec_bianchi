# REC HD | 2011 CDMS v2 printed-energy crosswalk, coding (2026-10-30)

**Source-locked inputs:** `source/CDMS2011_V2_EGY_V0_TRANSCRIPTION.json` (2011 official text transcription, not original bytes); `reference/pr161/data/LAMDA_HD_SOURCE_TRANSCRIPTION.json` (frozen PR161 source transcription), original PR161 full ZIP SHA `27fee6fc9cd815100b60e57bf730f9855ea49b41c280b15d4ceed3d3913695ac`; PR160 source ZIP SHA `d9a920979e73c81e378670874952b06e76811fa81f3b669d153d43febf60ce51`.

`code/cdms_v2_crosswalk.py` uses 65-digit Decimal and exact 299792458 m/s to calculate all eight printed CDMS `.egy` line gaps, frozen 2021 photon/term gaps, and the global source-level integrability/rounding offsets, plus the two measured 2022 combination residuals. Writes `evidence/{CROSSWALK.json,LINE_CROSSWALK.csv,LAB_COMBINATION_CROSSWALK.csv}`. Does not parse a fake `.fit`, infer covariance, refit published measured data or produce production source files. Complexity O(8).

`tests/test_crosswalk.py`: 8 science/typing tests. Initial tests failed due comparisons of decimal display strings and scientific input mutation validation expressed with ordinary Python `assert`, which is stripped by `-O`. The latter was a real implementation defect: one tampered source field failed to be rejected in optimized mode. Repaired by explicit `ValueError`-based validation, preserving the scientific gate. **Post-repair local execution: 8/8 normal PASS, 8/8 `python -O` PASS, compileall PASS.** See both retained logs.

```bash
cd REC_HD_CDMS2011V2_CROSSWALK_20261030
python code/cdms_v2_crosswalk.py --output evidence
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q code tests
```

Independent Wolfram exact rational arithmetic also confirmed the same global 8/8 print-cell condition, maximal line discrepancy 24917.6546Hz, experimental-minus-.egy residuals and line integrability. Wolfram same operator context is not independent *author* R6/C9. Full raw CDMS fit covariance was not retrieved; original source `FAIL7/8`, production HOLD.

**Outputs:** 9 CDMS original 2011 displayed v0 level entries (transcribed), 8 side-by-side photon/level lines, 8 compatible cumulative level offsets, 2 independent lab combination residuals and two data-based diagnostic figures. Not a new experimental line catalog and no non-LTE gas history.