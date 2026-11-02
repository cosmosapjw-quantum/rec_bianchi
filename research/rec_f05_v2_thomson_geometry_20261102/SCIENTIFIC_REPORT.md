# REC F05 original physical Thomson collision response at the V2 source/geometry boundary

Date: 2026-11-02 KST. Original REC #196 immutable parent HEAD
832551b69801eea008daf2c8cf19881c28649075.
Original REI #365 HEAD fab9429140038974a98f3ad3212036b0227e600e.
Conditional V2 owner REI #366 HEAD a09ea7b999c90a692de07c74352f835707e65838.
Original F05 source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b.
Original 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.

## New physical result

Actual original accepted160 source population/temperature arrays were compared
byte-for-byte to all four matching source_parent arrays inside the real
REI #366 V2 candidate NPZ SHA256
c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823.
All 46,080 real source H/He material cells and the original native
proper-volume forcing were consumed; original source z is frozen 5.95
on tick160->161 with H=2.253429258545391e-17 s^-1.
Original source time microtick dt=4871848749.16828 s.

Distinct physical models:
FROZEN_SOURCE: Gamma_161 = c*sigma_T*Ne_161(V2)/V_160.
EXPLICIT_EXPANDING_MATERIAL_CONTINUATION: V_161=V_160*exp(3Hdt);
Gamma_161=Gamma_161^frozen*exp(-3Hdt). The latter is NOT original
26-event owner model, but a genuine conditional physics bridge to
future same-clock Bianchi photon transport.

For the actual source microtick the geometrical rate factor is
exp(-3Hdt)=0.9999996706490588, relative change -3.2935094118613506e-7.

Volume-weighted source 46,080-cell Thomson collision rates (s^-1):

| Source interpretation | Lower | Upper |
|---|---:|---:|
| Original accepted tick160 | 1.3582333381182217e-18 | 1.3582334177000007e-18 |
| V2 candidate 161, original frozen V | 1.3582329823912596e-18 | 1.3582330625253458e-18 |
| V2 candidate 161, expanding V | 1.3582325350559484e-18 | 1.3582326151900082e-18 |

Strict (no interval-overlap ambiguity) source-cell change sign counts:

| Interpretation | Definite increase | Definite decrease | Undetermined |
|---|---:|---:|---:|
| Native frozen-volume chemistry only | 60 | 40350 | 5670 |
| Same V2 H/He candidate with theta=3H continuation | 0 | 43194 | 2886 |

All **60 native-chemistry definite-increase** source cells switch to
**definite-decrease** under the alternative expanding-volume continuation.
The result is nontrivial because its geometrical relative change is the
same order as original one-microtick electron abundance change.

Original source-scoped 46,080 physical row data:
results/ORIGINAL_F05_V2_THOMSON_GEOMETRY_46080.csv.gz
SHA256 b6943328fa70804d0a94b9ef8be1dcf64f329f2e8608abdaffc0ca6c7ac0de32.
Source result JSON SHA256
44841714d404497290fd231e26fa9d608286498be7b67f4b71e9a43f2db2dfc9.
Independent standard-library full-cell audit JSON SHA256
0921ee88d0abd14d2cbe7cc0b7f47b1a91029808068021fd46a5c1f0c967efc8.

## Derivation, validity and hostile review

Gamma=c sigma_T Ne/V (s^-1); a*n_e*sigma_T*c gives a
homogeneous conformal-time collision coefficient with a matched
photon clock. Full Bianchi directional, electron frame/tilt,
null geodesic and polarization physics are NOT calculated here.

The exact additive source-time finite difference splits into
chemical and geometrical terms. For signed geometry delta use
the correlated factor Gamma_frozen*(exp(-3Hdt)-1) instead of
overly wide independent subtraction. Every row was checked for
positive Ne and native V, physical interval ordering, original
source/z/H/volume identity, exact source acceptance state, and
two-branch gamma/finite-difference algebra.

**Blind-referee challenge**: The original owner F05 deliberately
holds z and proper cell volume at 5.95; assuming expansion and
calling its difference an original code defect would be incorrect.
The study therefore compares two distinct explicitly labeled
physical conventions and does not change original F05 source.
The result makes the assumption needed for a downstream photon
transport consumer concrete. No new canonical source tick or
observed scattering optical depth is claimed.

Original V1 tick161 defect > frozen gate remains FAIL.
V2 common-parent *discrete* defect PASS is not a continuous
ODE/global error certificate; V2 161 remains NONAUTHORITATIVE.
The original REI owner has a separate active versioned worker.
No source-side replacement, merge, tolerance reset, force push
or change to the owner trajectory.

Source-full local code execution EXIT 0; standard-library auditor
all 46,080 rows PASS, normal and optimized source-free regression
8/8 and 8/8 PASS, including intentional bad source hash rejection.
All event-stored JSON values audited by independent implementation.
The original source consumer requires pinned source NumPy 2.3.5,
pandas 2.2.3, SciPy 1.17.0, while publication CI re-audits
source-derived rows without the private upstream V2 state.
Native subagent and distinct-author referee NOT_RUN.

## Progress and stop boundary

Theory R1–R5: source owner, interpretation, equations and frozen model.
R6/R7: source-hostile assumption review and Wolfram identity -> 0.
R8–R10: scoped numerical physics admission and publishable report.
Coding C1–C5: immutable accepted/V2 source, native forcing and output;
C6–C9: per-cell physical identities and independent tests;
C10: source-including recovery backup with actual provider readback
to be recorded separately; never treat source-free CI as full-source replay.

At each phase REI canonical 28/88 (+0), REI working 33/88 (+0),
Physical Fast 4/7 (+0), REC H5 physical 0/313 (+0).
Production HOLD. Stop after one model-to-geometry bridge; next
original goal is official REI versioned tick161 ACCEPT/REJECT and
actual same-source-clock Bianchi photon characteristics.
