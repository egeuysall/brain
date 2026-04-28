import { listDocs, toDocHref, toRoutePath, toTreePath } from "@/lib/docs"

export const SITE_URL = "https://brain.egeuysal.com"
export const ROUTES_PER_PAGE = 20

export function toAbsoluteUrl(href: string) {
  return new URL(href, SITE_URL).toString()
}

export function toMarkdownHref(routePath: string) {
  const resourcePath = routePath.replace(/^resources\/?/, "")
  return `/resources/${resourcePath}.md`
}

export function toRoutesApiHref(page: number) {
  return page <= 1 ? "/api/routes.json" : `/api/routes/${page}.json`
}

export async function listRouteManifestEntries() {
  const docs = await listDocs()

  return docs.map(doc => {
    const filePath = doc.filePath ?? doc.id
    const routePath = toRoutePath(filePath)
    const href = toDocHref(filePath)
    const legacyHref = `/${routePath.replace(
      /^resources\//,
      "src/content/docs/resources/"
    )}`
    const markdownHref = toMarkdownHref(routePath)

    return {
      id: doc.id,
      title: doc.data.title ?? null,
      description: doc.data.description ?? null,
      date: doc.data.date ?? null,
      tags: Array.isArray(doc.data.tags) ? doc.data.tags : [],
      kind: doc.data.kind ?? null,
      updatedAt: doc.data.updatedAt ?? null,
      sourcePath: filePath,
      treePath: toTreePath(filePath),
      routePath,
      href,
      url: toAbsoluteUrl(href),
      legacyHref,
      legacyUrl: toAbsoluteUrl(legacyHref),
      markdownHref,
      markdownUrl: toAbsoluteUrl(markdownHref)
    }
  })
}

export function createRouteManifestPayload(
  entries: Awaited<ReturnType<typeof listRouteManifestEntries>>,
  page = 1
) {
  const totalItems = entries.length
  const totalPages = Math.max(1, Math.ceil(totalItems / ROUTES_PER_PAGE))
  const currentPage = Math.min(Math.max(1, page), totalPages)
  const startIndex = (currentPage - 1) * ROUTES_PER_PAGE
  const pageEntries = entries.slice(startIndex, startIndex + ROUTES_PER_PAGE)
  const previousHref =
    currentPage > 1 ? toRoutesApiHref(currentPage - 1) : null
  const nextHref =
    currentPage < totalPages ? toRoutesApiHref(currentPage + 1) : null

  return {
    generatedAt: new Date().toISOString(),
    pagination: {
      page: currentPage,
      perPage: ROUTES_PER_PAGE,
      totalItems,
      totalPages,
      previousHref,
      previousUrl: previousHref ? toAbsoluteUrl(previousHref) : null,
      nextHref,
      nextUrl: nextHref ? toAbsoluteUrl(nextHref) : null
    },
    routes: [
      {
        kind: "page",
        routePath: "",
        href: "/",
        url: toAbsoluteUrl("/")
      },
      ...pageEntries.map(entry => ({
        kind: "doc",
        routePath: entry.routePath,
        href: entry.href,
        url: entry.url,
        sourcePath: entry.sourcePath,
        title: entry.title,
        markdownHref: entry.markdownHref,
        markdownUrl: entry.markdownUrl
      })),
      ...pageEntries.map(entry => ({
        kind: "legacy-doc",
        routePath: entry.legacyHref.replace(/^\//, ""),
        href: entry.legacyHref,
        url: entry.legacyUrl,
        sourcePath: entry.sourcePath,
        title: entry.title,
        markdownHref: entry.markdownHref,
        markdownUrl: entry.markdownUrl
      })),
      ...pageEntries.map(entry => ({
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
        href: "/api/routes.json",
        url: toAbsoluteUrl("/api/routes.json")
      }
    ],
    notes: pageEntries,
    docs: pageEntries
  }
}
