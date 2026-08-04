#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="${1:-../rec_bianchi_backup_$(date -u +%Y%m%dT%H%M%SZ).bundle}"
git fsck --full
git bundle create "$OUT" --all
git bundle verify "$OUT"
sha256sum "$OUT" > "$OUT.sha256"
echo "$OUT"
