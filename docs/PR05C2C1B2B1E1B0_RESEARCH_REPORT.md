# PR-05C2C1B2B1E1B0 research report

## Decision

`PASS_BOUNDED_NO_GO_DYNAMIC_ATOMIC_MACRO_OWNERSHIP_OVERLAP_SPLIT_DOMAIN_REPLACEMENT_REQUIRED`

The proposed immediate dynamic atomic/history macro is blocked before nonlinear
solution.  This is not a solver-convergence failure.  It is a process-ownership
failure: the full original-HyRec native block and the v0.74 COM interior act on
the same physical frequency support.

## Quantitative evidence

- Native spikes in COM support: **8**, indices
  `136..143`.
- Adjacent native diffusion edges: **6**
  interior, **2** crossing, and
  **70** exterior.
- Canonical Aup rate mass in the COM interior:
  **98.015879639%**.
- Canonical Adn rate mass in the COM interior:
  **98.002814188%**.
- Absolute real-to-virtual coupling fraction in the interior:
  **99.854013757%**.
- Absolute virtual-to-real coupling fraction in the interior:
  **97.207854504%**.

The result is insensitive to any inferred native cell width because no such
width is introduced.  The obstruction follows from the canonical point-spike
centres and the source matrices themselves.

## Claim boundary

Durable: support census, overlap theorem, fail-closed production gate, explicit
target ownership contract, tests, plots, CSV/NPZ evidence.

Not claimed: exterior Schur operator implementation, owner swap, full dynamic
atomic macro, accepted-history append, or full Bianchi--HyRec endpoint.
