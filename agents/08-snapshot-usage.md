---
type: doc
date: 2026-03-23
author: Ryva
tags: [agents, snapshot, state]
---

# Using tooling/snapshot.json

Primary file:

- `tooling/snapshot.json`

## Purpose

`tooling/snapshot.json` is a static architecture snapshot that explains how Ryva works.

Use it to ground outputs in real implementation context:

- core entities and block types
- integration behavior
- recent commit and repo signals
- codebase structure and indexed paths

## Read Contract (Read-Only By Default)

Read first:

- `type`, `priority*`, and structural metadata
- `content.repo`, `content.defaultBranch`, and `content.description`
- `content.recentCommits`, `content.openIssues`, `content.openPRs`
- `content.codeContext` for implementation map and stack grounding

Treat age staleness as expected. The file is still valid as architecture context.

## Safety Rules

- Never store secrets in `tooling/snapshot.json`.
- Store URLs and IDs, not private tokens.
- Keep statements traceable to source links.
- Do not overwrite or regenerate this file unless the user explicitly requests it.
