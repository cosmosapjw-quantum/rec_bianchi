# Verification design and results

The common ledger aggregates by `max(normalized violation)` and never by sum.
All 3 snapshots and 6 packets pass,
with `epsilon_common=0.0`. The canonical JSON round trip and
SHA-256 digest are exact. The 120-digit 2x2 Schur residual is
`0.0`.
