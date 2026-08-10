# PR-05C2C1B2B1D parent-provenance and background-provider formalism

## Scope and conventions

This stage is a prerequisite stage, not a physical trajectory result.  It keeps
metric signature `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, and
homogeneous hydrogen-frame tetrad variables.

## R1: production parent provenance

A production macro parent is the tuple

```text
(occupation bytes, evidence class, accepted-history index/hash,
 atomic-state hash, background-sequence hash, network hash,
 interface hash, branch id, scalar metadata).
```

Only `SOURCE_DERIVED_ACCEPTED` may enter the production continuation factory.
`OPERATOR_VERIFICATION` and `MANUFACTURED` remain legal audit fixtures but fail
closed at the production boundary.  Exact byte serialization uses canonical
little-endian float64 occupation bytes and canonical sorted JSON metadata.

The accepted object used by this stage is a *schema witness only*.  It proves
that valid provenance is accepted and stale/mismatched provenance is rejected;
it is not a reconstructed physical parent.  Physical reconstruction is R3.

## R2: orthogonal Bianchi-II provider pilot

The provider evolves

\[
 K=N_1^2/12,\quad
 \Sigma^2=\Sigma_+^2+\Sigma_-^2,\quad
 \Omega=1-\Sigma^2-K,
\]

\[
 q=2\Sigma^2+\frac12(3\gamma-2)\Omega,
\]

\[
 \Sigma_+'=-(2-q)\Sigma_+ + N_1^2/3,
 \quad
 \Sigma_-'=-(2-q)\Sigma_-,
\]

\[
 N_1'=(q-4\Sigma_+)N_1,
 \quad
 (\ln H)'=-(1+q),
 \quad
 t'=H^{-1}.
\]

Physical tensors are reconstructed as

\[
 \sigma_{\hat a\hat b}=H\,\Sigma_{\hat a\hat b},
 \qquad N_{\hat a\hat b}=H\,\bar N_{\hat a\hat b},
 \qquad A_{\hat a}=0.
\]

The pilot is validated only for the expanding orthogonal Bianchi-II branch.
Bianchi IX requests emit a D-normalized H-zero event, tilted exceptional
`VI_-1/9` fails closed, and all other family labels remain registry/smoke only.

## Numerical closure

Maximum normalized-state endpoint error is `2.86109520186705879e-07` against the locked
v0.48 one-macro reference.  No all-family or finite-tilt provider claim is made.
