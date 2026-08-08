# Current state

- Durable stage: **PR-05C2C1B2A / v0.68**.
- Status: `PASS_PR05C2C1B2A_CANONICAL_TWO_PHOTON_RAMAN_SOURCE_ADAPTER_PRECONDITIONER_MULTI_MACRO_OPEN`.
- The canonical October-2012 `two_photon_tables.dat` member is byte locked and
  its 2s, 3s/3d and 4s/4d two-photon/Raman threshold registry is explicit for
  all 311 virtual bins.
- The `hydrogen.c::populateTS_2photon` real-to-virtual, virtual-to-real and real
  diagonal additions are reproduced against the original C source with maximum
  relative residual `1.64e-14`; detailed-balance ratios are exact at float64
  resolution.
- A separate positive paired scalar two-photon/Raman source implements the
  stimulated factors, energy relation, LTE/Planck null and analytic JVP.  It is
  a theory-contract adapter and is **not** relabelled as a coefficient
  decomposition explicitly stored by original HyRec.
- Canonical analytic-JVP gross residual is `7.71e-9`; the tiny far-wing
  active-edge diagnostic is `4.61e-7`.  The physical paired-action JVP residual
  is `3.72e-9` and the maximum Planck-null residual is `3.21e-14`.
- No global normalization is fitted.  Positive forward/reverse rates extend
  down to about `1.09e-66 H^-1 s^-1` in the randomized audit.
- PR-05 remains in progress.  A measured entropy/nullspace-preserving
  preconditioner, physical characteristic coupling of the canonical source and
  at least four canonical macro intervals in all nine locked lanes remain open.
- Next: **PR-05C2C1B2B measured preconditioner and multi-macro closure**.
