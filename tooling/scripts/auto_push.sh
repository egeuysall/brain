#!/bin/zsh

set -euo pipefail

REPO="/Users/egeuysal/Developer/brain"
LOCK_DIR="${HOME}/.cache/brain-git-sync.lockdir"
DEFAULT_COMMIT_MESSAGE="chore(auto): sync local changes"

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

COMMIT_MESSAGE="${BRAIN_AUTO_COMMIT_MESSAGE:-$DEFAULT_COMMIT_MESSAGE}"

if [[ -n "$(git status --porcelain)" ]]; then
  git add -A

  if git diff --cached --quiet; then
    echo "$(timestamp) [ok] No staged changes after add."
  else
    if git commit -m "${COMMIT_MESSAGE}"; then
      echo "$(timestamp) [ok] Created auto-commit."
    else
      echo "$(timestamp) [error] Auto-commit failed."
      exit 1
    fi
  fi
fi

if git push origin HEAD; then
  echo "$(timestamp) [ok] Pushed local commits."
  exit 0
fi

echo "$(timestamp) [warn] Push failed; attempting pull --rebase --autostash."

if ! git pull --rebase --autostash --prune; then
  if [[ -d .git/rebase-merge || -d .git/rebase-apply ]]; then
    git rebase --abort >/dev/null 2>&1 || true
  fi
  echo "$(timestamp) [error] Pull/rebase failed after push failure."
  exit 1
fi

if git push origin HEAD; then
  echo "$(timestamp) [ok] Pulled then pushed successfully."
  exit 0
fi

echo "$(timestamp) [error] Push failed after pull/rebase retry."
exit 1
