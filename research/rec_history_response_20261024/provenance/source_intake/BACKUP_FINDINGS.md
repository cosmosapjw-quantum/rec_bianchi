# Backup and attachment intake — 2026-10-24 followup

## Current backup truth

The named Dropbox subtree `/bianchi/rec_bianchi/20261016` returns **110 direct objects and 150 recursive objects**. Each listing completed in one page (`has_more=false`, empty cursor). The exact delta from the retained 104/144 inventory is six known REFINE01 archives: S0, S1, S2, S3, D1, and final companion. No retained ID disappeared; no retained name, namespace path, size, modification time or object type changed. The complete normalized responses, arguments and timestamps are in `PROVIDER_RESPONSES.json`; repeated text serialization and account-profile fields are omitted.

Exact metadata of S3 (`id:BSpOijBcT10AAAAAAD_9Xw`, rev `65e913a92e82d0af03d47`, 56,822,487 bytes), D1 (`id:BSpOijBcT10AAAAAAD_9ZA`, rev `65e92016e78070af03d47`, 52,576 bytes), and final companion (`id:BSpOijBcT10AAAAAAD_9ZQ`, rev `65e920e6dc54c0af03d47`, 691,877 bytes) matches their completed prior publication metadata. Prior capsule local SHA/CRC/payload records remain reused evidence. No fresh remote whole-byte digest is implied.

The single requested metadata-only Drive query combined the exact S3 basename `REC_HISTORY_REFINE01_S3_20261024_5587c1d27101.zip` with parent folder `1Xo_yT9v4WQfPvv-GJdYJ2O2CD5s6bJ1k` and `trashed=false`. It returned `results=[]`. The provider response exposes no pagination or account-level completeness guarantee for this legacy query. Prior S3 upload1 remains without completed ACK; remote creation and cancellation remain **UNKNOWN**. Retry0; no dual-provider completion claim.

## New matched-history / uncertainty source intake

No newly unknown backup object or name indicating a new matched-target history/independent uncertainty witness appears in the completely listed dated subtree. Global bounded filename queries REC_HISTORY, MATCHED and UNCERTAINTY and REC-scoped filename queries HISTORY, MATCHED, UNCERTAINTY and INDEPENDENT were also recorded. They each returned has_more=false but do not establish absence outside the provider's query semantics. Several broad queries return exactly 20 results despite requested max_results=1000, so no account-wide exhaustive recall is inferred. Although title_only was requested, the provider's result match_type says BOTH_FILENAME_AND_CONTENT; no semantic content admission is inferred from that label.

The REC_HISTORY results are known archives already covered by the subtree inventory. REC-scoped UNCERTAINTY returns 0; MATCHED returns only old `archive/expanded/Full_Bianchi_HyRec_C3B2A_substitution_audit_v0_28/absolute_normalization_match.csv`. INDEPENDENT returns old v0_39/v0_49 CSVs, v0_54/v0_55/v0_59/v0_60 review notes, and Git reference names. These are **name-only candidates, not new matched-target witnesses**. The supplemental global UNCERTAINTY/MATCHED results mostly refer to old REI or HTT work. No unrelated science file was fetched or read. Exact paths and IDs are retained in `SEARCH_RESPONSES.json` and `REC_SCOPED_SEARCH_RESPONSES.json` for root to assess. There is no new admissible source to pass from this mechanical survey.

## Twenty attached source copies

All **20 numbered attachments** in project_sources match the retained prior SHA256 exactly, including archives. The eight scoped archive member inventories and selected member comparisons are reused on whole-archive SHA identity; no re-extraction or campaign replay is needed. No attachment content changed, so no changed-source semantic read was performed. The earlier retained inventory's historical size-only limitation for 12 files is not rewritten: current whole-byte identity is established against that retained 2026-10-24 SHA inventory, not against its earlier pre-SHA intake.

No toolchain installation, shell bootstrap, tests, campaign replay or science computation was executed. User-supplied copies were read from scratch only; Library reads0. All writes by this intake are confined to this intake/backups directory. Provider mutation0, upload0, upload retry0, remote download0. Source and physical interpretations remain with root Astra.

## Evidence

- PROVIDER_RESPONSES.json — actual normalized listings, exact metadata, Drive query result and timestamps.
- SEARCH_RESPONSES.json — bounded global filename query responses.
- REC_SCOPED_SEARCH_RESPONSES.json — bounded REC filename query responses and discovered older candidate paths.
- BACKUP_DELTA.json — exact added-object delta, unchanged old metadata, witness-name coverage.
- ATTACHMENT_IDENTITY.json — twenty fresh attachment hashes compared with retained SHA inventory and reused archive inventory pointer.
- RECOVERY_IDENTITY.json — automated comparison to prior S3/D1/terminal companion metadata, preserved Drive unknown state.
