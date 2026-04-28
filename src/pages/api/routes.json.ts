import { listRouteManifestEntries } from "@/lib/route-manifest"

export async function GET() {
  const entries = await listRouteManifestEntries()

  return new Response(
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        routes: [
          {
            kind: "page",
            routePath: "",
            href: "/"
          },
          ...entries.map(entry => ({
            kind: "doc",
            routePath: entry.routePath,
            href: entry.href,
            url: entry.url,
            sourcePath: entry.sourcePath,
            title: entry.title,
            markdownHref: entry.markdownHref,
            markdownUrl: entry.markdownUrl
          })),
          ...entries.map(entry => ({
            kind: "legacy-doc",
            routePath: entry.legacyHref.replace(/^\//, ""),
            href: entry.legacyHref,
            url: entry.legacyUrl,
            sourcePath: entry.sourcePath,
            title: entry.title,
            markdownHref: entry.markdownHref,
            markdownUrl: entry.markdownUrl
          })),
          ...entries.map(entry => ({
            kind: "markdown",
            routePath: entry.markdownHref.replace(/^\//, ""),
            href: entry.markdownHref,
            url: entry.markdownUrl,
            sourcePath: entry.sourcePath,
            title: entry.title
          })),
          {
            kind: "api",
            routePath: "api/routes.json",
            href: "/api/routes.json"
          }
        ],
        notes: entries.filter(entry =>
          entry.routePath.startsWith("resources/notes/")
        ),
        docs: entries
      },
      null,
      2
    ),
    {
      headers: {
        "Content-Type": "application/json; charset=utf-8"
      }
    }
  )
}
