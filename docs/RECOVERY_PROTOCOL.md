# Runtime interruption recovery protocol

1. Classify the event as `RUNTIME_INTERRUPTION_RECOVERY`.
2. Record repository HEAD, branch, remotes, dirty state, running processes, file tree, sizes, mtimes, and SHA-256 in a new recovery inventory.
3. Separate `DURABLE_VERIFIED`, `PARTIALLY_RECOVERED`, `RECONSTRUCTED`, `TRANSCRIPT_ONLY`, and `MISSING` claims.
4. Do not inherit claims marked only in conversation text.
5. Run repository verification and the active test suite before continuing.
6. Resume from `state/PROJECT_STATE.json` and the latest stage ledger.
7. Commit and push each reconstructed bounded stage before proceeding.
