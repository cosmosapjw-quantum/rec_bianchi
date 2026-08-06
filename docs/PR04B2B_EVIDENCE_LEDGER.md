# PR-04B2B evidence ledger

| ID | Claim | Evidence | State |
|---|---|---|---|
| E1 | The canonical production table has 311 rows and the optional high-resolution table has 1493 rows. | Byte-locked ZIP members and `hyrec_params.h`; exact shape/hash audit. | SUPPORTED |
| E2 | The tables contain one energy centre plus four rates already integrated over a latent `Delta nu_b`; they do not contain a numerical edge column. | Canonical `readme.pdf`, `hydrogen.h`, and the five-value `fscanf` loop in `hydrogen.c`. | SUPPORTED |
| E3 | Production and high-resolution centre grids are not nested. | No exact common centre among all 311 production rows; nearest-distance census. | VERIFIED |
| E4 | Both diffusion configurations place only two centres in the v0.51 17-cell core. | Source-consistent energy-to-Hz conversion using v0.51 `nu_abs` and Doppler width. | VERIFIED |
| E5 | The full positive native edge measure cannot be mapped to the core while preserving `M0` and `M2`. | Positive-support theorem: target `M2/M0 <= 4.25^2`; measured native ratio exceeds the bound. | VERIFIED_NO_GO |
| E6 | Restricting to the two core centres is not a conservative replacement for the full native source. | Core mass is less than 0.2% of the 311-state edge measure and less than 0.7% of the diffusion-80 edge measure. | VERIFIED |
| E7 | Moments `M0,...,M4` alone do not identify seventeen cell masses. | A `5 x 17` moment matrix has rank 5 and nullity 12; two strictly positive, distinct weights with identical moments are constructed. | VERIFIED_NONUNIQUE |
| E8 | Common naive closures are not hidden solutions. | Nonnegative LP is infeasible for both centre-sampled and uniform-within-cell representations of the core two-spike moment vector. | VERIFIED_CONTROL |
| E9 | Tchakaloff-type positive quadrature results are existence results, not a source of uniqueness for this map. | Curto–Fialkow, arXiv:math/0207065, plus direct rank/null-space proof. | SUPPORTED |
| E10 | Multi-snapshot parity is not identifiable before a common map or exchange contract exists. | The compared objects have different support and state dependence; B2B.1/B2B.2 gate fails before B2B.3. | INFORMATIVE_BLOCKER |

## Missing evidence

The canonical runtime archive contains no explicit numerical array of spike
boundaries, no dedicated two-photon-table generator member, and no source
statement that opens either bundled table for writing. Any historical generator
outside the canonical archive is not available as project evidence. Therefore a source-derived
finite-volume overlap operator cannot be reconstructed from the archive alone.
A later closure may be introduced only as an explicit modelling choice and
must not be relabelled as canonical HyRec provenance.

## Tool status

- Web search: primary HyRec and truncated-moment sources used.
- Wolfram: `UNAVAILABLE_IN_RUNTIME`.
- Precise Special Functions: `UNAVAILABLE_IN_RUNTIME`.
- Fallbacks: SymPy exact rank/null-space identities, NumPy SVD, SciPy HiGHS
  feasibility, direct archive/source audit, and durable v0.51/v0.53 data.
- Live private GitHub connector: not exposed; only local bundle receipt is used.
