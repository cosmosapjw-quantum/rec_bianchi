#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REMOTE="git@github.com:cosmosapjw-quantum/rec_bianchi.git"
BACKUP_BRANCH="backup/full-bianchi-hyrec-v045-20260804"

git remote get-url origin >/dev/null 2>&1 && git remote set-url origin "$REMOTE" || git remote add origin "$REMOTE"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to push a dirty working tree." >&2; exit 2
fi

# Prevent accidental publication of unpublished artifacts when gh is available.
if command -v gh >/dev/null 2>&1; then
  visibility=$(gh repo view cosmosapjw-quantum/rec_bianchi --json visibility -q .visibility 2>/dev/null || true)
  if [[ "$visibility" == "PUBLIC" && "${ALLOW_PUBLIC_PUSH:-}" != "YES" ]]; then
    echo "Repository is public. Set ALLOW_PUBLIC_PUSH=YES only after an explicit publication decision." >&2
    exit 3
  fi
fi

git ls-remote origin >/dev/null
remote_main=$(git ls-remote --heads origin refs/heads/main | awk '{print $1}')
if [[ -z "$remote_main" ]]; then
  git push -u origin main --follow-tags
  pushed_ref=refs/heads/main
else
  git fetch origin main
  if git merge-base --is-ancestor origin/main main; then
    git push -u origin main --follow-tags
    pushed_ref=refs/heads/main
  else
    git branch -f "$BACKUP_BRANCH" main
    git push -u origin "$BACKUP_BRANCH" --follow-tags
    pushed_ref=refs/heads/$BACKUP_BRANCH
    if command -v gh >/dev/null 2>&1; then
      gh pr create --repo cosmosapjw-quantum/rec_bianchi --base main --head "$BACKUP_BRANCH"         --title "Backup Full Bianchi-HyRec artifacts through v0.45"         --body-file docs/HANDOFF_PROMPT.md || true
    fi
  fi
fi
remote_tree=$(git ls-remote origin "$pushed_ref" | awk '{print $1}')
local_head=$(git rev-parse HEAD)
python - <<PY
import json, pathlib, datetime
p=pathlib.Path('state/REMOTE_SYNC_RECEIPT.json')
p.write_text(json.dumps({
 'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'remote': '$REMOTE', 'ref': '$pushed_ref', 'local_head': '$local_head',
 'remote_head': '$remote_tree', 'match': '$local_head' == '$remote_tree'
},indent=2)+'\n')
PY
cat state/REMOTE_SYNC_RECEIPT.json
