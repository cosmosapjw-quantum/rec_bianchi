# C5 controls and plotting implementation

Owner: latest_intake. The native implementation agent owns common.py,
instrumentation, analysis, and the bounded runner. This change owns only
code/controls.py, code/plot_results.py and this implementation/preflight record.
It follows the frozen coding contract without introducing a new model,
tolerance, closure, or scientific admission.

## Interfaces and controls

Both modules expose run(output: Path). controls.py uses the agreed common.py
finite-record validation functions on eighteen independent manufactured
fixtures: fifteen exact expected refusals and three positive structural or
mathematical cases. The named cases follow the frozen contract order. They
include distinct prev and prev2 operands, the neutral-H minus sign, the actual
139-to-311 query route, valid last-writer overwrites, and an independently known
affine function u(t) = -2t - 3. Post-Saha records retain valid captured memory
shifts but deliberately violate the ODE recurrence; their rho remains null.

The control runner writes CONTROL_ROWS.jsonl, CONTROLS.json and SUMMARY.json.
It records the first unexpected result and stops. PASS is emitted only after
all eighteen expected outcomes have been observed during a later authorized
execution; preparation itself makes no control-result claim.

## Saved-data figures

plot_results.py consumes only results/analysis001/PLOT_DATA.json through the
schema agreed directly with the native implementation agent. It does not
import the analysis module or call native/source functions. Two PNG files and
a two-page PDF show committed thermodynamic state, native phase, final writer
differences and ownership, the actual 313 affine slopes/endpoint ranges, and
discrete recurrence diagnostics. Optional absent writer IDs are identified as
absent; missing writer values are gaps rather than fabricated zeros.

The committed Tm ratio is Tm_K/[native T0_K (1+z)]. The writer TM_eV/kN minus
committed Tm_K value is a Kelvin diagnostic conversion, not a replacement for
the native dispatcher argument. Affine slopes and endpoint ranges use separate
axes with their respective units. Exact rational values are converted to float
only for display; the saved rational packet remains authoritative. Positive
normalized residuals alone appear on a logarithmic axis, with the frozen
64*2^-52 arithmetic criterion; exact zero rho values are counted separately.
No numerical floor is introduced.

Native real/virtual QSS vectors are departures xi - xi(eq with 1s), not absolute
populations. This module introduces no QSS positivity test. All physical bounds
remain null, physical coverage remains 0/313, H6/H7 remain OPEN, L4 remains
false, and REI activation remains false. The plotted recurrence residual is
discrete arithmetic evidence and is not a physical defect.

Output names are NATIVE_COMMITTED_AND_WRITER.png,
H5_AFFINE_AND_RECURRENCE.png, NATIVE_PATH_FIGURES.pdf and
FIGURE_RECEIPT.json. The receipt hashes the saved input and each visual output.
Existing expected outputs cause refusal. A later failure preserves any partial
output for diagnosis rather than rerunning automatically.

## Preparation verification and release boundary

Only AST syntax parsing is authorized in this preparation step. No module
import, control execution, saved-data analysis, source/RHS execution, native
capture, or figure rendering is performed here. The separate bounded runner
retains the controls001 30 CPU / 60 wall and figures001 20 CPU / 60 wall caps.
The preparation receipt records actual AST parsing metadata CPU separately
from unmeasured editing/tool overhead. Root must release execution explicitly.
