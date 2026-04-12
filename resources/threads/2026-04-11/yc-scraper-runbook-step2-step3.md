# YC scraper runbook

Date: 2026-04-11

Repo found at: `/Users/egeuysal/yc-scraper`

Step 1 already done:

- `start_urls.txt` exists at `/Users/egeuysal/yc-scraper/scrapy-project/ycombinator/start_urls.txt`

## Goal

Use YC scraper output to find:

- B2B / technical companies
- small teams: 5-15
- at least 2 engineers likely
- founder social links present
- good fit for Ryva invisible-state pain

## Step 2: scrape company data

```bash
cd /Users/egeuysal/yc-scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd scrapy-project
scrapy runspider ycombinator/spiders/yscraper.py -o /Users/egeuysal/Developer/brain/resources/threads/2026-04-11/yc-output.jl
```

Notes:

- Output path points back into this repo.
- `.jl` best for big runs.

## Step 3: fast shortlist filter

This filter does **not** prove recent trigger. It gives best enrichment queue.

```bash
python3 - <<'PY'
import pandas as pd

inp = "/Users/egeuysal/Developer/brain/resources/threads/2026-04-11/yc-output.jl"
out = "/Users/egeuysal/Developer/brain/resources/threads/2026-04-11/yc-shortlist.csv"

df = pd.read_json(inp, lines=True)

tags_text = df["tags"].apply(lambda x: " ".join(x) if isinstance(x, list) else "")
desc = (
    df["company_name"].fillna("") + " " +
    df["short_description"].fillna("") + " " +
    df["long_description"].fillna("") + " " +
    tags_text.fillna("")
).str.lower()

b2b_terms = r"b2b|developer|devtools|developer tools|api|infra|infrastructure|security|compliance|analytics|workflow|engineering|support|data|platform|tooling|enterprise software|saas"
bad_terms = r"consumer|creator|gaming|social|dating|food|travel|content creator|influencer"

df["fit_score"] = 0
df.loc[df["status"].eq("Active"), "fit_score"] += 2
df.loc[df["team_size"].between(5, 15, inclusive="both"), "fit_score"] += 4
df.loc[df["num_founders"].between(2, 4, inclusive="both"), "fit_score"] += 1
df.loc[desc.str.contains(b2b_terms, na=False), "fit_score"] += 4
df.loc[desc.str.contains(bad_terms, na=False), "fit_score"] -= 4
df.loc[df["founder_details"].astype(str).str.contains("twitter.com|x.com|linkedin.com", case=False, na=False), "fit_score"] += 2

cols = [
    "company_name",
    "batch",
    "status",
    "team_size",
    "num_founders",
    "founders_names",
    "tags",
    "location",
    "website",
    "linkedin_url",
    "fit_score",
    "short_description",
    "long_description",
]

short = (
    df[
        df["status"].eq("Active")
        & df["team_size"].between(5, 15, inclusive="both")
        & desc.str.contains(b2b_terms, na=False)
    ][cols]
    .sort_values(["fit_score", "team_size"], ascending=[False, True])
    .head(150)
)

short.to_csv(out, index=False)
print(f"wrote {out}")
print(short.head(20).to_string(index=False))
PY
```

## Step 4: enrich for strict outreach use

Need add 3 missing checks before DM:

- role = CEO or CTO
- recent trigger <= 60d
- active posting history

Best manual order:

1. Open founder LinkedIn / X from `founder_details`
2. Check recent post for standups / async / blockers / hiring / process pain
3. Reject if no fresh trigger
4. Keep only CEO / CTO

## Strong post-search terms

Use on founder profile or web search:

- `standup`
- `async`
- `blocker`
- `PR`
- `review`
- `Slack`
- `Jira`
- `hiring engineer`
- `process`
- `shipping`
- `coordination`
- `ownership`

## Tight final filters

Reject if:

- solo founder
- team size outside 5-15
- no social posting history
- generic build-in-public only
- marketing-only founder
- no fresh trigger

Keep if:

- founder clearly hands-on
- company technical enough that eng coordination matters
- post gives believable DM opener

## Nice follow-up artifact

After `yc-shortlist.csv`, next file to generate:

- `yc-shortlist-enriched.md`

Format:

- Name
- Role
- Company
- Team size proof
- Trigger
- Why pain
- Why reply
- DM opener
