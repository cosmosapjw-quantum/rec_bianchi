# PR-05C2C1B2B1E0 research report

## Decision

`PASS_PR05C2C1B2B1E0_SOURCE_DERIVED_BOOTSTRAP_PARENT_COUPLED_SINGLE_MACRO_OPEN`

The parent-provenance blocker is resolved at the initial-data level.  The
previous q=1 operator fixture is replaced by a deterministic state evaluated
from the accepted original-HyRec scalar history at all 35 COM centres, with an
explicit isotropic hydrogen-frame lift over 26 directions.

## Evidence

- parent SHA-256: `ec6f1a7d43807102b957befe0ef491a08e515c103124bbdcb616df08f19e3d3f`
- accepted history index: `5127`
- point-characteristic queries: `35`
- minimum occupation: `7.27920591328606731e-15`
- median activity: `995.76396007`
- median increase over q=1 fixture: `995.76396007`
- isotropy residual: `0.00000000000000000e+00`
- production provenance validation: `True`

## Adversarial result

The valid parent is not already a physical macro root.  Its initial canonical
macro acceptance metric is `1.00000000311328652e+00`.
Therefore the next stage must solve one dynamic coupled macro; this stage does
not commit a history slice or select a preconditioner.
