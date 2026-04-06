---
type: note
date: 2026-04-06
author: Codex
tags: [outreach, x, icp, standup, slack, jira, ownership, review]
source: internal-research
---

# Thread 2 - repo wide context deep review

## Platform

- X

## Link

- https://x.com/withmartian/status/2036844557359603761

## Original Post (Key Excerpt)

```text
We've been tracking AI code review tools across OSS, and a new category is emerging.

We're calling it "Deep Review":
Standard AI review: PR-level, fast, human in the loop
Deep Review: repo-wide context, runs autonomously in the background
```

## Why It Matches Ryva ICP

It names the exact shift from local review to system-level context that small shipping teams feel once change volume rises.

## Underlying Problem

PR-only review misses cross-file dependencies, prior decisions, and ownership history that cause regressions later.

## Suggested Public Response (Copy)

```text
“Repo-wide context” is the key distinction. PR review catches local issues. Deep review catches work that looks correct in isolation but conflicts with prior decisions, neighboring systems, or release ownership once it lands.
```

## Suggested DM Idea (Copy)

```text
Where does repo-wide context actually live for your team today: old PRs, Slack, docs, or just whoever still remembers it?
```

## Snapshot

- Author: @withmartian
- Captured date label: March 25, 2026
- Recency window: within past 14 days
