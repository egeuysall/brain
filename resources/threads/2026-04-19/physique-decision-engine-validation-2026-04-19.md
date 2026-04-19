# Physique Decision Engine Demand Validation (Reddit + App Store)

Date: 2026-04-19
Mode: caveman/full

## Short summary

Signal **real** for "what next" pain.
Signal strongest on Reddit (phase + adjustment confusion).
App Store signal mostly: tracking friction + bad goals + weak coaching.

Blunt call: **YES, build now as narrow web MVP**.
Not full tracker. Decision engine only.

Data scope:

- Reddit: 31 recent posts scanned (0-30 days), 22 high-signal hits.
- App Store: 6 apps, 1,086 recent reviews (30d), 532 complaint-leaning filtered reviews.
- Freshness: cutoff around `2026-03-20` to `2026-04-19`.

---

## Section A — Core validation

### Do users want continuous decision guidance across cut/bulk/maintenance?

**Yes, medium-strong.**
Not phrased as "decision engine". Phrased as: "bulk stalling", "plateau", "how maintain", "macro adjustment", "goal wrong", "coaching useless".

### Evidence (Reddit + App Store)

Reddit (direct behavior pain):

- [Bulk is stalling](https://www.reddit.com/r/leangains/comments/1spa8gm/bulk_is_stalling/) — "after hard cut... strength not going up."
- [macro adjustment (non premium version)](https://www.reddit.com/r/Myfitnesspal/comments/1sndxvk/macro_adjustment_non_premium_version/) — "in cut... trying do macros... calculated calories."
- [Plateau affecting motivation](https://www.reddit.com/r/loseit/comments/1sq5ipz/plateau_really_affecting_my_motivation_how_did/) — "scale isn't moving... still calorie deficit."
- [maintain habits busy schedule](https://www.reddit.com/r/loseit/comments/1spxm8s/ways_to_maintain_healthy_weight_loss_habits_with/) — maintenance friction after loss phase.

App Store (tool failure around targets/coaching):

- MacroFactor review, 2026-03-24: "coaching... all it does is lower calories each week." ([link](https://itunes.apple.com/us/review?id=1553503471&type=Purple%20Software))
- MacroFactor review, 2026-04-13: "setting unhealthy caloric goals... can't reset... manually override." ([link](https://itunes.apple.com/us/review?id=1553503471&type=Purple%20Software))
- Cal AI review, 2026-04-14: "goal of 461 calories/day... 162 calories/day." ([link](https://itunes.apple.com/us/review?id=6480417616&type=Purple%20Software))
- Lose It! review, 2026-04-14: "goal gain 5 pounds... only diet plans for losing." ([link](https://itunes.apple.com/us/review?id=297368629&type=Purple%20Software))

### Strength of signal

- Phase/decision confusion: **strong on Reddit**, moderate on App Store.
- Explicit "tell me what to do next": **moderate** (not dominant wording).
- Manual adjustment behavior: **strong**.

### Are users already solving manually?

**Yes.**
Manual macro math, manual calorie edits, manual override attempts, manual interpretation of plateaus.

---

## Section B — Top pain patterns

### 1) Phase decision confusion (cut vs bulk vs maintain)

1. pain pattern: users unsure phase switch timing + next phase settings.
2. who has it: intermediate lifters, weight-loss users near/after goal, recomp users.
3. frequency: weekly-daily.
4. evidence count: Reddit `phase_cut_bulk_maintain=10` posts; App phase-related mentions `19` reviews (mixed pos/neg, not all direct pain).
5. current workaround: ask subreddit, trial-error calories, stick longer in wrong phase.
6. why tools fail: trackers log numbers; weak transition logic.
7. evidence snippets:
   - "Bulk is stalling... after hard cut." ([Reddit](https://www.reddit.com/r/leangains/comments/1spa8gm/bulk_is_stalling/))
   - "in a cut... trying do my macros." ([Reddit](https://www.reddit.com/r/Myfitnesspal/comments/1sndxvk/macro_adjustment_non_premium_version/))
   - "goal gain 5 pounds... gave losing plan options." ([App Store](https://itunes.apple.com/us/review?id=297368629&type=Purple%20Software))
8. map to idea: **direct**.
9. monetization speed: fast-medium.
10. verdict: **PURSUE**.

### 2) Trend plateau -> no clear calorie adjustment next step

1. pain pattern: "weight not moving" but no clear adjustment rule.
2. who has it: active cutters, long-term losers, lean bulkers.
3. frequency: weekly check-in pain.
4. evidence count: Reddit `plateau_weight_stall=2` + `calorie_adjustment_manual=5`; App unsafe/wrong target `7` + manual fixing `29` (indirect).
5. current workaround: cut more, random tweaks, cheat-day compensations, ask forum.
6. why tools fail: target numbers static/opaque; users distrust algorithm outputs.
7. evidence snippets:
   - "scale isn't moving... still at calorie deficit." ([Reddit](https://www.reddit.com/r/loseit/comments/1sq5ipz/plateau_really_affecting_my_motivation_how_did/))
   - "do calories cancel out? under maintenance 6 days." ([Reddit](https://www.reddit.com/r/loseit/comments/1spxscz/do_calories_cancel_out/))
   - "coaching... lowers calories each week." ([App Store](https://itunes.apple.com/us/review?id=1553503471&type=Purple%20Software))
   - "goal... 461 calories/day." ([App Store](https://itunes.apple.com/us/review?id=6480417616&type=Purple%20Software))
8. map to idea: **direct**.
9. monetization speed: fast.
10. verdict: **PURSUE**.

### 3) Tool gives data, user still decide alone

1. pain pattern: data logging exists; action guidance weak/absent.
2. who has it: tracker users who want outcomes, not dashboards.
3. frequency: daily.
4. evidence count: Reddit `next_step_confusion=4`, `tool_guidance_gap=10`; App coaching-not-actionable `2` direct, many indirect confusion reports.
5. current workaround: subreddit checks, self-interpret charts, manual override.
6. why tools fail: feature-heavy trackers optimize logging UX, not action engine.
7. evidence snippets:
   - "I'm not sure... rolling 7 day average" ([Reddit](https://www.reddit.com/r/Myfitnesspal/comments/1so1te0/nutrition_week_view_changed_to_rolling_7_day/))
   - "how do you actually track calories?" ([Reddit](https://www.reddit.com/r/loseit/comments/1spxyff/how_do_you_actually_track_calories/))
   - "issue with supposed coaching." ([App Store](https://itunes.apple.com/us/review?id=1553503471&type=Purple%20Software))
8. map to idea: **high**.
9. monetization speed: medium.
10. verdict: **PURSUE (keep narrow)**.

### 4) Logging + data-cleaning fatigue kills adherence

1. pain pattern: too many clicks, wrong entries, sync bugs, manual corrections.
2. who has it: all tracker users.
3. frequency: daily.
4. evidence count: Reddit tool-friction `10`; App `logging_overhead=56`, `manual_data_fixing=29`.
5. current workaround: manual edits, app switching, quit tracking.
6. why tools fail: input burden high; trust in data low.
7. evidence snippets:
   - "phantom calories added" ([Reddit](https://www.reddit.com/r/Myfitnesspal/comments/1sl7c8z/daily_calorie_total_different_from_nutrition/))
   - "renpho weight not syncing" ([Reddit](https://www.reddit.com/r/Myfitnesspal/comments/1smtk0b/renpho_weight_not_syncing/))
   - "hard time logging meals" ([App Store](https://itunes.apple.com/us/review?id=341232718&type=Purple%20Software))
   - "have to update macros manually" ([App Store](https://itunes.apple.com/us/review?id=6480417616&type=Purple%20Software))
8. map to idea: **partial** (your product can avoid this by low-input design).
9. monetization speed: medium.
10. verdict: **MAYBE** (supporting pain, not core wedge).

### 5) Post-cut maintenance adherence breakdown

1. pain pattern: after loss phase, habits break under life stress.
2. who has it: post-goal users, busy schedules.
3. frequency: weekly.
4. evidence count: Reddit `post_cut_or_maintenance_struggle=3`; App phase mentions include maintenance but low direct wording.
5. current workaround: motivation threads, ad-hoc rules.
6. why tools fail: no simple maintenance transition protocol.
7. evidence snippets:
   - "maintain healthy habits with busy schedule?" ([Reddit](https://www.reddit.com/r/loseit/comments/1spxm8s/ways_to_maintain_healthy_weight_loss_habits_with/))
   - "can't stick to diet/cut... driving me insane" ([Reddit](https://www.reddit.com/r/loseit/comments/1sq2ypm/i_cant_stick_to_a_dietcut_and_its_driving_me/))
8. map to idea: **direct**.
9. monetization speed: medium.
10. verdict: **PURSUE as phase-2**.

---

## Section C — Behavioral risks

### Do users follow structured plans?

Partly.
Evidence: "can't stick to diet/cut" + motivation crash on plateau.
Risk high for strict plans.
Implication: engine must give tiny next step, not rigid protocol.

### Control vs flexibility?

Users want both.
They want clear recommendation **and** override.
Evidence: MacroFactor complaints about inability to reset/override targets.

### Is daily logging realistic?

Only if logging friction minimal.
App Store full of "too many clicks", "hard logging", "manual fixes".
Implication: weight-only core loop likely better than full food logging.

### Long-term trust needed?

Yes.
If engine gives bad targets once, trust drops fast.
Evidence: unsafe calorie target complaints (461/162/800/980 etc).
Need conservative guardrails + explainable adjustment logic.

---

## Section D — Best wedge (refined)

Wedge:
**"Tell me exact calorie change for tomorrow from 7-day weight trend."**

Product shape (web-first, no full app):

- input (60 sec/day): morning weight, optional "adherence yes/no".
- output (single card):
  - `On track` / `Off track`
  - `Tomorrow: +150 / -150 / hold`
  - `Phase: cut / maintain / lean bulk`
  - `Why: trend + rate-of-change`
- safety rails: minimum calories by sex/size bounds; no extreme outputs.

No tracker clone. No workout logging. No dashboard maze.

---

## Section E — What to avoid

- Building full calorie tracker.
- Food database wars/barcode wars.
- "AI coach" with vague chat.
- Mobile-first heavy build before proving demand.
- Complex onboarding requiring macro literacy.
- Black-box recommendations without explanation/override.

---

## Section F — Final verdict

### Build now?

**YES (narrow scope).**

### Demand strength

- Core decision pain: **medium-strong**.
- Direct "tell me next action" wording: **moderate**.
- Manual adjustment + phase confusion + plateau frustration: **strong enough**.

### Fastest validation path (3-5 days)

Day 1:

- landing page + waitlist + promise: "tomorrow calorie action from weight trend."
- CTA: upload 14 days weight CSV or manual entry.

Day 2:

- concierge engine in script/sheet.
- output daily action by email/telegram for first 20 users.

Day 3-4:

- track adherence + confidence score ("I knew what to do today").
- compare baseline confusion vs after 3 days.

Day 5:

- ask prepaid pilot: $9-19/month.
- success threshold: 20 users, >=40% daily check-in, >=25% willing to pay.

Clear yes/no:

- If check-ins + prepaid hit threshold -> build product.
- If not -> pain maybe tracking fatigue, not decision pain. Pivot fast.
