# REC progress ledger through 2026-09-04

## REC-owned milestones

### PR #54 — representation-neutral source ownership

REC was narrowed to the owner of physical recombination source data and provenance. BASS owns state evolution and representation adapters. Paper-I/II effective-temperature constructions remain static information diagnostics, not transport closures.

### PR #55 — trusted RF-00 payload gate

The current BASS R6 source was executed with the admitted RF-00 wheel and installed shared object, with the development override unset:

```text
focused source suites      21/21
backend cone               54/54
unverified diagnostics     0
source/binding hashes      deterministic
source worktree            clean
```

This opened the BASS adapter sequence but did not create a physical REC source.

## BASS downstream milestones relevant to REC

```text
R7 expected adapter RED                       PASS
R8 constant-pair grid/coefficient adapter     PASS 33/33
R8B trusted-native nonregression              PASS
R9 expected finite-rank parity RED            PASS
R10 bounded scalar parity                     PASS 49/49
R10 post-GREEN hostile audit                  COMPLETE
R10A projection-authority RED contract        PUBLISHED / EXECUTION PENDING
```

R10's strongest numerical observation at rank 8 is:

```text
max parity residual       1.4226467226485795e-14
max Gram defect           5.662137425588298e-15
Gram condition inf        1.0000000000000364
declared tolerance        2.0e-13
```

This is same-implementation scalar constant-source evidence only.

## Current physical blocker

The historical phrase `SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT` must now be refined. The correct problem is not to force every model through exactly 26 directions. It is to materialize a source-identical angular interface with a declared finite subspace and a certified map.

```text
fixed 26 nodes
  = possible bounded diagnostic for a named subspace

fixed 26 nodes
  != arbitrary-higher-rank model-independent authority
```

## Claims retained

```text
REC owns primordial recombination microphysics and source provenance.
BASS owns geometry, transport state and representation consumers.
REI owns late reionization/opacity provider values.
HTT owns local-observer and processed observation response.
```

## Claims withheld

```text
physical REC source integrated in BASS
source-identical physical face admitted
full nonlocal atomic source complete
polarized REC source complete
finite-electron-tilt collision complete
REC provider export
PASS_REC_PHYSICAL_SPLIT
```
