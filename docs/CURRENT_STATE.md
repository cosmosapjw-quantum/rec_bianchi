# Current state

- Durable local stage: **PR-05C2C1B2B1D / v0.72**.
- Status: `PASS_PR05C2C1B2B1D_PARENT_PROVENANCE_FIREWALL_BIANCHI_II_PROVIDER_PILOT_R3_OPEN`.
- The dual-harness blocker audit showed that the locked `z~1100` COM fixture is
  an operator-verification state, not a previous accepted trajectory state.  It
  is now explicitly tagged `OPERATOR_VERIFICATION` and fails closed at the
  production macro boundary.
- A production parent is a content-addressed `AcceptedRadiationParent` carrying
  its accepted-history index/hash, atomic-state hash, background-sequence hash,
  network hash, interface hash and branch id.  Only
  `SOURCE_DERIVED_ACCEPTED` may enter the production continuation factory.
- The v0.72 source-derived object is a **schema witness only**.  No physical
  source-derived accepted parent has yet been reconstructed.
- The uploaded `bianchireview87` archive is byte-locked and supplies a read-only
  orthogonal, expanding Bianchi-II provider pilot.  Over one canonical
  `Δη=8.49e-5` interval its maximum normalized-state endpoint error against the
  locked v0.48 sequence is `2.8611e-7`.
- The provider reconstructs physical `H`, `sigma`, `N` and cosmic time, emits a
  D-normalized chart event for Bianchi IX recollapse, and fails closed for
  tilted exceptional `VI_-1/9` and every unvalidated family.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon,
  two-photon/Raman, and characteristic-source adapters remain unaffected.
- No all-11 provider support, finite-tilt provider validation, physical macro
  convergence, preconditioner selection or Rust production backend is claimed.
- Next: **PR-05C2C1B2B1E source-derived accepted-parent reconstruction at
  `z~1100`, Bianchi II**, using dynamic background microsteps and exactly-once
  canonical history commit.
