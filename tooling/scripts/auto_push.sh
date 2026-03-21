#!/bin/zsh

set -euo pipefail

REPO="/Users/egeuysal/Developer/brain"
LOCK_DIR="${HOME}/.cache/brain-git-sync.lockdir"

mkdir -p "${HOME}/.cache"

if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  # Another sync run is in progress.
  exit 0
fi

cleanup() {
  rmdir "${LOCK_DIR}" 2>/dev/null || true
}
trap cleanup EXIT

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

if [[ ! -d "${REPO}/.git" ]]; then
  echo "$(timestamp) [error] Repo not found: ${REPO}"
  exit 1
fi

cd "${REPO}"
export GIT_TERMINAL_PROMPT=0

if ! git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
  echo "$(timestamp) [error] No upstream branch configured."
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "$(timestamp) [info] Working tree has uncommitted changes; only committed changes can be pushed."
fi

git fetch --prune origin

LOCAL="$(git rev-parse @)"
REMOTE="$(git rev-parse @{u})"
BASE="$(git merge-base @ @{u})"

if [[ "${LOCAL}" == "${REMOTE}" ]]; then
  echo "$(timestamp) [ok] Nothing to push."
  exit 0
fi

if [[ "${REMOTE}" == "${BASE}" ]]; then
  if git push origin HEAD; then
    echo "$(timestamp) [ok] Pushed local commits."
    exit 0
  fi
  echo "$(timestamp) [error] Push failed."
  exit 1
fi

if [[ "${LOCAL}" == "${BASE}" ]]; then
  echo "$(timestamp) [skip] Branch is behind upstream; wait for pull sync."
  exit 0
fi

# Diverged: rebase local commits onto upstream, then push if ahead.
if git pull --rebase --autostash --prune; then
  LOCAL="$(git rev-parse @)"
  REMOTE="$(git rev-parse @{u})"
  BASE="$(git merge-base @ @{u})"
  if [[ "${REMOTE}" == "${BASE}" && "${LOCAL}" != "${REMOTE}" ]]; then
    if git push origin HEAD; then
      echo "$(timestamp) [ok] Rebased and pushed local commits."
      exit 0
    fi
    echo "$(timestamp) [error] Push failed after rebase."
    exit 1
  fi
  echo "$(timestamp) [ok] Rebased; nothing to push."
  exit 0
fi

if [[ -d .git/rebase-merge || -d .git/rebase-apply ]]; then
  git rebase --abort >/dev/null 2>&1 || true
fi

echo "$(timestamp) [error] Rebase failed during push sync."
exit 1
