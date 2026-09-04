# Four-repository authority and interface policy

| Layer | Owner | REC relation |
| --- | --- | --- |
| conventions, Bianchi algebra, background and transport state | BASS | exact-pinned consumer |
| primordial recombination microphysics and source provenance | REC | owner |
| late reionization, thermochemistry and opacity | REI | future exact-pinned provider |
| local-observer boost, mask/beam/filter/nuisance response | HTT | downstream output-only consumer |

## Interface invariants

### REC → BASS

The payload must bind:

```text
species/statistics
physical frame
time or ray-length basis
energy/frequency support
source formula family
source data identity
trajectory/event identity
state-parent identity
representation/projection certificate
```

A reduced integrated state may not receive a generic frequency-dependent source without a separately admitted moment-map/closure certificate.

### REC → REI

The splice must bind the end of primordial recombination and the start of late-time reionization without letting REI silently replace REC history or REC silently absorb late-time thermochemistry.

### BASS → HTT

BASS supplies cosmic-frame outputs and formula/convention identities. HTT applies local observer motion and processed observational response. The local boost must not feed back into REC rates or BASS background evolution.

### Cross-repository admission

A join requires all of:

```text
exact commit/tree/blob pins
canonical schemas and units
component runtime receipts
coupler/interface tests
separate-effects controls
coupled residual/convergence evidence
claim-boundary reconciliation
```

Matching prose, matching formulas, or passing component tests alone are not a cross-repository compatibility certificate.
