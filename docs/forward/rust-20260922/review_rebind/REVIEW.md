# Selected-He Rust fixed-input independent review

Reviewed implementation: `2ee3760870f9ac47eaab518a4c4a907f1a3f6f85`. The detached review worktree was `/tmp/rec-rust-he-review-20260930`. The independent fresh-context Astra/xhigh App Server thread ran in observed `readOnly` mode; lifecycle result was `MATCH` and `VALIDATOR_PASSED`. [REVIEW_BINDING.json](REVIEW_BINDING.json) retains the runtime identity and transcript SHA. The prior author-session `RUNTIME_MISMATCH` remains historical failure evidence, not this review's state.

## Finding F1 — MINOR source defect, dependency candidate blocked

The public `assemble_he_event_ledger` in `rust/rec_microphysics/src/ledger.rs:97-139` validates finite inputs but does not check generated outputs before `Ok`. At `r584=1e308`, canonical energies, all other rates and BF power/heat zero, the reviewed Rust library returns `Ok` with `p_internal=-inf`, `p_gamma=inf`, and `energy_residual=NaN`. The independent reviewer identified this from the source; a separate host Rust reproduction compiled against the tested SHA and observed the same values. See [defect_repro/receipt.json](defect_repro/receipt.json), its raw logs, and [native/review.txt](native/review.txt).

This is a standalone public API error-path defect. The combined material ledger has an additional finiteness guard, and the frozen finite fixtures did not exercise this overflow. Under the user's **any source defect** rule, severity does not restore dependency candidacy: `dependency_candidate_sha=null` and scoped Gate P review remains `HOLD_SOURCE_DEFECT_F1`. No source file was patched in this review unit.

Repair handoff: in a separate bounded work unit, add a generated-output finiteness check to the standalone event ledger, return `NumericalDomainUncertain` on overflow, and add one finite-input overflow regression. Create a new source SHA, run the complete fixed-input `cargo fmt`, `cargo test --locked`, and Python parity suite, then obtain a fresh independent review. Existing tables, domains, fixtures and tolerance remain frozen.

## Provenance and source scope

All ten locked `source_subset` members matched their declared byte sizes and SHA-256 values; all 44 entries in `task8/SOURCE_CONTENT_MANIFEST.sha256` matched. The local A7 ZIP hash matched the authority digest. A7/A6 are provenance; WU29, WU30, WU31-A1 and T4 interface/coverage/ledger/test matrix are the adopted source. The weak/JVP `study.py` blob pin matched `f1ad5926de6090e8317961c6cc58914cfd5c8ba3` and remains oracle provenance, not merged physics. Exact checks and public entry points are in [SOURCE_SCOPE_AUDIT.json](SOURCE_SCOPE_AUDIT.json).

The reviewer found no blocking formula or domain issue in 584/IR BB, P/S BF, S-to-g pair, angular and spectral measures, event trace, conservation, material frame, or distinct ray/atom clock semantics. Jacobs P/S remains high `q∈[1,1.4]` only, with no Bhatia splice. BF below threshold is physical zero; unprovided above-threshold values return `MissingAuthority`. D86 uses the printed 20-node half-grid, reflection and linear interpolation only on `y∈[0.025,0.975]`; outside returns `OutOfBand`. No total-rate rescale was found. The BB lower-population JVP in `examples/eval_fixture.rs:264-266` evaluates the affine coefficient directly. The old finite-difference subtraction gives `233856999.9921875`, whereas the direct coefficient gives `233856999.99999997` on the legacy fixture.

The reviewer independently recomputed 33 frozen records and 1,513 numerical components from source expressions; maximum difference divided by frozen reference scale was `2.91e-16`, below unchanged `4096ε`. The host independently checked 18 selected scalar/status observations from raw Rust output without importing the author's reference values. These checks include vacuum and populated BB, affine JVP, P/S BF, physical zero versus missing authority, D86 node and midpoint, out-band error, pair factor, and event ledger. [SPOT_CHECK.json](SPOT_CHECK.json) records the host values. The reviewer report records one corrected calculation setup during review; no repository file or tolerance changed.

## Host rerun and claim ceiling

On the exact detached tested SHA, `cargo fmt --manifest-path rust/rec_microphysics/Cargo.toml -- --check` exited 0; `cargo test --manifest-path rust/rec_microphysics/Cargo.toml --locked` exited 0 with 75 tests; `python scripts/check_rust_forward_parity.py` exited 0 with 251 cases, 3,027 numerical components, and 111 expected typed errors. The raw command streams and parity input/output are under `logs/`; [RERUN_RECEIPT.json](RERUN_RECEIPT.json) records timestamps, hashes and exact argv. The successful rerun does not erase F1.

Review lifecycle binding is valid. The scoped dependency decision is blocked by F1. This review does not promote full T4, Gate I, S4, S5, G10, E1C, history, observable, production, or scientific PASS. `state/PROJECT_STATE.json` was not modified.
