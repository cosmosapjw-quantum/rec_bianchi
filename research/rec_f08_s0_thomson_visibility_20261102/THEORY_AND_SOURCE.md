# REC → REI F08 S0: continuous native photon/HHe source to Thomson visibility

2026-11-02 | research-only | source-conditional original REI F08 S0.

## Authority, scope and original goal (R1–R4)

REC immutable parent #197:
ab71106999cb90d8be2435818511aca2c4ca2993.
Actual same-source photon + H/He donor BASS #328:
b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6;
native BASS #326 base 4984b42a9ed4025e4b3f20a3a61355a448e522ab.
Original REI F08 S0 source pair SHA256:
0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8.
Donor BASS continuous H/He source trajectory:
research/bass_rei_f08_s0_continuous_native_20261102/results/
SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz
SHA256 75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843.

This original source is F08 S0, and is NOT the separate F05
46,080-cell 26-event accepted160 state. Never import or equate F05
material densities, Hubble clock, four-group radiation or 131072 tick
history. The F08 research Rust stages are conditional independently
coupled, not the full original paired_runtime interval-certified
H/He+photon owner production.

BASS #328 genuinely evolves own photon survivors, emitted photons
and gas H/He, T, energy cumulatively for 160 original steps, in
original S0 Bianchi I versus FLRW geometries and 13.7-eV exact
birth-energy CHARACTERISTIC versus original 17-node HAT controls.
640 actual gas+photon model steps and 320 model comparisons.
No new gas ODE is run here. REC delivers the FIRST time-history
Thomson conditional collision and redshift-visibility *consumer*
directly on those 640 native physical states and 128 source rays,
not an arbitrary fixed density or disconnected source opacity.

## Mathematically defined physical observables (R5)

Signature (-,+,+,+); retain c and k_B.
Metric explicitly prescribed by original S0 source:
ds²=-c²dt²+sum_i a_i²(t)(dx^i)²,
a_i(t)=exp(H_i t), constant H_i.
Original S0 source:
Bianchi I H=(1.01,0.99,1.00)*1e-14 s^-1,
FLRW=(1,1,1)*1e-14 s^-1,
n_H(t)=n_H0 exp[-(H1+H2+H3)t], n_H0=1e-4 cm^-3,
f_He=0.083, original proper dt=6.25e8 s,
original horizon T=160*dt=1e11 s,
native initial x_HII=.9, x_HeII=.3, x_HeIII=.6.

Original self-evolved gas electron fraction (per hydrogen):
    x_e(t) = x_HII(t)+f_He [x_HeII(t)+2*x_HeIII(t)],
    n_e(t)=n_H(t)*x_e(t).

For photons on exact ORIGINAL S0 Bianchi null characteristics, the
unscattered Thomson collision hazard in the homogeneous comoving
electron rest frame is:
    Gamma_T(t)=c sigma_T n_e(t)  [s^-1],
    d tau/dt along increasing time to receiver = -Gamma_T(t)
    tau(t,T)=int_t^T Gamma_T(u) du,
    S(t,T)=exp[-tau(t,T)].
The visibility density per source proper second is
    g_t(t)=Gamma_T(t)*exp[-tau(t,T)]   [s^-1].
In the dilute limit tau<<1, 1-S is the source-conditioned probability
of at least one scattering along the *unscattered* null ray. No angular
redistribution, stimulated/inverse Compton energy exchange or CMB
polarization source has been solved. This is real time-resolved
transport along prescribed native original S0 geometry, not observed
last-scattering at z=0.

At fixed (t,T), all 128 ray directions share exactly the same tau
in homogeneous comoving electrons. But due to anisotropic energy
redshift, fixed photon REDSHIFT selects different emission times.
Original conserved q_i direction:
    g_q(t)=sqrt(sum_i q_i² exp[-2 H_i t]),
    1+z_q(t,T)=g_q(t)/g_q(T).
The positive ray-specific Hubble function
    H_ray(t,q)=sum_i H_i q_i² exp[-2H_i t]
               /sum_i q_i² exp[-2H_i t].
Thus
    |dt/dz|=1/[(1+z)H_ray],
    d tau/dz=Gamma_T(t(z,q))/[(1+z)H_ray(t(z,q),q)],
    g_z(z,q)=Gamma_T exp(-tau)/[(1+z)H_ray].
This is the physically relevant comparison at fixed photon redshift,
without inventing angle dependence of tau at fixed proper time.
Use all original 128 q rays. For FLRW the q dependence vanishes.

## Computational source-conditioned temporal closure

The BASS original Rust source provides gas endpoints at t_k=k*h, no
validated dense-time H/He continuum extension. Do NOT pretend the
per-step path is a rigorously enclosed original solution.
Define an explicit positive piecewise AFFINE interpolation of x_e
between each pair of ACTUAL adjacent native stage states
(including true original S0 initial gas state). Keep the original
proper n_H(t)=nH0 exp(-theta t), theta=sum H_i.
Within segment [t_k,t_{k+1}], x_e(t)=x0+(x1-x0)*s,
s=(t-t_k)/h. Define lambda=theta*h. Then the Thomson depth
increment is integrated **analytically for this chosen interpolant**:

  delta_tau=c sigma_T n_H(t_k) h [ x0 A(lambda)+(x1-x0)B(lambda) ],
  A(lambda)=(1-exp(-lambda))/lambda,
  B(lambda)=[1-(1+lambda)exp(-lambda)]/lambda².

For small lambda use cancellation-safe positive series
A=sum_{j>=0}(-lambda)^j/[j!(j+1)],
B=sum_{j>=0}(-lambda)^j/[j!(j+2)].
Limits lambda→0: A=1, B=1/2. The original S0 lambda=1.875e-5,
so 12 series terms are far below f64 discretization uncertainty.
This makes no numerical time-quadrature error for the explicitly
selected source-endpoint interpolation; interpolation/model error
relative to the exact original native IVP is NOT certified.

For each of four models generate tau_k=Σ_{i>=k}delta_tau_i,
g_t(k), per-step scattering probability
  deltaP_k=S(t_{k+1},T)-S(t_k,T)>0;
test Σ deltaP_k = 1-exp(-tau_0).
At fixed redshift target z*=f * z_min with f={1/4,1/2,3/4},
z_min=min_{q,geom} z_q(0,T), all 128 source rays have the
required redshift within the actual source time horizon.
Solve actual analytic g_q(t)/g_q(T)-1=z* by bounded monotone
bisection, evaluate tau(t,T) and g_z at that time, and
measure the Bianchi directional spread at same z*.
This is not a fake present-day sky or claimed true F08 pair-integrator
acceptance.

## One finite blind-referee pass (R6/R7)

Critique 1: tau should be direction-dependent in Bianchi I.
False for homogeneous comoving electron gas at fixed physical
endpoints; anisotropy enters time-redshift conversion and/or real
electron tilts/inhomogeneity, which are NOT present in this donor.
The zero-shear FLRW limit must make tau(z) independent of q.

Critique 2: BASS donor is itself an independent conditional S0
continuous coupled photon HHe driver, not the original full
interval-certified paired_runtime. Correct. Keep source owner
REI F08 admission=HOLD; do not promote BASS native runtime evidence.

Critique 3: one may infer a high-precision visibility curve from
160 steps. Only exact within prescribed piecewise-affine source
state temporal closure. No certified continuum interpolation,
recombination error band, Thomson collision redistribution or
global cosmological CMB.

Critique 4: could use F05 electron cell archive in F08 without
matching source. Reject. This unit consumes only actual original
REI F08 S0 BASS source. Preserve all native 51+12+4 source locks
when possible and independently verify donor hash/metadata.

R8–R10, C1–C10: one original physical model/closure through
published source-linked ray visibility, independent Gaussian
quadrature audit and cold source inclusive backup. Each stage
keeps central REI 28/88, working 33/88, Fast 4/7,
REC H5 physical 0/313 unless ORIGINAL owner accepts a node.
Production HOLD, Draft/NO_MERGE/NO_FORCE_PUSH/NO_OWNER_SWAP,
no tolerance change, no auto-next or photon source substitution.
No native subagent accessible; serial same-author hostile audit,
different-author referee NOT_RUN.

Refs: Pontzen & Challinor, MNRAS 380 1387 (2007);
Sung & Coles, MNRAS 412 290 (2011); exact project source
has priority over any general-paper formula.
