# PR-04B2A research contract — physical native edge-flux map

## Classification

`BOUNDED_RESEARCH_CONTRACT / PR-04B2A / v0.53-candidate`

## Primary research question

Can the original October-2012 HyRec real/virtual algebra at one actual FULL-mode
FLRW trajectory snapshot be mapped, without a fitted normalization, to the
physical logarithmic-frequency photon flux per hydrogen atom while preserving
source-identical baseline output and keeping the v0.52 native-proxy firewall?

## Subquestions

1. Can diagnostics be added under a compile-time guard so the guard-off history
   bytes are unchanged and the guard-on stdout history remains byte-identical?
2. What exact identity relates the native virtual-state average distortion
   `x_v/x_1s`, the incoming/outgoing distortions `Dfplus/Dfminus`, optical depth
   `Dtau`, and physical photons per H per `d ln nu`?
3. Do the native primitive and steady-Schur representations give the same
   physical edge action and its first four ordinary-frequency moments?
4. Which part of the v0.51 17-cell COM–KHW measure is directly comparable to
   this native edge action without inventing a scale or treating virtual
   populations as photon finite-volume occupancies?
5. Which remaining mismatch belongs to PR-04B2B/PR-05 rather than this bounded
   stage?

## In scope

- canonical owner-attested official-site `HyRec_Oct2012.zip` bytes;
- source-identical GNU-C baseline and guarded diagnostic build;
- one predeclared FULL-mode hydrogen-recombination snapshot near `z=1100`;
- ordinary frequency `nu` in Hz and logarithmic coordinate `y=ln nu`;
- physical distortion photons per H per `d ln nu`;
- exact native edge-flux/escape identity;
- primitive versus Schur parity, dimensions, signs, conservation, JVP, stable
  small-optical-depth evaluation, and high-precision reference checks;
- an explicit fail-closed statement for any direct COM–KHW/native claim not
  supported by the common physical measure.

## Out of scope

- changing canonical HyRec source bytes in the repository;
- fitting a normalization or empirical offset;
- claiming virtual-state proxy populations are physical photon-cell numbers;
- full all-redshift Bianchi coupling;
- PR-05 production interface, PR-06 monolithic FLRW history parity;
- Raman production, polarization, fine structure, J-state interference, or
  atomic alignment.

## Conventions

- metric signature: `(-,+,+,+)`;
- local frame: hydrogen orthonormal tetrad;
- ordinary frequency: `nu` in `Hz`;
- jump sign: `Delta nu = nu_target - nu_source`;
- photon energy jump: `Delta E_gamma = h Delta nu`;
- atom recoil energy jump: `Delta E_H = -h Delta nu`;
- logarithmic frequency: `y = ln nu`;
- cosmological time: `eta = ln a`, so `d/dt = H d/d eta`;
- constants `c`, `h`, and `k_B` remain explicit;
- original HyRec source quantities are cgs/eV unless converted explicitly.

## Evidence policy

Accepted evidence, in descending order:

1. canonical archive bytes and direct source execution;
2. source-level algebra with exact symbolic verification;
3. independent high-precision numerical verification;
4. double-precision regression against a full trajectory snapshot;
5. primary literature and the official HyRec page for architecture/variable
   interpretation.

Transcript claims and fitted output agreement are not evidence.

## Completion bar

PR-04B2A may be promoted only if all of the following hold:

- guarded-off history SHA-256 equals the v0.52 baseline;
- guarded-on stdout history SHA-256 is also identical;
- exactly one locked snapshot is emitted with complete thermodynamic,
  real/virtual, optical-depth, incoming/average/outgoing radiation data;
- the native collision/escape action and logarithmic edge flux agree without a
  free scale at double precision and at high precision;
- units and signs close analytically;
- primitive and Schur physical edge moments through order four agree on their
  common domain;
- analytic JVP and finite-difference JVP agree;
- no direct v0.51/native equality is promoted unless a source/target partition
  and measure-preserving projection are explicitly established;
- immutable artifact, tests, ledger, manifest, ZIP, bundle, and binary-safe
  patches are produced.

If the exact edge identity closes but direct 17-cell COM–KHW/native moment
parity remains underdetermined, the bounded result is `PR-04B2A PASS / PR-04
OPEN`, not a forced PR-04 completion.
