#!/usr/bin/env -S npx tsx

type XSearchResponse = {
  data?: Array<{
    id: string
    text: string
    created_at?: string
    author_id?: string
    public_metrics?: {
      retweet_count?: number
      reply_count?: number
      like_count?: number
      quote_count?: number
      bookmark_count?: number
      impression_count?: number
    }
  }>
  includes?: {
    users?: Array<{
      id: string
      name?: string
      username?: string
    }>
  }
  errors?: Array<{ title?: string; detail?: string; type?: string }>
}

type QueryResult = {
  query: string
  ok: boolean
  error?: string
  posts: Array<{
    id: string
    text: string
    createdAt?: string
    authorId?: string
    authorUsername?: string
    authorName?: string
    metrics?: XSearchResponse["data"][number]["public_metrics"]
    url: string
  }>
}

const DEFAULT_QUERIES = [
  "standup waste",
  "engineering manager slack chaos",
  "PR confusion",
  "who owns this bug",
  "had to jump on a call to figure it out"
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
    maxResults: Number(args.get("max-results") ?? "10"),
    queries: args.get("queries")
      ? args
          .get("queries")!
          .split(",")
          .map(q => q.trim())
          .filter(Boolean)
      : DEFAULT_QUERIES
  }
}

function getBearerToken(): string {
  const token = process.env.X_BEARER_TOKEN?.trim()
  if (!token) {
    throw new Error("X_BEARER_TOKEN is required and must be non-empty.")
  }
  return token
}

async function searchOneQuery(
  query: string,
  token: string,
  maxResults: number
): Promise<QueryResult> {
  const params = new URLSearchParams({
    query,
    max_results: String(maxResults),
    "tweet.fields": "created_at,author_id,public_metrics",
    expansions: "author_id",
    "user.fields": "username,name"
  })
  const url = `https://api.x.com/2/tweets/search/recent?${params.toString()}`
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  })

  const payload = (await res.json()) as XSearchResponse

  if (!res.ok || payload.errors?.length) {
    const errFromPayload = payload.errors?.[0]
    const detail =
      errFromPayload?.detail ||
      errFromPayload?.title ||
      `HTTP ${res.status} ${res.statusText}`
    return { query, ok: false, error: detail, posts: [] }
  }

  const usersById = new Map(
    (payload.includes?.users ?? []).map(user => [user.id, user] as const)
  )
  const posts =
    payload.data?.map(tweet => {
      const user = tweet.author_id ? usersById.get(tweet.author_id) : undefined
      return {
        id: tweet.id,
        text: tweet.text,
        createdAt: tweet.created_at,
        authorId: tweet.author_id,
        authorUsername: user?.username,
        authorName: user?.name,
        metrics: tweet.public_metrics,
        url: `https://x.com/${user?.username ?? "i"}/status/${tweet.id}`
      }
    }) ?? []

  return { query, ok: true, posts }
}

async function main() {
  const { out, maxResults, queries } = parseArgs(process.argv.slice(2))
  if (!out) {
    throw new Error("Provide --out <path>.")
  }
  if (!Number.isInteger(maxResults) || maxResults < 10 || maxResults > 100) {
    throw new Error("--max-results must be an integer between 10 and 100.")
  }
  if (queries.length === 0) {
    throw new Error("At least one query is required.")
  }

  const token = getBearerToken()
  const all: QueryResult[] = []
  for (const query of queries) {
    const result = await searchOneQuery(query, token, maxResults)
    all.push(result)
  }

  const fs = await import("node:fs/promises")
  const path = await import("node:path")
  await fs.mkdir(path.dirname(out), { recursive: true })
  const output = {
    generatedAt: new Date().toISOString(),
    source: "x_api_recent_search",
    queries,
    results: all
  }
  await fs.writeFile(out, `${JSON.stringify(output, null, 2)}\n`, "utf8")

  const okCount = all.filter(r => r.ok).length
  const totalPosts = all.reduce((sum, r) => sum + r.posts.length, 0)
  console.log(
    JSON.stringify(
      { okQueries: okCount, totalQueries: all.length, totalPosts, out },
      null,
      2
    )
  )
}

main().catch(error => {
  const message = error instanceof Error ? error.message : String(error)
  console.error(`fetch_posts failed: ${message}`)
  process.exit(1)
})
