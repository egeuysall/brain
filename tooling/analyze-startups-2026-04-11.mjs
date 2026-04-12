import fs from "fs"

const inputPath =
  "/Users/egeuysal/Developer/brain/resources/threads/2026-04-11/startups.json"
const outputPath =
  "/Users/egeuysal/Developer/brain/resources/threads/2026-04-11/startups-json-data-first-shortlist.md"

const raw = JSON.parse(fs.readFileSync(inputPath, "utf8"))
const startups = raw.startups || []

const catBoost = {
  "Developer Tools": 5,
  Security: 5,
  Analytics: 4,
  "Customer Support": 3,
  SaaS: 3,
  "Artificial Intelligence": 3,
  Fintech: 3,
  Sales: 2
}

const tagBoost = {
  "developer-tools": 3,
  security: 3,
  privacy: 2,
  compliance: 2,
  cloud: 2,
  analytics: 2,
  "customer-support": 2,
  fintech: 2,
  communication: 2,
  communications: 2,
  automation: 1,
  saas: 1,
  ai: 1,
  sales: 1
}

const positive =
  /developer|developers|engineering|engineer|dev team|sre|it manager|procurement|data team|support team|product team|saas compan|b2b|compliance|security|privacy|api|integration|analytics|customer support|help desk/i
const negative =
  /creator|content creator|influencer|seo|agency|agencies|marketer|marketers|social media|video sales|ugc|coach|freelancer|blog|newsletter|therapy|psychologist|proxy provider|sneaker|gaming|game server/i

function formatMoney(n) {
  const value = Number(n || 0)
  if (!value) return "$0"
  return `$${Math.round(value).toLocaleString("en-US")}`
}

function score(startup) {
  const text = [
    startup.description,
    startup.problemSolved,
    startup.targetPersona,
    startup.valueProposition,
    startup.name
  ]
    .filter(Boolean)
    .join(" ")

  let score = 0
  if (startup.status === "active") score += 2
  if (startup.businessType === "B2B") score += 5
  if (startup.systemCategory === "Software") score += 2
  score += catBoost[startup.userCategory] || 0

  for (const tag of startup.tags || []) score += tagBoost[tag] || 0

  if (startup.founderTwitter) score += 2

  const followers = startup.founderFollowers || 0
  if (followers >= 200 && followers <= 15000) score += 3
  else if (followers > 0 && followers < 200) score += 1
  else if (followers > 15000 && followers <= 50000) score += 1

  const mrr = startup.mrr || 0
  if (mrr >= 10000) score += 3
  else if (mrr >= 2000) score += 2
  else if (mrr >= 500) score += 1

  if (positive.test(text)) score += 3
  if (negative.test(text)) score -= 4
  if (startup.onSale) score -= 3
  if (startup.stealthMode) score -= 2

  return score
}

function whyFit(startup) {
  const points = []
  if (startup.userCategory)
    points.push(`${startup.userCategory.toLowerCase()} company`)
  if ((startup.tags || []).includes("developer-tools"))
    points.push("developer-tools tag")
  if ((startup.tags || []).includes("security")) points.push("security tag")
  if ((startup.tags || []).includes("analytics")) points.push("analytics tag")
  if ((startup.tags || []).includes("customer-support"))
    points.push("customer-support tag")
  if (startup.businessType === "B2B") points.push("B2B")
  if (startup.founderTwitter)
    points.push(`founder on X (${startup.founderTwitter})`)
  if (
    (startup.founderFollowers || 0) >= 200 &&
    (startup.founderFollowers || 0) <= 15000
  ) {
    points.push("reply-sized audience")
  }
  if ((startup.mrr || 0) >= 2000)
    points.push(`real revenue (${formatMoney(startup.mrr)} MRR)`)
  return points.slice(0, 5).join(", ")
}

function caveat(startup) {
  const caveats = [
    "dataset lacks role",
    "dataset lacks team size",
    "dataset lacks recent trigger"
  ]
  if ((startup.founderFollowers || 0) === 0) caveats.push("no follower count")
  if ((startup.mrr || 0) === 0) caveats.push("pre-revenue or unsynced revenue")
  return caveats.join(", ")
}

const shortlist = startups
  .map(startup => ({ ...startup, score: score(startup) }))
  .filter(startup => startup.score >= 24)
  .filter(startup => startup.businessType === "B2B")
  .filter(startup => startup.status === "active")
  .filter(startup => startup.systemCategory === "Software")
  .filter(startup => startup.founderTwitter)
  .sort((a, b) => b.score - a.score || (b.mrr || 0) - (a.mrr || 0))
  .slice(0, 15)

const lines = []
lines.push("# Startups.json data-first shortlist")
lines.push("")
lines.push("Date: 2026-04-11")
lines.push("")
lines.push("Source: `resources/threads/2026-04-11/startups.json`")
lines.push("")
lines.push("Method:")
lines.push("- Script scored only local dataset fields.")
lines.push(
  "- Boosted B2B, software, devtools/security/analytics/support signals, founder X presence, moderate follower counts, and non-trivial MRR."
)
lines.push(
  "- Penalized agency/creator/SEO/social-heavy entries and sale listings."
)
lines.push(
  "- Important: dataset does **not** include role, team size, or recent founder trigger. This file is best used as priority-enrich list, not final DM list."
)
lines.push("")
lines.push("## Ranked table")
lines.push("")
lines.push(
  "| # | Startup | Founder | Category | MRR | X followers | score | why it surfaced |"
)
lines.push("|---|---|---|---|---:|---:|---:|---|")

shortlist.forEach((startup, index) => {
  lines.push(
    `| ${index + 1} | ${startup.name} | ${startup.founderName || "Unknown"} | ${startup.userCategory || "-"} | ${formatMoney(startup.mrr)} | ${startup.founderFollowers || 0} | ${startup.score} | ${whyFit(startup)} |`
  )
})

lines.push("")
lines.push("## Per startup")
lines.push("")

shortlist.forEach((startup, index) => {
  lines.push(`### ${index + 1}. ${startup.name}`)
  lines.push(
    `- Founder: ${startup.founderName || "Unknown"}${startup.founderTwitter ? ` ([x.com/${startup.founderTwitter}](https://x.com/${startup.founderTwitter}))` : ""}`
  )
  lines.push(`- Why fit: ${whyFit(startup)}.`)
  lines.push(
    `- Problem: ${startup.problemSolved || startup.description || "No problem statement in dataset."}`
  )
  lines.push(
    `- Target: ${startup.targetPersona || "No target persona in dataset."}`
  )
  lines.push(`- Caveat: ${caveat(startup)}.`)
  lines.push(
    `- Links: [TrustMRR](${startup.url})${startup.website ? `, [Website](${startup.website})` : ""}`
  )
  lines.push("")
})

fs.writeFileSync(outputPath, `${lines.join("\n")}\n`)
console.log(`wrote ${outputPath}`)
