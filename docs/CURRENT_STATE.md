# Current scientific state

## Summary

The durable endpoint is **PR-04C3 / v0.57**. PR-01 through PR-03 are complete,
and **PR-04 is now complete at the explicitly bounded source-conditioned
split-domain operator-contract level**.

The original-HyRec native radiation state and the 35-state COM–KHW state remain
representation-local. Their interface at `x=+-21.25` is coupled only through
single-owner photon-number and exact face-energy packets. v0.57 places the three
source-conditioned lanes near `z=1300,1100,900` into one typed common ledger,
but applies every load-bearing gate separately at each redshift. Signed
cross-snapshot summation and averaging are forbidden.

The next bounded stage is **PR-05A: BackgroundSnapshot/RadiationFeedback schema
and primitive original-HyRec operator source lock**. Full trajectory integration
belongs to later PR-05 sub-stages, and FLRW recombination-history parity belongs
to PR-06.

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

Constants `c`, `h`, and `k_B` remain explicit. The implemented sector is
homogeneous and scalar. Bianchi geometry enters through `BackgroundSnapshot`
characteristics and never through type-dependent local atomic coefficients.

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

The exact boundary owners are byte locked:

| Side | State | Index | Cell interval in x | Physical face |
|---|---|---:|---|---:|
| red | `FR00` | 29 | `[-21.25,-16.25]` | `-21.25` |
| blue | `FB02` | 34 | `[16.25,21.25]` | `+21.25` |

For integrated transfer magnitude `q_s=Delta t Phi_N^s`, the isotropic scalar
occupation increment is

```text
Delta f_(i_s,a) = sigma_s n_H q_s / g_(i_s),
sigma_red=-1, sigma_blue=+1,
sum_a w_a=1.
```

The exact transported energy uses the interface face frequency. The difference
between exact face energy and the broad finite-cell centroid is retained as an
unresolved representation correction and is never reassigned to atomic recoil.

## Positive coupled interface operator inherited from v0.56

The production variables are

```text
f=exp(u)>0,
rho_s=exp(v_s)>0.
```

The bounded coupled residual is

```text
R_f = f-f_old-Delta t C[f]-sum_s rho_s Delta f_s,
R_rho,s = rho_s-1,
```

with exact analytic matrix-free JVP. Strict net-residual Newton is attempted
first. Only after documented line-search stagnation may convergence be accepted,
and then only when both the gross-term normwise backward error and independent
photon-number closure are below `1e-11`.

The dilute-occupation-normalized net residual floor near
`1.73712431307357e-10` remains disclosed as a diagnostic and is not relabelled
as a strict `1e-11` pass.

## v0.57 componentwise common ledger

The snapshots are independent evidence lanes, not consecutive timesteps of one
integrated solution. The common ledger is therefore an ordered object

```text
L_common = {z1300: L_1300, z1100: L_1100, z900: L_900}
```

with one schema, unit/sign registry, six unique packet IDs and a complete
SHA-256 provenance chain. Its aggregate diagnostic is

```text
epsilon_common = max_k max_j normalized_violation(L_k,j),
```

never a signed sum or average.

The production ledger is

```text
schema:                  PR04C3_COMMON_INTERFACE_LEDGER_V1
common-ledger SHA-256:   0495d07ae4db9a53369eccac793fbc15f45396b35bec5bba46af6e865e53af53
snapshot lanes:          1300, 1100, 900
packet count:            6
epsilon_common:          0
state classification:    OPERATOR_VERIFICATION_Q_ACTIVITY_1
direct state remap:      FORBIDDEN_NOT_USED
fitted normalization:    FORBIDDEN_NOT_USED
```

A deliberate adversary with residuals `(e,-e,0)` has zero scalar sum but a
nonzero componentwise maximum. It is rejected, demonstrating that the new gate
cannot hide opposite-sign errors at different redshifts.

## Componentwise scientific gates

Across all three lanes:

```text
maximum gross backward error:          1.3200190226745005e-17
maximum independent number residual:   2.5609198306764287e-14
maximum analytic/JVP relative error:    1.26832969415376e-09
maximum native direct/source residual:  3.5248307871551763e-15
maximum native Schur/direct residual:   1.1881452091534302e-15
maximum native structural edge error:  2.0517225706554158e-11
transported face-energy residual:       exactly 0
interface atom source:                  exactly 0
minimum occupation:                     strictly positive
collision entropy production:           nonpositive
restart round trip:                     exact
```

The native structural-edge threshold is the inherited `3e-11` source-arithmetic
and cancellation gate. It was not tightened post hoc to a value that the
canonical C arithmetic does not support.

Primitive, dense and Schur native actions are compared under the original source
normalization. COM collision/interface actions are compared only through shared
number and exact face-energy variables. No direct native/COM state equality is
constructed.

## Branch, provenance and independent checks

All in-step boundary-speed zeros remain localized for Bianchi II, tilted
class-B `VI_h`, and exceptional `VI_-1/9`. Future HyRec history endpoints,
duplicate packet IDs, missing lanes, changed face frequencies and inconsistent
local `n_H` fail closed.

The compiler-dependent original-HyRec executable hash is guarded by the shared
pinned-toolchain fixture, while the numerical-output hash remains
unconditional. The repository-wide AST scanner prevents a third unguarded
binary-hash assertion.

Wolfram independently verified the two-by-two Schur residual, exact pairwise
cancellation, log-variable positivity, and the difference between a zero signed
snapshot sum and a nonzero componentwise maximum. Precise Special Functions
provided 120-digit `zeta(3)`, `zeta(4)` and `Gamma(3)` references. Both pinned
research harnesses were validated and used; their ten-phase records are inside
the immutable v0.57 artifact.

## Scientific disposition and claim boundary

```text
PR-04A:       COMPLETE
PR-04B1:      COMPLETE
PR-04B2A:     COMPLETE
PR-04B2B:     COMPLETE_PASS_NO_GO
PR-04C0/C1A: COMPLETE
PR-04C1B/C2: COMPLETE
PR-04C3:     COMPLETE
PR-04:       COMPLETE_OPERATOR_CONTRACT
PR-05A:      NEXT
```

The closed claim is:

> The source-conditioned scalar split-domain interface contract is conservative,
> positive and differentiable at the declared recombination snapshots.

The following claims are deliberately not made:

- a native-derived physical COM interior trajectory;
- a full recombination-history integration;
- FLRW `x_e(z)`, visibility or CMB-spectrum parity.

Those are PR-05 and PR-06 responsibilities.

## Immediate next stage: PR-05A

PR-05A first locks the trajectory-facing schemas and the primitive original-HyRec
rate/ownership registry before changing the evolution equations. It must census
`Alpha[2]`, `DAlpha[2]`, `Beta[2]`, `R2p2s`, `A2s`, `A3s3d`, and `A4s4d`, then
publish a one-owner replacement matrix for Sobolev escape, native `A1s`
diffusion, escape-compressed `Tvv`, and scalar `Dfplus` feedback.

No compressed term may be removed until its explicit split-domain replacement
is present in the same residual and conservation ledger. The first executable
closure is a bounded one-step source-conditioned primitive residual at the three
locked redshifts, not a full history.

See `docs/PR05_PRIMITIVE_TRAJECTORY_INTERFACE_PLAN.md`.

## Remote status

Managed GitHub connector verification found PR #15 merged into `main`:

```text
remote main:  ecd2d9e8b758dd1727c060d8cf210f08e723b9cf
remote tree:  09a718222b13f6dfd4671d2e1b62cdb2ec9a880a
PR head:      bca8873df96a086f4d9ac65033ba491043d1dade
CI:           verify-durable-backup run 49, success
open PRs:     none observed
```

The v0.57 author branch descends from the exact author v0.56 endpoint rather
than the GitHub merge tree. Delivery therefore uses a self-contained feature
Git bundle whose receipt lists only v0.57 commits for cherry-pick onto a fresh
`origin/main`, plus a full recovery bundle. Shared history must never be
force-pushed.
