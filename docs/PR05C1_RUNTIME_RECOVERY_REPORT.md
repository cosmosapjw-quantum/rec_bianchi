# PR-05C1 v0.62 runtime-interruption recovery report

## Classification

`RUNTIME_INTERRUPTION_RECOVERY`.

## Evidence split

- **DURABLE_VERIFIED parent:** v0.61 full Git bundle, HEAD `8a3b6452042615bc8900d65250e4bce0712706c7`.
- **PARTIALLY_RECOVERED v0.62:** two pre-existing v0.62 commits, artifact ZIP and unregistered bundle bytes survived in `/mnt/data`.
- **TRANSCRIPT_ONLY:** the first completion report's final receipts, tags and downloadable registration.
- **SUPERSEDED:** the later inference that no v0.62 bytes existed, which relied only on the incomplete generated-file registry.
- **RECONSTRUCTED:** all-trial step-doubling hardening, research/tool receipts, remote connector receipt, immutable artifact and final delivery seal.

## Root cause

The scientific stage had reached local Git/artifact generation, but conversation attachment registration did not complete. The runtime preserved repository and bundle bytes while the file registry exposed no v0.62 entry. Recovery therefore had to inspect both Git/filesystem state and the file registry rather than treating either alone as complete evidence.

## Scientific hardening found during recovery

The original adaptive acceptance used residual and positivity diagnostics from the full backward-Euler trial while accepting the two-half-step state. A RED regression demonstrated that a failed half-step could therefore be accepted. v0.62 now requires the full step and both half steps independently to satisfy convergence, positivity, backward-error and algebraic-residual thresholds. The immutable artifact records the RED/GREEN evidence.

## Recovered scientific boundary

The source-conditioned rank-one DAE controller, canonical macro history transaction and deterministic event rollback/restart are verified. Full COM-KHW/interface coupling and source-derived Bianchi boundary speeds remain PR-05C2.

## Current artifact

- `archive/bundles/Full_Bianchi_HyRec_PR05C1_adaptive_canonical_macro_v0_62.zip`
- SHA-256 `294f390aa3094092b9c54885c0fa1b305b845e2b2e7f7d5df89d16d3f4929348`
- size `24961` bytes
