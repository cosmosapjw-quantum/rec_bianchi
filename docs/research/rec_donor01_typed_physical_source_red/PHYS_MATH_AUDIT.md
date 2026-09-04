# PHYS-MATH audit — REC-DONOR-01 RED

## Verdict

```text
status        PASS_FOR_TEST_CONTRACT
physics pass  NOT CLAIMED
P0            0 within the frozen RED scope
P1            0 within the frozen RED scope
```

The audit asks whether the proposed tests encode a coherent physical source
contract.  It does not validate any source values because the implementation
and physical payload are deliberately absent.

## Definitions and conventions

- Photon occupation `f` is dimensionless and nonnegative.
- The source coordinate is photon energy in joules.
- The source time basis is physical seconds.
- `eta` and `kappa` are separately nonnegative and have units `s^-1`.
- `chi=kappa-eta` is a signed derived rate with units `s^-1`.
- The source frame is the declared hydrogen/atomic rest frame.
- The local-observer frame is downstream and excluded.
- No natural-unit substitution is made; `c`, `hbar`, and `k_B` remain external
  physical constants wherever later adapters require them.

## Algebra

For

```text
C[f] = eta*(1+f) - kappa*f,
```

expansion gives

```text
C[f] = eta - (kappa-eta)*f.
```

The tangent with independent primary coefficients is

```text
dC = (1+f)*deta - f*dkappa - (kappa-eta)*df.
```

The exact binary-friendly fixture used by the test is

```text
f=1/2, eta=1/4, kappa=3/4,
df=1/8, deta=1/2, dkappa=-1/4,
```

which gives

```text
dC = (3/2)(1/2) - (1/2)(-1/4) - (1/2)(1/8)
   = 13/16
   = 0.8125.
```

For `kappa>eta`, setting `C[f_eq]=0` gives

```text
f_eq = eta/(kappa-eta) >= 0.
```

For `eta>kappa`, the denominator is negative and no finite nonnegative
stationary occupation exists; the contract therefore raises a typed boundary
rather than returning a negative equilibrium.  At `eta=kappa=0`, `C=0`
identically.  At `eta=kappa>0`, the source is constant positive and has no
finite equilibrium; the later implementation must keep that distinction.

## Dimensional checks

```text
eta*(1+f)       s^-1
kappa*f         s^-1
C[f]            s^-1 = df/dt
packet kernel   photon_packet H^-1 s^-1
deposition      H m^-3 / phase-space measure
output          s^-1 after exactly one declared conversion
```

A packet kernel cannot be added directly to `C[f]`; their units and state
meanings differ until deposition is applied.

## Nonlocality counterexample

For two companion bins with weights `(w1,w2)`, consider spectra

```text
A=(f1,f2),  B=(f1,f2+1).
```

They agree at the first target bin.  A local pair evaluated there is identical,
but a nonlocal packet functional

```text
R(A)=w1*f1+w2*f2,
R(B)=w1*f1+w2*(f2+1)
```

differs by `w2`.  Thus two-photon/Raman dependence cannot be identified from a
single local affine pair without an additional approximation theorem.

## Positivity, thresholds, and regularity

- Negative or nonfinite primary coefficients are rejected.
- Negative total occupation is rejected.
- The declared support uses lower-inclusive and upper-exclusive endpoints and
  an exact zero-outside policy.  This is a contract fixture, not a universal
  statement about every physical line profile.
- The RED does not claim differentiability at an event surface or at a support
  policy switch.
- No positivity claim is inferred for an integrated or projected state.

## Representation and rank

The source law is a spectral physical object.  Angular grid and PSTF bindings
are consumer realizations and must not change its semantic identity.  A fixed
26-node face cannot represent arbitrary scalar rank because its finite sample
space has finite dimension and because rank/exactness also depend on the
realized evaluation matrix, weights, basis convention, and conditioning.  The
contract therefore rejects the combination `node_count=26` plus
`ARBITRARY_HIGH_RANK` without claiming that every bounded 26-node use is
invalid.

## Hidden assumptions and limits

1. The local affine law is bosonic and pointwise in the represented spectral
   coordinate.  It is not a complete HyRec collision operator.
2. Detailed balance is tested only for the local affine branch with
   `kappa>eta`.
3. The nonlocal kernel fixture is discrete and establishes typing/nonlocality,
   not a physical two-photon spectrum.
4. The trajectory binding is identity/provenance, not a solved background.
5. The contract does not identify global tilt, electron tilt, or observer
   motion.
6. The moment-map test establishes a firewall, not a closure theorem.

## Adversarial mutations

| Mutation | Required result |
|---|---|
| delete stimulated `+eta*f` contribution | affine-action test fails |
| replace primary pair by unsigned `chi` | negative-`chi` test fails |
| mutate payload SHA | source semantic identity changes |
| include angular representation in source hash | grid/PSTF neutrality test fails |
| treat packet rate as `s^-1` occupation rate | units/deposition test fails |
| omit restart identity | trajectory mutation test fails |
| use finite-difference JVP under analytic label | JVP-method test fails |
| accept arbitrary-rank 26-face | rank-firewall test fails |
| apply local observer boost inside REC | frame-firewall test fails |

## Formal-tool boundary

Fresh connected Wolfram context and evaluator calls both returned HTTP 502
before a kernel result.  No Wolfram result is used as evidence.  The identities
above are exact elementary algebra recorded for later independent replay.
