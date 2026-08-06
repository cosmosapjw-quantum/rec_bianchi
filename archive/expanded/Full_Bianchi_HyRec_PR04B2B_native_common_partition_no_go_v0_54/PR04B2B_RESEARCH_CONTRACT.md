# PR-04B2B research contract — native/common partition identifiability

## Classification

`BOUNDED_RESEARCH_CONTRACT / PR-04B2B / v0.54`

## Primary question

Does the canonical October-2012 original-HyRec production representation
identify a **positive, conservative and unique** projection onto the v0.51
17-cell COM–KHW core that preserves event mass and ordinary-frequency moments
through order four without a fitted normalization?

## Subquestions

1. Are the production and high-resolution tables nested discretizations with an
   archive-defined conservative restriction operator?
2. Does the canonical archive contain numerical spike boundaries, or only
   centres and already-integrated transition coefficients?
3. Can the full positive native physical edge measure be supported on the
   v0.51 interval `x in [-4.25,4.25]` while preserving `M0` and `M2`?
4. If the exterior measure is discarded, do `M0,...,M4` identify seventeen
   positive target-cell masses uniquely?
5. Which minimum interface replaces a failed direct equality without mixing an
   occupation-independent COM–KHW event tensor with an escape-compressed native
   trajectory source?

## In scope

- exact byte/member audit of both canonical two-photon tables;
- production and high-resolution grid support, nesting and core-overlap census;
- explicit distinction between latent spike widths and runtime centre lists;
- positive-measure support inequalities;
- exact/numerical moment-matrix rank and null-space analysis;
- constructive positive non-uniqueness witnesses;
- fixed centre/uniform-cell feasibility controls;
- fail-closed decision and next conservative exchange contract.

## Out of scope

- inventing table-generation metadata absent from the canonical archive;
- choosing maximum entropy, optimal transport or another regularizer and
  presenting it as source-derived;
- changing production `NVIRT=311` to the 1493-row reference configuration;
- fitting v0.51 event mass to v0.53 net trajectory flux;
- multi-snapshot parity after the common-map identifiability gate fails;
- PR-05 background integration or PR-06 monolithic history parity.

## Conventions

- metric `(-,+,+,+)`;
- hydrogen orthonormal tetrad;
- ordinary frequency `nu` in Hz;
- `x=(nu-nu_Lya)/Delta_nu_D`;
- `Delta nu=nu_target-nu_source`;
- `Delta E_gamma=h Delta nu`, `Delta E_H=-h Delta nu`;
- `c`, `h`, and `k_B` explicit;
- no free scale, offset, post-hoc output matching, or silent grid substitution.

## Evidence hierarchy

1. canonical archive bytes, source and bundled documentation;
2. v0.51/v0.53 durable NPZ evidence;
3. exact algebra and positive-measure inequalities;
4. independent high-precision/numerical rank and LP checks;
5. primary HyRec and truncated-moment literature for interpretation.

## Completion bar

The bounded stage may close only if it records exact table hashes and
configurations, proves either existence/uniqueness or a precise no-go, provides
constructive evidence, preserves all earlier firewalls, passes targeted and
regression tests, and packages an immutable ledger/manifest/ZIP. A no-go closes
PR-04B2B as an informative result but does **not** complete PR-04.
