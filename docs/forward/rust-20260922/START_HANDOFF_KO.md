# selected-He Rust fixed-input port — start handoff

Repository: `cosmosapjw-quantum/rec_bianchi`; branch: `forward/rust-he-sources-20260922`. Original base: `5a09f3797210284f83a1a1adb0e0092d1ac48475`. Actual tested source: `2ee3760870f9ac47eaab518a4c4a907f1a3f6f85`. Resolve the evidence delivery tip with `git ls-remote origin refs/heads/forward/rust-he-sources-20260922`; do not substitute the earlier dispatch `c99a3579064a9691ba33809fc062ddc0a35396b7` for source.

The callable material-frame Rust library is at `rust/rec_microphysics/`. Read `SOURCE_IMPORT_LOCK.json`, `SOURCE_DOMAIN_MANIFEST.json`, `FORWARD_STATUS.json`, and `task9/EXECUTION_RECEIPT.json` for the exact adopted WU29/WU30/WU31-A1/T4 subset, represented domains, first failure, tested commands, and raw logs. Ten raw authority files are preserved in `source_subset/`. The 44-file source-content manifest at `task8/SOURCE_CONTENT_MANIFEST.sha256` matches the tested source commit.

The three required local commands passed at the tested SHA: `cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check`; `cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked` (75/75); `python scripts/check_rust_forward_parity.py` (251 cases, 3,027 numeric components, 111 expected typed errors). Their raw stdout/stderr and exits are in `task9/logs/tested/`. The first candidate's format and BB-JVP cancellation failures are in `task9/logs/initial/`. No source table, reference, or 4096-epsilon tolerance was changed by the repair.

Current boundary: fixed-input tests PASS; T4 Gate P remains `HOLD_INDEPENDENT_REVIEW_RUNTIME_BINDING` because the registered Astra/xhigh reviewer had a sandbox mismatch and the official same-session correction was rejected. Its informal no-finding text is not admitted independent review. Gate I and full original T4 are deferred. `allow_consumer_integration=false`. Existing S3 accepted, S4 partial, S5 gated, G10 open, G11–G13 gated, D86 canonical, P0 physical OPEN, HOST4 physical HOLD, HH propagation unauthorized remain intact.

Next executable action is limited to an independently bound review of this exact tested SHA in a later authorized session, followed only then by a separately scoped exact-rev consumer integration in the other repository, or close this port with the current HOLD. Do not start E1C, a history run, G10, or a new physics campaign from this handoff.

Create-only dual-provider backup of the tested source/log package succeeded with R1 metadata and native hash match; see `task9/BACKUP_RECEIPT.json`. Upload is not restore validation.
