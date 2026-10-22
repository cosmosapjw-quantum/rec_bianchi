# Figure versions

The current publication figures and exact plotted arrays are in **v3**.
All three v3 PNGs were directly inspected. Their byte identities and the
independent scientific review are recorded in
`../evidence/PHYSICS_FIGURE_AUDIT.json`.

- v1: retained correction evidence; overlapping figure/panel titles.
  `v1/01_compton_energy_budget.pdf` is a retired failed export of **0 bytes**,
  retained as an artifact of that failed render. It is not a usable PDF.
  The current export is `v3/01_compton_energy_budget.pdf` (22,232 bytes).
- v2: layout repaired. PNG02 is intentionally retained as a failed,
  truncated PNG artifact (incomplete IDAT checksum). Do not use it.
- v3: buffer rendering, PNG CRC verification before write, byte readback,
  and actual visual review. PNG01 and PNG03 are byte-identical to v2.

The current v3 PDFs are vector exports of the same Matplotlib figure objects. The
recorded direct visual review covers PNGs, not independently rendered PDFs.
No source budget or ODE was rerun to repair the figures.
