---
type: note
date: 2026-03-24
author: Codex
tags: [reddit, reliability, metrics, platform]
source: https://www.reddit.com/r/ExperiencedDevs/comments/1rztutg/how_to_measure_failure_rate_for_retryable_jobs/
---

# Thread 2 - Retryable jobs distort failure metrics

## Quick Actions

- Reddit thread: [Open post](https://www.reddit.com/r/ExperiencedDevs/comments/1rztutg/how_to_measure_failure_rate_for_retryable_jobs/)
- Local index: [Back to top 5](./2026-03-24-top-5-team-coordination-pain.md)

## Snapshot

- Role signal: Platform/reliability operator
- Time signal: 2026-03-21T15:09:47+00:00 (within 48-72h at collection)
- Situation type: KPI definition conflict affecting incident and planning signals

## Pain Summary

The author explains that one retry-heavy job can overwhelm attempt-based failure metrics and misrepresent fleet health. They are deciding between job-level and attempt-level views and need a framework that balances customer impact with system burden.

## Why This Is High-Signal

- First-person operational scenario with real metric distortion.
- Explicit tradeoff between two valid but incomplete reliability definitions.
- Decision quality risk: priorities shift based on whichever metric dominates.

## Suggested Public Reply (Copy)

```text
This is a real ops trap. Attempt-level rates tell retry burden, but they can bury actual job outcomes. A split view usually works better: job success/failure for customer impact, plus retry intensity for system strain.
```

## Suggested DM (Copy)

```text
Great example of metric design driving wrong decisions. If helpful, I can share a two-tier reliability scorecard (job outcome + retry burden + P95 attempts) that avoids single noisy jobs hijacking priority.
```

## Personalization Notes

- Mirror their numeric example to prove you read the post.
- Keep recommendation in terms of dashboard semantics, not abstract stats.
- Avoid prescribing one metric as universally correct.
