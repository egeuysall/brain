# Ryva Knowledge Repo

This repository is the canonical knowledge source for Ryva.

## Design Rules

- Keep one compact canonical index: `context/latest/knowledge.json`
- Keep one JSON file per automated entry:
  - `context/latest/diary/*.json`
  - `context/latest/blog/*.json`
- Keep manual knowledge in `resources/**`
- Avoid duplicate large files so models do not process repeated content
- Keep stale context out of default retrieval

## Repository Layout

- `context/latest/knowledge.json` active index and retrieval policy
- `context/latest/diary/*.json` one file per diary entry (latest state)
- `context/latest/blog/*.json` one file per blog post (latest state)
- `resources/` manual files (`notes`, `docs`, `articles`, `newsletters`, `decision-logs`, `transcripts`)
- `tooling/scripts/sync_knowledge.py` feed sync + normalization
- `tooling/scripts/schedule_guard.py` 6:00 AM America/Chicago hour guard (delay-tolerant)
- `tooling/tests/` unit tests

## Default Ryva Retrieval Policy

Use this order for speed and signal quality:

1. `context/latest/knowledge.json`
2. `resources/**`
3. Expand to `context/latest/diary/*.json` and `context/latest/blog/*.json` only when needed

This keeps normal queries lightweight while preserving full entry-level detail.

## Sync Behavior

Run manually:

```bash
python3 tooling/scripts/sync_knowledge.py
```

What the sync does:

- Fetches `https://egeuysal.com/diary.json` and `https://egeuysal.com/blog.json`
- Validates schema and item fields (fail closed)
- Writes per-entry files atomically
- Rebuilds `context/latest/knowledge.json` deterministically
- Removes legacy duplicates (`context/latest/feeds.json`, `context/latest/feeds.md`, and other obsolete outputs)

## CI Schedule

Workflow: `.github/workflows/knowledge-sync.yml`

- Triggers: `schedule` + `workflow_dispatch`
- Daily target: **6:00 AM America/Chicago**
- DST-safe schedule: two UTC cron slots with runtime guard enforcing exact local time
- Concurrency guard prevents overlapping runs
- Commits only when content changed

## Local CI Test With act

```bash
act workflow_dispatch -j sync --container-architecture linux/amd64
```

- `git push` is skipped under `act`
- Use `linux/amd64` on Apple Silicon for better compatibility

## Security Defaults

Sync is secure-by-default:

- HTTPS-only feed fetch
- Request timeout and payload size caps
- JSON/schema validation before writing
- Atomic writes to prevent partial/corrupt files
- Non-zero exit on invalid or untrusted input

## Manual Knowledge Inputs

Drop your files under `resources/`:

- `resources/notes/`
- `resources/docs/`
- `resources/articles/`
- `resources/newsletters/`
- `resources/decision-logs/`
- `resources/transcripts/`

Authoring template: `resources/FORMAT.md`
