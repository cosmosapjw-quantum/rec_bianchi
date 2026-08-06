# PR-04C3 componentwise common-ledger formalism

## Conventions

Metric `(-,+,+,+)`; hydrogen orthonormal tetrad; ordinary frequency `nu` in
Hz; explicit `c,h,k_B`; homogeneous scalar sector. Red/blue faces are
`x=-21.25,+21.25`. Exact face energy owns the transported-energy ledger and a
pure computational crossing has zero atom source.

## Ordered common ledger

The three snapshots are not consecutive timesteps. The common object is
`{z1300:L1300,z1100:L1100,z900:L900}`. Every metric carries a unit, evidence
class, criterion, threshold and scale. The only aggregate is the maximum
normalized componentwise violation. A signed sum over redshift is forbidden.

## Native and COM comparison

Original-HyRec primitive, dense and Schur solutions are recomputed at each
snapshot. The COM collision/interface solve is rerun exactly from the v0.56
`q_activity=1` Bose-Einstein operator-verification state. The two
representations are compared only through photon number and exact face energy;
no state-vector equality or fitted scale is introduced.

## Claim

PR-04 closes only at the source-conditioned operator-contract level. Native/COM
trajectory integration remains PR-05 and FLRW recombination-history parity
remains PR-06.
