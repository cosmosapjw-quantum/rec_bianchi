# R3O independent PHYS-MATH / R6 audit

Date: 2026-10-19 UTC. Role: new independent reviewer, neither frontier implementer.
Scope: the h2 low-redshift continuation and the independent h4 primordial start,
their original-C harnesses, restart mathematics and retained short-run evidence.
The requested `physmath-research-loop` canonical built-in protocol 1.0.0 was read
and applied to this R6 assignment. No implementation file was modified.

## Decision and ranked findings

**R6_COMPLETE_WITH_ONE_P2_OPEN. C9 code audit can proceed.**

No P0 or P1 equation, source-stage, grid, seed-ownership or physical-domain
mismatch was found in the reviewed bounded paths. The original equations and
the retained h2 16-step / h4 8-step comparisons support a scoped implementation
review. The following P2 must be resolved before claiming that every supported
low-z checkpoint restart produces the final z=0 interpolation.

### R6-P2-01 — a terminal restart reports the cubic-stencil stop without its stencil

- **Location:** `src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py`,
  `continue_refined_low_z`, lines 248–250, 301–317; checkpoint emission at
  lines 252–256. Relevant caller: `scripts/verify_r3o_lowz.py`, lines 485–489.
- **Observed contract mismatch:** the module accepts a checkpoint at any input
  index through `END_IZ-1`. It starts its state list with only that checkpoint.
  If one or two steps remain, it reaches `END_IZ=211716` and returns
  `STOP_AT_SOURCE_Z0_CUBIC_STENCIL`, while `z0` is `None` because fewer than four
  states are present. The checkpoint callback records a `state_tail`, but the
  restart function has no input that consumes the retained tail.
- **Independent reproduction:** a controlled Peebles fixture, with finite
  positive state and valid event metadata, produced the following actual results.
  These are six controlled terminal steps, not a physical late-time trajectory.

| Restart input | New steps | Returned state count | Returned status | `z0` |
|---:|---:|---:|---|---|
| 211715 | 1 | 2 | `STOP_AT_SOURCE_Z0_CUBIC_STENCIL` | `None` |
| 211714 | 2 | 3 | `STOP_AT_SOURCE_Z0_CUBIC_STENCIL` | `None` |
| 211713 | 3 | 4 | `STOP_AT_SOURCE_Z0_CUBIC_STENCIL` | Present |

- **Impact:** state/RHS memory is sufficient for the next ODE step, but it is
  insufficient for the four-point terminal observable. A late restart can
  therefore advertise the stencil stop without delivering the stencil. The
  retained 16-step smoke is unaffected. The current uninterrupted `--mode full`
  starts at 58389, retains the complete local history, and additionally rejects a
  missing `z0`; this finding does not demonstrate failure of that uninterrupted
  path. Automatic CLI resume is already explicitly unimplemented.
- **Minimum correction:** either accept and validate the saved, contiguous
  terminal state tail and perform the real four-point interpolation, or return
  a distinct incomplete-stencil status when it is unavailable. Do not invent
  missing values or reconstruct them from only RHS memory. No broad new resume
  feature is required to correct the status contract.
- **Closure evidence:** retain one-, two- and three-step terminal restart cases;
  require either an explicitly incomplete result or the correct original cubic
  evaluated on actual retained states. Keep the ordinary bounded-smoke status
  and uninterrupted end contract unchanged.

## Authoritative source and review identity

Repository/capsule root:
`/workspace/scratch/afe554957b2e/rec_work`.
Parent handoff HEAD used by this implementation:
`23e0a3a6c439a1f015aa8f7380f4eedf0b569df7`.
This review does not claim a new Git commit or a genuine local Git checkout.

The authoritative archive was opened directly:
`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, 726,954 bytes,
SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

Primary source locations read from that ZIP:

| Reference | Original member and location | Audited obligation |
|---|---|---|
| O1 | `HyRec/history.c`, 37–69 | Derived grid, `izH0`, `nz`, RT end |
| O2 | `HyRec/history.c`, 250–317 | Steady thermal closure, thermal branch, He predictor |
| O3 | `HyRec/history.c`, 326–408 | H post-Saha correction, input-time RHS and H/He memory |
| O4 | `HyRec/history.c`, 458–484 | H+Tm step, internal FULL→EMLA switch, both RHS tails |
| O5 | `HyRec/history.c`, 508–596 | Primordial closures, initial seeds, input-state outer guards |
| O6 | `HyRec/helium.c`, 29–171 | Saha roots and He recombination operator |
| O7 | `HyRec/hydrogen.c`, 65–104, 142–262 | Peebles Fudge=1, table domain, EMLA rates |
| O8 | `HyRec/hydrogen.c`, 316–347, 633–716 | Spectral step constraint and causal two-neighbor interpolation |
| O9 | `HyRec/hyrectools.c`, 117–145 | Source four-point end-clamped interpolation |

The active definitions in `HyRec/hyrec_params.h`, Lyman energies in
`HyRec/hydrogen.h`, and all 311 energies in `HyRec/two_photon_tables.dat` were
also read. Both run manifests' original-member hashes were independently
recomputed from the authoritative ZIP and matched. Their only changed compiled
member is `hyrec_params.h`, with the h2 or h4 `DLNA` token substitution.

Reviewed implementation SHA256 values:

| File | SHA256 |
|---|---|
| `src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py` | `484d8822b1cf4b607d47c196571f7bdbee7eabfad7bc77489d6befdd8106294b` |
| `src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py` | `6247e0681d74e5b6f26f9818faf4a49af4ce61e64e4970bfe3b7c21ad951fd10` |
| `scripts/verify_r3o_lowz.py` | `192f6ba070f35d7cede83fc03a96757064844f517f9b6c5910c2d7d305ddb193` |
| `scripts/verify_r3o_h4_start.py` | `96e03f326342940606dba33dd44d8f172d5bb6a773dc15f404635babca6f4deb` |
| `scripts/c_harness/original_hyrec_r3o_lowz_harness.c` | `d179b07d33562557924f763b85a58f5a2cec48ec2a78c4ab39a6702d82e88756` |
| `scripts/c_harness/original_hyrec_r3o_h4_start_harness.c` | `8b50858c0e0a3d1e6eef19e9f159673156162f70a7363b51945a9f238aa2ec8a` |

Every dependency listed in the two retained verification receipts matched its
current source hash at review intake. Source-local scalar functions, thermal
and Peebles dependencies, the causal photon routine and the shared C wrapper
were actually read where used; their unchanged status is not inferred from
implementer summaries alone.

## 1. Restart memory: what is sufficient, and why

Use `n` for the global accepted input state and `h` for its own grid spacing.
The inherited R3N result and direct original-source inspection give

\[
y_{n+1}=y_n+h\left(\frac54F_n-\frac14F_{n-2}\right).
\]

At state `n`, `prev=F[n-1]` and `prev2=F[n-2]`. The step consumes `prev2`,
then rotates `(prev2,prev)` to `(prev,F[n])`. Therefore the low-z augmented
state `(n, xe, Tm, Hprev, Hprev2, Tprev, Tprev2, stage-event)` is sufficient
for forward stepping under the fixed cosmology and operators. Neither a
reset of these derivatives nor reevaluation of old derivatives with the new
stage operator implements the original recurrence. O4 and O5 carry both
tails across FULL→EMLA and EMLA→Peebles without reseeding.

The Python boundary loader takes the final two Python U6 input-RHS records;
its C boundary parser takes the final two native `STEP` records separately
(`primordial_2012_refined_low_z.py`, 131–168, 191–213). The update at
283–288 and C harness call at 100–107 implement the required rotation.
An absorbing Peebles event is part of restart state: without it, a current
guard that becomes true again could incorrectly reenter an outer loop that
the original source has already left.

For an affine post-restart source `F(y)=Ly+b`, suppose the accepted state is
unchanged and only the two stored derivatives are perturbed by
`delta F[n-2]`, `delta F[n-1]`. Direct subtraction yields

\[
e_1=-\frac h4\delta F_{n-2},\qquad
e_2=\left(I+\frac{5h}{4}L\right)e_1-\frac h4\delta F_{n-1}.
\]

For a time-dependent affine source, use `L[n+1]` in the second expression.
This is an exact two-step identity on a fixed branch. An independent
`fractions.Fraction` calculation with `h=1/100`, `L=-3`, `b=2`,
`y=1/4`, previous derivatives `5/7,4/9`, and perturbations `1/11,-2/13`
gave `e1=-1/4400`, `e2=69/416000`, exactly equal to direct recurrence
subtraction. Thus omitting either stored derivative has a specific first-
or second-step effect even when the restarted state itself is exact.

For the h4 FULL path, an RHS tail alone is not sufficient: the source also
depends on accepted radiative history. The returned endpoint carries H/He
state, `post_saha`, both H/He RHS tails and accepted virtual/Lyman prefixes.
At endpoint 72900 the final two memory columns belong to inputs 72898 and
72899. Direct inspection of `python_h4_full_start.npz` confirms that
`final_predictor` equals the last two H/He RHS array entries, in order.
The four-state terminal output requirement is separate and causes R6-P2-01.

## 2. Input-time guards, floor indexing and source output endpoint

In O5, the loop variable `iz` is the prospective output index; `z` and
`Tm_output[iz-1]` are the input state. O4's internal RT switch also receives
the input index. Consequently the first low-z input is 58389, after the
reviewed U6 has accepted that boundary without evaluating EMLA there.
The new Python code evaluates both table guards before each update and
records the event at the failing input, matching the source.

Let `H0=8.49e-5`, `h_l=H0/2^l`, and

\[
z_i=8001\exp(-h_l i)-1,\qquad
i_{H0}=\left\lfloor1+\frac{\log(k_BT_0\,8001/(f_s^2m_rT_{R,\max}))}{h_l}\right\rfloor,
\]
\[
N_z=\left\lfloor2+\frac{\log8001}{h_l}\right\rfloor.
\]

Here the source temperatures in the `izH0` expression are in eV,
`T_R,max=0.4`, `T0=2.7255 K`, `f_s=m_r=1`. Independent evaluation produced:

| Grid | Step | Raw start index before `floor(1+x)` | `izH0` | `Nz` | Last output index | First `TR_MIN`-false input, if ratio guard remains true |
|---|---:|---:|---:|---:|---:|---:|
| h | 8.49e-5 | 18222.80068054458 | 18223 | 105859 | 105858 | 72466 |
| h2 | 4.245e-5 | 36445.60136108916 | 36446 | 211717 | 211716 | 144931 |
| h4 | 2.1225e-5 | 72891.20272217832 | 72892 | 423432 | 423431 | 289861 |

The h4 class computes the floor expression using its own `DLNA`; it does not
copy a multiplied checkpoint index (`primordial_2012_quarter_start.py`,
45–63). The exact integer multiples at this particular `izH0` are a property
of these parameters, not a general event-index mapping. In particular the
table-exit indices and final output indices are not all obtained by scaling
the original-h integers.

For h2 the literal left-to-right `TR_MIN` guard gives:

| Input index | z | Rescaled Tr in eV | Temperature guard |
|---:|---:|---:|---|
| 144930 | 16.031137951546718 | 0.004000029855176720 | True |
| 144931 | 16.030414995085543 | 0.003999860057513351 | False |
| 144932 | 16.029692069313200 | 0.003999690267057735 | False |

Thus the controlled sequence is EMLA on 144930→144931 and Peebles on
144931→144932. A physical h2 trajectory can encounter the `Tm/Tr > 0.1`
condition earlier; this review does not choose its unexecuted event index.
`source_stage_guard` 96–105 and the absorbing selection 268–279 match O5.

The h2 final state has `z=-2.238689928646398e-5`; the final RHS input has
`z=2.0063051384022756e-5`. O1 and O9 intentionally need that last, slightly
negative-z output to interpolate at zero. It is not a new negative-z RHS
evaluation. The correct final stencil is 211713–211716; its clamped fraction
lies between 1 and 2 and must not be clipped to an interior-cell fraction.
The standalone cubic formula and native call match O9. A full uninterrupted
low-z lane would require 153327 steps from 58389; none was run by this audit.

## 3. Independent primordial He closures and causal photon prefix

The h4 module reuses only unchanged scalar formulas from the h2 module;
those formulas contain no time-step clock. Its own loops generate every
primordial state using `QuarterStartCosmology.redshift` and h4 finite
differences. Its CLI has no checkpoint input, and its independent native
trajectory rebuilds its own He history (`original_hyrec_r3o_h4_start_harness.c`,
55–83). C trajectory states are not assigned to Python evolution variables.

The source closures are preserved:

- HeIII Saha uses `xe=1+fHe+xHeIII`, with fully ionized H and
  `xHeII+xHeIII=fHe`, until the source `xHeIII <= 1e-8` exit.
- HeII evolution initializes from the original He Saha root, closes neutral
  H with `rec_saha_xH1s`, uses original helium post-Saha/predictor updates,
  and takes the steady matter-temperature closure. The neglected residual
  HeIII at this source transition is the original closure.
- At the FULL boundary, the hydrogen derivative seeds are centered finite
  differences of the independently generated h4 electron history minus
  the correctly indexed He derivatives. Output row `i` stores the derivative
  evaluated at input `i-1`. At 72892, He columns are rows 72891 and 72892,
  owning inputs 72890 and 72891; the H differences are centered at those
  same inputs (`source_native_derivative_seeds`, 167–184; O5).
- H/He post-Saha uses the multiplicative output clock inside the correction,
  and the absolute source grid for accepted output states. Its finite
  differences remain the original `z±0.5` and one-percent abundance probes;
  h4 refines time, not those closure prescriptions.

For photon transport, O8 returns zero incoming distortion for local indices
0 or 1, or emission before the source history. Later it requires emission
strictly before the last accepted time and interpolates two accepted
neighbors. The h4 implementation explicitly uses `dlna=h4`, `shear_q=0`,
and past columns only (278–291). It commits one current-input photon column
per accepted step (337–346); post-Saha trial columns are not committed.
The native harness also clears its trial column before the next step
(116–118). The shared C callback receives detached past arrays; its `z0(c)`
uses the supplied h4 cosmology.

Independently reading the 311 source energies and the three original Lyman
energies gives 313 adjacent transport links and

\[
\min\log(E_s/E_f)=8.49527887747085\times10^{-5}
                 =4.002487103637621\,h_4>h_4.
\]

The strict causal spacing is therefore satisfied for this bounded h4 start.
At accepted endpoint 72900 the stored photon arrays have shapes `[311,8]`,
`[311,8]`, `[3,8]`. The first and third are sufficient outgoing histories for
the next FULL source evaluation; the average spectrum remains diagnostic.

## 4. Physical domain and thermal stability qualification

Abundances are per H nucleus; public temperatures are K; the Hubble rate is
in inverse seconds. The original hydrogen operator consumes density in
cm^-3 and temperatures in eV, with the `1e-6` conversion from m^-3 and
original Boltzmann constant preserved. The new low-z stage fixes helium
neutral, uses original EMLA inside its table domain, and then original
Peebles with Fudge=1. It performs no photon source evaluation after the RT
boundary. Its fixed-cosmology validation and positive finite state checks
are compatible with the requested q=0, no-reionization domain.

For h4, FULL atomic source checks remain in use. The exact `Tm=Tr` closure
case receives the pre-existing one-ULP downward representation before the
rate-table conversion (295–296), and the common-input C comparison receives
that same input. This is explicit floating-point boundary handling, not an
independent change to the physical post-Saha closure; the independent native
trajectory still uses the original C closure. The bounded parity result is
the appropriate numerical evidence for this representation choice.

The original thermal RHS in O2 is piecewise:

\[
F_T=\begin{cases}
-T_r,&T_r/T_m-1<10^{-10},\\
-2T_m+A(T_r-T_m),&\text{otherwise},
\end{cases}\qquad
A=\frac{f_s^2}{m_r^3}\,
  \frac{4.91466895548409\times10^{-22}\,T_r^4}{H}
  \frac{x_e}{1+x_e+f_{He}}\ge0.
\]

With `Tr, xe, H` frozen, only the second branch has `lambda=-2-A`.
The first branch has zero derivative with respect to `Tm` at fixed `Tr`;
the switch is not globally affine. The established scalar strict-decay
condition `-2<h*lambda<0` would imply `h(2+A)<2` on the second frozen branch.
It does not prove stability of the evolving coupled H+Tm system or across
the branch switch. `source_thermal_rhs` uses the literal original branch
(86–93), rather than the generic always-Compton source adapter.

The parent R3N conditional second-order and scalar stability results are
reused. The short same-h comparisons do not establish a global temporal
order across stage changes, photon-history interpolation, or fixed
post-Saha closure errors. No new impossibility/no-go result is asserted.

## 5. Actual evidence inspected and new audit execution

These are inspected implementer executions; they are not new production
runs by this reviewer.

| Retained result | Directly inspected evidence | Scoped result |
|---|---|---|
| h2 low-z | `rec_recovery/r3o_lowz_smoke_001/verification.json` and all 16 `accepted_pairs.jsonl` records | Inputs 58389–58404, outputs through 58405; EMLA only; `SMOKE_PASS_SAME_H_PENDING_REVIEW` |
| h4 start | `rec_recovery/r3o_h4_runs/start_002/verification.json`, NPZ files, original-C `native_oracle.stdout` | 72893 He rows, 8 FULL steps, 9 nodes, 9 memory rows; `PASS_SAME_H_START` |

Verification receipt SHA256:

- h2: `3f509eb19c97f95352036034f81f153306d41f813afe41d68ef3cee684ab21bc`.
- h4: `6291598aae822e08be8c572437cbe04564b498b9e4c84279876dc7f82c66534e`.

The actual h4 full-start NPZ is 43,904 bytes and hashes to
`40dd109a4c4acfcc46087353840d2e694d0a14b928e7b622d5c2baaecf5b6fef`;
its independent He NPZ is 2,680,322 bytes and hashes to
`0b4e1911cb32c40f3bec6cefbc0c138ec635d4d25f2a0a6e504c812718529f93`.
Both matched their receipts on direct read. The native output whole-file
hash also matched, and its counted records were `HE=72893`, `STEP=8`,
`V=2488`, `A=2488`, `L=24`, `MEM=9`, `META=NODE=DONE=1`.

Retained numerical comparisons read from the receipts:

| Quantity | Observed bound |
|---|---:|
| h2 scaled xe discrepancy | 7.434376394267938e-14 |
| h2 scaled Tm discrepancy | 2.49687949887451e-16 |
| h2 common-input H RHS discrepancy | 2.1707559781417694e-14 |
| h2 common-input thermal RHS discrepancy | 3.621030056849089e-14 |
| h4 He-history scaled xe discrepancy | 2.2080761383365098e-16 |
| h4 common-input FULL RHS discrepancy | 2.0511717324644962e-13 |
| h4 integrated H/xe/Tm discrepancy | Zero in retained binary64 states |
| h4 integrated absolute HeII discrepancy | 5.421010862427522e-20 |
| h4 maximum average-spectrum tolerance ratio | 7.883083461150054e-6 |
| h4 matrix residual | 2.8638673618951863e-16 |

The new audit calculation used Python with bytecode writes disabled, one
BLAS/OpenMP thread, and a 5-second hard CPU limit. It independently evaluated
the three floor grids, threshold neighbors, exact affine memory-error
identity, all source spectral gaps, and the six controlled terminal fixture
steps. It completed with exit code 0, process CPU **1.015703294 s**, wall
**0.994122062 s**. A separate bounded raw-evidence inspection used process
CPU **0.138511780 s** under a 2-second hard CPU limit. Combined measured
process CPU for these two new calculation/readback commands was
**1.154215074 s**, within the requested 5-second small-calculation allowance.
No new full production history, native trajectory or test-suite replay was run.

Minimal reproduction of R6-P2-01, with the controlled fixture explicitly
separate from physical evidence:

```python
from full_bianchi_hyrec.trajectory import primordial_2012_refined_low_z as m

class NoEmla:
    def hydrogen_rhs_ln_a(self, **kw):
        raise AssertionError("unexpected EMLA")

c = m.HyRec2012Cosmology()
for steps in (1, 2, 3):
    cp = m.LowZCheckpoint(
        m.END_IZ - steps, 1e-4, .05,
        0., 0., -.1, -.1, 144931, "TR_MIN",
    )
    result = m.continue_refined_low_z(cp, c, NoEmla(), max_steps=steps)
    print(steps, result["status"], result["z0"] is None)
```

## 6. Environment, preserved holds and handoff to C9

Two read-only `exec_command` invocations failed before process execution
because bubblewrap could not create its mount marker: `No space left on
device (os error 28)`, exit 101. A read-only capacity check confirmed the
32-GiB overlay at 100% use; this is an environment failure. No attempted
calculation is counted as passing from those failures. The reviewer removed
only its own 108,673-byte temporary ZIP-member copies after reading them.
The parent separately reported recovery by deleting obsolete extraction and
completed duplicate R3N readbacks, preserving verified raw inputs and code.
Subsequent bounded audit commands succeeded. Vigilode/Rust reuse intake is
parent-owned and does not change the scope of this R6 review.

The following states remain unchanged:

- Original U5 h `HOLD_9_FAIL`; h2 `HOLD_8_FAIL`.
- Historical budget `CLOSED_HOLD_NOT_RESET`.
- `REI_activation=false` / no Bianchi, REI or CMB admission.
- Full h2 low-z to the source z=0 stencil: **NOT_RUN**.
- Full h4 continuation and global physical h/h2/h4 convergence: **NOT_RUN**.
- New production speedup: no claim.

**C9 recommendation:** proceed with code/reliability audit on the above hashes
and carry R6-P2-01 as an open, localized contract finding. The equations,
input-stage ownership, independent h4 start and retained short same-h evidence
are sufficiently coherent for that audit. Closing P2 requires only the
specific terminal-restart behavior check described above, not repeating
completed U4/U5/U6 or the complete primordial start. Parent handles changes,
DAG publication, commit/push and remote preservation; this file itself
claims none of those publication actions.
