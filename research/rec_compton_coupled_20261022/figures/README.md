# Retained figures

The final report uses **v2**: three PNG/PDF pairs, all 58 plotted NumPy
arrays, five CSV tables and a byte/hash-bound `FIGURE_MANIFEST.json`.
The root author and the separate reviewer actually opened all three v2 PNGs.
The independent reviewer also reconstructed the curve/table mappings from
the saved inputs; see `../evidence/independent_review/FIGURE_V2_REVIEW.json`.

1. `01_temperature_response`: the existing saved baseline and both coupled
   branches on the same 109 comparison points; the lower panels show the
   temperature change relative to each initial condition's own baseline.
2. `02_energy_transfers_and_audit`: modeled transfers, separately labeled
   omitted-collision diagnostics with coefficient-support partitions, and
   gas-balance quadrature curves/endpoints. Positive energy means gas gain.
3. `03_branch_vs_refinement`: branch differences and both observed refinement
   changes. The stress panel excludes shear; these finite comparisons do
   not supply global error bounds.

v1 is preserved with its original plotter, stdout/stderr and actual visual
finding: the upper energy-panel symlog tick labels collided. v2 uses fixed
ticks and a writable temporary Matplotlib cache. The runtime, saved IVPs
and science analysis were unchanged, and no ODE was rerun to fix a figure.
The original render manifests retain their historical
`RENDERED_AWAITING_INDEPENDENT_VISUAL_REVIEW` status. The subsequent review
receipts establish the actual final visual/data verdict.
