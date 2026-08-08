# PR-05C2B explicit-closure optimized macro formalism

The stage keeps the original-HyRec scalar boundary history and the 35-state
COM--KHW state representation-local.  Directional boundary data are supplied
by an explicitly noncanonical positive closure.  Source-temperature frequency
faces and mode measures are recomputed exactly; conductances use a positive
symmetric thermodynamic closure whose discrepancy is measured against direct
selected-pair COM--KHW quadrature.

The collision hot path contracts all unordered state pairs through vectorized
harmonic tensors.  Residual evaluations use an action-only path that omits
entropy/four-force diagnostics.  Analytic JVPs may be applied in batches; the
bounded 35x26 reference Jacobian is assembled in chunks without materializing
a dense identity.

A canonical macro residual is

```text
R = f - f_old - dt [ C_Bose(f) + L_frequency(f) + S_interface ].
```

At z~900 and z~1100 a diagonal/AP-initialized GMRES path converges.  At z~1300
an exact batched dense reference resolves the cancellation-dominated system.
This is a bounded reference solver, not the final scalable production path.

The result is an explicit-closure outcome: angular momentum is not recovered
from scalar HyRec data, P0 remains the production face fallback, and selected
thermodynamic conductances carry a measured closure uncertainty.  No fitted
normalization is introduced.
