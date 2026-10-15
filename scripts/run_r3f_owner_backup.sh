#!/usr/bin/env bash
# Owner-PC create-only dual backup after NCP return; not run by ChatGPT.
set -euo pipefail
: "${SOURCE_ARCHIVE:?Provide local verified NCP return archive path}"
: "${BACKUP_RUN_ID:?Provide new create-only backup run id}"
test -f "$SOURCE_ARCHIVE"
sha=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')
base=$(basename "$SOURCE_ARCHIVE")
for remote in "dbx:bianchi/rec_bianchi/20261016/${BACKUP_RUN_ID}" \
              "gdrv:rec_bianchi_research_backups/20261016/${BACKUP_RUN_ID}"; do
    rclone copyto --immutable "$SOURCE_ARCHIVE" "$remote/$base"
    remote_sha=$(rclone cat "$remote/$base" | sha256sum | awk '{print $1}')
    test "$sha" = "$remote_sha" || { echo "BACKUP_READBACK_FAIL $remote" >&2; exit 5; }
    printf 'BACKUP_REMOTE_VERIFIED %s SHA256 %s\n' "$remote/$base" "$sha"
done
