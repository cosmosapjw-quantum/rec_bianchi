# REC → REI F08 S0 | Original-native Thomson source and Stokes polarization

2026-11-15 KST. Research-only physics, no production admission.

## Exact original source and actual Rust experiment

Parent REC #198 HEAD fa5c484405e901992501ab01795079ed8f2bdee1.
BASS #328 source HEAD b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6.
Original REI F08 S0 input pair SHA256:
0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8.
Original 640 native gas+photon source SHA256:
75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843.

Recovered real BASS 106-file source archive from 2026-11-03 cold
backup (inner SHA256 dc48688e734838a0933fabe97025d7c354ccd972a03ecb8ca6e33be5460e0673).
Original immutable source locks 12/12 S0, 51/51 Rust, 4/4 photon.
Compiled unmodified original Rust offline, ran 4 true original cases:
BI/FLRW times characteristic-energy/fixed-hat; 160 consecutive original
proper source steps each. Actual original Rust result 640 rows is
BYTE EXACT the historical BASS source SHA above.
Recorded each original post-absorption per-direction photon survivor
number and energy on all 128 original rays, 81,920 genuine
physical stage/ray records. SHA256
70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1.

## New single-Thomson-collision operator

Metric (-,+,+,+), c=29979245800 cm/s,
sigmaT=6.6524587051e-25 cm2, proper dt=6.25e8 s,
n_H0=1e-4 cm^-3, fHe=0.083, native source electron fraction
xe=xHII+fHe*(xHeII+2*xHeIII) and Gamma=c sigmaT ne.
Scattering event probability p=-expm1(-Gamma dt) ~1.28e-9
at each ACTUAL original source stage, post photoabsorption.
No source/worker mutation, no original gas feedback.

Original 128 q midpoint sky has mean(q_z²)=21/64 !=1/3,
mean(q_z^4)=777/4096. Naive original equal-area Thomson spin
quadrature induces 0.0057571049986292816 (0.5757%) spurious
polarization for perfectly isotropic incoming light.
Use strictly positive quadrupole moment exact weights
w_i=[1+(4/63)(q_zi²-21/64)]/128;
sum(w)=1, sum(w q^a q^b)=delta_ab/3.
Original photon ray masses are SOURCE PRESERVED. For THIS optional
collision measurement they are projected to corrected angular weights
with global photon-number and energy totals conserved exactly.
Projection per-ray photon L1 change relative to source total ~1.5873%.
Physical source angle-phase K_ij=3/4 w_i (1+(qi.qj)^2) is positive,
column stochastic, and K*w=w. Compute elastic source
deltaN_i=p[(K N_projected)_i-N_projected_i], likewise energy,
and tangent-plane generated Stokes Q/U from incoming unpolarized
native photons with 2x2 polarization coherency projection.

New actual source-conditioned event rows 4*160*128 = 81,920
and source event budget stage rows 640.
Peak generated linear polarization / freshly scattered-in intensity:
  S0_BI CHARACTERISTIC = 3.802540573834771e-7
  S0_BI ORIGINAL_HAT   = 1.4534869156488892e-7
  S0_FLRW CHARACTERISTIC = 1.1036721190577541e-16
  S0_FLRW ORIGINAL_HAT = 1.4404468688031792e-16.
Expected scattering events per H over original 160 source stages:
  BI CHARACTERISTIC 9.416952332565137e-9;
  BI ORIGINAL_HAT 9.417066885600722e-9;
  FLRW virtually identical.
BI characteristic last-step absolute generated source
polarization ≤1.6589520813498469e-19 photons/H in one outgoing ray.

Physical data sha256:
  original 81920 native source rays:
    70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1
  collision 81920 Stokes:
    5517fc071ac41656e2aa8aa31996b2251c5795db8d51b033d7b804482c66bcba
  640 physical stage budgets:
    0889fdb688ef8b7bfac5e345a77a79028c49a4100e16a6ee85a8e99d08d7985d
  science result:
    2b29412bec84517073806a469161e63302492069580eb44f987acc534db3504a
  independent coherency:
    a4e50f554cbfb7985f7611ff38d7e4a7f4eb108ec8f8a57dd00aaa8047347316
  independent angular 640-stage:
    e5172af071c288cf3bddfa4a3f51ba85e70c6d9ce92180bcaa04ba2f3ce0a378
  angular systematic JSON:
    cc9755b998f1b9219dbe4822df9ca4452a96027e34654e9d08268370daed258c

## Adversarial referee and exact failed science gate

A second implementation uses true 2x2 incoming photon coherency
rather than the producer's spin-phase K,Q,U. It rechecks all
81,920 original source ray rows, four source models and 640 stages.
Implementation relative to scattered-intensity discrepancy max
9.314909370037561e-16, all elastic source number and energy
sums conserved, Stokes positivity holds. FLRW isotropic Q/U zero
to ~1.44e-16. This is discrete implementation parity, not
proof of continuum angular accuracy.

An independent angular l<=2 least-squares harmonic method used
all original 128 q and the same original photon counts.
BI characteristic weighted-versus-harmonic quadrupole difference
~1.1648% (relative). BI fixed-hat case tick142 photon number
quadrupole norm weighted=2.7223369859687518e-9, absolute
method difference=1.1303899183023097e-10, relative
difference=4.152277708926094%.
The PREDECLARED 3% ANGULAR METHOD GATE **FAILED at exactly ONE
source model/time/observable**, S0_BI ORIGINAL_HAT tick142 number.
All other qualifying BI samples below 3%. The failure is
preserved in SYSTEMATIC_RESULT.json, tolerance NOT widened.
The discrepancy occurs near a small quadrupole and is
NOT a rigorous continuum angular discretization error bound.
FLRW quadrupole absolute ~1e-16; relative ratios meaningless.

Source-free normal 10/10 and python -O 10/10 regression tests
include EXPECTED method-gate-FAIL factual assertion, source hash
tamper rejection, full-row independent coherency audit. Original
Rust source 640 full stages already truly rerun, input SHA-locked.
Native_subagent=NOT_RUN; distinct-author blind referee=NOT_RUN.

## Physical limitations, DAG and constructive next action

No Thomson scattering feedback to original H/He photon gas,
no multiple scattering, polarization parallel transport,
Einstein-solved Bianchi metric, measured CMB map,
KN/recoil/thermal electron correction. This is a leading
single-scattering Born SOURCE, not a completed polarized
Boltzmann photon trajectory. Original S0 photon energy 13.7eV,
T~50,000 K; neglected effects E/(me c²)~2.7e-5 and
kBT/(me c²)~8e-6. Small characteristic/hat numerical
comparisons cannot be promoted to observational claims.

REI original F08 paired_runtime production HOLD; source F05
26-event 46,080-cell history is NOT mixed with F08 S0.
REI F05 official tick160/131072, V2 tick163 research only.
DAG per stage: REI canonical 28/88, working 33/88,
Physical Fast 4/7, REC H5 physical 0/313, all DELTA 0.
No main merge, force push, source owner swap, tolerance relaxation
or auto-next. Next true science is original REI F08 paired-runtime
interval-certified actual photon H/He Thomson coupling and
resolving angular method discrepancy at tick142.
Avoid opening another opacity-only atlas.

Primary literature: Hu and White PRD56 596 (1997),
Challinor PRD62 043004 (2000);
Sung and Coles JCAP06(2011)036. Original source is the SSOT.
