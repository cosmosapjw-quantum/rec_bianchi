# PR-04B2B plan — measure-preserving native-to-17-cell partition

## Classification

`BOUNDED_RESEARCH_PLAN / PR-04B2B / v0.54-candidate`

## Research question

Can the canonical original-HyRec frequency representation and the v0.51
17-cell COM–KHW common measure be placed on one positive, conservative
source/target partition that preserves the physically required event mass and
frequency-jump moments without a fitted normalization?

## Why a new bounded stage is required

PR-04B2A closes the physical edge normalization of the native trajectory
algebra, but only two native centre frequencies lie in the v0.51
`|x|<=4.25` core. A centre list is not a finite-volume partition. Furthermore,
PR-04B2A compares a net escape-compressed trajectory source, whereas v0.51
stores an occupation-independent source-conditioned event tensor. Direct
numeric ratios would mix two different objects.

The canonical archive contains two source tables:

```text
two_photon_tables.dat        311 rows, production NVIRT=311
two_photon_tables_hires.dat 1493 rows, reference option NVIRT=1493
```

`hyrec_params.h` explicitly presents the high-resolution table as an optional
higher-accuracy configuration. It is therefore admissible as an immutable
reference lane, but not as a silent replacement for the production operator.

## Fixed conventions

- metric `(-,+,+,+)`;
- hydrogen orthonormal tetrad;
- ordinary frequency `nu` in Hz;
- `y=ln nu`, `eta=ln a`;
- `Delta nu=nu_target-nu_source`;
- `Delta E_gamma=h Delta nu`, `Delta E_H=-h Delta nu`;
- `c`, `h`, `k_B` explicit;
- no free multiplicative scale, empirical offset, or output-fit normalization.

## B2B.1 — table and grid census

1. Record exact member SHA-256, row count, column count, energy range, and
   monotonicity for both canonical tables.
2. Rebuild source-consistent ordinary-frequency centres using the canonical
   `hc`, `fsR`, and `meR` conventions.
3. Infer admissible cell edges from the source construction, not from midpoint
   guessing alone. Where the source does not define unique edges, record the
   ambiguity explicitly.
4. Quantify the production-to-high-resolution restriction/prolongation error
   for every primitive table column and for the full source operator.

## B2B.2 — identifiability and positive projection

Let `S_native` denote a positive native event/edge measure on a source/target
partition and `S_17` the v0.51 17-cell measure. Seek a nonnegative projection
`P` satisfying at least

```text
P >= 0,
1^T P S_native = 1^T S_native,
M_r[P S_native] = M_r[S_native],  r=1,...,4,
```

with source and target conditioning preserved.

Required audits:

- rank of the moment constraint matrix;
- dimension of the feasible null space;
- positivity of the feasible set;
- uniqueness or non-uniqueness under source/target conditioning;
- sensitivity to cell-edge perturbations and production/high-resolution grid
  refinement.

If the constraints do not identify a unique map, publish a no-go theorem or a
parameterized family with explicit additional closure assumptions. Do not
select a member by matching the desired output.

## B2B.3 — source-conditioned trajectory comparison

Use predeclared FULL-mode FLRW snapshots near

```text
z = 1300, 1100, 900
```

subject to exact nearest-grid locks. At each snapshot compare:

1. canonical native primitive action;
2. dense and structured-Schur action;
3. high-resolution reference/restriction lane;
4. projected 17-cell physical action;
5. v0.51 direct COM–KHW source-conditioned event action.

The comparison must distinguish:

- occupation-independent event mass;
- state-dependent net collision source;
- redshift boundary flux;
- escape compression;
- source and target cell integration;
- ordinary-frequency jump moments.

## Hard gates

- exact canonical member hashes and source configurations;
- positive projection weights or an explicit proof that none exist;
- zeroth event-mass conservation;
- ordinary-frequency moments `r=1..4` within a predeclared refinement tolerance;
- source/target conditioning and detailed-balance compatibility;
- photon number and same-event atom+photon energy closure;
- primitive/direct/Schur parity;
- analytic/JVP parity;
- positivity-preserving implicit update;
- no free normalization;
- geometry–microphysics firewall on identical local hydrogen-frame states.

## Decision tree

- **Positive unique/refinement-stable map exists:** close PR-04B2B and proceed to
  a final PR-04 trajectory-integration closure.
- **Positive map exists but is non-unique:** publish the family and identify the
  minimum additional physical closure required; PR-04 remains open.
- **No positive moment-preserving map exists:** publish the no-go result and
  keep the native transport and COM–KHW event representations as distinct
  coupled modules. Do not force equality; revise the PR-05 interface around a
  conservative exchange contract.

## Required durable outputs

Implementation, tests, formalism, rank/feasibility proof, CSV/NPZ evidence,
source member manifests, immutable stage ZIP, Git commits, local remote-check
receipt, full bundle, and binary-safe incremental/remote-milestone/cumulative
patches.
