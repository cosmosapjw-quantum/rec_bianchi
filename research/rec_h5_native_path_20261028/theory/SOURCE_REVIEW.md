# REC-H5-NATIVE-PATH01 — independent source/theory feasibility review

Date: 2026-10-28 KST. Role: independent source/theory reviewer, not production
implementer. Requested tier Astra; runtime model identity not independently
observable. Scope: read-only source inspection and constructive mathematical
input design. No build, native trajectory, reference producer, numerical
experiment or scientific check was run for this review.

## Recommendation and useful next result

Acquire **one instrumented native fixed-step thermodynamic/QSS path**, retaining
the original model, cosmology, tables, step size and operation order. Export
native thermodynamic nodes together with their actual radiation-producing
calls, derivative-memory operands and phase labels. Bind the resulting nodes
to the original 313 H5 source cells and construct a declared continuous
represented path on those stored geometric cells.

This supplies data that the old photon-only history does not contain:
all-time thermodynamic state, native derivative evaluations, the actual
algebraic closure states and the association between final radiation slots
and their generating thermodynamic calls. Its first useful theorem is a
finite causal transition/reconstruction result; a second conditional implicit
closure derivative lemma gives the explicit route from those operands to
future whole-cell curvature work. A continuous full-state physical ODE bound
is not a consequence of a trace alone.

The previous 313 native-reference computation stays frozen and is consumed
by identity. The new trajectory is justified by newly requested observables
missing from its old export, not by a request to repeat the completed
reference, KS/PB/GEO or HD calculations.

## Source and policy actually read

Read live AGENTS from
`cosmosapjw-quantum/rei_bianchi`, branch
`research/orchestration-sandbox-20261022`, after an initial `main/AGENTS.md`
lookup returned 404. Its tier separation, existing-checkout, typed identity,
scientific-integrity and execution-transition rules apply. Read the prior
native-reference HANDOFF_KO and the existing vendor C/Python atom and history
adapter sources. The parent supplied shared HEAD
`7de02b3e05705ead4eeb313c8487a21d4e6876a6` and new local unit budget 600 CPU
seconds, including source/theory 120, implementation 300, review 120 and
packaging 60. Previous budgets are preserved.

The recovered original archive became available during this read. Its local
SHA256 is `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`,
matching the existing original-source lock. Sources below are under
`inputs/original/HyRec/` in this new unit. Read their relevant source sections;
the original history.c supersedes any assumption inferred from the older
single-face Python wrapper.

| Source | SHA256 | Relevant role |
|---|---|---|
| history.c | 8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976 | cosmology, thermal closures, stage updates, history driver |
| history.h | 99c590758874ecbe80e83b218660863c6aa43786175f64d483267c78b209d710 | state parameters and function signatures |
| hyrec_params.h | cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2 | phase thresholds, native step and table selection |
| hyrec.c | 22d094f86e005ad567614d212055df2764c8b624da10cc902ef912840de47681 | allocation, original main, output interpolation |
| input.dat | f8073ba70197378e156a6723e229ff47cc9f0d8be0121f1fce82aff6c64abcbc | original native cosmology |
| hydrogen.c | 421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b | actual QSS closure, causal radiation, H derivative |
| helium.c | 1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece | helium source dependency; function use read through history.c |

Original hydrogen.c is identical to the vendor source already reviewed in
R6. The original archive input has T0=2.728, obh2=.021976, omh2=.13, okh2=0,
odeh2=.343, w0=-1, wa=0, Y=.24, Nnueff=3.04; fsR=meR=1 are assigned in the
active reader. The final two `1.` tokens are not active additional inputs
while the optional reader statements remain commented out.

The current checkout was observed on `research/rec-source-synthesis-20261027`,
local HEAD `eb3b390eb59a4c48b5aa2d3bec928465b9c35f2e`, with existing dirty and
untracked work. No checkout, clone, worktree, reset or prior-file edit occurred.

## 1. Exact evolution and closure structure

### Native clock, prescribed background and model phases

The original source uses DLNA=8.49e-5 and
`z_i=(1+ZSTART)*exp(-DLNA*i)-1`, ZSTART=8000. H(z) is prescribed from the
native cosmological density terms, and nH=nH0*(1+z)^3 with cgs conversion at
hydrogen calls. H is therefore an exported background operand, not an
independent evolved variable. TR is kN*T0*(1+z) in hydrogen's eV units, with
kN=8.617343e-5; source rescaling conventions remain unchanged.

`rec_build_history` changes mathematical branch:

1. HeIII/HeII Saha initialization, Tm=Tr.
2. HeII recombination with hydrogen in Saha equilibrium and algebraic Tmss;
   early He post-Saha correction then the native multistep update.
3. Simultaneous H/He recombination, algebraic Tmss, possible H post-Saha
   correction, until the helium threshold.
4. Hydrogen-only evolution, algebraic Tmss until DLNT_MAX.
5. Hydrogen plus differential Tm evolution; radiative transfer eventually
   changes from FULL to EMLA2s2p when the native nzrt criterion is met.
6. Low-temperature/table-limit continuation with the Peebles model.

The actual 313 source cells must receive observed branch labels; their phase
must not be assigned merely from an approximate redshift expectation.

### Actual native multistep recurrence

For a non-post-Saha evolving scalar, the implemented recurrence is

\[
 X_{n+1}=X_n+h\left(\frac54 F_n-\frac14 F_{n-2}\right),\qquad h=\mathrm{DLNA}.
\]

The source shifts `prev2=prev; prev=current` after using `prev2`. This is a
second-order formula using n and n-2; it is not ordinary AB2 using n and n-1.
For the neutral-hydrogen coordinate xH1s the same ionization derivative is
subtracted. Hydrogen-only xe and differential Tm are updated with the plus
sign. Some derivative memories are initialized from centered finite
differences of preceding native arrays, rather than a fresh RHS evaluation.
Post-Saha steps instead apply their explicitly coded algebraic correction.

The code is fixed-step and exposes no adaptive accepted-step/dense-output
object. “Committed native node” is an appropriate data label; “certified dense
accepted ODE segment” would assert information this source does not provide.

### Temperature closure

Before the thermal switch, the source uses

\[
 T_m=\frac{T_r}{1+H(1+x_e+f_{\rm He})/(C T_r^4 x_e)},
\]

where native C includes fsR/meR scaling. This is an algebraic steady-state
closure. After the switch the native differential expression is

\[
 T_m'=-2T_m+\frac{C T_r^4x_e}{H(1+x_e+f_{\rm He})}(T_r-T_m),
\]

with an explicit near-equality branch returning -Tr when
`Tr/Tm-1 < 1e-10`. Using this differential expression to assign a defect to
the earlier algebraically constrained thermal path requires a declared model
choice/discrepancy term; source export does not make the two closures equal.

### Hydrogen and photon algebraic closure

Each `rec_HMLA_2photon_dxHIIdlna` call performs:

\[
 u_n=\mathcal P_n(Y_{<n}),\quad
 M(\theta_n)v_n=s(\theta_n,u_n),\quad
 Y_n=Q(\theta_n,v_n,u_n),\quad F_{H,n}=R_H(\theta_n,v_n).
\]

Here theta contains the actual thermodynamic/background arguments, u has
311 virtual plus 2 incoming Lyman departures, and v contains 2 real and 311
virtual algebraic departure populations. The solve uses an 80-bin
tridiagonal diffusion block, diagonal divisions elsewhere and a 2-by-2 Schur
complement. It is not evolution of 313 independent population ODEs.

The returned scalar derivative is the recombination rate divided by H,
with x1s=1-xHII. Radiation outputs are algebraic escape updates, three
outgoing Lyman departures and average virtual departures. The call mutates
history slot iz as well as returning its scalar derivative. The Python
`full_2012_atomic_source.py` explicitly implements an uncommitted single-face
candidate and does not implement the coupled time history.

## 2. The central instrumentation issue: call ownership

`rec_xH1s_postSaha` calls the same mutating hydrogen source at Saha and
perturbed ±Dxe trial states at a future output index. Consequently a photon
slot can be written several times before its final physical-input call.
Moreover, two mutating calls appear as operands of a subtraction: C does not
provide a general left-before-right evaluation guarantee for those operands.
Source-text order is not sufficient evidence of the observed final writer.

The minimum useful export must distinguish a sequential call ID, actual
native input state and index, phase/post-Saha role, returned derivative and
slot written. Link each final stored radiation slot to its actual final
writer; where it is overwritten by the later input-state closure call, record
that relation. Do not label every transient write a committed node.

The diagnostic must observe the existing expression order and state changes,
not restructure the calls to impose a desired ordering. A new call added only
to obtain a derivative can itself mutate history and would change the native
run. Hooks should expose values already computed. Full matrices need not be
stored per step: state, existing returned rates, algebraic populations and
sparse closure diagnostics are much smaller useful operands.

Capture both public Tm in K and the actual TM/TR passed into the native
closure. `rec_HMLA_2photon_dxHIIdlna` recomputes TM as `(TM/TR)*rescaled_TR`;
even fsR=meR=1 does not justify dropping its binary64 operation-order identity.

## 3. Constructive finite-path theorem

Fix source constants, tables, compiler/arithmetic convention, cosmological
input, phase predicates and initial data. Augment the recorded state by the
derivative memories, phase flags and causal history prefix. Each native
iteration is then a finite transition on that augmented state, with the
actual ordered call trace providing the association to its algebraic
radiation writes. Causal interpolation reads the strict prefix prescribed by
`interp_Dfnu`; thermal-prefix branches return zero departure.

Thus a single observed trace can supply a reproducible sequence of
thermodynamic nodes, source evaluations and final radiation slots. On a fixed
non-post-Saha step, exact real interpretation of the represented exported
scalars defines the discrete recurrence residual

\[
 r_n^{\rm disc}=X_{n+1}-X_n-h(5F_n-F_{n-2})/4.
\]

Its arithmetic size diagnoses the represented recurrence. It is not the
continuous defect `Xhat'-F(eta,Xhat)`, and it contains no truncation-error or
model-error certificate. A small algebraic residual `Mv-s` similarly concerns
the instantaneous solve; turning it into a state-error radius needs a bound
on the appropriate inverse on the declared domain.

For any two exported nodes assigned to the existing H5 geometric endpoints
a<b, define the represented segment

\[
 \widehat\theta(t)=(1-\alpha(t))\theta_L+\alpha(t)\theta_R,
 \qquad \alpha(t)=(t-a)/(b-a).
\]

This is an explicit continuous reconstruction, absolutely continuous on a
finite partition, with exact a.e. derivative
`(theta_R-theta_L)/(b-a)`. Positivity of both endpoint values proves
positivity of that reconstructed scalar; component bounds are endpoint
min/max. These useful mathematical facts concern the represented path.
They do not certify proximity to the physical solution. Artificial zero
within-cell second derivatives cannot replace a bound on physical curvature;
derivative jumps at adjoining knots also matter for global regularity.

## 4. Concrete subsequent closure-derivative lemma

On a chosen interval where closure/table/escape/stencil branches are smooth,
let theta(t), u(t) be C2 and suppose M(t) is invertible throughout. The unique
algebraic closure v=M^{-1}s obeys

\[
 v'=M^{-1}(s'-M'v),\qquad
 v''=M^{-1}(s''-M''v-2M'v').
\]

Proof: differentiate Mv=s once and twice and solve the resulting linear
systems. For the algebraic output Q(t,v(t)),

\[
 Y''=Q_{tt}+2Q_{tv}v'+Q_{vv}[v',v']+Q_vv''.
\]

Here partial t derivatives include the declared theta/u dependence. This
supplies an actual route to a curvature enclosure using uniform inverse,
coefficient and reconstructed-input derivative bounds; it does not reinterpret
QSS populations as independently evolved ODE coordinates.

For an ideal source characteristic with fixed energies,
q(t)=t-ln(Es/Et), the represented incoming history is affine on every region
with fixed source stencil. There its slope is the exported endpoint secant
and its second derivative is zero. Pullback knot crossings, rate-table knots,
escape thresholds and model switches must partition that smooth calculation.
This continuous ideal characteristic is a declared extension; floating-point
native query evaluation is recorded separately. Physical self-consistency
would additionally require the coupled delayed radiation relation rather
than treating the stored prefix as an error-free external history.

## 5. Minimum finite input packet and acceptance boundary

The executable packet can contain the following without claiming the absent
physical certificate:

- Original source/table/input identities, exact build flags, compiler/runtime
  and native phase thresholds; original archive and 313 context locks.
- Native global index, radiative local index, native z, eta_z=-log(1+z),
  stored geometric eta and the deterministic clock discrepancy.
- Committed thermodynamic nodes: xe, xHII/xH1s, helium variable when active,
  Tm_K, source TM/TR, H and nH with explicit units and phase validity.
- Source-call records with true inputs, returned native derivatives,
  derivative-memory operands and post-Saha/trial role; final slot ownership.
- Actual algebraic real/virtual populations and radiation outputs where
  available from existing computations, plus compact pointwise solve
  diagnostics whose interpretation remains instantaneous.
- A 313-row join preserving source index, original stored endpoints/query,
  exact alpha, old samples and old anchor; pointers to thermodynamic/path
  records needed by each cell. Record agreement or difference with old
  radiation values using a predeclared numerical identity criterion.
- Explicit piecewise reconstruction formulas and their represented slopes,
  ranges and knot/phase partition. Record the derivative provenance as
  native RHS, initialization finite difference, secant, or algebraic closure;
  these labels are not interchangeable.

Do not equate the stored geometric eta to the exact logarithm of rounded
native z. The physical clock remains eta=-ln(1+z), but old H5 cells are exact
real interpretations of their recorded endpoint scalars. Their index join
and any coordinate discrepancy must stay explicit; no physical retiming
error follows just from knowing that discrepancy.

All-state norm/scales, physical initial error, model discrepancy,
whole-domain differential defect and stability, uniform open tube and
bootstrap, physical endpoint errors/curvature, physical epsilon and outgoing
bound remain separate obligations. Scope can advance to **actual native path
and algebraic closure operands acquired and mapped**, while physical bound
coverage remains 0/313. H6/H7 remain OPEN, L4/REI activation false.

## Next executable transition

Parent can freeze a finite instrumented acquisition contract around the
original driver with call/slot ownership and clock/phase labels, then release
one bounded lower-tier run. Existing completed reference outputs are reused.
The next independent review should compare the instrumentation diff with
the original update expressions and inspect the actual path/ownership and
source-agreement records. It should admit exactly the observed trace and
declared reconstruction scope, then leave the closure-derivative lemma's
uniform bounds as explicit subsequent work.
