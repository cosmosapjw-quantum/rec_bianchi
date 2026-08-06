# Current scientific state

## Summary

The durable endpoint is **PR-04C0/C1A / v0.55**. PR-01 through PR-03 are
complete. PR-04A established the positive 17-cell COM–KHW common measure;
PR-04B1 locked canonical October-2012 original HyRec; PR-04B2A derived the
physical logarithmic-frequency edge flux; PR-04B2B rejected a direct global
native-to-COM remap by support and identifiability no-go. v0.55 now closes the
single-owner interface architecture and extracts six source-identical positive
photon packets at `x=+-21.25` for the predeclared `z~1300,1100,900` snapshots.

PR-04 remains open. The next bounded stage is **PR-04C1B/C2 far-boundary
deposition and coupled implicit interface operator**.

## Canonical provenance and conventions

```text
archive: archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip
size:    726954 bytes
SHA-256: 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27
class:   OFFICIAL_SITE_CANONICAL_ARCHIVE_OWNER_ATTESTED_BYTE_LOCKED
```

Internal May/October metadata differences are intrinsic to the canonical
release and are not an uncertainty gate.

```text
metric signature: (-,+,+,+)
local frame:      hydrogen orthonormal tetrad
frequency:        ordinary nu in Hz
x:                (nu-nu_Lya)/Delta_nu_D
y:                ln(nu)
Delta nu:         nu_target-nu_source
Delta E_gamma:    h Delta nu
Delta E_H:       -h Delta nu for a physical collision event
```

Constants `c`, `h`, and `k_B` remain explicit. Homogeneous backgrounds only;
all geometry enters local microphysics through the established
`BackgroundSnapshot` adapter.

## PR-04C0 ownership theorem

The registry assigns exactly one owner to ten process groups:

- original-HyRec free streaming, line escape and real/virtual algebra;
- COM–KHW local collision, stimulated Bose term and recoil four-force;
- COM internal Liouville transport;
- analytic Planck reference;
- red and blue cross-interface transfers.

Duplicate, missing and undeclared ownership fail closed. Each interface packet
is evaluated once and applied once to each representation with opposite signs.
With the replacement switch off, the state arrays are copied exactly and the
interface ledger is zero.

## PR-04C1A source-identical packets

At each snapshot the exact physical interface energy is

```text
E_I = E_Lya + x_I E_Lya sqrt(2 T_m/m_H),  x_I=+-21.25.
```

The least canonical native energy strictly above `E_I` supplies the free-
streaming characteristic. The query in `ln a` is reconstructed with the same
positive two-point linear interpolation used by original HyRec. Diagnostics
are emitted only after the current `Dfminus_hist[:,iz]` endpoint has been
solved and stored; four of six packets legitimately use that current endpoint.
No future endpoint is used.

| Target | Actual source grid redshift |
|---:|---:|
| 1300 | `1299.9971824762927` |
| 1100 | `1099.9986525171403` |
| 900 | `900.0168986313175` |

The six independent Python reconstructions have maximum relative residual

```text
1.6537648327370854e-16.
```

Total occupations and packet fluxes are strictly positive:

```text
minimum total occupation:          4.579328929122558e-16
minimum total number flux /H/s:    1.6796324053145323e-15
maximum total number flux /H/s:    8.859343319670963e-14
```

The Planck reference is retained as a nonnegative component and the nonthermal
distortion is retained as a signed audit component. No packet is distributed
over COM cells in this release.

## Energy ownership correction

A computational representation crossing is not a new atom-photon collision.
Therefore v0.55 supersedes the preliminary interface rule that paired the
transported absolute photon energy with an equal-and-opposite atom source.
The correct interface ledger is

```text
Phi_N_native + Phi_N_COM = 0,
Phi_Egamma_native + Phi_Egamma_COM = 0,
Phi_EH_interface = 0.
```

Atomic recoil remains owned by the physical native or COM collision event. The
six v0.55 packets close number and transported photon energy exactly and have
zero interface atom source. This prevents a double count of recoil energy.

## Independent checks

- Wolfram symbolic evaluation: backward-Euler scalar relaxation positivity,
  exact opposite-sign number/energy cancellation, and
  `Integral[x^2/(exp(x)-1),0,infinity]=2 Zeta(3)`.
- Precise Special Functions: 100-digit `Zeta(3)` and `Gamma(3)=2`.
- Independent mpmath 120-digit parity:
  `Zeta(3)` relative residual `1.216241572349676e-100`; Planck integral identity
  residual `0` at the retained precision.
- Bianchi II, V and exceptional `VI_-1/9` labels give identical packet hashes
  at fixed local hydrogen-frame state.
- Canonical, guard-off and guard-on 8001-row histories have identical SHA-256;
  guard-off binary is byte-identical to the canonical portable binary.

## Scientific disposition

```text
PR-04C0:       COMPLETE
PR-04C1A:      COMPLETE
PR-04C1B/C2:   OPEN
PR-04:         IN_PROGRESS
```

v0.55 proves the interface representation and its source data exist without a
fitted normalization. It does **not** yet perform far-boundary deposition,
solve a coupled implicit residual or claim full trajectory parity.

## Immediate next stage

**PR-04C1B/C2** must:

1. attach blue/red packets only to the existing `FB02`/`FR00` far-boundary and
   Liouville ghost state, never directly to an interior collision cell;
2. build one monolithic residual containing native packet evaluation,
   far-boundary transport and the 35-state nonlinear Bose collision action;
3. use log occupations/nonnegative packet accumulators and an analytic block
   JVP with independent finite-difference/high-precision references;
4. localize every red/blue boundary-speed zero within each timestep for
   Bianchi II, a class-B representative and exceptional `VI_-1/9`;
5. close positivity, number, transported photon energy, physical collision
   four-force, restart and free-energy gates without fitted normalization.

See `docs/PR04C1B_C2_COUPLED_INTERFACE_PLAN.md`.

## Remote status

The read-only GitHub connector verified remote `main` at
`ad316eb60878ff6c92e5f2326b539ad850c62dc9`, tree
`1ec27d34c8b8d15ac56ca6efa500ce6838a3a57e`, containing v0.54 plus the remote
CI/toolchain overlay. v0.55 has not been pushed by this runtime. The owner
fetches, applies, tests, pushes and opens the PR locally without force-push.
