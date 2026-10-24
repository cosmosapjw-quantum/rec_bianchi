# REC history 입력 source/clock mapping

Scope: R1/R2 source reuse + stage-local C2 mapping for the unchanged LINE02
snapshot and its 313 scalar retarded queries. This is one production mapper's
source inspection, not an independent scientific review and not a trajectory run.
Repository pin: `cosmosapjw-quantum/rec_bianchi@93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`.

## 1. Exact clock and ownership

Let h2=8.49e-5/2, h4=8.49e-5/4, eta_global(g)=-ln(8001)+g h.
Both producer cosmologies define z(g)=8001 exp(-g h)-1. The original photon
column zero is **not** the initial global z=8000 node:

| Candidate | Global photon start g0 | Column mapping | Stored full outgoing prefix |
|---|---:|---|---|
| R3i h2 U4 | 36446 | j=g-36446 | 761 inherited columns + newly accepted steps |
| R3i h2 U5 | 36446 | j=g-36446 | 2006 inherited columns + newly accepted steps |
| R3q h4 event / R3s h4 smoke | 72892 | j=g-72892 | 8 inherited columns + newly accepted steps |

Consequently eta0=-ln(8001)+36446 h2=-ln(8001)+72892 h4 exactly as a
real-number relation between the declared decimal clocks. A floating clock
implementation may round this in its own stated sequence. Candidate eta0 must be
derived from its producer; the LINE02 snapshot's META,zstart is a different input
and cannot be substituted.

For a stored prefix with n columns, outgoing column j belongs to input state
g=g0+j. The producer evaluates the source on that input state, stores the three
arrays at column j, and advances to state g+1. Thus the final accepted state has
global index g0+n while the final stored photon column has global index g0+n-1.
The state endpoint is not an additional photon knot.

For strict native interpolation, accepted queries satisfy

`eta0 <= eta_query < eta0 + (n-1) h`.

For an admitted interior query, k=floor((eta_query-eta0)/h),
alpha=(eta_query-eta0)/h-k, and both k,k+1 must be in the retained prefix.
The latest stored knot is excluded by the native `interp_Dfnu` contract, even
though its value exists. Native scalar prehistory eta_query<eta0 returns a
thermal departure of zero; this is an explicit model boundary condition, not
evidence of retained data coverage. No source-cell extrapolation is implied.

Source locations:

- `primordial_2012_refined_start.py`: constants18–25, cosmology51–89.
- `primordial_2012_refined_u4_exit.py`: constants27–32; imported prefix39–61;
  j=g-RT_IZ132; causal gather139–142; input-state write170–172;
  output-state metadata198–205; retained slice216–219.
- `primordial_2012_refined_u5_thermal.py`: constants29–31; j116;
  input-state gather142–145; source write159–161; state/step176–182;
  retained slice191–197.
- `primordial_2012_quarter_start.py`: h4 constant29, source archive33,
  redshift60–63.
- `primordial_2012_quarter_continuation.py`: starter columns48–66;
  j164; gather172–174; input-state write218–220; output state260 and
  photon_col268; return284–285.
- `causal_virtual_redshift.py`: shape/committed-prefix182–184, eta0/face228–229,
  upper accepted236–243, strict cell245–251, sparse history gather271–287.
- Native `hydrogen.c::interp_Dfnu`:633–652; native `fplus_from_fminus`:667–718.

## 2. Source identity: May/October wording is not a mismatch

The actual restored LINE02 vendor/hydrogen.c and the separately fetched R3s
source_extract/HyRec/hydrogen.c are byte-identical:

- SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`
- size37471 bytes; Git blob `2df4561f1b1ef80991ca3b7645666a630eea19b7`.

The source comments say "Added/Modified May2012" inside the project's canonical
October2012 archive. `ORIGINAL_HYREC_CANONICAL_PROVENANCE_SUPERSESSION.json`
explicitly records that these are intrinsic release metadata and not an
uncertainty or mismatch gate. The archive pin is
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`,726954B.
The text diff is empty (`HYDROGEN_VERSION_DIFF.patch`).

R3iU4, R3qevent and R3ssmoke retained verification receipts report this same
source archive and hydrogen.c, and history.c SHA256
`8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976`.
The latter was independently fetched and byte checked here. h2 and h4
hyrec_params.h differ as expected because DLNA is changed. The h4 header is
`46b4cb3f7a463ddbae966c02114e16f8e079615e4838f5dcbcb6cd1c5a67a83f`;
the h2 modified header is producer-reported
`e83d8031975c0a64cdb45a2b8ba03a4a0a75c85fac5cf2437aadc915e25751bf`.
This report does not replace the original runtime/capsule receipts.

## 3. Energy grid and departure/frame conventions

The actual R3s native `two_photon_tables.dat` was fetched exactly,25191B,
Git blob `df04635e8fd5ed03481547a7967a14030d90a79b`, SHA256
`93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9`.
The parent primary can compare its first column with the fixed LINE02 CSV's
VIRTUAL energy column; the mapper has not performed that scientific array check.
The header uses NSUBLYA140, NSUBLYB271, NVIRT311 and MODEL FULL.

Arrays are outgoing signed departures with virtual shape[311,n] and
Lyman shape[3,n] ordered Lyalpha,Lybeta,Lygamma. `average_virtual` is a
different in-bin field and cannot replace `virtual_out`. The 313 incoming
owners comprise311 virtual incoming faces plus2 Lyman incoming faces.
`fplus_from_fminus` picks the next higher virtual outgoing channel except at
the three line gaps, where the appropriate Lyman outgoing owns the input.
The lowest virtual outgoing channel is not one of these upstream faces.

Both retained trajectory callers pass `shear_q=0.`. That is the older scalar
FLRW anisotropy parameter; it is not the local positive expansion ratio q in
HISTORY01, whose FLRW value is1. Source propagation uses eta=ln a and E a
constant. The actual native departure basis is Wien, f_W=exp(-E/TR); retained
signed departures are meaningful. The optional nonzero-shear Planck correction
in the older causal module is outside this scalar candidate admission and is
not promoted into the separate HISTORY02 owner's characteristic work.

## 4. Physical parameters must still match

Code-byte and energy-grid identity are not physical history equivalence.
The exact canonical archive input.dat has:

| Parameter | Canonical input fixture | h2/h4 Python cosmology default |
|---|---:|---:|
| T0[K] | 2.728 | 2.7255 |
| omega_b h2 | .021976 | .0224 |
| omega_m h2 | .13 | .14309694000000003 |
| omega_k h2 | 0 | 0 |
| omega_de h2 | .343 | .31113726660800006 |
| w0,wa | -1,0 | -1,0 |
| YHe | .24 | .2454 |
| N_eff | 3.04 | 3.03821934419124 |
| fsR,meR | 1,1 | 1,1 |

`history.c::rec_get_cosmoparam`212–243 defines the input order and sets the
fixed fsR/meR flags; `history.c`42 defines
nH0=11.223846333047*omega_bh2*(1-YHe) m^-3.
The saved LINE02 CSV supplies TR_eV_rescaled,nH_cm3,fsR,meR and exact z.
Its diagnostic instrumentation emits those actual source variables rather
than inferring them from a fixture name. The parent should compare the implied
T0=TR_eV_rescaled*fsR^2*meR/[kB_native(1+z)] and nH0 against these parameter
owners in its predeclared primary. This mapper does not certify solely from
the presence of input.dat that every old run read that fixture.

The candidate source domain should remain distinct until the actual saved
candidate state/metadata are checked. Physical parameter mismatch, if measured,
requires a justified model-transfer/response uncertainty; it is not a time-grid
interpolation error that can be hidden in h2/h4 disagreement.

## 5. Container metadata and evidence binding

The h2U4 writer in `verify_r3i_h2_u4_exit.py`227–232 saves only states_json,
steps_json,virtual_out,average_virtual,lyman_out. Its NPZ does **not** embed
dlna or source_zip_sha256; these must be bound from its immutable producer
receipt and source mapping. h4 writer `verify_r3q_h4_continuation.py`373–380
additionally embeds dlna,source_zip_sha256,parent_checkpoint_sha256 and
rei_activation. Do not invent absent NPZ fields.

The source mapping here reads pinned current producer code and retained original
verification/capsule-closure receipts. It does not rerun or rehash all96/100
original capsule source members. The parent must cross-check `steps_json`
input_iz/output_iz/photon_col and last state with the actual recovered arrays
before admitting the mapping for the selected payload.

## 6. Status and exact remaining obligation

Source mapper status: source/clock ownership reconstructed; all fetched source
files tied to exact Git blob and SHA256 identities in SOURCE_IDENTITIES.json.
Scientific trajectory executions0; actual history array loads0; new IVP0;
native runtime0; old campaign replay0. No external mutation.

Remaining parent work is the frozen actual-array/header/coverage check at the
unchanged LINE02 query domain, energy-grid comparison, physical-parameter
comparison, and explicit uncertainty admission. Same-h parity and lossless
storage equivalence cannot establish a curvature bound or endpoint uncertainty.
No universal absence statement or new no-go theorem is asserted.

Skill context actually read: c38/physmath-research-loop1.3.0 SKILL.md,
references/THEORY_LOOP.md(R1/R2 and selected-stage binding),
references/POLICY_INTEGRATION.md. Applied exact scope, immutable source identity,
reuse, finite review, separate source/physical uncertainty, and no broad no-go.

Tool observations: one local transfer serialization attempt failed with
JSONDecodeError before writing fetched source bytes; the diagnosed repair used
a JSON file and base64 decoding, then exact Git hash checks. This was a
metadata-transfer failure, not a scientific computation failure. Two speculative
source-path fetches returned404; corrected paths were resolved from the pinned
Git tree. These do not indicate missing runtime or missing actual history data.
