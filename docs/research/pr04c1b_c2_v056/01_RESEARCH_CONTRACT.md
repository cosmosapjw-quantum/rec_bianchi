# PR-04C1B/C2 v0.56 Research Contract

## PRIMARY_RQ

Can the six source-identical v0.55 interface packets be coupled to the existing
`FR00`/`FB02` COM--KHW far-boundary states by a single-owner implicit operator
that is positive, photon-number conservative, transported-photon-energy
conservative, restartable, and branch-event exact, without a native-to-COM
state remap or fitted normalization?

## SUB_RQS

1. What exact state indices, intervals, measures, orientations and energy
   centroids own the two outer faces?
2. How is a packet rate in `photons H^-1 s^-1` converted to a dimensionless COM
   occupation update without losing units or angular normalization?
3. How must face-frequency energy be represented when the destination state is
   a finite interval whose mode-weighted centroid differs from the face?
4. What block residual/JVP and nonlinear variables preserve positivity and
   avoid a singular number--energy parametrization?
5. How are red/blue speed zeros localized for Bianchi II, class B and
   exceptional `VI_-1/9`, and what remains outside PR-04C1B/C2?

## IN_SCOPE

- homogeneous scalar radiation sector;
- exact existing 35-state COM--KHW network;
- v0.55 source-identical packets near z=1300, 1100 and 900;
- `FR00=[-21.25,-16.25]`, `FB02=[16.25,21.25]`;
- log-positive resolved occupations;
- nonnegative integrated transfer magnitudes;
- analytic matrix-free JVP and Newton--GMRES;
- number, transported-energy, atom-source, restart and branch ledgers;
- regression hardening of the compiler-dependent HyRec binary hash gate.

## OUT_OF_SCOPE

- direct native-to-35-state or native-to-17-cell state equality;
- full recombination-history integration (PR-05);
- FLRW history parity (PR-06);
- angle-resolved original-HyRec boundary intensities not present in v0.55;
- interpreting the finite-cell centroid as the exact transported photon energy;
- fitted scale, maximum-entropy or optimal-transport closure.

## CONVENTIONS

Metric `(-,+,+,+)`; ordinary frequency in Hz; `c,h,k_B` explicit;
`x=(nu-nu_Lya)/Delta_nu_D`; positive packet magnitude follows its direction;
red face is the left face of `FR00`; blue face is the right face of `FB02`;
angular quadrature weights sum to one.

## EVIDENCE STANDARD

Canonical repository bytes, source-identical HyRec instrumentation, exact NPZ
state registries, analytic identities, independent high-precision checks,
unit tests that are observed RED before implementation, full fast and slow
regressions, and immutable receipts. Transcript claims are not evidence.

## COMPLETION BAR

- exact boundary adapter with no inferred cell geometry;
- dimensional identity `Delta f = sign n_H q / g_cell` verified;
- exact number and transported-energy cancellation, zero interface atom source;
- face/cell energy mismatch explicitly retained in an unresolved correction;
- analytic JVP relative error <1e-8 and nonlinear residual <1e-11;
- strict positivity and collision entropy/free-energy gate;
- all in-step speed zeros localized rather than endpoint-classified;
- guard-off collision action exact;
- source-conditioned three-snapshot closure evidence;
- common binary-hash gate plus a fail-fast policy scanner;
- git bundle deliverables.
