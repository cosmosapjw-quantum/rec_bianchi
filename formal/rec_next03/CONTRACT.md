# REC-NEXT-03 conditional formula and authority contract

## Status and scope

This package is a **nonauthoritative conditional proof contract**.  It records
formulae that can be checked exactly, the premises under which they hold, and
the authority or data that is still absent.  A proof or CAS result from this
directory is not source-identical directional data, an implementation-parity
result, a production admission, or a scientific pass.

The continuation base is commit
`6f6ed7720505537c9f404656cb2bc53d117e40ab` with tree
`da55957cfc70f76120724677431b351c5f52d019` and parent
`7adb61ed0f391f62ca2a43b7d8f9e6cb0933da0a`.  The scientific terminal and
claim remain, respectively:

```text
BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT
NO_PASS_REC_PHYSICAL_SPLIT
```

## Imported evidence seals

These hashes identify inputs; they do not elevate their claims.

| Input | SHA-256 | Role |
|---|---|---|
| `Pasted markdown(20260831-031556).md` | `bdc46bf765a53699f8bd20832d6032562f32b276e06cb4c501613743ca5c1c07` | nonauthoritative audit narrative |
| `REC_BIANCHI_FORMULA_DERIVATION_PACKAGE_20260831(1).zip` | `15f0d1af469f333d14488900b6ef031aaba071643efecdc850f4720aa7155e12` | proposed formula package |
| package README | `3c38afe7cb83f95e45374b022f8d8549f3ab563d12edcaa7b3d07b22d88df427` | package scope |
| package derivation report | `f933b67c1a5e2f4dd2d4be039b8177d7661523cbcc897d1699dc696239438bb4` | formula derivations |
| package formula-contract JSON | `49754d1d7be053496856c382dede92d6dbca7b842ce0db87c27c545805fd3e56` | proposed machine contract |
| package Wolfram seed | `c5d93b7b3b46d5abc370f9780926760e7491886b2c488bc638f47e24aba51471` | exact-check seed |

`SOURCE_MAP.json` records the additional harness, xAct, and repository
provenance.

## Mathematical conventions

- Metric signature: `(-,+,+,+)`; spatial orientation: `epsilon_123=+1`.
- `nu` is ordinary frequency in hertz; photon energy is `h nu`, with
  `h=2 pi hbar`.
- Angular weights are positive and sum to one.
- Occupation `f` is a dimensionless nonnegative phase-space scalar.
- Original-HyRec spectral distortion `Delta_f=f-f_ref` is signed and is a
  different stored variable from `f`.
- Geometric rates and face-relative speeds have units `s^-1`.

## Conditional formula layer

### Rotation-free hydrogen boost

Under an approved normal tetrad, `|beta|<1`, and no extra spatial rotation,
the proposed standard boost is

```text
u_H^a = gamma (u_n^a + beta^i e_i^a)
D = gamma (1 - beta dot e_n)
nu_H = D nu_n
e_H = [e_n + (((gamma-1)(beta dot e_n)/beta^2)-gamma) beta] / D
R_H = R_n + D0(log D)
```

Exact orthonormality, determinant `+1`, and aberrated unit norm are formula
checks only.  `HYDROGEN_STANDARD_BOOST_TETRAD_V1` is a proposed ID.  It must
not be silently aliased to the repository's existing generic tetrad tag.

### Moving Doppler coordinate and three distinct zero surfaces

For

```text
x = (nu_H - nu0) / Delta_nu_D
```

the speed relative to a moving face `x_b(t)` is

```text
v_b = ((nu0 + x_b Delta_nu_D) R_H - nu0_dot) / Delta_nu_D
      - x_b D0(log Delta_nu_D) - x_b_dot.
```

The following events are separately typed and are not interchangeable:

| Event | Guard | Meaning | Required handling |
|---|---|---|---|
| characteristic turning | `R_H=0` | frequency characteristic stalls/turns; virtual-spike expressions containing `1/|R_H|` are singular | dedicated turning policy |
| red-face topology | `v_red=0` | red incoming/outgoing ownership changes | red event and restart |
| blue-face topology | `v_blue=0` | blue incoming/outgoing ownership changes | blue event and restart |

Red inflow is `v_red>0`; blue inflow is `v_blue<0`; equality is grazing.
Only for a static line and grid does

```text
v_b = ((nu0 + x_b Delta_nu_D) / Delta_nu_D) R_H.
```

Even then, sign and zero equivalence require positive face frequency and
positive Doppler width.  On a moving grid, neither implication is generally
valid.

At a transversal face event, the supplied identity-reset saltation formula is
conditional on a nonzero guard derivative:

```text
delta_t_star = -(g_y delta_y_minus + g_p delta_p)
               / (g_t + g_y F_minus)
S_event = I + (F_plus-F_minus) g_y / (g_t + g_y F_minus).
```

Simultaneous zero nodes require a single accepted transaction.  Tangential
grazing is fail-closed; an epsilon replacement of the speed is forbidden.  The
left and right upwind derivatives at zero differ unless the two traces agree,
so no ordinary Frechet JVP exists at that switch in general.

## Variable and unit firewalls

### Signed distortion versus total occupation

The virtual spike acts on signed `Delta_f`:

```text
Delta_f_minus = T Delta_f_plus + (1-T) Delta_f_eq.
```

A total-occupation update is valid only after an explicit, approved reference
field adapter:

```text
f_minus = T f_plus + (1-T) (f_ref + Delta_f_eq).
```

The reference field, its frame dependence, its bytes, and the adapter JVP must
be bound.  A virtual-spike output must never be passed directly to a positive
total-occupation source law.

### Packet rates versus occupation rates

The one-photon pair `(eta,kappa)` has occupation-rate units `s^-1` and acts as

```text
C_occ = eta (1+f) - kappa f.
K_1gamma = c^3 n_H A_ul phi(nu) / (8 pi nu^2)
eta_1gamma = K_1gamma x_u
kappa_1gamma = K_1gamma (g_u/g_l) x_l.
```

Two-photon and Raman table coefficients instead produce photon-packet rates
per hydrogen atom per second:

```text
R_2gamma,s = K_s [x_u(1+f_t)(1+f_c) - g_u1 x_1 f_t f_c]
R_Raman,s  = K_s [x_u f_c(1+f_t) - g_u1 x_1(1+f_c) f_t].
```

They cannot be added to the one-photon occupation action.  The typed
conversion is

```text
C_occ_iq = (n_H / mu_i) sum_s B_is R_sq.
mu_i = (8 pi / (3 c^3)) (nu_hi^3 - nu_lo^3).
```

The factors `n_H/mu_i`, the deposition `B_is`, profile/line normalization, and
resonant channel ownership must each be applied exactly once.  In affine form
`chi=kappa-eta` may be negative; nonnegativity belongs to the microscopic pair,
not to `chi`.

For constant microscopic coefficients, the conditional exact transfer is

```text
f_1 = exp(-chi dt) f_0 + eta (1-exp(-chi dt))/chi,
chi = kappa-eta,
lim_(chi->0) f_1 = f_0 + eta dt.
```

An implementation needs a stable small-`|chi dt|` evaluation and the complete
analytic JVP; rejecting every negative affine `chi` would incorrectly reject
population inversion even when `eta` and `kappa` are nonnegative.

## Deposition and remap obligations

Any deposition matrix must obey

```text
B_is >= 0,  sum_i B_is = 1,  sum_i E_i B_is = E_s.
```

Its moving JVP includes `dn_H`, `dmu_i`, `dB_is`, and `dR_sq`.  Adjacent
two-node barycentric deposition is unique only after adding and approving a
nearest-bracketing-node locality/minimal-support axiom.  The proposed ID
`ADJACENT_TWO_NODE_BARYCENTRIC_DEPOSITION_V1` is not that approval.

For a moving map, the complete deposition tangent is

```text
delta F_iq = (delta n_H/n_H - delta mu_i/mu_i) F_iq
             + (n_H/mu_i) sum_s (delta B_is R_sq + B_is delta R_sq).
```

A fixed-node remap must satisfy positivity and the discrete geometric
conservation laws, together with their differentiated forms.  A Lagrangian
path avoids that remap but still requires an executable backtraced sampler,
accepted directional history, and event/restart contract; a mode string is not
an implementation.

## Proposed IDs are not authority

The following strings identify review candidates only:

- `HYDROGEN_STANDARD_BOOST_TETRAD_V1`
- `TOTAL_OCCUPATION_FROM_HYREC_DISTORTION_V1`
- `LAGRANGIAN_BACKTRACED_FACE_SAMPLER_V1`
- `ADJACENT_TWO_NODE_BARYCENTRIC_DEPOSITION_V1`
- `ZERO_SPEED_EVENT_SALTATION_ACCEPTED_TRANSACTION_V1`

No digest-shaped string, boolean, theorem, CAS receipt, or local execution may
approve one of these IDs.  Approval requires a separately authenticated
repository authority record and source-byte verifier.

## Mutation boundary

The formal execution prompts authorize no repository source, test, evidence,
branch, PR, or claim mutation. Before evidence only, a local Codex executor
may provision the exact requested formal dependencies through
`scripts/provision_rec_next03_formal_toolchains.py` in a caller-selected
external root; that setup may materialize the pinned Lean/mathlib workspace
and records its own nonauthoritative receipt. Evidence execution itself may
create only disposable build state and explicit receipts in a caller-selected
directory outside the Git worktree, with network disabled by the verified
namespace. A local executor must preserve raw receipts as archival seals and
compare a canonical semantic projection separately. Missing tools or premises
yield `UNEXECUTED_ENVIRONMENT_GAP` or a fail-closed result, never a synthetic
pass.

The complete stable obligation list is in `OBLIGATIONS.json`.  Tool requests
and execution boundaries are in `TOOLCHAINS.lock.json` and `prompts/*.json`.

## External Wolfram license-slot boundary

A Wolfram runtime message that identifies license-slot contention or a
license/activation availability boundary is external execution capacity, not a
counterexample to any encoded formula. The isolated runner records each failed
probe/execution attempt, waits at most 3600 seconds in 30-second polls, and
retries only this classified availability case. It never activates, relicenses,
installs, or kills another Wolfram job. If capacity does not recover by the
deadline, the Wolfram backend is `ENVIRONMENT_GAP`, never `FAIL` or `PASS`.
Any non-license formal-command failure remains a fail-closed `FAIL`.
