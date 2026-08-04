# Full Bianchi–HyRec PR-01B0 bridge audit v0.35

This artifact corrects the PR-01 bridge design before the full
Maxwellian event kernel is implemented.

## Key results

- TDD: [32m.[0m[32m.[0m[32m.[0m[32m                                                                      [100%][0m
[32m[32m[1m3 passed[0m[32m in 16.68s[0m[0m
- no-recoil Hummer line-column reproduction:
  4.148980e-13
- shift-only pair-balance residual:
  2.162873e-05
- microscopic Rayleigh recoil mean:
  -4.629199542864e-04
- v0.33 line-centre drift:
  -1.446401888909e-04
- relative mismatch:
  6.875482e-01
- production/reference shift-only M1 convergence:
  1.187774e-10

## Decision

- PR-01B0 root-cause audit: PASS
- original exact-event = v0.33 gate: SUPERSEDED
- shift-only Hummer kernel: REJECTED
- full Maxwellian microreversible event kernel: OPEN

The next artifact is PR-01B1, not a forced fit to v0.33.
