#!/usr/bin/env -S npx tsx

import fs from "node:fs/promises"
import path from "node:path"
import { chromium } from "playwright"

type Candidate = {
  query: string
  url: string
  postId: string
  author: string
  text: string
  createdAt?: string
}

const DEFAULT_QUERIES = [
  "standup waste",
  "engineering manager slack chaos",
  "PR confusion",
  "who owns this bug",
  "had to jump on a call to figure this out",
  "context is scattered in slack",
  "jira is useless",
  "things falling through cracks engineering"
]

function parseArgs(argv: string[]) {
  const args = new Map<string, string>()
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (!arg.startsWith("--")) continue
    const key = arg.slice(2)
    const value = argv[i + 1]
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for --${key}`)
    }
    args.set(key, value)
    i += 1
  }

  return {
    out: args.get("out"),
    maxPerQuery: Number(args.get("max-per-query") ?? "30"),
    scrolls: Number(args.get("scrolls") ?? "8"),
    headless: (args.get("headless") ?? "true") === "true",
    queries: args.get("queries")
      ? args
          .get("queries")!
          .split(",")
          .map(q => q.trim())
          .filter(Boolean)
      : DEFAULT_QUERIES
  }
}

async function collectFromPage(query: string, page: any): Promise<Candidate[]> {
  const rows: Candidate[] = await page.evaluate(q => {
    const seen = new Set<string>()
    const output: Candidate[] = []
    const articles = Array.from(document.querySelectorAll("article"))
    for (const article of articles) {
      const link = article.querySelector<HTMLAnchorElement>(
        'a[href*="/status/"]'
      )
      if (!link?.href) continue
      const match = link.href.match(/x\.com\/([^/]+)\/status\/(\d+)/)
      if (!match) continue
      const author = match[1]
      const postId = match[2]
      const url = `https://x.com/${author}/status/${postId}`
      if (seen.has(url)) continue
      seen.add(url)

      const textNode =
        article.querySelector('[data-testid="tweetText"]') ??
        article.querySelector('div[lang]')
      const text = (textNode?.textContent ?? "").replace(/\s+/g, " ").trim()

      const timeEl = article.querySelector("time")
      const createdAt = timeEl?.getAttribute("datetime") ?? undefined

      output.push({
        query: q,
        url,
        postId,
        author,
        text,
        createdAt
      })
    }
    return output
  }, query)

  return rows.filter(row => row.url && row.postId)
}

async function searchOneQuery(
  browser: any,
  query: string,
  maxPerQuery: number,
  scrolls: number
): Promise<Candidate[]> {
  const context = await browser.newContext({
    viewport: { width: 1280, height: 2200 },
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
  })
  const page = await context.newPage()
  const url = `https://x.com/search?q=${encodeURIComponent(
    `${query} lang:en -is:retweet`
  )}&src=typed_query&f=live`
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 })
  await page.waitForTimeout(2500)

  const combined = new Map<string, Candidate>()
  for (let i = 0; i < scrolls; i += 1) {
    const batch = await collectFromPage(query, page)
    for (const row of batch) {
      if (!combined.has(row.url)) combined.set(row.url, row)
    }
    if (combined.size >= maxPerQuery) break
    await page.mouse.wheel(0, 4000)
    await page.waitForTimeout(1200)
  }

  await context.close()
  return [...combined.values()].slice(0, maxPerQuery)
}

async function main() {
  const { out, maxPerQuery, scrolls, headless, queries } = parseArgs(
    process.argv.slice(2)
  )
  if (!out) throw new Error("Provide --out <path>")
  if (!Number.isFinite(maxPerQuery) || maxPerQuery < 1) {
    throw new Error("--max-per-query must be > 0")
  }
  if (!Number.isFinite(scrolls) || scrolls < 1) {
    throw new Error("--scrolls must be > 0")
  }

  const browser = await chromium.launch({ headless })
  const byQuery: Record<string, Candidate[]> = {}
  let total = 0
  for (const query of queries) {
    try {
      const items = await searchOneQuery(browser, query, maxPerQuery, scrolls)
      byQuery[query] = items
      total += items.length
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      byQuery[query] = [
        {
          query,
          url: "",
          postId: "",
          author: "",
          text: `ERROR: ${message}`
        }
      ]
    }
  }
  await browser.close()

  const payload = {
    generatedAt: new Date().toISOString(),
    source: "x_search_playwright",
    queries,
    total,
    results: byQuery
  }
  await fs.mkdir(path.dirname(out), { recursive: true })
  await fs.writeFile(out, `${JSON.stringify(payload, null, 2)}\n`, "utf8")
  console.log(JSON.stringify({ out, total, queries: queries.length }, null, 2))
}

main().catch(error => {
  const message = error instanceof Error ? error.message : String(error)
  console.error(`fetch_x_posts_playwright failed: ${message}`)
  process.exit(1)
})
