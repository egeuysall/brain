---
type: note
date: 2026-03-30
author: Codex
x_username: "@egewrk"
tags: [founder-posts, x, linkedin, reddit, ryva]
source_notes:
  - "Playwright X search attempted: https://x.com/search?q=standup%20waste&src=typed_query&f=live -> login flow wall"
  - "Playwright r.jina fallback attempted: https://r.jina.ai/http://x.com/search?q=who%20owns%20this%20bug&src=typed_query&f=live -> login content only"
  - "X fallback script used: tooling/scripts/fetch_posts.ts"
  - "X results: resources/threads/2026-03-30/founder-posts-x-results.json (5/5 queries OK, 15 posts; high keyword noise and 0 results for two coordination queries)"
  - "Reddit scripts run (required): tooling/scripts/reddit_harvest.py"
  - "Reddit outputs: resources/threads/2026-03-30/founder-posts-candidates.json and resources/threads/2026-03-30/founder-posts-high-signal.json"
  - "Reddit signal: https://www.reddit.com/r/startups/comments/1s7nbpo/we_kept_losing_decisions_after_meetings_so_i/"
  - "Reddit pushback signal from same thread: https://old.reddit.com/r/startups/comments/1s7nbpo/we_kept_losing_decisions_after_meetings_so_i/odau9dv/ and https://old.reddit.com/r/startups/comments/1s7nbpo/we_kept_losing_decisions_after_meetings_so_i/odbj1tt/"
  - "Diary continuity: context/latest/diary/2026-03-28.json (latest available diary in repo)"
---

X:
The fastest way to hide a real team problem is to describe it like a product pitch.

Today’s signal pull was rough:
- X queries like "engineering manager slack chaos" and "had to jump on a call to figure it out" returned nothing usable
- "PR confusion" was mostly non-engineering chatter
- on Reddit, a post about losing decisions after meetings got "is this promotion?" replies fast

When credibility drops, teams stop sharing real coordination failures and go back to private recap meetings.

Rule I am using now: one concrete failure, one decision gap, one next action. No tool framing first.

@egewrk

LinkedIn:
Yesterday’s diary theme for me was specific conversation depth over broad distribution.

Today’s crawl explained why that matters.

I pulled coordination queries on X and got very little operator signal. Two of the most relevant queries returned zero useful posts. Another query was full of non-engineering noise.

Then I looked at a Reddit thread about a real issue: teams losing decisions after meetings. The discussion quickly shifted to "is this promotion?" instead of the operating problem.

That is a trust problem, not just a tooling problem.

If the writing sounds like distribution, people ignore the process debt.
If the writing sounds like lived pain, they engage.

So I am tightening how I write founder content:
- lead with one failure mode
- state the missing decision explicitly
- end with one next step

No polish-first language.

Reddit:
Subreddit: r/startups
Title: How do you share coordination problems without getting read as promo?
Body:
I noticed something while reading recent startup threads.

A founder posted about losing decisions after meetings, and the comments turned into "is this promotion?" pretty quickly.

I get why that happens. But it also means we lose chances to talk about actual execution problems in small teams.

I am trying to figure out a better format for posting these without sounding like a pitch.

What format works best for you?

For example:
- one concrete failure that happened
- what decision was missing
- what changed after

Do you have a structure that keeps it useful and discussion-first?
