#!/bin/zsh

set -euo pipefail

REPO="/Users/egeuysal/Developer/brain"
LOCK_DIR="${HOME}/.cache/brain-autopull.lockdir"

mkdir -p "${HOME}/.cache"

if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  # Another run is in progress.
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

before_head="$(git rev-parse @)"

if git pull --rebase --autostash --prune; then
  after_head="$(git rev-parse @)"
  if [[ "${before_head}" == "${after_head}" ]]; then
    echo "$(timestamp) [ok] Already up to date (rebase/autostash mode)."
  else
    echo "$(timestamp) [ok] Pulled latest changes (rebase/autostash mode)."
  fi
  exit 0
fi

if [[ -d .git/rebase-merge || -d .git/rebase-apply ]]; then
  git rebase --abort >/dev/null 2>&1 || true
fi

echo "$(timestamp) [error] Pull failed in rebase/autostash mode."
exit 1
