# Current scientific state

## Summary

The durable endpoint is **PR-04C1B/C2 / v0.56**. PR-01 through PR-03 are
complete. PR-04A established the positive 17-cell COM–KHW common measure;
PR-04B1 locked canonical October-2012 original HyRec; PR-04B2A derived the
physical logarithmic-frequency edge flux; PR-04B2B rejected a direct global
native-to-COM remap by a support and identifiability no-go; PR-04C0/C1A then
constructed a single-owner split-domain interface and six source-identical
positive face packets at `x=+-21.25` for `z~1300,1100,900`.

v0.56 connects those packets only to the exact `FR00`/`FB02` far-boundary
states and closes the bounded positive coupled interface operator. PR-04 remains
open because the three lanes have not yet been sealed under one componentwise
common-ledger claim. The next bounded stage is **PR-04C3**.

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
collision energy: Delta E_gamma=h Delta nu, Delta E_H=-h Delta nu
interface atom source: identically zero for a pure representation crossing
```

Constants `c`, `h`, and `k_B` remain explicit. The implemented stage is
homogeneous and scalar. Geometry enters local microphysics only through the
established `BackgroundSnapshot` adapter.

## Fixed split-domain architecture

Original HyRec retains full-support radiation transport, escape and real/virtual
state algebra. COM–KHW retains the 35-state local collision, Bose stimulation,
recoil four-force and internal Liouville operator. The interface owns only the
red and blue crossings at `x=-21.25` and `x=+21.25`.

A crossing is evaluated once and applied with opposite signs:

```text
Phi_N_native + Phi_N_COM = 0,
Phi_Egamma_native + Phi_Egamma_COM = 0,
Phi_EH_interface = 0.
```

Higher moments remain representation-local. A fitted normalization, direct
state-vector equality, maximum-entropy map and optimal-transport map remain
forbidden as canonical closures.

## Exact far-boundary adapter

The adapter is read from the byte-locked v0.47 state registry rather than
inferred from centres:

| State | Index | Interval in x | Interface face | Mode measure |
|---|---:|---|---|---:|
| `FR00` | 29 | `[-21.25,-16.25]` | left/red | `1.6400603146104614e18 m^-3` |
| `FB02` | 34 | `[16.25,21.25]` | right/blue | `1.6429495492454702e18 m^-3` |

For an integrated transfer magnitude

```text
q_s = Delta t Phi_N^s                         [photons/H],
```

the scalar occupation increment is

```text
Delta f_(i_s,a) = sigma_s n_H q_s / g_(i_s),
sigma_red=-1, sigma_blue=+1,
sum_a w_a=1.
```

Dimensional check: `n_H/g_i` is dimensionless and `q_s` is photons per H, so
`Delta f` is dimensionless. Summing `w_a g_i Delta f_i` returns
`sigma_s n_H q_s`, hence photon number closes without an angular fit.

The exact transported energy is tied to the physical interface face,
`n_H h nu_face q_s`. The broad-cell mode centroid produces only a diagnostic
proxy. Its nonzero difference from the face energy is retained in an unresolved
representation-correction accumulator and is never reassigned to atomic recoil.

## Positive monolithic residual and JVP

The production variables are

```text
f=exp(u)>0,
rho_s=exp(v_s)>0.
```

The residual is

```text
R_f = f-f_old-Delta t C[f]-sum_s rho_s Delta f_s,
R_rho,s = rho_s-1.
```

The exact analytic action is

```text
D R_f[du,dv]
 = f du-Delta t D C[f](f du)-sum_s rho_s dv_s Delta f_s,
D R_rho,s[dv_s] = rho_s dv_s.
```

Newton–GMRES acts matrix-free. Central differences are an audit, not the
production Jacobian. Guard-off mode delegates to the pre-existing collision
solver and is exact.

## Resolved numerical blocker: dilute residual cancellation

For the full 35-state `q_activity=1` network, the net residual divided only by
very dilute occupations stops improving near

```text
1.73712431307357e-10.
```

This is a float64 subtraction floor after gain, loss and interface terms have
already cancelled to much smaller normwise backward error. The threshold was
not weakened and the value was not reported as a `1e-11` pass.

The accepted rule is fail-closed:

1. continue ordinary net-residual Newton while it decreases;
2. only after line-search stagnation, require simultaneously
   - gross-term normwise backward error `<1e-11`, and
   - independent photon-number closure `<1e-11`;
3. neither condition alone can declare convergence.

Across the three source-conditioned lanes:

```text
maximum gross backward error:       1.3200190226745005e-17
maximum independent number residual: 2.5609198306764287e-14
maximum analytic/JVP relative error:  1.279553711820355e-09
maximum float/mpmath discrepancy:     3.694332974648189e-15
transported-energy residual:          exactly 0
interface atom source:                exactly 0
minimum accepted occupation:          strictly positive
collision entropy production:         nonpositive
```

The gross backward-error gate measures the residual against the separately
accumulated magnitudes of the large terms and therefore diagnoses whether the
computed state solves the floating-point equations, rather than dividing a
roundoff-sized net difference by an astrophysically tiny occupation.

## Branch, restart and geometry gates

Piecewise-linear boundary speeds are integrated only after every in-step zero is
localized. The stored audit includes red and blue roots for Bianchi II, tilted
class-B `VI_h`, and exceptional `VI_-1/9`. Endpoint-only sign classification has
nonzero signed-flux error in every selected lane and is rejected.

The coupled state, both boundary accumulators, exact face-energy corrections and
solver metadata have an exact portable restart round-trip. At fixed local
hydrogen-frame state, the microphysical packet/collision action is independent
of the Bianchi label.

## Binary-hash regression hardening

PR #14 correctly moved the compiler-dependent HyRec executable hash gate into a
shared `binary_hash_is_meaningful` fixture while leaving the numerical-output
hash unconditional. v0.56 adds an AST policy scanner to the quick verifier:
any future assertion involving `ORIGINAL_HYREC_PORTABLE_BINARY_SHA256` fails CI
unless it is dominated by the shared positive gate. This prevents a third
file-local recurrence rather than merely repairing the two known call sites.

## Harness and independent checks

- Coding harness SHA-256:
  `6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4`.
- Research harness SHA-256:
  `9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934`.
- Both validators passed and the ten research phases are archived inside the
  v0.56 artifact.
- Wolfram independently returned exact number/energy cancellation, the analytic
  block-JVP factors, the finite-interval photon mode measure, and the
  mode-weighted frequency centroid.
- Precise Special Functions supplied 100-digit `zeta(3)` and `zeta(4)` values;
  the retained high-precision small-system solve agrees with float64 to
  `3.694332974648189e-15`.

## Scientific disposition and claim boundary

```text
PR-04C0:       COMPLETE
PR-04C1A:      COMPLETE
PR-04C1B/C2:   COMPLETE at bounded source-conditioned operator level
PR-04C3:       OPEN
PR-04:         IN_PROGRESS
```

The v0.56 runs use the six physical native face packets but an unfitted
`q_activity=1` COM Bose–Einstein reference state. They prove that the declared
interface operator is conservative, positive and differentiable at all three
snapshots. They do **not** reconstruct a physical COM interior trajectory from
native HyRec. v0.54 already forbids relabelling such an underdetermined state map
as canonical.

## Immediate next stage: PR-04C3

PR-04C3 must construct a **componentwise** common ledger. The three snapshots
are independent source-conditioned lanes; their signed rates must never be
summed so that an error at one redshift cancels an error at another. Closure is
therefore a vector of per-snapshot number, transported-energy, atom-source,
positivity, JVP, restart and branch gates, followed by a maximum normalized
residual.

The required final decision is one of:

1. **operator-contract closure:** all componentwise gates pass, PR-04 closes at
   the declared split-domain operator level, while trajectory integration and
   FLRW history parity remain PR-05/PR-06; or
2. **bounded no-go:** a common claim cannot be made without an independently
   source-derived COM interior state, in which case direct trajectory parity is
   explicitly blocked rather than fabricated.

See `docs/PR04C3_COMMON_LEDGER_PLAN.md`.

## Remote status

GitHub PR #14 is merged. Remote `main` is
`47106fec89c176c3f3b91ed7e4ff198dea323968`, tree
`b1cc9c0959bd89418a4f24a51959c44bb163fe88`, and contains the shared
binary-hash gate fix at PR head
`2b4419939b4a07920f0548f6cc22210e643505f4`.

The local v0.56 branch descends from the exact author v0.55 tree with a
behaviorally equivalent local gate commit, not from the GitHub merge tree.
Therefore exact remote-tree cherry-pick parity is not assumed. Delivery uses a
self-contained feature Git bundle and an ordered feature-commit receipt for
application onto a freshly fetched `origin/main`, plus a full recovery bundle.
