# Current state

- Durable local stage: **PR-05C2C1B2B1E1B0 / v0.75**.
- Status: `PASS_BOUNDED_NO_GO_DYNAMIC_ATOMIC_MACRO_OWNERSHIP_OVERLAP_SPLIT_DOMAIN_REPLACEMENT_REQUIRED`.
- The v0.73 source-derived parent and v0.74 positive COM collision--transport subblock root remain valid.
- A full dynamic atomic/native/history macro is not currently admissible: the complete original-HyRec native block overlaps the COM interior on eight canonical point spikes (`136..143`).
- The native diffusion graph has six nonzero interior edges, two cross-interface edges and seventy exterior edges.
- Canonical Aup and Adn rate fractions inside the COM support are `98.015879639%` and `98.002814188%`; the absolute Tvr and Trv interior fractions are `99.854013757%` and `97.207854504%`.
- Therefore full native A1s diffusion, completed Tvv and a new COM atomic source cannot be added to the v0.74 residual without duplicate owners.
- The only passing configuration is an explicit contract witness: exterior native diffusion/source, interior COM collision/source, exterior Schur Tvv and one split-domain interface owner. This is not implementation evidence.
- No native finite-volume cells are inferred and no fitted normalization is introduced.
- The v0.65 scalar theory and v0.66--v0.68 direct-node, one-photon, two-photon/Raman, and characteristic-source adapters remain unaffected.
- Next: **PR-05C2C1B2B1E1C split-domain replacement**. Dynamic macro solution, preconditioner and Rust work remain deferred until the owner swap is complete.
