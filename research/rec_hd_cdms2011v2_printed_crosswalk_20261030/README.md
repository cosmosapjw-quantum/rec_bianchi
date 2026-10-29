# REC-HD-CDMS2011V2-PRINTED-CROSSWALK-20261030

Bounded historical spectroscopy source-data reconciliation. **No source switch.**

Run from extracted project root:

```bash
python code/cdms_v2_crosswalk.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
```

Reads `source/CDMS2011_V2_EGY_V0_TRANSCRIPTION.json` (OFFICIAL RENDERED TEXT ONLY, no raw source bytes) and inherited frozen PR161 `reference/pr161/data/LAMDA_HD_SOURCE_TRANSCRIPTION.json`.

Outputs eight transition rows, nine-level joint consistency, two measured residuals and two physical diagnostic plots. Exact `Decimal` source computations. Full parent ZIPs in `inputs/` are immutable source reference backups, not newly validated original CDMS/LAMDA raw files. Gate: canonical 28/88, REC physical 0/313, 35Hz FAIL7/8, production HOLD. Different-author R6/C9 NOT_RUN.
