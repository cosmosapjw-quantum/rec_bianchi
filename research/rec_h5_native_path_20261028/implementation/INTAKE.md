# Read-only native path intake — 2026-10-28 KST

Controller: Astra owns framing, frozen scope, numerical acceptance, release and
review. Requested implementation routing remains lower tier; actual runtime
model identity is not independently exposed. No native build, scientific run,
test, numerical RHS evaluation or prior computation replay occurred in this
intake. Old completion records and budgets were preserved.

## Source recovery and immediate recommendation

The exact canonical original source is now available at
`inputs/original/HyRec/`, recovered from the pinned repository27d20e3d4ef908d4ac5e9b6d8e1d98045a7294d6
archive `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`.
The downloaded726,954 bytes match SHA256
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`;
the archive contains29 entries. Extraction preserved source bytes. The binary
GitHub connector rejected UTF8-only access; the default network socket was
blocked; an approved read-only network escalation downloaded the exact pinned
raw URL. No authentication or repository mutation was performed.

Use this canonical archive for the new capture, rather than the remote h4
worker header: the canonical `hyrec_params.h` has DLNA=8.49e-5, while the
inspected h4 worker header has DLNA=(8.49e-5/4.). The history.c code itself is
the same source lead, but adopting that worker header would change the clock.

The shortest useful capture is an append-only observation of (a) committed
native grid rows and branch transitions, and (b) actual evaluated RHS calls
with their role, original arguments and returned values. These need separate
record types: the original algorithm contains post-Saha probes and algebraic
radiation updates, so a list of hydrogen function calls is not automatically
an accepted coupled-state path or a continuous ODE RHS.

## Immutable source identities observed locally

| Canonical member | Bytes | SHA256 |
|---|---:|---|
| history.c |30963 |8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976 |
| history.h |4184 |99c590758874ecbe80e83b218660863c6aa43786175f64d483267c78b209d710 |
| hydrogen.c |37471 |421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b |
| hydrogen.h |7837 |e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba |
| hyrec.c |7843 |22d094f86e005ad567614d212055df2764c8b624da10cc902ef912840de47681 |
| hyrec_params.h |3764 |cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2 |
| input.dat |44 |f8073ba70197378e156a6723e229ff47cc9f0d8be0121f1fce82aff6c64abcbc |
| Alpha_inf.dat |132000 |c543c755d99ba8e999450dd5cb486a3ad88d26378da0ccc8363b10418e4832bd |
| R_inf.dat |1700 |ce914f4b552ba55ba00f7916f36b0986f19adfdb638e5aefae91f7b2d05a8112 |
| two_photon_tables.dat |25191 |93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9 |

Original input.dat tokens, in original order, are:

```text
2.728
.021976
.13
0
.343
-1 0
.24
3.04
1.
1.
```

`rec_get_cosmoparam` reads T0, obh2, omh2, okh2, odeh2, w0/wa, Y and Nnueff;
fsR/meR default to1 in the source. Preserve the original file and parsing
behavior, including the two trailing1 tokens. Derived nH0 is assigned by the
native expression11.223846333047*obh2*(1-Y), not a substituted cosmology.

## Exact source function and operation map

Line numbers below refer to the recovered canonical sources.

| Source location | Function / operation | Capture significance |
|---|---|---|
| history.c37 | rec_set_derived_params | Computes nH0, fHe, grid sizes, RT start index/redshift and RT cutoff |
| history.c173 | rec_HubbleConstant, non-CAMB branch | Native algebraic background H(z), including matter/curvature/dark-energy/photons/massless-neutrinos; H is not integrated as a dynamical state here |
| history.c212 | rec_get_cosmoparam | Exact original input tokens and derived-parameter call |
| history.c255 | rec_Tmss | Algebraic steady-state matter temperature in Kelvin |
| history.c266 | rec_dTmdlna | Actual thermal ODE derivative in Kelvin per ln(a); special near-Tm=Tr branch returns -Tr |
| history.c280 | rec_get_xe_next1_He | Helium derivative plus post-Saha or fixed-step update; hydrogen is Saha constrained |
| history.c326 | rec_xH1s_postSaha | Saha/perturbed hydrogen probes at output time, including native finite differences, not accepted-state RHS samples |
| history.c372 | get_rec_next2_HHe | Coupled H/He step; actual input xe=xHeII+(1-xH1s), HII derivative and helium derivative, post-Saha or ODE H update |
| history.c417 | rec_get_xe_next1_H | Pure-H step with steady-state Tm; evaluates hydrogen RHS at input state, then post-Saha or fixed-step update |
| history.c458 | rec_get_xe_next2_HTm | Pure-H simultaneous xe/Tm ODE update; logs actual returned dxedlna and dTmdlna before update |
| history.c492 | rec_build_history | Owns committed xe_output/Tm_output, local xH1s/xHeII, branch chronology and outgoing virtual history allocation/free |
| hydrogen.c142 | interpolate_rates | Native table interpolation and temperature branch/domain decisions |
| hydrogen.c355 | populate_Diffusion | Native thermal diffusion rates |
| hydrogen.c413 | populateTS_2photon | Instantaneous source/rate matrices, escape-compressed virtual block and sources |
| hydrogen.c542/569 | solveTXeqB / solve_real_virt | Tridiagonal elimination and real/virtual algebraic population solve, not a photon time derivative |
| hydrogen.c633/667 | interp_Dfnu / fplus_from_fminus | Strict causal prefix interpolation and actual313 incoming characteristic routes |
| hydrogen.c730 | rec_HMLA_2photon_dxHIIdlna | State-dependent hydrogen RHS with radiation memory; overwrites current outgoing/average radiation slot as a side effect |
| hydrogen.c816 | rec_dxHIIdlna | Dispatcher among PEEBLES, RECFAST, EMLA2s2p and FULL |
| helium.c | rec_helium_dxHeIIdlna and Saha helpers | Actual helium closure used by early/coupled phases; retain native source rather than inventing xe=xHII in these phases |
| hyrec.c main | Allocation, rec_build_history call, output interpolation, cleanup | Internal native-grid arrays can be dumped before cleanup; ordinary stdout is interpolated integer-redshift output, not the stored native path |

The prior vendor Python `original_hyrec_native.py` is a diffusion/source lock
and diagnostics module. `full_2012_atomic_source.py` provides instantaneous
`build_original_full_atomic` and `complete_original_full_atomic` source-map
operations. It does not supply the original full thermal/helium integration
driver. The latter Python function explicitly generates an uncommitted outgoing
history candidate. These are not substitutes for capturing the original C
driver chronology.

## Native chronology and distinction between rows and calls

`rec_build_history` executes the following source phases on the fixed DLNA
grid. It has no adaptive accept/reject mechanism or a posteriori acceptance
certificate. Here “committed row” means the state assigned to the native output
arrays by this deterministic discrete algorithm.

1. HeIII→HeII Saha phase: xe_output from the Saha function, Tm=Tr.
2. HeII→HeI: helium post-Saha/ODE step, hydrogen Saha constraint, Tm from
   rec_Tmss. Native derivative-history startup uses finite differences of saved
   rows; these startup values must not be relabelled actual RHS evaluations.
3. Simultaneous H/He: helium ODE derivative, H derivative, then H post-Saha or
   fixed-step update. Tm remains algebraically assigned by rec_Tmss.
4. Pure H with steady-state Tm: rec_get_xe_next1_H, then rec_Tmss at output time.
5. Pure H and Tm ODEs: rec_get_xe_next2_HTm, initially MODEL/FULL with source
   switch to EMLA2s2p when RT becomes unneeded.
6. Low-redshift PEEBLES xe/Tm ODE update.

The ODE update uses the literal native multistep combination
DLNA*(1.25*current_derivative-0.25*derivative_prev2), followed by history shifts.
Capture the derivatives actually used and their history values if the exact
discrete update is to be reconstructed. Do not rename that update an arbitrary
standard integrator or infer an error estimate from it.

Most importantly, `rec_xH1s_postSaha` calls rec_dxHIIdlna at the Saha state and
at ±Dxe probes at the output index. Each FULL call can mutate that radiation
slot. A later actual input-state evaluation may overwrite it. Instrumentation
inside hydrogen.c alone therefore records temporary/probe states too. It needs
call-role tags supplied by the call sites and a separate final-row event after
the enclosing driver assigns its state. Do not change that write chronology
while observing it. Whether any first-hit historical snapshot was recorded
during a probe needs call-role evidence rather than assumption.

For Tm steady-state/Saha phases the path is constrained algebraically. Evaluating
rec_dTmdlna there and labelling it the derivative actually used would invent a
closure. Similarly xr[2] and xv[311] are instantaneous algebraic departures;
outgoing radiation is a causal transport/history map, not a311-coordinate
photon ODE supplied by these routines. A unified differentiable full-state F
requires an explicit additional contract.

## Available and missing arrays

The original saved history NPZ was inspected by ZIP/NPY headers only; no array
payload was loaded or numerical routine imported. It contains:

| Member | Shape / role |
|---|---|
| average_virtual |311×7489 photon departures |
| outgoing_virtual |311×7489 photon departures |
| outgoing_lyman |3×7489 line departures |
| eta, source_indices |7489 |
| energy_eV, frequency_Hz |311 |
| dlna, z_start, schema, completeness | Scalars |
| source_hash_keys / source_hash_values |2 each |

It has no all-time xe, xHII, xHeII, Tm, H or nH arrays. The locked native CSV
contains those thermodynamic arguments at one face only. Canonical C does have
all-grid xe_output and Tm_output internally; xH1s/xHeII are local branch-state
variables, and H/nH/TR are calculated at evaluation times. Ordinary hyrec
stdout prints interpolated xe and Tm/Tr at integer redshifts with decimal
formatting; that output alone cannot recover exact native-grid states or
helium partition.

## Minimal observation points to freeze next

- In rec_build_history, emit a committed-row event immediately after each
  branch's final xe_output/Tm_output assignment, with global index, native z,
  original clock expression, branch, actual available H/He fractions and
  thermal closure label. Record explicitly unavailable variables instead of
  reading uninitialized locals in phases where they do not exist.
- At the actual H/He/thermal call sites, tag input-evaluation versus post-Saha
  probe, global/local radiation index, call counter and branch. Record original
  arguments, actual returned derivatives and previous derivative operands
  before the native update. A capture must add no additional source evaluation.
- In rec_HMLA_2photon_dxHIIdlna after its algebraic solve and final radiation
  writes, emit the actual passed xe/xHII/nH/H/TM/TR, returned dxedlna, xr/xv,
  incoming/outgoing/average photon data and prefix ownership. This is an actual
  source evaluation record; it is not a photon ODE derivative record.
- Dump Dfminus_hist before rec_build_history frees it; xe/Tm and the externally
  owned Dfnu/Lyman arrays can also be dumped before main cleanup. Preserve
  binary64 values via raw arrays or hexadecimal serialization. The capture
  domain and stop event must be frozen before a build/run.

Stored H5 geometric eta and native represented z/clock remain distinct source
objects. Save both identities and bind indices; do not replace the admitted
stored clock by a newly reconstructed clock without an explicit bridge.

## Build/runtime dependencies and prior evidence

The original PR05B2 stage driver at pinned repository commit27d20e3d4ef908d4ac5e9b6d8e1d98045a7294d6,
`scripts/run_pr05b2_causal_history_stage.py`, lines214–263, used:

```text
gcc -std=c11 -D_DEFAULT_SOURCE -O3 -Wall -Wextra -Wpedantic
    [-DPR05B2_DIAGNOSTICS]
    hyrectools.c helium.c hydrogen.c history.c hyrec.c -lm -o <executable>
```

It runs the executable with cwd=extracted HyRec and stdin=input.dat. Dependencies
are a C compiler, system libm/libc, native headers and the bundled Alpha_inf.dat,
R_inf.dat and two_photon_tables.dat. No CAMB library is needed for this standalone
command; do not inherit the Makefile library target's icc/-DCAMB defaults.
Python/NumPy were used by the old driver for packaging raw arrays and scalar
history analysis, not as dependencies of the native executable.

Historical PR05B2 source instrumentation wrote the three snapshots and raw
radiation history at z≈900; SOURCE_HISTORY_PROVENANCE.json records7489 rows,
z_start1700.4825068138662, DLNA8.49e-5 and source_snapshot_z900.0168986313175.
Its history binary SHA is60b716a16ccf1af3ecd761cc16b1a417ffa03b8e34cf7a032c12e9f3ef529b38;
the saved NPZ SHA isd4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1.
The old stage performed canonical, guard-off and guard-on builds/runs. This
intake does not repeat those runs or convert their same-toolchain byte checks
into cross-toolchain numerical criteria.

The selected historical HARNESS_EXECUTION_RECEIPT files report harness validator
PASS, not native CPU/wall/RSS. The old native compiler log reports signedness
and unused-TR warnings; the inspected native-oracle BUILD.json is a fragment
shared-library compile with an h4 manufactured history grid, not a full native
trajectory timing. A measured full native path runtime was not found in these
selected receipts. Do not invent one or reuse unrelated6-column thermodynamic
derivative timing as a native trajectory measurement. Root must set the new
bounded one-shot capture allowance from this explicit unknown-runtime state.

## Intake resources and helper preparation

Read-only shell inspection commands imposed15CPU seconds and512MiB address
space; the native source was never executed. ZIP recovery was separately capped
at10CPU seconds/512MiB, with a15-second network timeout. Its measured recovery
block used0.060370423CPU seconds; whole process at checkpoint used0.151165CPU
seconds. NPY-header/source-hash metadata inspection block used0.007777159CPU
seconds, whole process0.123616CPU seconds. Shell/connector/startup/serialization
tails are not fully measured and are not asserted zero.

At root's later explicit request, `delivery/prepare_stage.py` was copied from
the prior unit and changed only for the owned path, namespace, REC_H5_NATIVE_PATH
schema/prefix and2026-10-28 ZIP date. Preparation was capped10CPU seconds; its
process checkpoint reported0.049766CPU seconds. The helper was not executed,
tested, used to publish or used to infer any backup ACK.

Live shared AGENTS was read at7de02b3e05705ead4eeb313c8487a21d4e6876a6.
The accepted prior HANDOFF_KO.md was read. The prior reference unit remains
complete; its313 reference coverage and0/313 physical coverage are preserved.
No full physical K/M2/defect/stability/tube/e0/epsilon/outgoing claim is made here.
