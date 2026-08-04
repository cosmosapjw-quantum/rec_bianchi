#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python scripts/verify_repo.py --all
if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "chore(backup): update durable project state $(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi
scripts/build_bundle.sh
scripts/push_backup.sh
