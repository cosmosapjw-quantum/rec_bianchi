# LINE01 C1–C8 implementation note

Current status: **PASS_AFTER_TARGETED_ROUNDING_REPAIR — 704 checks PASS, 0 FAIL.**

Historical pre-execution status at creation: CODE_COMPILED; SCIENCE_NOT_RUN; awaiting parent RUN_AUTHORIZED. The sections explicitly marked pre-execution below record that earlier checkpoint, not the current execution state.
No old suite, cosmological IVP, native HyRec runtime, or completed campaign was run.

## Implementation

`code/line_source.py` implements a frozen source-card registry, explicit population
scope, and an exclusive `standalone_detached` owner. It rejects simultaneous
canonical ownership. The copied ANGULAR01 `escape_moments.py` remains byte-identical
(SHA256 `f8a91ddad8833d4c0079025af81fb8df4b9423da3d87a8363093603922da0c2e`).

The three immutable cards are the effective coincident collapsed 2p card and two
separate NIST fine components. The effective card follows FROZEN_CONTRACT and its
collapsed-source addendum; the earlier general derivation's single-fine-component
recommendation does not override that frozen choice. The whole-n=2 card is rejected.

The finite source uses unchanged angular quadrature, common signed population
exchange, nonnegative effective reservoir channels, zero ionic/electron yield,
separate atomic-internal/radiation energy, zero thermal exchange, and spatial/PSTF
injection. These are source rates, not stored radiation or matter stress.

The exact local thick map uses a monotone scalar root with `brentq`, at most128
iterations, the proven finite bracket, stable `expm1` packet, and exact zero-step
and equilibrium branches. No ODE solver is imported. The complete population path
is checked against the frozen gate. Coarse analytic population/energy/tensor upper
bounds are retained in log form even when their floating values underflow. A zero
rounded bracket width is explicitly marked as unresolved, never exact finite-opacity
equality. All certificates distinguish model truncation from floating interval proof.

The original Einstein donor is loaded from `vendor/rec_source_adapter.py` by selecting
only `_readonly` and `IsotropicEinsteinLineSource` AST nodes. Their original class and
function bodies, decorators and method formulas are compiled unchanged. Unrelated
native imports are excluded. The run records module Git blob/SHA256 and each selected
source segment SHA256. This isolates dependency loading, not a rewritten donor formula.

## Frozen execution accounting

`code/run_line01.py` creates only `results/attempt001/`, refuses overwriting, and
appends each completed raw row to a flushed/fsynced JSONL stream. On an exception it
preserves the original traceback, partial raw rows, counters and manifest. On an
acceptance failure the raw failed evidence is retained. New attempts require an
explicit amendment rather than an automatic retry.

The exact finite plan is36source states,27local map rows,6selected original-Einstein
and independent full-sphere comparisons,2 finite-opacity separable reference roots,
and3tracks×81analytic samples. The local map counter is270=27+243. The2finite references
reuse an already evaluated dimensionless thick map with identical g,f,x0,omega and
path threshold20; their isotropic separable quadratures are distinct reference work,
with quadrature/root function evaluation counts recorded. No additional thick-map
rows are introduced for those reference endpoints.

The six fine-component source fixtures are two cards×three driving cases at t=1
with the triaxial shear. The fixed rotation is Rz(0.37)Ry(0.41), applied to
S=diag(-0.4,0.1,0.3). Eigh and full-sphere directions are independent discretizations.
The six reference rows compare the exact donor action at the profile-averaged
occupation and the frequency-crossing number normalization, with gross microscopic
normalization near equilibrium.

The27map rows use a90decimal-digit mpmath W0 oracle at the frozen binary64 scalar
coefficients y0,d0,b,x_eq,N,omega. It does not use the production log root or endpoint.
Eigh/Q quadrature error, scalar algebra/root rounding, finite-opacity truncation,
atomic-table uncertainty, and collapsed-model error remain different quantities.

There are18explicit invalid-input API probes, recorded separately from physics rows.
They exercise source-card/scope, owner, finite/positive input, directional expansion,
whole-path gate and negative-step rejection. They do not rerun old tests.

## Figures and raw provenance

Three figure tracks show the new detached model's upper-level fraction, signed
photon packet, opposite radiation/internal energy, and PSTF energy packet. The
native track uses one byte-verified saved scalar source state at z≈1100 and supplied
shear. Each track exports81rows to CSV plus PNG and PDF; PLOT_MANIFEST records exact
hashes, units and data paths. None of these is a new cosmological history.

The runner records the frozen contract hash, all code hashes, package versions,
source reconstruction, donor AST reuse, acceptance checks and raw artifact hashes.

## Verification at the pre-execution checkpoint (historical)

`python -m py_compile code/line_source.py code/run_line01.py` succeeded.
At that earlier checkpoint the source matrix, map, quadratures and plot samples had not yet been executed.
A single independent physics/code/plot review remains a separately owned stage.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; global convergence NOT_RUN;
production NOT_APPROVED; REI_activation=false. Historical cohort and local-only
failure-raw preservation boundaries are unchanged.

## Final bounded execution and targeted correction

After the parent's StageA publication and dual-backup authorization, attempt001
completed 36 source rows and 25 map rows, with 616 checks passing. The next native
map at omega=1 stopped because z0=-7.898205430874699e-17 is below one ulp
of omega: the real lower/upper log-root bracket rounded to the same float.
This was a numeric bracket-construction defect, not a failed physical gate.

The original FAIL, traceback, all partial rows, 616 PASS checks and manifest remain
unchanged. Original core and runner bytes were copied to evidence/attempt001_code/
before patching. The parent authorized exactly one targeted correction: move the
lower bracket one float toward minus infinity, the upper one toward plus infinity
with the upper clamped to0. The physical formulas and tolerances were unchanged.
The exact pre/post hashes and diff are recorded in results/resume001/.

Resume001 reused the 36 successful source and 25 successful map rows unchanged. It
computed only the 2 missing native map rows, 6 direct Einstein/full-sphere comparisons,
2 finite-opacity reference roots,18 invalid-input probes and 243 analytic plot samples.
The completed frozen matrix is 36/27/6/2 plus 3 tracks × 81 samples. Acceptance is
704 PASS = 616 reused + 88 new; FAIL 0. The initial failure remains a separately retained
record. The attempted native omega=1 row was retried once; no other successful
science rows were replayed. No new or old cosmological/local IVP was run.

All 3 PNG images were opened and visually inspected by the implementer. The axes,
units, signs, legends and detached-local-step captions are readable. The three
CSV datasets and 3 PNG/PDF pairs have hashes in figures/PLOT_MANIFEST.json.
This constructor inspection is separate from the single independent review pass.

results/SUMMARY.json records counters, residual maxima, native state/map numerical
values, original failure preservation and figure identities. The scientific scope
and every inherited HOLD/NOT_RUN/NOT_APPROVED/REI_activation=false remain unchanged.
