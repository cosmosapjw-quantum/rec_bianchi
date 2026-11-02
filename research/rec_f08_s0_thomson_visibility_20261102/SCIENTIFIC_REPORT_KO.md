# REC → REI IGM | F08 S0 native continuous H/He Thomson ray visibility

2026-11-02 KST | REC consumer track | Original REI F08 S0 research, HOLD.

## Immutable science identities

- REC predecessor #197 HEAD
  ab71106999cb90d8be2435818511aca2c4ca2993.
- Actual BASS native continuous F08 donor #328 HEAD
  b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6,
  original native parent #326 HEAD
  4984b42a9ed4025e4b3f20a3a61355a448e522ab.
- Original REI F08 S0 source photon+H/He pair SHA256
  0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8.
- Actual full 640-row native BASS donor gas and photon trajectory
  SHA256 75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843.
- Original REI 128-ray qhat source input newly losslessly frozen in REC
  SHA256 a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92.
- Original BASS donor source manifest, 12 S0 input files, 51 Rust
  original modules and 4 photon checkpoint files individually rehashed
  before input snapshot. The original donor has existing source-native
  160 actual Rust coupled stages per background/representation, 640
  physical gas+photon states, independently documented by BASS.
- **Do not confuse F08 S0 time or ionization state with F05.**
  No F05 46,080-cell source, tick160/131072 matter, four-group 26-event
  OTS photon and candidate V2 tick161 are imported into this experiment.

## New source-physical objective and exact formulas

The original F08 S0 self-evolved photon+gas states from BASS #328 are
used as real electron history for Thomson collision along 128 EXACT
native photon q directions. This advances a missing REC photon
visibility receiver from true *time-dependent* coupled material,
not a synthetic fixed electron screen.

Original source backgrounds (prescribed, NOT Einstein solved):
Bianchi I H=(1.01,.99,1.00)e-14 s^-1,
FLRW H=(1,1,1)e-14 s^-1; each has theta=3e-14 s^-1,
n_H0=1e-4 cm^-3, f_He=.083, native gas initial
(xHII,xHeII,xHeIII)=(.9,.3,.6).
Original proper dt=625,000,000 s, 160 steps to T=1e11 s.
Source photon energy E_birth=13.7 eV, 128 actual source ray directions.

Normal-electron-frame, unscattered-ray leading Thomson physics:

  n_e(t)=n_H0 exp(-theta t)*[xHII+fHe(xHeII+2*xHeIII)].
  Gamma(t)=c sigma_T n_e(t).
  tau(t,T)=int_t^T Gamma(u) du.
  Survival S(t,T)=exp[-tau(t,T)].
  Proper-time visibility g_t=Gamma(t) exp[-tau(t,T)].
  Probability of at least one scattering=1-exp[-tau(0,T)].

Metric signature (-,+,+,+). With exact original Bianchi I
conserved photon covariant q_i:

  g_q(t)=sqrt(sum_i q_i^2 exp[-2H_i t]).
  1+z_q(t,T)=g_q(t)/g_q(T).
  H_ray(t,q)=sum_i H_i q_i^2 exp[-2H_i t] /
             sum_i q_i^2 exp[-2H_i t].
  g_z(z,q)=Gamma(t(z,q))exp[-tau(t(z,q),T)]/
            [(1+z)H_ray(t(z,q),q)].

The source is homogeneous and electrons are comoving. Thus tau at
FIXED proper endpoints is direction-independent even in Bianchi I,
but tau at FIXED photon redshift is angular because the emission
time t(z,q) varies with original exact Bianchi null characteristics.
No artificial optical depth anisotropy is inserted.

The original native gas source has 160 discrete output points but
NO certified dense-time continuum extension. We explicitly define
x_e linearly between ACTUAL consecutive source gas endpoints.
n_H(t) is original exact exponential. The Thomson micro-step
integral is computed analytically for this explicit interpolant
with A(lambda)=int_0^1 exp(-lambda s)ds,
B(lambda)=int_0^1 s exp(-lambda s)ds, lambda=theta dt.
For lambda=1.875e-5 use cancellation-free 16-term series.
The temporal interpolation error relative to original actual
F08 paired_runtime is NOT proven.

## New actual numerical outcomes

Original actual 640 native gas+photon records yield:
4 model histories x 161 original proper endpoints = 644
time visibility records, and
4 model histories x 128 native rays x 3 common supported photon
redshift values = 1536 native Bianchi ray visibility records.
Source-native q and H both come from original photon checkpoint.
Chosen common photon redshift values are fractions 1/4,1/2,3/4 of
the minimum source-supported horizon redshift across the two metrics:
z=(0.00024784916355596875,0.0004956983271119375,
   0.0007435474906679063). This is NOT source z=5.95 F05.

| Same proper emission time t0=0, receiver T=1e11s | Thomson tau |
|---|---:|
| S0 Bianchi I, characteristic source photon representation | 2.0492658300588584e-7 |
| S0 Bianchi I, original fixed-hat representation | 2.0492646932530454e-7 |
| S0 FLRW, characteristic | 2.0492658300588912e-7 |
| S0 FLRW, original fixed hat | 2.049264693417559e-7 |

The model is optically thin: source original no-scattering
survival is near 0.9999997951, and total probability of at least
one Thomson event is about 2.04926562e-7.

At **fixed source photon redshift**:
S0 Bianchi I characteristic relative ray tau spread
(max-min)/mean is 1.8179034%, 1.8166684%, 1.8152680% for the
three native source-supported redshifts. At z=0.00049569832711,
tau range [1.0078259528244626e-7,1.0263015969430765e-7],
while matched FLRW tau≈1.0169798524577e-7 independent of q.
FLRW angular relative spread below 7e-13 (f64 root accuracy),
matching the zero-shear exact limit.
A fixed-time redshift-τ comparison would *not* exhibit this anisotropy.

Characteristic minus fixed-hat total tau in S0 Bianchi I
is only about 1.137e-13 (relative 5.55e-7).
**Adversarial physics limitation:** leading Thomson ignores
Klein-Nishina frequency correction of order Eγ/(m_e c²)
≈2.68e-5 at 13.7eV and thermal electron corrections of order
k_B T/(m_e c²)≈8.4e-6 at T≈50,000 K. Hence the tiny
representation-dependent τ difference is internally reproducible
under the Thomson closure, NOT a physical observation-level
discriminant without higher-order scattering physics.
The ~1.82% geometry effect is much larger in this model,
but neither this horizon nor gas source is observationally calibrated.

## Reproduction, independent blind-referee attempt and negative controls

- Data: results/ORIGINAL_F08_S0_4MODE_644_TEMPORAL_THOMSON.csv.gz
  SHA256 e334e760a45b9ce1044d96a005b795ee3843be1be8c4c969956191dfa5a17fda.
- Rays: results/ORIGINAL_F08_S0_128RAY_1536_REDSHIFT_VISIBILITY.csv.gz
  SHA256 9f5865f0ab176c8865011042e97f4648b1e73385cd5b5aa23637eade96c15fab.
- Result JSON SHA256
  3362ccd832b9d7af121c32e4fe7ba2cc04f4b992bf5238868477b2c1ed6f23b3.
- Independent audit JSON SHA256
  49c81023f0551f62da82c20e9f17b351678c6994e08aac459fb679df3f8e2b87.

Independent source-free stdlib audit does not import REC generator;
uses two-point Gauss–Legendre quadrature on every original native
temporal segment, recomputes 644 time and 1536 ray responses with
2,180 checks, physical redshift/geodesic direction and conservation
of scattering probability, and verifies FLRW angular invariance.
Local normal 9/9 and Python -O 9/9 regression including source
SHA tamper rejection PASS. Local source-input deterministic
science regenerated byte-for-byte, but hosted CI uses scientific
numeric checks rather than assuming cross-platform libm byte
identity. Wolfram checked exact source interpolation integrals
and limit A→1, B→1/2.

Important limits: no Thomson collision redistribution into the
native Rust gas/photon IVP, no polarization collision quadrupole,
no native F08 full interval-root time-step certificate, no
present-day observed CMB, no F05/REC H5 physical query admission,
no full anisotropic Einstein constrained metric. Do not promote
to original owner canonical science or production.

R1–R10 source-selection/derivation/physics/hostile check and
C1–C10 actual implementation/audit/backup comprise ONE
REC-scoped physical unit, not 20 canonical DAG completions.
Baseline throughout: REI central 28/88 (+0), working 33/88,
Physical Fast 4/7, REC H5 physical 0/313 (+0).
Draft/HOLD, no merge, no force push, no owner/production mutation,
no tolerance changes, no automatic next step.
Next owner causal path: REI full source paired_runtime interval
certification of source-matched continuous photons/HHe and
F05 official versioned V2 owner ACCEPT/REJECT, not further
unrelated source-only τ atlases.
