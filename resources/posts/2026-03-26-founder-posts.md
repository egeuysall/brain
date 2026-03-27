---
type: note
date: 2026-03-26
author: Codex
x_username: "@egewrk"
tags: [founder-posts, x, linkedin, reddit, ryva]
source_notes:
  - "Reddit thread signal: resources/threads/2026-03-27/2026-03-27-thread-3-standup-blockers-surface-too-late.md"
  - "Reddit thread signal: resources/threads/2026-03-27/2026-03-27-thread-7-pr-velocity-without-quality-visibility.md"
  - "Reddit thread signal: resources/threads/2026-03-27/2026-03-27-thread-1-new-pm-slack-decision-loss.md"
  - "Diary continuity: context/latest/diary/2026-03-25.json"
  - "X API fallback attempted: /tmp/ryva-signals/x_search_raw_2026-03-26.jsonl (account credits depleted)"
---

X:
PR velocity up and standups still saying “still working on X” for day 3 is fake progress.

You are measuring motion, not state.

The signal that matters is state change:

- what changed since yesterday
- what is blocked now
- who owns unblock

If those 3 are missing, the sprint risk is already here.

More build-in-public notes at @egewrk.

LinkedIn:
A pattern from this week keeps repeating:

Teams improve visible activity, then still get surprised late.

I saw posts from engineering managers saying PR velocity is up but quality ROI is unclear, and others saying the same standup update repeats for 3 days before anyone realizes work is actually blocked.

That is the same root issue.

We optimize for motion metrics:

- faster standups
- more PRs
- more updates

But delivery reliability comes from state-change clarity:

- what decision changed
- what blocker appeared
- who owns the next unblock

Yesterday I was tightening this exact principle in our own output: one decision per block, explicit ownership, no blended summaries.

If your team feels “busy but surprised,” check whether you track state change or just activity.

Reddit:
Subreddit: r/EngineeringManagers
Title: PR velocity is up, but repeated standup updates still hide blockers. How are you detecting fake progress?
Body:
I keep seeing this combo:

- PR count goes up
- standups are short and clean
- same person says “still working on X” for 2-3 days
- blocker only gets explicit when sprint risk is already obvious

Feels like we are good at tracking motion, but weak at tracking state change.

I am testing a simple rule internally:
if the update is materially the same for 2 days, we require explicit blocker owner + next unblock decision.

Not more meetings, just a forced transition from status text to ownership.

Has anyone tried a similar rule?
Did it help, or did it create noise?
