# REC-F05 original accepted H/He Compton physical diagnostic

Unit: `REC_ORIGINAL_F05_ACCEPTED160_CMB_COMPTON_ENERGY`.
2026-11-01. New source-conditioned physical observable; not a second
ionization IVP, Compton solver insertion, geometry or production event.

## Original identity

- Parent REC PR #193 exact HEAD `488c68a69050401c96f730b192f38b498f6ceddd`.
- Original REI 26-event source TAR SHA256
  `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.
- H/He native initial NPZ SHA256
  `7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d`.
- Original accepted160 numerical arrays SHA256
  `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`.
- 46,080 distinct physical cells, 3 source-validation lanes (not
  independent physical samples). Original tick0→64→128→160 accepted
  history; original tick161 unaccepted. z_mid=5.95 from original forcing,
  native tick time 4.87184874916828e9 seconds.

## Distinct new physics

The direct source-data electron+logT Compton exchange for an explicitly
**additional isotropic CMB blackbody** at T0=2.728 K, Tgamma=18.9596 K,
under nonrelativistic thermal electrons. Not the four-group original F05
ionizing photon spectrum. Derivation and units: THEORY.md.

All 46,080 original accepted endpoint temperature boxes are above Tgamma.
The source-conditional instantaneous Compton energy-transfer total is

    Q_C in [-1.0692656716215571e39, -1.0692641897309627e39] erg/s.

The translational gas energy is

    U_kin in [3.3720281148255865e55, 3.3720326300631297e55] erg.

The original one-tick *frozen endpoint* energy-exchange scale is

    |Q_C(t160)| dt_tick / U_kin(t160)
      in [1.5448526087286702e-7, 1.5448568183386892e-7].

This diagnostic could inform whether adding CMB Compton coupling to the
REI F05 physical model materially affects a one-tick energy budget.
**It is not the actual integrated Compton correction over that tick**, not
a rigorous truncation estimate and not an F05 scientific acceptance
or restored continuum time history. No generated CMB sky or y-map.

## Executed local verification

Fresh Python 3.12/NumPy original-source code execution with intact
source SHA locks, full 46,080 rows and gas/electron box bounds.
7/7 dedicated unittest PASS, 7/7 Python -O unittest PASS.
2 initially incorrect test expectations (cold/equilibrium boundary and
electron corner pairing) were detected and repaired; the physical code
and original sources were unchanged. Negative inverted/negative interval
tests PASS; direct alternative cgs formula checked; original REC #193
source electron aggregate numerical parity checked.

Full 46,080-row new data SHA256:
`0a69fadf60f61f5e667f979562f13aa498ee3c3c1ab652eb6d07bddab2ad787d`.
JSON source science SHA256:
`c56b2c307c01d8ee968baf54eb6fa12fc23b1d39c8ace2f081c06df12732f389`.
Local rerun and fresh CI execution are separate evidence tiers.

## Blind-referee/physics objections and transitions

- Valid point: an externally chosen isotropic CMB temperature is not
  identical to REI's actual ionizing spectrum. It is an explicitly
  *additional conditional bath*, never a photon-source replacement.
- Valid point: a very small frozen one-tick exchange does not imply
  F05 local tolerance satisfied or integrated IVP error bounded.
  No claim made; original historical FAIL/HOLD is retained.
- Valid point: a homogeneous radiation field means directional Thomson
  transport and Bianchi Sachs null paths remain missing. This unit
  reports local electron–photon energy transfer only.
- Valid point: electron temperature single-Maxwellian nonrelativistic
  closure is a physical assumption; original gas T is interpreted as
  Te for this diagnostic and cannot independently demonstrate Te=Tion.
- Next physical owner action is original F05 V2 source-owner decision
  and source/clock matched Bianchi transport, NOT further local
  surrogate opacity atlases.

DAG stays REI canonical 28/88 (+0), working 33/88 (+0),
Physical Fast 4/7 (+0), REC H5 physical 0/313 (+0).
No original source mutation, no accepted tick161, no production,
no merge, no force push, no tolerance change, no reionization source swap.

## Research loop execution mapping

Theory: R1 concrete question; R2 primary HyRec material-temperature
Compton law; R3 exact scope/units; R4 choose energy exchange rather
than another Thomson opacity atlas; R5 derivation; R6 internal hostile
scope review; R7 actual source data and Wolfram symbolic identity;
R8 conditionally admit numeric diagnostic only; R9 equation-to-code
and interval form; R10 one report plus handoff.

Code: C1 frozen parent and source inputs; C2 REIADP1 and NPZ loader;
C3 four-corner box arithmetic; C4 single-source full-row plan;
C5 source executable; C6 normal/-O seven regression tests;
C7 temperature, negative cooling, energy identity and Rust parity;
C8 CSV/JSON hashes and repeatability, not continuum convergence;
C9 adversarial test-corner correction; C10 source-scoped Draft
delivery, cold archive and next action. Stage completion is scoped to
this diagnostic, not to the parent physical DAG or global REI project.
