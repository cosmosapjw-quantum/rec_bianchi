# PR-04B2B validation matrix

| Requirement | Test/check | Expected | Status |
|---|---|---|---|
| Recovery | v0.53 bootstrap/quick/fast | pass | PASS |
| Provenance | archive and table member hashes | exact | PASS |
| Table shape | production `(311,5)`, reference `(1493,5)` | exact | PASS |
| Grid monotonicity | strictly increasing energy | exact | PASS |
| Grid nesting | exact production centres in reference | report, not assume | PASS: zero |
| Core overlap | diffusion centres in `|x|<=4.25` | audit | PASS: two in each lane |
| Boundary provenance | explicit edge column/array | absent => fail closed | PASS |
| Dimension/sign | positive edge measure; `x` dimensionless | exact | PASS |
| Support theorem | native `M2/M0` versus `4.25^2` | violation proves no-go | PASS |
| Zeroth moment | core restriction fraction | report loss | PASS |
| Rank | target moment matrix | rank 5 | PASS |
| Nullity | 17-cell masses with five moments | 12 | PASS |
| Positive ambiguity | two positive weights, equal moments | constructive | PASS |
| Fixed-basis controls | centre and uniform LP | no false success | PASS: infeasible |
| No fitted scale | implementation/search audit | none | PASS |
| Source firewall | proxy/rate direct substitution | remains forbidden | PASS |
| B2B.3 trajectory parity | only after common-map gate | blocked, not fabricated | INFORMATIVE_BLOCKER |
| Targeted tests | new partition tests | all pass | PASS |
| Regression | fast suite | all pass | PENDING_SEAL |
| Scientific | slow suite | all pass | PENDING_SEAL |
| Packaging | ledger/evidence/manifest/ZIP | produced | PENDING_SEAL |
| Reproducibility | fresh bundle/patch replay | exact tree | PENDING_GIT_SEAL |
