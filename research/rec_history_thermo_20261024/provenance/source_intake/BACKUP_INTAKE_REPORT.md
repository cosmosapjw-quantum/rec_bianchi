# Backup intake — observed 2026-10-24

Requested execution routing: `gpt-6.1-sol`, high. Actual runtime model identity was not observed; no runtime-model claim is made. Scientific interpretation and admission remain with root Astra. This task performed read-only provider intake and local evidence assembly; no scientific run, native action, IVP, campaign replay, upload, merge or activation occurred.

## Dropbox inventory

`/bianchi/rec_bianchi/20261016` direct listing: **116 entries, one page, has_more=false**. Recursive listing: **156 entries, one page, has_more=false**. Raw pages are in `raw/dropbox_direct_page1.json` and `raw/dropbox_recursive_1.json`. An initial trailing-slash request returned INVALID_PATH; removing only the terminal slash succeeded.

The newest REC-HISTORY sequence in the complete listing is RESP01 S0/S1/S2/S3/D1/final companion. Preceding REFINE01, HISTORY02R, ADM01 and HISTORY checkpoint objects remain listed. Exact current metadata reads confirmed:

| Object | Dropbox ID | Bytes | Server modified UTC | Revision |
|---|---|---:|---|---|
| RESP01 S2 | id:BSpOijBcT10AAAAAAD_9dg | 7,473,354 | 2026-10-24 09:47:04 | 65e92fab888f90af03d47 |
| RESP01 S3 | id:BSpOijBcT10AAAAAAD_9eQ | 1,242,740 | 2026-10-24 09:54:56 | 65e9316cd39c60af03d47 |
| RESP01 D1 | id:BSpOijBcT10AAAAAAD_9eg | 28,103 | 2026-10-24 09:58:13 | 65e932295acba0af03d47 |
| RESP01 final companion | id:BSpOijBcT10AAAAAAD_9fQ | 15,571 | 2026-10-24 10:02:35 | 65e933229a6db0af03d47 |

All four sizes match the assigned expected identities. Metadata alone does not verify ordinary whole-file SHA256. Expected S2 SHA256 remains `a41da3e7df6b26bd6af756473bd8bdcdd96a915dfa2561b07fe2ca29c6f26c37`; expected companion SHA256 remains `050ac0576b5953d37fb469b01df4889ff84f7de89372fdc86c5ede9554c87184`.

## Text recovery and byte-recovery limits

The installed provider `download_link` action returned temporary download URLs for S2 and the companion, with provider content hashes and matching sizes. No authenticated workspace file reference was returned, and no separate Dropbox materialization action was exposed. Temporary URLs are omitted from saved output. No HTTP GET was attempted and the earlier blocked remote-HTTP route was not repeated. Original ZIP bytes were **not recovered** and no remote ZIP CRC or whole-file SHA256 is newly claimed.

The provider-supported `fetch` action successfully extracted the companion text. All six recovered payload files match their embedded PAYLOAD_MANIFEST byte counts and SHA256 exactly; see `COMPANION_TEXT_RECOVERY.json` and `companion_extracted/`. The manifest itself is also retained. Thus the final handoff, publication receipt, D1 receipt, CI observations, PR readback and S3 unsigned-hash receipt are reusable text evidence, while original ZIP-byte identity remains unreverified.

Provider fetch also returned S3 extracted text, preserved in `raw/S3_fetch.json`. Only selected text members were separated: FROZEN_CONTRACT, NEXT_INPUT_CONTRACT, REPORT_KO, PAYLOAD_MANIFEST and S2_RAW_ARCHIVE_LOCATORS. The four substantive selected members match their S3 embedded payload-manifest size/SHA identities. See `S3_SELECTED_TEXT_RECOVERY.json`. No S2 fetch was attempted: S2 exceeds the fetch tool's documented 5 MiB limit. No binary was reconstructed and no S3-wide member extraction was performed.

The recovered handoff locates RAW_RESPONSE.npz, COEFFICIENTS.npz and exact execution snapshots in immutable S2. S3 binds 73 raw members to that S2 dependency; `S3_extracted/research/rec_history_response_20261024/provenance/S2_RAW_ARCHIVE_LOCATORS.json` contains their individual locators. These are future recovery leads, not a new numerical execution authority.

## Google Drive inventory and limits

Read-only REC search, REC_HISTORY legacy search, a name-filter search, backup-root listing and its 20261016 child listing are saved under `raw/drive*`. The backup root `1BTX6wu9Rim5pYKcK62m9wR65jKx1oGy4` returned 17 direct objects, including R3S execution and R3Q reviewed-result archives, dated 2026-10-20/21. Its 20261016 folder `1Xo_yT9v4WQfPvv-GJdYJ2O2CD5s6bJ1k` returned 16 historical R3F/R3G/R3H/R3I folders. The legacy REC_HISTORY keyword search returned five loosely related text hits; the explicit name filter for REC_HISTORY/RESP01/REFINE01 returned no results. No current RESP01 Drive backup was established.

Drive listing exposes only url/top_k and returned no pagination token or completeness assertion; inventory is limited to observed connector results. Empty search results do not resolve a previously unknown write outcome. The prior REFINE01 S3 upload remains **UNKNOWN_SERVER_STATE_UNCHANGED**; no upload or blind retry occurred.

## Stage reporting

Provider observations verify presence and current metadata, not scientific validity or new completion. Recovered companion historical records say RESP01 finite R1–R10/C1–C10 is 20/20 COMPLETE_SCOPED, with physical completion null, physical HOLD, global convergence NOT_RUN, production NOT_APPROVED and REI activation false. These are preserved historical statements; root decides present scientific admission.
