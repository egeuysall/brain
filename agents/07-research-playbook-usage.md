---
type: doc
date: 2026-03-23
author: Ryva
tags: [agents, research, sourcing, playbook]
---

# Using RESEARCH_PLAYBOOK.md

Primary source:

- `resources/threads/RESEARCH_PLAYBOOK.md`

## How Agents Should Use It

1. Use Exa MCP to generate candidate posts.
2. Verify candidates directly on source pages before inclusion.
3. For Reddit, prefer `old.reddit.com` verification for timestamp and body.
4. Enforce inclusion/exclusion filters from the playbook.
5. Produce dated outputs under `resources/threads/YYYY-MM-DD/`.

## Required Daily Outputs

- `YYYY-MM-DD-top-5-team-coordination-pain.md`
- Thread-level markdown files
- `candidates.json`
- `high_signal.json`
- `candidates.md`

## Command Examples

```bash
python3 tooling/scripts/reddit_harvest.py \
  --subreddits EngineeringManagers,ExperiencedDevs,ProductManagement,projectmanagement,devops \
  --min-hours 48 \
  --max-hours 72 \
  --output-json resources/threads/$(date +%F)/candidates.json \
  --output-md resources/threads/$(date +%F)/candidates.md
```

```bash
python3 tooling/scripts/reddit_harvest.py \
  --subreddits EngineeringManagers,ExperiencedDevs,ProductManagement \
  --only-high-signal \
  --output-json resources/threads/$(date +%F)/high_signal.json
```

## Quality Gate Before Publish

- Links open and are not removed.
- Timestamp verified on source page.
- Pain is first-person and operational.
- Suggested reply and DM are each under 80 words.
- Evidence is concrete, not generic.
