# REC-H5-NATIVE-REFERENCE01 — independent R6 review

Decision: **PASS** for the source-specific analytical construction in
`CONSTRUCTION_CANDIDATES.md`, SHA256
`dd7401ab7c189d7ce435047f99048ef5cc68b1db6f589a25d3ad255bc1603a9b`.
Reviewer: separately delegated theory reviewer, requested Astra tier; runtime
model identity not independently observable. Date: 2026-10-27.

This admission covers the analytical reference construction and its binding to
the immutable 313-query context. Numerical enclosure implementation and actual
producer output are subsequent coding/review obligations. Parent owns the final
R3/R5 freeze and stage publication. The targeted R3 clock clarification has
subsequently been read and F01 closed below. No solver, physical trajectory, matrix,
certificate, science producer or old primary run was executed by this reviewer.

## Method and original sources

Read the selected PhysMath Research Loop 1.0.0 skill, RESEARCH_POLICY,
THEORY_LOOP including R6, and EVIDENCE_AND_HANDOFF. Reviewed the construction
against the old H5 DERIVATION, SOURCE_CONTEXT and ACTUAL_BOUND_INPUTS; read the
original `hydrogen.h`, the relevant `hydrogen.c` interpolation/routing/outgoing
formulas, native wrapper equilibrium and temperature mappings, and the native
CSV metadata. Re-derived derivatives, stationary points, translation identity,
reference conversion and chord composition independently by substitution and
polynomial factorization. A bounded Python standard-library check used exact
`Fraction.from_float(float.fromhex(...))` arithmetic for the 313 metadata rows;
it did not evaluate the new scientific producer.

The exact check verified all 313 incoming indices and source routes, strict
cell containment, causal endpoint-prefix membership, geometric alpha,
`(q-a)(b-q)/2`, and the stored absolute anchor radius. Every check passed
313/313. Applied limits: 20 CPU seconds, one interpreter thread, 512 MiB address
space. Measured arithmetic/check CPU before source hashing: 0.012264343 seconds.
Subsequent source hashing and shell/source-reading overhead were not
separately measured. No CAS or external research service was used.

## Independent mathematical checks

1. **Reference and derivatives.** Put `x=E exp(eta)/(kN T0)>0`. The clock gives
   `dx/deta=x`, hence `w'=-xw`, `w''=(x²-x)w` and
   `w'''=(-x³+3x²-x)w`. Therefore `G_eta=xw` and
   `G_etaeta=-(x²-x)w`; the proposed signs are correct. `G_f=1`,
   `G_ff=G_etaf=0`. Units are dimensionless occupation per powers of the
   dimensionless logarithmic scale-factor clock. No proper-time derivative is
   substituted. Native `kN=8.617343e-5 eV/K` and positive source energies are
   appropriate; modern SI conversion would select different reference inputs.

2. **Finite extrema.** For `h(x)=(x²-x)e^-x`,
   `h'(x)=(-x²+3x-1)e^-x`. On a positive finite interval the only nonzero
   interior absolute extrema are `(3±sqrt(5))/2`; the cusp of `|h|` at `x=1`
   is zero and cannot enlarge a maximum. Endpoints cover singleton intervals.
   For `x e^-x`, its derivative has sole positive root 1. For an interval
   strictly above `(3+sqrt(5))/2`, both absolute derivative envelopes attain
   their maximum at the left endpoint. Conservative interval inclusion of
   critical points is required exactly as the construction states.

3. **Exact translation.** Substituting `yhat=fhat-w` into
   `F_y(eta,y)=F_f(eta,y+w)-w'` cancels both reference derivative terms and
   returns `fhat'-F_f(eta,fhat)`. Error differences are unchanged, as are a
   fixed norm, state Lipschitz bound and a translated equal-radius tube.
   These conclusions require the same exact reference and corresponding
   translated domain. They do not construct the physical F, defect, stability
   or bootstrap proof. For `|delta f|/s_f`, the scalar observable constant is
   `s_f`; the constant 1 applies to unscaled scalar occupation and cannot fill
   a full-state K field.

4. **Characteristic and temperature split.** At
   `q_ideal=-ln((1+z)Es/Et)`, substitution gives
   `x_s(q_ideal)=Et/[kN T0(1+z)]=x_t`. Thus
   `B_char=e^-x_t expm1(-x_t expm1(delta_q))` has sign opposite to
   nonzero `delta_q`. The independent native temperature is the exact real
   represented by the CSV binary64 value. Consequently
   `B_TR=e^-x_t-exp(-Et/TRhat)` and
   `B_total=w_s(qhat)-exp(-Et/TRhat)` have the proposed signs and telescope
   exactly. There is no basis to treat either deterministic conversion as
   physical temperature uncertainty or physical occupation retiming error.

5. **Chord and anchor.** For the frozen geometric cell and exact rational
   alpha, the interpolation remainder gives
   `|Iw-w(q)| <= M2_ref (q-a)(b-q)/2`. Above `x=1`, convexity gives
   `J_ref=Iw-w(q)>=0`. Independently expand the direct difference:
   `uhat+w_native-I(y+w)=(uhat-Iy)+(w_native-Iw)`.
   Using `Iw=w(q)+J_ref` and `w(q)=w_native+B_total` yields exactly
   `r_anchor-J_ref-B_total`. The proposed radius follows by one application of
   the triangle inequality. The anchor already accounts for native versus
   geometric interpolation and represented arithmetic; adding it again as a
   separate endpoint/query term would double count. The candidate does not do
   so. The optional lower bound `min(yL,yR)+w(b)` is valid for this represented
   reconstruction because alpha is a positive partition and w decreases.

## Source and clock mapping checks

`hydrogen.c:633–652` returns direct linear interpolation of signed departures;
its thermal-prefix and strict causal support branches agree with the context.
`hydrogen.c:667–718` uses the next virtual bin except at the Lyman boundaries.
The context routes `139→311`, `270→312`, `310→313`, `311→140`, and `312→271`,
and `i→i+1` for other incoming virtual bins. These agree with the source
meaning: outgoing Lyman alpha/beta/gamma indices 311/312/313, but incoming
Lyman alpha/beta indices 311/312 with target energies E21/E31.

`hydrogen.h:29–37` supplies E21, E31, E41 and the native Boltzmann constant.
`full_2012_atomic_source.py:247–248` supplies the native radiation/matter
temperature conversion. `original_hyrec_native.py:378–384` uses the Wien
equilibrium and a factor three only for its line-centre population coordinate.
`hydrogen.c:794–796` confirms the outgoing Lyman departure formulas. No extra
population degeneracy or exponential interpolation factor belongs in the
photon reference or stored departure interpolation.

The native CSV identifies `z=1099.9986525171403`, `iz_local=5127` and
`TR_eV_rescaled=0.25882399309326415`. Its TR is kept distinct from the exact
real product of represented kN, T0 and `(1+z)`. The stored endpoint hex values
are the primary H5 geometric clock. Their bridge must not be described as
using an exact real arithmetic native grid instead.

## Finding and remaining implementation obligations

**F01, editorial clock identity (closed).** At initial review time README
R1 says “existing native-real causal grid”, whereas construction section 6 and
the parent-selected implementation target use immutable H5 stored geometric
endpoints. Impact: a reader could infer a different interpolation alpha and
anchor definition. Smallest fix: clarify in R3/README that the primary cells
are the exact reals represented by SOURCE_CONTEXT endpoint hex values; a
native-real-grid comparison is separate. The subsequently read R3 `FROZEN_CONTRACT.md`, section “Primary clock and
source locks”, explicitly selects stored geometric endpoints/query and exact
rational alpha. The corrected README R1 matches this selection and labels the
predecessor native-real grid separately. F01 is closed by this targeted read;
the analytical candidate itself needs no change. Previous candidate SHA,
checks and budget are preserved. No numerical replay or new analytical review
campaign was performed; implementation review remains a C9 obligation.

No mathematical/source-binding revision was identified. The numerical code
must still demonstrate outward enclosures of conversions and every arithmetic
operation, correctly rounded elementary-function contracts, conservative
critical-point inclusion, independent high-precision point agreement, and
the stated analytic controls. These are code admission obligations, not claims
of an already performed numerical check.

Physical full-state K, F, d, L, initial error, tube, total physical M2 and H5
epsilon remain null; physical coverage remains 0/313. HISTORY02's generic
reference adapter and derivative reasoning are reusable prior work; this
unit's contribution is the actual source-specific 313-cell application and
partial producer. No general novelty or strong no-go result is admitted.

Source byte identities and scoped check records are in `REVIEW_R6.json`.
