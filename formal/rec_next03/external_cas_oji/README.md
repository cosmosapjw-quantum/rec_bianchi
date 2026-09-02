# REC-NEXT-03 external CAS axis: Octave / JAS / Julia

This directory adds three executable formula-oracle lanes to the active
`rec_bianchi` PR #47 lineage.  It does not modify production physics.

## Independence classes

- GNU Octave with the `symbolic` package is mandatory execution evidence but is
  explicitly classified as a **SymPy-backed cross-language wrapper**.
- Java Algebra System (JAS) is an independent exact Java polynomial core.
- Julia combines Symbolics.jl for differential identities with Nemo/FLINT exact
  polynomial arithmetic.

The aggregate gate requires all three engines to execute, but counts only JAS
and Julia/Nemo-Symbolics as distinct independent algebra cores.

## Physical scope

The identities are taken from the actual REC code paths:

- `background/characteristics.py`;
- `trajectory/paired_source_transfer.py`;
- the research-only directional-face event semantics.

Conventions are `(-,+,+,+)`, `epsilon_123=+1`, explicit `c`, and code rates in
`s^-1`.  Where a BASS formula is parameterized by physical ray length `s=c t`,
`R_t=c R_s` and `V_t=c V_s`.  The REC small-beta identity branch is bounded
numerical regularization, not exact software parity.

## Claim boundary

```text
EXTERNAL_FORMULA_ORACLE_ONLY
NO_SOURCE_IDENTICAL_DIRECTIONAL_FACE
NO_PROVIDER_EXPORT
NO_PASS_REC_PHYSICAL_SPLIT
NO_BASS_AUTHORITY_REDEFINITION
NO_NUMERICAL_OR_SCIENCE_PROMOTION
```
