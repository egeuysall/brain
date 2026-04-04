---
type: note
date: 2026-04-04
author: Codex
tags: [outreach, x, icp, standup, slack, jira, ownership, review]
source: internal-research
---

# Thread 28 - playbook split reduces agent context drift

## Platform

- X

## Link

- https://x.com/Alex_Rogov_js/status/2038316896408216018

## Original Post (Key Excerpt)

```text
@akshay_pachaar This is the right mental model. CLAUDE.md = constitution, Skills = specialized playbooks. We moved our deploy checklist, PR review flow, and test scaffolding into separate skills. Context usage dropped noticeably and Claude stopped "forgetting" mid-session.
```

## Why It Matches Ryva ICP

The post maps directly to execution consistency problems in deployment, testing, and review handoffs.

## Underlying Problem

Single giant instruction contexts degrade reliability because task boundaries are not modularized.

## Suggested Public Response (Copy)

```text
This is a useful operations move: separate policy from procedure. Keep immutable guardrails in one place, and run task playbooks as independent artifacts with clear inputs/outputs. Teams usually see lower context drift and fewer half-completed workflows when each step has a narrow contract.
```

## Suggested DM Idea (Copy)

```text
Do you separate global guardrails from per-workflow playbooks in your delivery process?
```

## Snapshot

- Author: @Alex_Rogov_js
- Captured date label: March 29, 2026
- Recency window: within past week
