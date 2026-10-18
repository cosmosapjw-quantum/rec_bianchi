# REC R3k P1: recovered source and execution scope

Date: 2026-10-18. Parent: PR102 `e0cfdf76a6e8bf04110715d14efaad7077aeff8b`. Related PR103: `3a5adf6cac28555acd14707b6fd5659535e4763d`.

## Backup-first recovery

Google Drive and Dropbox directories were listed before scientific work. The new PR102 tested-source ZIP was materialized: 103326154 bytes, SHA256 `8e33b961ad8cf3fdf3dfb62c6cb48c4f0ff8e36fc41c9b8c07eb969cc2223fbf`. Its manifest identifies GitHub Actions execution of 24 characterization tests at the parent commit, not an actual U5-checkpoint run. The included source tree was extracted with Python tarfile's data filter. The inner tree and test-file hashes in the manifest were read, but not all independently recomputed before runtime interruption.

A newer PR103 recovery raw archive exists (756025129 bytes). Google Drive materialization returned HTTP 413. The smaller U5 raw archive (308069518 bytes) was then materialized, but the sandbox execution backend subsequently returned container ClientError and both Python backends returned ServerError. No cause of the backend failure was established. No new U5-checkpoint runtime check or archive SHA verification is claimed from this failed session.

PR103's published receipt reports 4/128-step baseline/patched byte equivalence and same-h C parity for 80000 spectral fields and 40064 links. Its 128-step process-tree timings do not establish a speedup; full 5210-step U6 remains NOT_RUN under the existing budget hold. This work therefore does not repeat PR103's duplicate-scan-only change.

## Selected constructive step

PR102 already contains OwnedFLRWHistory and an opt-in U6 integrator. We will add a reusable, byte-exact baseline/owned comparison runner and validate the history transport on the SHA-pinned, real h/2 U4 checkpoint already tracked in Git. That bounded physical source test is useful despite the current U5 runtime blocker; it is not a substitute for U5-checkpoint temporal parity. Existing 24 synthetic characterization tests are retained unchanged.

The source-original H+He implementation, 311 virtual bins, DLNA, stage boundaries, thermal and atomic rates, and historical mean-photon tolerances remain unchanged. Native subagents are NOT_RUN because no native delegation tool is exposed. CI supplies execution evidence, not independent scientific review.

## Why one-time validation is sufficient under the stated ownership model

At construction, every stored prefix entry is copied and tested finite. A caller cannot mutate the object by changing the original arrays. Assume a valid prefix of length j. append validates every component of the candidate column before writing any of it; incrementing the accepted-column count only afterward extends the invariant to j+1. The gather is allowed to use only k and k+1 <= j-1. Induction therefore eliminates the need to revalidate the whole owned prefix at each gather. This relies on a single trusted writer and trusted observers; read-only NumPy views are not a security boundary against deliberate .base access.

The q=0 field is a spectral distortion, so negative finite values are not automatically unphysical. No clipping or positivity test on the distortion is introduced. Bitwise equality of incoming values plus identical source arithmetic and predictor tails should propagate identical states and outgoing values; the paired runner tests this rather than assuming it.

Legacy two-prefix validation visits B*N*(2*P+N-1) elements with B=314. At P=16733, N=5210 this is 63269979500 elements. PR103 removes only one of these passes. The owned path changes this validation cost to one prefix plus 625 appended-field checks per step and bounded 313-link gathers. This is a complexity comparison, not a measured full-solver speedup.

## Phase DAG

P1 BACKUP_INTAKE: completed for directory discovery, PR receipt reconciliation and source-tree extraction; large raw SHA validation blocked.
P2 OWNED_PHYSICAL_CHARACTERIZATION: implementation next; execute through CI because sandbox failed.
P3 U5_CHECKPOINT_PAIRED_RUNNER: implementation next; actual U5 execution remains NOT_RUN unless a real receipt is returned.
P4 PUBLICATION_AND_BACKUP: commit each phase and save CI code/evidence artifact to independent providers.

Inherited gates: old h U5 HOLD_9_FAIL; h/2 U5 HOLD_8_FAIL under its original criterion; full U6 NOT_RUN; h/4 and Python three-grid convergence NOT_RUN; REI activation=false. The prior allocation ledger is retained and never reset by this work.
