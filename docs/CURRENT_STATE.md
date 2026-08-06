# Current scientific state

## Summary

The durable endpoint is **PR-04B2B / v0.54**. PR-01 through PR-03 are
complete. PR-04A established the positive 17-cell COM–KHW common measure;
PR-04B1 locked the canonical October-2012 original-HyRec source and native
proxy algebra; PR-04B2A derived the source-identical physical logarithmic
photon edge flux; PR-04B2B now proves that a direct positive
native-to-17-cell equality is not available.

PR-04 remains open. The next bounded stage is **PR-04C split-domain
conservative exchange contract and multi-snapshot closure**. The native
transport and COM–KHW collision representations will retain their own supports
and exchange only explicitly conserved number/energy fluxes through a declared
interface.

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
Delta E_H:       -h Delta nu
```

Constants `c`, `h`, and `k_B` remain explicit. Homogeneous backgrounds only;
all geometry enters local microphysics through the established
`BackgroundSnapshot` adapter.

## Canonical table audit

The production and optional high-resolution original-HyRec table members are
byte locked as follows.

| Lane | Member | Shape | SHA-256 |
|---|---|---:|---|
| production | `HyRec/two_photon_tables.dat` | `311 x 5` | `93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9` |
| high-resolution reference | `HyRec/two_photon_tables_hires.dat` | `1493 x 5` | `db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93` |

Each row contains one energy centre and four coefficients already integrated
over a latent spike width. The runtime reads exactly five values. The canonical
runtime archive contains no explicit numerical edge column, no dedicated
two-photon-table generator member, and no source statement that opens either
bundled table for writing.

The two numerical centre grids are separate rather than exactly nested:

```text
exact production-centre matches in high-resolution table: 0
nearest difference, minimum: 1.0000000010e-6 eV
nearest difference, median:  5.1800000000e-4 eV
nearest difference, maximum: 4.4412600000e-2 eV
```

Only two diffusion-lane centres in either table lie inside the v0.51 core
`|x|<=4.25`. Therefore centre inclusion cannot recover source-cell boundaries
or a conservative restriction operator.

## Positive-support no-go

Let a positive target measure be supported on the 17-cell union
`[-4.25,4.25]`. Then necessarily

```text
M2/M0 <= 4.25^2 = 18.0625.
```

The locked v0.53 physical native edge measure gives

| Source measure | `M2/M0` in Doppler `x` | Violation factor |
|---|---:|---:|
| full 311-state measure | `1.344707749773356e8` | `7.44474878767256e6` |
| diffusion 80-state measure | `2.1808728753005056e4` | `1.2074036679864391e3` |

The same values were re-summed at 100-digit precision from the exact binary64
inputs:

```text
full:       134470774.977335589307785774837433014082942740474657777...
diffusion:  21808.7287530050561936684447521005490738212556071880921...
```

Hence no nonnegative map to the 17-cell core can preserve even `M0` and `M2`
of the full or diffusion-only native positive measure. This result is
independent of interpolation order, optimizer, midpoint assumptions or a
chosen regularizer.

Restricting the native source to the two centres inside the core is not
conservative:

```text
core mass / full 311-state mass:   0.0017361780045445255
core mass / diffusion-80 mass:     0.006550012987972702
```

## Identifiability no-go after support restriction

Moments `M0,...,M4` give five constraints for seventeen target-cell masses.
For the explicit uniform-within-cell finite-volume basis, exact rational SymPy
arithmetic gives

```text
rank:    5
nullity: 12
```

The durable artifact contains two distinct strictly positive 17-vectors with
exactly equal moments through order four. The independent floating-point
witness has

```text
minimum weight:       0.047058823529411764
moment residual:      1.4210854715202004e-14
L1 separation:        0.0627429665766292
```

Thus moment matching alone does not identify a unique positive projection.
Tchakaloff-type existence results do not provide the missing uniqueness or
source provenance. Maximum entropy, minimum transport cost, midpoint/Voronoi
cells or another regularizer would be additional modelling assumptions and are
not promoted as canonical HyRec structure.

As non-load-bearing controls, the actual two-core-centre moment vector is
nonnegative-LP infeasible under both cell-centre Dirac and uniform-within-cell
17-cell bases. These controls are not needed for the support theorem.

## Scientific disposition

```text
PR-04B2B:                         PASS_NO_GO
direct native-to-17-cell map:    REJECTED_BY_SUPPORT_AND_IDENTIFIABILITY
silent high-resolution substitute: FORBIDDEN
free normalization:              FORBIDDEN
multi-snapshot direct parity:    BLOCKED_NOT_FABRICATED
PR-04:                            IN_PROGRESS
```

This is an informative no-go, not a solver failure. It prevents an
unidentifiable remap from being hidden inside the production interface.

## Immediate next stage

**PR-04C split-domain conservative exchange contract** must:

1. lock operator ownership so that each collision, escape and redshift term has
   exactly one owner;
2. retain the 35-state COM–KHW collision domain on `x in [-21.25,21.25]` and
   original-HyRec on its full native support;
3. use a number/energy flux packet at the two physical interfaces rather than
   a global state-vector projection;
4. instrument exact nearest-grid FLRW snapshots near `z=1300,1100,900`;
5. apply every interface flux once with opposite signs to the two modules;
6. close number, photon-plus-atom energy, positivity, equilibrium, branch,
   primitive/direct/Schur, analytic/JVP and local Bianchi-firewall gates;
7. keep higher moments representation-local unless an independently
   source-derived positive interface packet measure exists.

See `docs/PR04C_SPLIT_DOMAIN_EXCHANGE_PLAN.md`.

## Tool and remote status

The pinned coding and research harnesses were byte-locked, validated and used
to produce the research contract, evidence ledger, hypothesis audit,
validation matrix and independent adversarial review.

Web research used primary HyRec, truncated-moment and conservative-interface
literature. Wolfram and Precise Special Functions were not exposed in this
runtime; SymPy exact rational algebra, mpmath 100-digit arithmetic, NumPy SVD,
SciPy HiGHS and direct canonical archive/source audits were used instead.

The live private GitHub connector was not exposed. The owner performs fetch,
push and PR creation locally. No remote synchronization is claimed without a
durable live-remote receipt.
