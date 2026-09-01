# Tri-repository formula synchronization — REC lane

This directory is the REC-side manifest for the BASS/REC/REI control plane.

Canonical owner registry and compiler live in `cosmosapjw-quantum/bass` under `coordination/tri_repo_sync/`. This repository remains the unique authority owner for:

- primordial H/He atomic kinetics;
- directional source-face reconstruction;
- recombination provider export and its validity/error envelope.

REC consumes BASS conventions, Bianchi algebra, and eventually the durable GR background contract by exact commit pin. It does not copy or redefine those formulas.

The current manifest preserves the active PR #47 boundary:

```text
BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT
SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT
NO_PASS_REC_PHYSICAL_SPLIT
NO_PROVIDER_EXPORT
```

This synchronization branch changes no REC production physics, tests, formal contracts, or provider authority. It only publishes typed ownership and dependency metadata. Scientific promotion, PR readiness, merge, and Jira completion remain manual.