# Tooling

Automation code for this knowledge repository.

- `scripts/`: sync, schedule guard, and research support scripts
- `tests/`: unit tests for tooling scripts

## Script Index

- `tooling/scripts/sync_knowledge.py`: sync external knowledge feeds into local context files
- `tooling/scripts/schedule_guard.py`: validate scheduled automation constraints
- `tooling/scripts/reddit_fix_json.py`: sanitize malformed Reddit JSON payloads and validate JSON
- `tooling/scripts/reddit_harvest.py`: harvest Reddit candidates from `old.reddit.com` with age-window filters and high-signal heuristics

## Local Checks

```bash
python3 -m unittest discover -s tooling/tests -p 'test_*.py'
python3 tooling/scripts/sync_knowledge.py
```

## Reddit Research Helpers

```bash
# 1) Sanitize malformed JSON (if using reddit JSON endpoints)
python3 tooling/scripts/reddit_fix_json.py --input /tmp/raw.json --output /tmp/clean.json --stats

# 2) Harvest candidates directly from old.reddit
python3 tooling/scripts/reddit_harvest.py \
  --subreddits EngineeringManagers,ExperiencedDevs,ProductManagement,projectmanagement,devops \
  --min-hours 48 \
  --max-hours 72 \
  --output-json resources/threads/2026-03-24/candidates.json \
  --output-md resources/threads/2026-03-24/candidates.md
```

Local GitHub Actions run with `act`:

```bash
act workflow_dispatch -j sync --container-architecture linux/amd64
```
