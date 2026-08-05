# Current scientific state

## Summary

The durable endpoint is **PR-04B2A / v0.53**. PR-01 through PR-03 are complete.
PR-04A supplied the positive 17-cell physical common measure; PR-04B1 locked
the canonical October-2012 original-HyRec source and native proxy algebra;
PR-04B2A now closes a source-identical map from that algebra to physical photon
edge flux per hydrogen atom per logarithmic-frequency interval at one actual
FULL-mode FLRW trajectory snapshot.

PR-04 remains open. The remaining claim is not a normalization constant: it is
an explicit measure-preserving map between the native frequency representation
and the v0.51 17-cell COM–KHW event partition, including conditional jump
moments and trajectory coupling.

## Canonical original-HyRec provenance

The project canonical input is:

```text
archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip
size:    726954 bytes
SHA-256: 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27
entries: 29 safe ZIP members
```

The owner attests that this is the unique archive supplied by the official
HyRec site for the October-2012 release. Internal May-2012 source headers and
October-2012 ZIP timestamps are therefore intrinsic metadata of the canonical
release, not a candidate qualifier or mismatch gate. This v0.53 provenance
classification supersedes only the wording used in v0.52; immutable v0.52
bytes and numerical results are unchanged.

The canonical source builds without source edits under GNU C. Its portable
binary SHA-256 is
`a5ebb0e67b58f5d85f3387458eb96025f93b5b53b1ce4fd76c3a160c51d4b733`,
and its 8001-row history SHA-256 is
`9fdee53a363aeb3b7c6963564543089e1b5ed91e39b0d4471efd052aa66b6485`.

## Locked conventions

```text
metric signature: (-,+,+,+)
local frame:      hydrogen orthonormal tetrad
frequency:        ordinary nu in Hz
y:                ln(nu)
eta:              ln(a), so d/dt = H d/deta
Delta nu:         nu_target - nu_source
Delta E_gamma:    h Delta nu
Delta E_H:       -h Delta nu
```

Constants `c`, `h`, and `k_B` remain explicit. Original-HyRec source quantities
remain in cgs/eV unless an explicit conversion is applied.

## Closed in PR-04B2A

A compile-time diagnostic guard was inserted only in a temporary extraction of
`hydrogen.c`. With the guard disabled, the binary and history hashes are
identical to the canonical build. With the guard enabled, the public history is
still byte-identical and exactly one complete internal snapshot is emitted.

The locked trajectory state is:

| Quantity | Value |
|---|---:|
| internal redshift | `1099.9986525171403` |
| local history index | `5127` |
| `x_e=x_HII` | `0.1449299966903522` |
| `x_1s` | `0.8550700033096478` |
| `n_H` | `250.18675437302318 cm^-3` |
| `H` | `4.969651222923834e-14 s^-1` |
| `T_m` | `0.25882127610727856 eV` |
| `T_r` | `0.25882399309326415 eV` |
| `T_m/T_r` | `0.9999895025729527` |
| optical-depth range | `[2.951084650306298e-9, 4040.01252094867]` |

For occupation distortion `Delta f_nu`, define

```text
N_y = 8 pi nu^3 Delta f_nu / (c^3 n_H),
```

which is the distortion photon content per H per `d ln nu`. Because
`n_H proportional a^-3`, homogeneous free streaming obeys

```text
partial_eta N_y - partial_y N_y = A(nu) C[f]/H,
A(nu) = 8 pi nu^3/(c^3 n_H).
```

For each native virtual spike,

```text
P_b      = (1-exp(-tau_b))/tau_b,
fbar_b   = P_b fplus_b + (1-P_b) feq_b,
fminus_b = fplus_b + (1-exp(-tau_b))(feq_b-fplus_b),
tau_b    = x_1s Gamma_b/(H A_b),
```

and therefore

```text
x_1s Gamma_b(feq_b-fbar_b)
  = x_1s Gamma_b P_b(feq_b-fplus_b)
  = H A_b(fminus_b-fplus_b).
```

Both sides have units `s^-1` per H. Multiplication by `h nu_b` gives `W/H`,
with the exact opposite entry assigned to the atom.

## Numerical closure

| Gate | Result |
|---|---:|
| guard-off binary/history equality | exact |
| guard-on public history equality | exact |
| optical-depth normalization residual | `2.251e-16` |
| source structural edge identity | `5.971e-12` |
| cancellation-safe structural identity | `3.414e-15` |
| source vs dense solution | `3.525e-15` |
| Schur vs dense solution | `1.188e-15` |
| direct spectral-moment residual, `r=0..4` | `1.250e-13` |
| Schur spectral-moment residual, `r=0..4` | `7.541e-14` |
| analytic/finite-difference edge JVP | `4.157e-9` |
| explicit stress-step minimum | `-5.548e-16` |
| implicit minimum occupation | `4.042e-19` |
| photon-plus-atom energy residual | `0 W/H` |
| 100-digit edge-identity residual | `2.214e-101` |
| float64 escape vs 100-digit reference | `4.882e-16` |

The spectral quantities here are signed source moments
`sum_b J_b nu_b^r`, with units `Hz^r s^-1` per H. They are not yet the
source-conditioned COM–KHW jump moments of v0.51.

## Disclosed validation deviation

The preregistered validation matrix initially used a `<1e-12` threshold for a
first-order comparison of the nearest internal grid point with the separately
cubic-interpolated public `z=1100` output. The observed relative differences
were `5.992e-11` for `x_e` and `1.478e-10` for `T_m/T_r`; the initial threshold
was therefore not met and is not reported as met.

This comparison was reclassified as a non-load-bearing grid/interpolation
diagnostic. The load-bearing instrumentation gates are the exact binary and
history hashes and the complete internally emitted state. The physical edge,
energy, JVP, positivity, dense/Schur, and high-precision thresholds were not
changed after observing the data.

## Software verification before Git sealing

```text
artifact verifier:          PASS
repository quick verifier: PASS
repository all verifier:   PASS
fast tests:                96 passed, 24 deselected
slow scientific tests:     24 passed across 8 files
scientific verifier:       PASS
```

The scientific verifier executes every slow node in a fresh interpreter to
avoid a known extension-module teardown stall while preserving the exact
collected test set. Fresh-bundle and patch replay are performed after the Git
payload is sealed.

## Explicit firewall and open claim

The v0.52 result remains fixed:

```text
x_b=x_1s f_nu_b, raw Aup/Adn, and completed Tvv
    are not literal physical finite-volume photon cells.
```

Only two native virtual centres lie inside the v0.51 production core
`|x|<=4.25`. Centre overlap does not define source/target cell boundaries or
conditional jump moments. The native quantity measured here is a
state-dependent, escape-compressed net trajectory source; v0.51 `C0` is an
occupation-independent event-mass tensor. Their ratio is not a physical
normalization and was not fitted.

## Immediate next stage

**PR-04B2B — measure-preserving native-to-17-cell partition and trajectory
parity** must:

1. byte-lock and audit the canonical `two_photon_tables_hires.dat` as a
   reference/refinement lane without silently changing production `NVIRT=311`;
2. reconstruct native cell boundaries rather than infer cells from centre
   inclusion;
3. determine whether a positive conservative projection to the 17 v0.51 cells
   can preserve the required zeroth through fourth moments;
4. publish an identifiability theorem or no-go result if the map is
   underdetermined;
5. compare source-conditioned native and COM–KHW actions at multiple
   predeclared FLRW snapshots without a free scale;
6. keep PR-04 open unless normalization, conservation, conditional moments, and
   trajectory parity close on one common measure.

## Tool and remote status

The coding and research harnesses were byte-locked, validated, and used to
structure the research contract, evidence ledger, adversarial hypothesis audit,
and validation matrix. Wolfram and Precise Special Functions were not exposed
in this runtime; SymPy exact algebra, mpmath at 100 digits, direct canonical C
execution, and independent NumPy dense/Schur calculations were used instead.

The live GitHub connector was also not exposed. The owner performs fetch,
push, and PR creation locally. No remote update is claimed without a durable
remote receipt.
