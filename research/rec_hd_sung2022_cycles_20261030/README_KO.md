# REC HD | Sung2022 actual four-line spectroscopy + three experimental closure cycles

This is an additive, source-qualified experimental evidence package built upon immutable REC PR163. It contains *actual measured* line-center/line-shape parameters from Sung et al. JQSRT 295, 108412 (2023, online 2022), combined with five previously authenticated measurements. All comparisons preserve the distinction between measured photon ν, frozen LAMDA photon νP, frozen LAMDA level-energy νE and historical CDMS printed energies.

Core output: 4 new measured photon lines, 3 exact experimental cycle residuals, 4 measured-source-bound photon observable rows, 12 conditional pressure-shift/width rows at 296 K, exact rank 6, nullity 3; source covariance and physical production gates remain HOLD. Scientific report: `THEORY_KO.md` and `REPORT_KO.md`.

No raw CDMS v2 bytes, 2011 fit covariance, Sung raw scans or complete paper PDF are fabricated or included; the table literals were transcribed from accessible published full text. `backup/REC_HD_1984_LAB_GRAPH_20261030_SOURCE.zip` preserves the original inherited source archive byte-for-byte.

Rerun:
```
python src/lab_cycles.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python src/figures.py
```
