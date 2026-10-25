# PB01 execution and representation

Preparation: `python code/prepare.py` hashes only used input files, the unchanged
vendor adapters and new Python sources, then performs py_compile. It does not
import scientific source code or read numerical arrays. PATH_MANIFEST records
portable explicit source paths and accepted immutable identities. Restoring a
new layout requires a new authorized preparation freeze, retaining raw bytes.

Root PREEXEC review and actual S0/S1 acknowledgements precede root's
`evidence/RUN_READY.json` (`authorization: RUN_READY`). Then exactly one initial
`python code/run_bounded.py` invokes the primary with CPU30s/wall90s/1GiB and
one BLAS thread. No existing attempt/results path is overwritten and there is no
automatic retry. Source rebuild, solve, inverse, linear-system RHS, native and
IVP counts remain zero. Requested executor gpt-6.1-sol; observed model unknown.

Point action counting: every matrix-vector action and sparse functional/coordinate
pairing used for forward/JVP/VJP/oracle evidence is charged before evaluation.
One five-row event action charges five event actions; caps are256 and512.
Interval passes are separately counted. Elementwise matrix construction and
scalar Fraction arithmetic are not hidden linear solves. All exact toy actions
are included. The action counter is persisted before each counted action.

Native history_boundary.py is an unchanged byte copy. Only native_links,
interpolation and interpolation_jvp are called, never its frozen-source solve
owner. Alpha uses the native operation order. The chart treats binary64 alpha,
h and endpoint samples as exact constants; Fraction evaluates actual differences
of rounded finite coordinates. Delta-alpha is a separate arithmetic bridge.
Stored Js anchor is preserved by connected u=u0+chart increment. Physical query
law, reference offset, geometry, measure and physical uncertainty are not chosen.

Each source row, requested finite input, exact actual differences, completed
case arrays and metrics are saved immediately. A later exception/kill retains
prior results and stdout/stderr, with the parent resource receipt. Approximate
point products remain distinct from certified query/event intervals.

Conditional numerical boxes never populate physical_bound or physical_epsilon.
The endpoint norm is inherited by the disjoint-support proof; query, common-clock
and radius-scaled gains are distinct. Opposite event energies are paired by sign.

After separate figure authorization, the existing saved-data command is:
`python code/figures.py --results results/primary001 --out results/figures001`.
Alternatively root writes evidence/FIGURES_RUN_READY.json with authorization FIGURES_RUN_READY and invokes code/run_figures_bounded.py, which enforces the separate10CPU/30wall allocation. Root must keep this allocation and root plus the
same independent reviewer must inspect actual PNGs. No figures are run by prepare
or primary, and no source/solve is invoked by the figure script.
