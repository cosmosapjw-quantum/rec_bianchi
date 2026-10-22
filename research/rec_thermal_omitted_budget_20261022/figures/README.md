# Figure versions

The current publication figures and exact plotted arrays are in **v3**.
All three v3 PNGs were directly inspected. Their byte identities and the
independent scientific review are recorded in
`../evidence/PHYSICS_FIGURE_AUDIT.json`.

- v1: retained correction evidence; overlapping figure/panel titles.
- v2: layout repaired. PNG02 is intentionally retained as a failed,
  truncated PNG artifact (incomplete IDAT checksum). Do not use it.
- v3: buffer rendering, PNG CRC verification before write, byte readback,
  and actual visual review. PNG01 and PNG03 are byte-identical to v2.

The PDFs are vector exports of the same Matplotlib figure objects. The
recorded direct visual review covers PNGs, not independently rendered PDFs.
No source budget or ODE was rerun to repair the figures.
