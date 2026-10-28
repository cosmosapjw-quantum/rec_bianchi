# Visual review of saved-data figures

The root author opened both PNG figures from PLOTS_attempt001. The right-hand
legend in source_bridge_comparison.png partly occluded the final blue marker.
Only that legend location in study.py was changed to center right. PLOTS_attempt002
regenerated figures from the same saved C7/C8/C8_NATIVE outputs; no scientific
solve or native call was repeated. Both attempt002 PNGs were opened and checked.
Labels, logarithmic scales, thresholds, markers and legends are readable.

Use execution/PLOTS_attempt002 as the delivery figure set. Attempt001 is retained
with its original resource receipt. All plot runs count in RESOURCE_LEDGER.json.

Interpretation: 132 writer points are saved discrete evaluations. Lines connect
those points for display and do not certify time interpolation. In control labels,
z/s/d mean zero, signed-negative and doubled incoming. Their nine comparisons
represent one incoming direction at each of three distinct points. J and incoming
occupation departures are dimensionless. The source-prefix model and the original
real-model failures are displayed separately. The expm1 comparison is diagnostic;
the production HyRec source is unchanged. Plotted magnitudes are not physical
error enclosures or interval-certified Lipschitz constants.
