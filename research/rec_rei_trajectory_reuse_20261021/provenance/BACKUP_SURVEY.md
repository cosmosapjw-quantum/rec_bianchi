# REC/REI conversation, backup and live-output survey

Date: 2026-10-21 UTC. Survey task: `/root/cross_context_backups`. This is a read-only source survey and owned intake capture; no upstream workspace or remote source was changed, and no ODE, benchmark or NCP execution was performed.

## Finding that changes the next-step choice

The current shared REI unified workspace completed the requested collisionless z20→2 trajectories while this survey was underway. Its B1 status records 143 completed component cases and 35 verified reused cases. Its B2 status records all 237 unique tails completed, with 153 joined samples per trajectory: the original 121 z20→4 samples plus 32 new samples to z2. Re-executing that grid would duplicate completed work.

The relevant source root is `/workspace/scratch/b7c8740ffe58/rei_unified_20261021/repo/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021`. The source `components/unified_pilot.py` SHA256 is `a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64`. The canonical vendor source commit recorded in configs is `3b85dedce84d37b3e165da00685a8a984950aafe`. These are distinct identities: the source wrapper and new raw files were captured from a shared live workspace and are not asserted to belong to a new remote commit.

The subsequent upstream independent `B2_FINAL_RAW_AUDIT.json` reports `PASS_SCOPED_NUMERICAL_RAW`, all 237 completed, six paired refinement checks passing, and `scientific_admission=PENDING_ACTUAL_FIGURE_REVIEW`. Its audit charges no IVP or benchmark execution. This does not remove REC's physical HOLD, global-convergence NOT_RUN or production NOT_APPROVED states. Older D0/D1 root status text is an earlier snapshot and does not override the newer case receipts.

## Frozen input for the selected REC contribution

The compact input package is `/workspace/scratch/36ad4bc67b35/intake/unified_z2_20261021`.

| Item | Captured evidence |
|---|---|
| Primary grid | 7 Sigma values × 5 signed matter values × 5 signed radiation values = 175 cases |
| Axis support | 63 cases: `(5+5−1)×7` |
| Mixed withheld | 112 cases |
| Extra guards retained | 3 component guards: aligned extreme, anti-aligned extreme, initial matter/radiation cancellation |
| Selected total | 178 trajectories; all required original prefix raw/input/result receipts are present |
| Excluded from compact copy | 56 extra radiation-baseline nominal cases and 3 original radiation guards |
| Capture | 2026-10-21T10:47:46.921755Z |
| Copied payload | 1,686 files, 31,925,390 bytes, before generated subset/manifest metadata |
| Stability | Source stat/size/SHA checked twice and destination SHA matched; zero failures |
| Snapshot manifest SHA256 | `d7b147aa0293646b068e754a9bf03f2b8e47e3544b405a1ad5bfce366b34143e` |
| Subset-selection SHA256 | `53b6aae32baaf1d83e4d50db952fac7c635b05e65276acd484d6454914c28b5e` |

`SUBSET_SELECTION.json` is the authoritative list of the selected 178 cases. The original upstream MANIFEST/CHECK/STATUS files are deliberately retained byte-for-byte and describe their original full cohorts. Each selected combined raw file and tail is bound by its source result; each source prefix raw/input/result is bound by the B2 case manifest. The original all-237 intake check found no failed hash bindings.

The Sigma grid is `[0, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1]`. The signed matter grid is `[-0.0003, -0.0001, 0, 0.0001, 0.0003]`. The signed radiation grid is `[-0.001, -0.0003, 0, 0.0003, 0.001]`. The Cartesian grid is complete. On historical radiation-only reused configs, `P_m_i` defaults to 0 and `P_r_i` defaults to `Pi_F_signed_i`; use the actual config keys, not rounded output values, for coordinates.

Each `z2_extension/results/cases/<id>/raw.npz` holds the full joined history. The 175 nominal grid cases have `raw_y.shape=(40,153)`; the three component guards have `(56,153)`. Preserve signed shear as `sqrt(6)*s/H`; `Sigma_F` is its nonnegative norm. For the diagonal LRS convention `diag(-p,-p,2p)`, signed `P_X=sqrt(6)*(8*pi*G/c^2)*p_X/H^2`, with stress in J/m³. Sum signed matter and radiation components before taking the total norm. A small saved trajectory reconstruction residual would be an empirical surrogate comparison, not a true-solution error certificate or a proof of physical decoupling.

The earlier broader intake is retained at `/workspace/scratch/36ad4bc67b35/intake/unified_z2_snapshot_20261021` for survey provenance only. Its manifest SHA256 is `5e0027d52f94a021d52cc33c3f4d650162ef573c82f725f79370b83ba0f11786`; 2,265 payloads, 39,948,399 bytes, captured 2026-10-21T10:45:30.174892Z. It should not be redundantly packed alongside the compact subset in a new backup.

## Recovered remote archives

| Archive | Drive ID | Local size | Current byte SHA256 | Verification |
|---|---|---:|---|---|
| REC_REI_AXIS153_FINAL_4cffa8a0_20261021.zip | `1-hexKFeKp01jcFpsE5oholxxTdyqG-zd` | 1,002,866 | `962f9434bf46009c44e1a4be886448f0b80fbcc263e1883181c4a90227f95db8` | Matches user-pinned archive digest; prior 49-payload validation reused |
| REI_BIANCHI_MATTER_RADIATION_FINAL_20261021.tar.gz | `1i6x-HcPTctzSQwsxkET-CfTGfjpC-Dx7` | 37,945,383 | `2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d` | Matches published expected archive digest |
| REI_UNIFIED_D0D1_RECOVERY_20261021_20261021T080025Z.tar.gz | `1qHeeBL1y1uIbd7vY0pwo8t4asdNI8kbh` | 10,829,091 | `25e1196e3050ae535273f1b88baf99183656bcd0930be49ff9a359e960594abf` | Current fetched-byte identity; no independent expected digest asserted |

These archives are in `/workspace/scratch/36ad4bc67b35/recovered`. The latest D0/D1 file was discovered by direct folder listing after broad search results had missed it. Its Drive creation timestamp is 2026-10-21T10:34:44.907Z; its Dropbox counterpart is `id:BSpOijBcT10AAAAAAD_gLA`, modified 10:35:25Z. The archive itself is a pre-execution recovery snapshot; newer live case receipts provide the completed B1/B2 state.

REC116's Dropbox file is `id:BSpOijBcT10AAAAAAD_flw`; its historical whole-byte Dropbox readback remains NOT_RUN. Fetching the current Drive copy does not change that historical provider-specific status. The PR198 final archive's Dropbox counterpart is `id:BSpOijBcT10AAAAAAD_fYA`; its ACK is Drive `1TiStfVpIT2CiivFZfxNrVlq_kEyq6dpI` and Dropbox `id:BSpOijBcT10AAAAAAD_fcw`. The ACK records source `b140170ce0c58159368b6b81be49ac35ca764851`, final head `8bd35af5f11c7ea5945b656be1c013d1c1933498`, final tree `cfb162b177de0eb39e5fc3d20ba306f6a4fd2cab`, and the completed PR198 z20→4 families. These are separate from warm C15/PR213 and from the newer PR199 unified trajectories; do not merge rows or coefficients across them.

## Current remote linkage

Direct PR199 metadata returned actual head `8b71c13e23202edfce1ee67fb2da552fefb9a583`, branch `research/rei-age-exposure-envelope-20261018`, open draft, unmerged. The PR body contains historical head text; API `head` is the observed current remote identity. This survey has not established that the newly completed 237 trajectories are published under that remote head. The frozen input explicitly uses the live-workspace snapshot and exact hashes. Compact metadata is saved in `agent_backups/PR199_CURRENT_METADATA.json`.

## Coverage and limits

The Personal Context service was called and returned `Personal context is unavailable for this conversation.` No other conversation contents were retrieved; no all-conversations coverage is claimed.

Drive REC folder `1BMLUuRlxjx84QyhL1_iQfwPivY2H-EmR` returned 12 direct files. REI folder `1phclg92jkhC5KgvnXhks8GbOFlya4qGe` was listed with the connector's 100-item bound. The search service's title/date filtering did not reliably produce only requested current rows, so the direct folder receipts and explicit archive identities were used. The bounded Drive list is not a globally exhaustive survey of all folders or histories.

The relevant Dropbox folders were listed directly with max 600 results: `ns:183516487//bianchi/research_backups/rei_bianchi` and `ns:183516487//bianchi/rec_bianchi/20261016`. Both returned `has_more=false` for those specific folders. Other Dropbox namespaces/folders were not recursively surveyed. The bounded inventory, provider metadata and sanitized ACK content are in `agent_backups/BACKUP_INVENTORY.json`.

## Backup API capability available to the parent

New backup uploads are supported, using unique create-only filenames in the established REC destinations. The runtime-adapted current schemas take absolute local paths:

```javascript
await tools.mcp__codex_apps__google_drive_upload_file({
  file_uri: "/absolute/path/to/unique_archive.zip",
  file_name: "unique_archive.zip",
  mime_type: "application/zip",
  parent_folder_id: "1BMLUuRlxjx84QyhL1_iQfwPivY2H-EmR"
});
await tools.mcp__codex_apps__dropbox_upload_file({
  source_file: "/absolute/path/to/unique_archive.zip",
  destination_path: "/bianchi/rec_bianchi/20261016/unique_archive.zip"
});
```

For Dropbox async responses use `mcp__codex_apps__dropbox_check_upload_file_status` with the returned operation token and recommended wait. Do not report success until `status=completed`. For Drive download, first inspect observed file metadata, then `google_drive_fetch` with `download_raw_file:true, include_base64:false`. The returned temporary download URL is sensitive; it should be consumed without printing or persisting it. Dropbox `download_link` returns a single-use URL; consume it directly without HEAD/Range preflight. Ordinary sandbox Python networking is denied; the authorized read-only download with `require_escalated` passed automatic review in this session.

The survey and snapshot were initially read-only. The parent subsequently authorized Stage 1 backup uploads to the existing destinations; they will be recorded separately after it supplies the final packaged scope. No upload completion is claimed by this survey document.
