# REC HD actual source-driven nonLTE molecule cooling

Start `THEORY_KO.md`, `CODING_KO.md`, `REPORT_KO.md`, `DAG_DELTA.json` and `HANDOFF_NEXT_THREAD_KO.md`. Preserves original PR160 in `sources/PR160_PARENT_SOURCE_IMMUTABLE.zip`. The complete 2021 LAMDA raw hd.dat was **not** re-downloaded; data source is transcribed official web-visible text, internally classified.

```bash
python src/hd_nlte.py --source data/LAMDA_HD_SOURCE_TRANSCRIPTION.json --output evidence/NONLTE_GRID.json
python src/export_tables.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python tests/independent_mpmath.py
python src/render_figures.py
```

The auxiliary 2-node DAG holds one complete scoped J1 physics node and a partial full9 reconciliation. This does not change the central 28/88 or physical 0/313.