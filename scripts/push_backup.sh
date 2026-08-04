#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REPO_SLUG="cosmosapjw-quantum/rec_bianchi"
REMOTE_SSH="git@github.com:${REPO_SLUG}.git"
REMOTE_HTTPS="https://github.com/${REPO_SLUG}.git"
BACKUP_BRANCH="backup/full-bianchi-hyrec-v045-20260804"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to push a dirty working tree." >&2
  exit 2
fi

# This repository contains unpublished work. Abort on a public target unless
# the owner has made an explicit publication decision.
if command -v gh >/dev/null 2>&1; then
  visibility=$(gh repo view "$REPO_SLUG" --json visibility -q .visibility 2>/dev/null || true)
  if [[ "$visibility" == "PUBLIC" && "${ALLOW_PUBLIC_PUSH:-}" != "YES" ]]; then
    echo "Repository is public. Set ALLOW_PUBLIC_PUSH=YES only after an explicit publication decision." >&2
    exit 3
  fi
fi

cleanup() {
  if [[ -n "${ASKPASS_FILE:-}" && -f "${ASKPASS_FILE:-}" ]]; then
    rm -f "$ASKPASS_FILE"
  fi
  # An EXIT trap's own status becomes the script's status; keep it neutral so a
  # successful push does not report failure just because there was no temp file.
  return 0
}
trap cleanup EXIT

export GIT_TERMINAL_PROMPT=0

# Probe transports in preference order. Availability of the ssh binary is not
# evidence that the key is authorized, so test the actual handshake.
ssh_works() {
  command -v ssh >/dev/null 2>&1 || return 1
  ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1 |
    grep -q 'successfully authenticated'
}

if ssh_works; then
  REMOTE="$REMOTE_SSH"
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  REMOTE="$REMOTE_HTTPS"
  # gh holds the credential; nothing is written to Git config or the remote URL.
  GIT_CONFIG_COUNT=1
  GIT_CONFIG_KEY_0=credential.helper
  GIT_CONFIG_VALUE_0='!gh auth git-credential'
  export GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0
elif [[ -n "${GITHUB_REC_BIANCHI_TOKEN:-}" ]]; then
  REMOTE="$REMOTE_HTTPS"
  ASKPASS_FILE=$(mktemp)
  cat > "$ASKPASS_FILE" <<'ASKPASS'
#!/usr/bin/env bash
case "$1" in
  *Username*) printf '%s\n' 'x-access-token' ;;
  *Password*) printf '%s\n' "$GITHUB_REC_BIANCHI_TOKEN" ;;
  *) printf '\n' ;;
esac
ASKPASS
  chmod 700 "$ASKPASS_FILE"
  export GIT_ASKPASS="$ASKPASS_FILE"
  export GIT_TERMINAL_PROMPT=0
else
  cat >&2 <<'EOF'
No usable GitHub authentication transport is available.

Preferred: register an SSH key with the cosmosapjw-quantum account, e.g.
  gh ssh-key add ~/.ssh/cosmo_lab_authority_ed25519.pub   # needs admin:public_key
  (or paste the .pub contents at https://github.com/settings/keys)
Alternative: authenticate the gh CLI with `gh auth login` (repo scope).
Fallback: export a repository-scoped fine-grained token as
  GITHUB_REC_BIANCHI_TOKEN
The token is read only through a temporary GIT_ASKPASS file and is never
written to Git config, the remote URL, or the repository.
EOF
  exit 4
fi

git remote get-url origin >/dev/null 2>&1 && git remote set-url origin "$REMOTE" || git remote add origin "$REMOTE"
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
      gh pr create --repo "$REPO_SLUG" --base main --head "$BACKUP_BRANCH" \
        --title "Backup Full Bianchi-HyRec artifacts through v0.45" \
        --body-file docs/HANDOFF_PROMPT.md || true
    fi
  fi
fi

remote_head=$(git ls-remote origin "$pushed_ref" | awk '{print $1}')
local_head=$(git rev-parse HEAD)
python - <<PY2
import datetime, json, pathlib
path=pathlib.Path('state/REMOTE_SYNC_RECEIPT.json')
path.write_text(json.dumps({
  'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'remote': '$REMOTE',
  'ref': '$pushed_ref',
  'local_head': '$local_head',
  'remote_head': '$remote_head',
  'match': '$local_head' == '$remote_head',
},indent=2)+'\n')
PY2
cat state/REMOTE_SYNC_RECEIPT.json
