# What To Build Next (Evidence-Based)

Source idea: [fitness-app-idea.md](https://bri.egeuysal.com/egeuysall/fitness-app-idea.md)  
Validation window: **2026-04-09 to 2026-04-22 (UTC)**

## What this actually proves

People are not asking for full plans.  
They are repeatedly asking for **next decisions under pressure**.

Biggest pain is food/adherence decision loops.  
Workout adaptation matters, but it is secondary.

Trust is fragile in this category.  
Paywall friction + wrong/inconsistent outputs destroy retention quickly.

Evidence:

- `meal_or_calorie_decision`: **168** posts (from `reddit-search-14d*.json` rollup)
- `adherence_breaks`: **82** posts
- `crowded_or_equipment`: **44** posts
- Low-star app complaints: pricing/paywall **149**, reliability/sync **109** (from App Store pull)
- See: `analysis-summary.json`, `appstore-low-star-14d.json`, `appstore-workout-low-star-14d.json`

---

## What you build first

### 1) Meal and deficit correction (Primary Wedge)

Core loop:

- User inputs: meal photo or rough text ("ate burger + fries")
- Engine outputs exactly one decision:
  - "Eat this, then add protein at dinner"
  - "Too high for target, cut carbs later"
  - "Hold current plan, no extra correction"

Why first:

- Highest pain density is calorie/meal confusion and immediate "what now?"

References:

- [r/workout: confused about deficit + protein goals](https://www.reddit.com/r/workout/comments/1sos2gp/im_really_confused_about_maintaining_a_calorie/)
- [r/loseit: can’t eat to target / calorie confusion](https://www.reddit.com/r/loseit/comments/1sp08or/cant_seem_to_eat_less_than_2000_calories_a_day/)
- [r/WeightLossAdvice: “eating healthy” but not losing](https://www.reddit.com/r/WeightLossAdvice/comments/1ssy8us/im_eating_healthy_but_not_losing_weight_what_am_i/)

---

### 2) Adherence rescue (Daily Retention Engine)

Core loop:

- User input: "I messed up" / "I binged" / "I went off plan"
- Output: one immediate stabilizing action:
  - "Hold calories tomorrow"
  - "High-protein next meal"
  - "No punishment cardio"

Important rule:

- No guilt language.
- No full reset plans.
- Only the next actionable move.

Why second:

- This is frequent and emotionally urgent; users fail here repeatedly.

References:

- [r/loseit: binging/extreme hunger after deficit](https://www.reddit.com/r/loseit/comments/1sq93jg/struggling_with_bingingextreme_hunger_after/)
- [r/loseit: gained 15 lbs in a month after stress](https://www.reddit.com/r/loseit/comments/1st14xr/gained_15lbs_in_a_month/)
- [r/WeightLossAdvice: “FOOD. NOISE. HELP.”](https://www.reddit.com/r/WeightLossAdvice/comments/1st1bqa/food_noise_help/)

---

### 3) Crowded gym mode (Secondary but Valuable)

Core loop:

- User taps: "Gym crowded"
- Output: 3-exercise no-wait fallback (same target muscle group, minimal setup)

Why third:

- Real pain, but smaller than food/adherence loops in this 14-day window.

References:

- [r/workout: “gym was really crowded” adaptation](https://www.reddit.com/r/workout/comments/1sryp3f/today_was_really_crowded_in_the_gym_and_somehow_i/)
- [r/workout: first-time gym, super crowded](https://www.reddit.com/r/workout/comments/1sl3x24/i_cant_even_do_some_exercises_with_minimum_weight/)
- [r/workout: beginner, small space/home constraints](https://www.reddit.com/r/workout/comments/1srfz4j/beginner_woman_restarting_fitness_at_home_small/)

---

## What to delay

- Full workout periodization systems
- Long-term physique prediction
- Detailed macro micromanagement
- Heavy onboarding and profile setup

Why:

- Lower alignment with top pain signals in this dataset.

---

## Positioning

Not tracker.  
Not generic AI coach.

Use:

- **"Get the exact next move for your cut/bulk in seconds."**
- **"Built for messy days, not perfect plans."**

---

## Viral loop (from observed behavior)

People share struggle moments, not clean plans.

Build share cards:

- Situation: "Gym packed" / "Meal was off" / "I slipped"
- Decision: one correction
- Blunt line: "Still on track because of this move"

---

## Paywall + trust warning (critical)

Trust/purchase friction is a major churn driver in low-star reviews.

Observed in 14-day low-star data:

- Pricing/paywall trust complaints: **149**
- Reliability/sync/data-loss complaints: **109**

References:

- [Cal AI](https://apps.apple.com/us/app/cal-ai-calorie-tracker/id6480417616)
- [MyFitnessPal](https://apps.apple.com/us/app/myfitnesspal-calorie-counter/id341232718)
- [Fitbod](https://apps.apple.com/us/app/fitbod-gym-fitness-planner/id1041517543)
- [JEFIT](https://apps.apple.com/us/app/jefit-workout-plan-gym-tracker/id449810000)

Product implication:

- First answer must feel useful and believable immediately.
- Do not hard-block early utility behind paywall.

---

## Security and safety requirements (must ship with v1)

- Reject or safely handle ED-adjacent and self-harm-adjacent prompts.
- Add age-sensitive guardrails for minors (no aggressive calorie cuts).
- Never output extreme deficit recommendations.
- Include "uncertain" mode when confidence is low; ask one clarifying question.
- Keep outputs conservative by default (safe defaults over aggressive optimization).

---

## Real product definition

Context-aware decision engine.

Inputs:

- body context
- meal/intake context
- current situation (stress/social/crowded gym/time)

Output:

- **one action now**

---

## Final call

Do not build a full fitness operating system first.

Build a **decision engine for messy days**:

1. Meal/deficit correction
2. Adherence rescue
3. Crowded gym fallback

Everything else can layer after this core loop proves retention.
