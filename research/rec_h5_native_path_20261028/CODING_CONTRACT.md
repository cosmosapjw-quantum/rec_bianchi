# REC-H5-NATIVE-PATH01 coding contract

This is the root's implementation contract. theory/THEORY.md with R6 alpha/sign
corrections is authoritative. R9 freezes this file before execution. No changes
to original inputs or old published files. New files only under this owned unit.
Requested implementation executor: existing lower-tier native_reference_implementation;
observed runtime identity is not inferred from requested label. Independent
Astra reviewer did not implement this producer.

## Source and owned paths
Use inputs/INPUT_LOCKS.json; verify its original archive/member and four retained
input hashes. Canonical archive48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27;
input.dat original T0=2.728,omegabh2=.021976,omegamh2=.13,curvature0,
omegaDEh2=.343,w0=-1,wa=0,YHe=.24,Neff=3.04,fsR=meR=1.
Header DLNA8.49e-5,MODEL FULL. Use recovered original native C/H and tables,
not historical h4 refined header. Original files stay byte-exact. Instrument
copies under build/source/ using code/instrument.py and emit unified source diff.
Runtimes/caches/ELF are build artifacts, never mistaken for source.

## Capture contract
One original full native trajectory from its unmodified input, with observation
hooks only. Native main and all native arithmetic/branch conditions remain.
Compile one instrumented executable with gcc -O3 -D_DEFAULT_SOURCE and -lm
plus its observation macro/helper. No fast-math or time-step/physical changes.
The executable runs in its copied-source directory with original input.dat stdin.
Capture relevant radiation-local rows0..7488 (original stored history length)
and at least four preceding committed rows for initialization context. Native
continues its normal full run; only required window has detailed output.

1. COMMITTED nodes: global/local indices, native z, phase identifier, xe and
Tm_K taken directly after driver assignments; xH1s/xHII/xHeII where native
branch locals define them; fixed-neutral helium explicitly tagged. Null is
required for an unobserved variable, not an invented value. Other background
fields may be captured from actual source-call inputs; separately tag values
recomputed by a pure background function at committed z. Actual H,nH,TM,TR
for every captured hydrogen call are mandatory. Preserve Kelvin/eV and m^-3/
cm^-3 labels, original multiplication order and actual binary64 values.

2. SOURCE CALLS: every actual hydrogen dispatcher invocation in this window,
monotonic call id, caller/phase/probe tag, local slot, model, actual z/xe/xHII/
nH/H/TM/TR and returned dxHII/deta. Use wrappers/hooks so each native invocation
is called exactly once and the observed evaluation order of probe operands is
recorded. Count global calls even outside detailed window; hard ceiling200000
hydrogen dispatcher calls and40000 detailed-window calls. If exceeded, save
prefix and stop. Do not add rec_dTmdlna calls during algebraic-temperature phases.

3. RECURRENCE operands: native X_in/X_out, native current derivative, prev/prev2
before shift, actual update branch and component sign sigma; store integrated
H/HII,HeII or Tm components actually used. Post-Saha updates receive their own
tag and no fabricated recurrence residual. Capture source initialization
operands/indices if their derivative memories were seeded from secants.

4. SLOT ownership: an event records each actual FULL photon write. Preserve last
writer per captured local slot. Export final outgoing virtual311, outgoing
Lyman3 and average311 arrays for0..7488 immediately before their lifetime ends,
plus native energy nodes. Record endian/dtype/order/shape for raw files.
Zero-initialized versus written slots are distinguishable. Selected QSS capture
uses the deduplicated integer local slots among the626 endpoint references
plus target local5127: record2real and311virtual
solved values, corresponding outgoing values and actual call id for EVERY
write in those selected slots. Last-writer matching must therefore be possible
without assuming the last call is a committed-state call. No full dense matrix
export is required; equation source, actual coefficient inputs and QSS solution
are the supplied closure operands. Capture only actual values, no new solve.

## Analysis and exact schema
code/analyze.py reads saved native capture, old history/context/target CSV and
prior reference packet. It does not run native, reevaluate RHS or import the
previous reference producer. Each original query retains its route, endpoint
indices, exact stored a,b,q and exact rational alpha. Join both committed-node
and final-writer thermodynamic fields. Primary common actual fields are xe,
xHII,TM_eV,TR_eV,H_s_inv,nH_cm3 from final-writer calls; committed xe,Tm_K and
available partition fields are a separate path. Do not collapse the two views.
For each available finite binary64 endpoint field serialize exact rational
left/right/query/slope and endpoint min/max via Fraction.from_float, using
unchanged original geometric endpoints. Retain native z and distinct clock
labels. Required complete joins:313queries/626endpoint slots. Missing required
writer/call or committed xe/Tm endpoint is a scoped failure, not a zero fill.

## Frozen checks
A literal eps64=2^-52 is used in every tolerance below.
A. Source inputs/archive/header unchanged. Generated C diff adds observations
and necessary local result variables, not changed physical arithmetic/branches.
B. Retained photon data compare all captured7489rows with old arrays using
componentwise abs(new-old)<=512*eps64*max(abs(new),abs(old)); both zero require
exact zero. Report bitwise-equal counts, maximum absolute/relative difference,
all nonmatching positions if any and actual source outputs. This is finite
source parity, not a physical error bound. Do not widen on failure.
C. Native target z/parameter inputs at local5127 are compared to saved target
CSV with same512eps component scale; discrete indices/routing/energies and
T0/fsR/meR identity are exact. Old stdout SHA is reported if available but is
not substituted for scientific agreement. Full numerical arrays, not hashes,
are the comparison evidence.
D. Call ids/order/phase, writer slot and selected QSS-output/final-array join
are exact structural/represented-value checks. Local/global mapping uses
observed izH0. No inferred C operand evaluation order. State/CALL discrepancies
are reported as data, not automatically asserted failures.
E. For actual integrated components compute exact rational rho from THEORYeq2
including sigma. Require abs(rho)<=64eps*operation_gross; zero gross requires0.
Validate memory shift and recorded initialization separately. Do not apply an
ODE recurrence to post-Saha/algebraic phases.
F. Exact313 affine constructions satisfy endpoint identities, exact query
alpha equality and convex hull; slope denominators positive. Domain evidence
is reported with actual minima, phases and interval coverage. No numerical
positive min is used as a physical uniform tube. Segment curvature0 describes
the affine representation only; do not put0 into physical_M2.
G. All outputs retain physical_query_bounds/full_state_K/physical_M2/physical_
defect/stability_L/positive_uniform_ode_tube/initial_error/physical_epsilon/
physical_outgoing_bound=null; H6/H7OPEN,L4false,REIactivationfalse.

## Targeted controls
Implement18named deterministic controls using small manufactured records or
copies of saved actual selected records, with no native/RHS rerun:
(1) bad immutable source hash;(2) wrong global/local index;(3) a>=b;
(4) outside query;(5) unknown phase;(6) duplicate call id;
(7) reversed call order;(8) missing required final writer;
(9) writer slot mismatch;(10) changed query route;
(11) omitted prev2;(12) using prev instead of prev2 in a nondegenerate fixture;
(13) nonfinite required state;(14) cm^-3/m^-3 conversion mismatch on known input;
(15) neutral-H wrong sign in a nondegenerate fixture;(16) manufactured post-Saha
row must be kept separate from recurrence;(17) legitimate overwritten slot
selects last actual writer;(18) endpoint/query affine identity and convex hull.
Controls1-15 expect explicit refusal/failure of the affected contract. Controls
16-18 are positive structural/math controls. Use distinct meaningful fixtures,
not copies of implementation branches. Keep names/results/values in raw JSON.

## Modules, commands and finite run sequence
Use code/instrument.py, capture_support.c/.h, analyze.py, controls.py,
plot_results.py and run_bounded.py (names may be combined without contract
change; report actual mapping). Root RUN_READY required after C5 source review.
The runner exposes build001,capture001,analysis001,controls001,figures001 modes
and records exact command/source/input snapshot, exit status, inclusive child
CPU, wall, RSS and logs; setslimits before child exec and process-group timeout.
One thread via relevant BLAS/OpenMP environment. Per-child address space1GiB.

build001: at most30CPU/60wall, one instrumented native build.
capture001: at most60CPU/120wall, one new native trajectory; global200000calls/
40000detailedcalls, no parameter variation or prior admission tests.
analysis001: at most60CPU/120wall, one saved-data source/recurrence/313join pass.
controls001: at most30CPU/60wall, one18control pass on saved/small records.
figures001: at most20CPU/60wall, saved-data-only2PNG and1multipagePDF.
Implementation cumulative300CPU. Remaining100CPU is reserved for a controller-
authorized diagnosed repair; it is not preauthorized. Separate review120CPU
and packaging60CPU remain bounded. First-failure logs/prefix are preserved;
return scientific/input/convention ambiguity to root. Do not replay completed
native capture to repair an analyzer or figure issue.

Figures: (1) native committed xe,Tm/Tr and phase/call ownership across retained
window, with writer/committed discrepancies where present; (2) actual313field
slopes/ranges and discrete recurrence residuals using meaningful component
scales and explicit units. Mark zeros/roundoff and exact-versus-floating views.
Root and independent reviewer inspect actual images; no source recalculation
in rendering. Scientific pass requires independent read of source/diff/raw/
figures, not a smoke import or receipt count.

## Return and claim boundary
Supply native capture/raw packet, exact313path packet, source-parity and
recurrence statistics,18controls, figures, code/instrumentation/build identity,
actual budgets, failure records and precise next continuous-model inputs.
Native path acquisition fills a data dependency; it does not close H5's
physical epsilon. Keep all prior completed packets and failures unchanged.

